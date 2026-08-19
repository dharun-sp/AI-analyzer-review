"""
database.py
-----------
Very small SQLite wrapper. No ORM on purpose — keeps things easy to read
for a prototype. Everything is stored in a single file: reviews.db
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "reviews.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create tables if they don't exist yet. Safe to call every startup."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            summary TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            review_text TEXT NOT NULL,
            sentiment TEXT,
            positive_features TEXT,
            negative_features TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    conn.commit()
    conn.close()


def create_product(name: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, created_at) VALUES (?, ?)",
        (name, datetime.utcnow().isoformat()),
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return product_id


def save_review_result(product_id: int, review_text: str, analysis: dict):
    """analysis is expected to look like:
    {
        "sentiment": "positive" | "negative" | "neutral",
        "positive_features": [...],
        "negative_features": [...]
    }
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reviews
           (product_id, review_text, sentiment, positive_features, negative_features)
           VALUES (?, ?, ?, ?, ?)""",
        (
            product_id,
            review_text,
            analysis.get("sentiment", "neutral"),
            json.dumps(analysis.get("positive_features", [])),
            json.dumps(analysis.get("negative_features", [])),
        ),
    )
    conn.commit()
    conn.close()


def save_product_summary(product_id: int, summary: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE products SET summary = ? WHERE id = ?", (summary, product_id))
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_reviews_for_product(product_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE product_id = ?", (product_id,))
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        r = dict(row)
        r["positive_features"] = json.loads(r["positive_features"] or "[]")
        r["negative_features"] = json.loads(r["negative_features"] or "[]")
        results.append(r)
    return results
