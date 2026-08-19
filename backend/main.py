from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import csv, io
import database as db
import ai_service
import aggregator

app=FastAPI(title='AI Product Review Analyzer')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
db.init_db()

class BulkAnalyzeRequest(BaseModel):
    product_name:str
    reviews:List[str]

def clean_reviews(values):
    return [str(r).strip() for r in values if r is not None and str(r).strip()]

def parse_csv(contents):
    text=None
    for enc in ('utf-8-sig','utf-16','cp1252','latin-1'):
        try: text=contents.decode(enc); break
        except UnicodeDecodeError: pass
    if text is None: text=contents.decode('utf-8',errors='replace')
    try: dialect=csv.Sniffer().sniff(text[:10000],delimiters=',;\t|')
    except csv.Error: dialect=csv.excel
    rows=list(csv.reader(io.StringIO(text),dialect))
    if not rows:return []
    aliases={'review','review_text','review text','text','comment','feedback','content','review_body','review body','body'}
    header=[str(x).strip().lower() for x in rows[0]]
    matches=[i for i,x in enumerate(header) if x in aliases]
    if matches:
        i=matches[0]
        return clean_reviews(row[i] if i<len(row) else '' for row in rows[1:])
    try: has_header=csv.Sniffer().has_header(text[:10000])
    except csv.Error: has_header=True
    data=rows[1:] if has_header else rows
    if not data:return []
    idx=max(range(len(data[0])),key=lambda i:sum(len(r[i]) if i<len(r) else 0 for r in data))
    return clean_reviews(row[idx] if idx<len(row) else '' for row in data)

def run_analysis(product_name,reviews):
    reviews=clean_reviews(reviews)
    if not reviews: raise HTTPException(400,'No review text found.')
    pid=db.create_product(product_name.strip())
    analyses=ai_service.analyze_reviews(reviews)
    for text,analysis in zip(reviews,analyses): db.save_review_result(pid,text,analysis)
    stored=db.get_reviews_for_product(pid)
    data=aggregator.build_dashboard_data(db.get_product(pid),stored)
    summary=ai_service.generate_summary(
    stored,
    data['sentiment_distribution'],
    data['top_positive_features'],
    data['top_negative_features']
    )

    recommendation=ai_service.generate_product_recommendation(
    stored,
    data['top_positive_features'],
    data['top_negative_features']
    )

    db.save_product_summary(pid,summary)

    data['summary']=summary
    data['recommendation']=recommendation
    data['product']['summary']=summary
    data['product']['recommendation']=recommendation

    return data

@app.post('/analyze/text')
def analyze_text(payload:BulkAnalyzeRequest): return run_analysis(payload.product_name,payload.reviews)

@app.post('/analyze/file')
async def analyze_file(product_name:str=Form(...),file:UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(400,'Please upload a CSV file.')
    return run_analysis(product_name,parse_csv(await file.read()))

@app.get('/products')
def products(): return db.get_all_products()

@app.get('/dashboard/{product_id}')
def dashboard(product_id:int):
    product=db.get_product(product_id)
    if not product: raise HTTPException(404,'Product not found')
    return aggregator.build_dashboard_data(product,db.get_reviews_for_product(product_id))

@app.get('/')
def root():
    return {'status':'AI Product Review Analyzer backend is running','gemini_configured':bool(ai_service.API_KEY),'model':ai_service.MODEL_NAME}
