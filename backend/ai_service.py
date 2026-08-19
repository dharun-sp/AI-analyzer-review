import json
import os
import re
import time
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))
API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
MODEL_NAME = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite').strip()
BATCH_SIZE = max(1, int(os.getenv('GEMINI_BATCH_SIZE', '25')))
MAX_RETRIES = max(0, int(os.getenv('GEMINI_MAX_RETRIES', '3')))
RETRY_BASE_SECONDS = float(os.getenv('GEMINI_RETRY_BASE_SECONDS', '2'))
client = genai.Client(api_key=API_KEY) if API_KEY else None

def _clean_json(text):
    text = (text or '').strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.I)
        text = re.sub(r'\s*```$', '', text)
    return text.strip()

def _normalise(item: Any):
    if not isinstance(item, dict):
        return {'sentiment':'neutral','positive_features':[],'negative_features':[]}
    s = str(item.get('sentiment','neutral')).lower().strip()
    if s not in {'positive','negative','neutral'}: s = 'neutral'
    def fs(v):
        return [str(x).strip() for x in v[:8] if str(x).strip()] if isinstance(v,list) else []
    return {'sentiment':s,'positive_features':fs(item.get('positive_features',[])),'negative_features':fs(item.get('negative_features',[]))}

def local_fallback(review):
    text=review.lower()
    pos={'good','great','excellent','love','loved','amazing','perfect','happy','fast','easy','comfortable','recommend','worth'}
    neg={'bad','terrible','awful','hate','hated','poor','slow','broken','expensive','worst','disappointed','problem','issue','difficult'}
    ph=[w for w in pos if re.search(rf'\b{re.escape(w)}\b',text)]
    nh=[w for w in neg if re.search(rf'\b{re.escape(w)}\b',text)]
    s='positive' if len(ph)>len(nh) else 'negative' if len(nh)>len(ph) else 'neutral'
    return {'sentiment':s,'positive_features':[],'negative_features':[]}

def _request_batch(reviews):
    if not client:
        raise RuntimeError('Gemini client is not configured. Check GEMINI_API_KEY in backend/.env')
    numbered='\n'.join(f'REVIEW {i+1}: {r}' for i,r in enumerate(reviews))
    prompt = f'''Analyze each customer review independently. Never merge reviews.
Return ONLY a JSON array with exactly {len(reviews)} objects, in the same order as the input.
Each object: {{"sentiment":"positive|negative|neutral","positive_features":["short feature"],"negative_features":["short feature"]}}
Features are short 1-3 word topics. Use empty arrays when none apply.

{numbered}'''
    last=None
    for attempt in range(MAX_RETRIES+1):
        try:
            response=client.models.generate_content(
                model=MODEL_NAME, contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1,response_mime_type='application/json'))
            parsed=json.loads(_clean_json(getattr(response,'text','')))
            if isinstance(parsed,dict) and 'results' in parsed: parsed=parsed['results']
            if not isinstance(parsed,list) or len(parsed)!=len(reviews):
                raise ValueError('Gemini returned an unexpected number of results')
            return [_normalise(x) for x in parsed]
        except Exception as exc:
            last=exc
            if attempt<MAX_RETRIES: time.sleep(RETRY_BASE_SECONDS*(2**attempt))
    raise RuntimeError(str(last))

def analyze_reviews(reviews, batch_size=None):
    size=batch_size or BATCH_SIZE
    out=[]
    for start in range(0,len(reviews),size):
        batch=reviews[start:start+size]
        try:
            result=_request_batch(batch)
        except Exception as exc:
            print(f'WARNING: Gemini batch {start+1}-{start+len(batch)} failed; using local fallback. Reason: {exc}')
            result=[local_fallback(r) for r in batch]
        out.extend(result)
    return out

def analyze_review(review_text):
    return analyze_reviews([review_text],1)[0]

def _local_summary(counts,positive,negative,total):
    if not total: return 'No reviews were analyzed.'
    dominant=max((('positive',counts.get('positive',0)),('neutral',counts.get('neutral',0)),('negative',counts.get('negative',0))),key=lambda x:x[1])[0]
    p=', '.join(x.get('feature','') for x in positive[:3] if x.get('feature')) or 'no dominant praised feature'
    n=', '.join(x.get('feature','') for x in negative[:3] if x.get('feature')) or 'no dominant complaint'
    return f'Overall sentiment is {dominant} across {total} reviews. Customers most often praised {p}. The main areas of concern were {n}.'

def generate_summary(reviews,sentiment_counts,top_positive,top_negative):
    if not client: return _local_summary(sentiment_counts,top_positive,top_negative,len(reviews))
    prompt=f'''Write a concise 3-4 sentence business summary.
Sentiment breakdown: {sentiment_counts}
Top praised features: {top_positive}
Top complained-about features: {top_negative}
Total reviews: {len(reviews)}
Do not use markdown.'''
    try:
        for attempt in range(MAX_RETRIES+1):
            try:
                r=client.models.generate_content(model=MODEL_NAME,contents=prompt,config=types.GenerateContentConfig(temperature=0.2))
                text=(getattr(r,'text','') or '').strip()
                if text: return text
                raise ValueError('Empty Gemini summary')
            except Exception:
                if attempt<MAX_RETRIES: time.sleep(RETRY_BASE_SECONDS*(2**attempt))
                else: raise
    except Exception as exc:
        print(f'WARNING: Gemini summary failed; using local summary. Reason: {exc}')
        return _local_summary(sentiment_counts,top_positive,top_negative,len(reviews))
def generate_product_recommendation(reviews, top_positive, top_negative):
    if not reviews:
        return 'No recommendation available because no reviews were analyzed.'

    if not client:
        if top_negative:
            features = ', '.join(
                x.get('feature', '') for x in top_negative[:3]
                if x.get('feature')
            )
            if features:
                return f'Consider improving the product in these areas: {features}.'
        return 'Customers generally appear satisfied. Continue improving the features customers value most.'

    prompt = f'''Based on the customer reviews and their most common praised and complained-about features,
provide one concise product recommendation.

Top praised features: {top_positive}
Top complained-about features: {top_negative}
Total reviews: {len(reviews)}

The recommendation should:
- Focus on the most important customer needs.
- Suggest a practical product improvement or direction.
- Be specific rather than generic.
- Be 1-2 sentences.
- Do not use markdown.
'''

    try:
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2
                    )
                )

                text = (getattr(response, 'text', '') or '').strip()

                if text:
                    return text

                raise ValueError('Empty Gemini recommendation')

            except Exception:
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BASE_SECONDS * (2 ** attempt))
                else:
                    raise

    except Exception as exc:
        print(
            f'WARNING: Gemini product recommendation failed; '
            f'using local recommendation. Reason: {exc}'
        )

        if top_negative:
            features = ', '.join(
                x.get('feature', '') for x in top_negative[:3]
                if x.get('feature')
            )

            if features:
                return (
                    f'Consider improving the product in these areas: '
                    f'{features}.'
                )

        return (
            'Customers generally appear satisfied. Continue improving '
            'the features customers value most.'
        )