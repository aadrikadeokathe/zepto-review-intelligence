"""
Loads scraped reviews into SQLite and runs the core SQL aggregations.
This is the piece that makes the project read as "SQL", not just pandas —
worth keeping even though pandas could do the same math.
"""

import sqlite3
import pandas as pd

CSV_PATH = "data/raw_reviews.csv"
DB_PATH = "data/reviews.db"


def load_to_sqlite(csv_path: str, db_path: str):
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    df.to_sql("reviews", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded {len(df)} rows into {db_path}")


def run_core_queries(db_path: str):
    conn = sqlite3.connect(db_path)

    print("\n--- Rating distribution ---")
    print(pd.read_sql("""
        SELECT rating, COUNT(*) AS review_count
        FROM reviews
        GROUP BY rating
        ORDER BY rating DESC
    """, conn))

    print("\n--- Reviews per month ---")
    print(pd.read_sql("""
        SELECT strftime('%Y-%m', review_date) AS month, COUNT(*) AS review_count,
               ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY month
        ORDER BY month
    """, conn))

    print("\n--- Most 'helpful' low-rated reviews (likely real pain points) ---")
    print(pd.read_sql("""
        SELECT review_text, rating, helpful_count
        FROM reviews
        WHERE rating <= 2
        ORDER BY helpful_count DESC
        LIMIT 10
    """, conn))

    conn.close()


if __name__ == "__main__":
    load_to_sqlite(CSV_PATH, DB_PATH)
    run_core_queries(DB_PATH)
