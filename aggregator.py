"""
aggregator.py
-------------
Takes the raw per-review results (already stored in SQLite) and turns
them into the shapes the dashboard needs: sentiment distribution,
feature frequency counts, and word-cloud-ready word frequencies.
"""

from collections import Counter
import re

STOPWORDS = {
    "the", "a", "an", "is", "it", "this", "that", "and", "or", "but", "was",
    "were", "for", "with", "to", "of", "in", "on", "i", "my", "product",
    "very", "so", "just", "not", "have", "has", "had", "im", "its",
}


def compute_sentiment_distribution(reviews: list) -> dict:
    counts = Counter(r["sentiment"] for r in reviews)
    return {
        "positive": counts.get("positive", 0),
        "negative": counts.get("negative", 0),
        "neutral": counts.get("neutral", 0),
    }


def compute_feature_frequency(reviews: list, key: str, top_n: int = 10) -> list:
    """key is 'positive_features' or 'negative_features'.
    Returns a list of {feature, count} sorted descending, for bar charts."""
    counter = Counter()
    for r in reviews:
        for feature in r.get(key, []):
            counter[feature.strip().lower()] += 1

    return [{"feature": f, "count": c} for f, c in counter.most_common(top_n)]


def _word_freq_from_texts(texts: list, top_n: int) -> list:
    counter = Counter()
    for text in texts:
        words = re.findall(r"[a-zA-Z']+", text.lower())
        for w in words:
            if len(w) > 2 and w not in STOPWORDS:
                counter[w] += 1
    return [{"text": w, "value": c} for w, c in counter.most_common(top_n)]


def compute_word_frequencies(reviews: list, top_n: int = 50) -> list:
    """Word frequency across ALL review text (used as a fallback / overview)."""
    return _word_freq_from_texts([r["review_text"] for r in reviews], top_n)


def compute_word_frequencies_by_sentiment(reviews: list, top_n: int = 40) -> dict:
    """Separate word clouds for positive vs negative reviews, per the spec.
    Words from 'positive' sentiment reviews vs 'negative' sentiment reviews."""
    positive_texts = [r["review_text"] for r in reviews if r["sentiment"] == "positive"]
    negative_texts = [r["review_text"] for r in reviews if r["sentiment"] == "negative"]
    return {
        "positive": _word_freq_from_texts(positive_texts, top_n),
        "negative": _word_freq_from_texts(negative_texts, top_n),
    }


def build_dashboard_data(product: dict, reviews: list) -> dict:
    return {
        "product": product,
        "total_reviews": len(reviews),
        "sentiment_distribution": compute_sentiment_distribution(reviews),
        "top_positive_features": compute_feature_frequency(reviews, "positive_features"),
        "top_negative_features": compute_feature_frequency(reviews, "negative_features"),
        "word_frequencies": compute_word_frequencies(reviews),
        "word_frequencies_by_sentiment": compute_word_frequencies_by_sentiment(reviews),
        "summary": product.get("summary", ""),
    }
