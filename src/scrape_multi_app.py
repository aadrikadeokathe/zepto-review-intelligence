"""
Runs the scrape + sentiment scoring pipeline for MULTIPLE apps, saving each
into its own subfolder under data/apps/<slug>/. This powers the app-vs-app
comparison view in the dashboard.

This does NOT run topic clustering or AI summaries per app — that's kept
to your main Zepto deep-dive to control API usage. The comparison view
works off scrape + sentiment data only, which is enough for headline
metrics (avg rating, % negative, top complaint themes via word frequency).
"""

import os
import pandas as pd
from google_play_scraper import Sort, reviews
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

APPS = {
    "zepto": {"app_id": "com.zeptoconsumerapp", "display_name": "Zepto"},
    "blinkit": {"app_id": "com.grofers.customerapp", "display_name": "Blinkit"},
    "instamart": {"app_id": "in.swiggy.android.instamart", "display_name": "Swiggy Instamart"},
}

TARGET_COUNT_PER_APP = 1500  # smaller than the main Zepto scrape (4000) — this is for
                              # comparison breadth, not deep single-app analysis
DATA_DIR = "data/apps"

analyzer = SentimentIntensityAnalyzer()


def scrape_app_reviews(app_id: str, target_count: int) -> pd.DataFrame:
    all_reviews = []
    continuation_token = None

    while len(all_reviews) < target_count:
        batch, continuation_token = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token,
        )
        if not batch:
            break
        all_reviews.extend(batch)
        if continuation_token is None:
            break

    return pd.DataFrame(all_reviews)


def score_sentiment(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return analyzer.polarity_scores(text)["compound"]


def classify_sentiment(score: float) -> str:
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


def process_app(slug: str, app_id: str, display_name: str):
    print(f"\n--- Processing {display_name} ({app_id}) ---")
    out_dir = os.path.join(DATA_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    df = scrape_app_reviews(app_id, TARGET_COUNT_PER_APP)
    if len(df) == 0:
        print(f"  WARNING: 0 reviews scraped for {display_name} — check app_id is still valid")
        return

    keep_cols = ["reviewId", "content", "score", "thumbsUpCount", "at"]
    df = df[[c for c in keep_cols if c in df.columns]]
    df = df.rename(columns={
        "content": "review_text", "score": "rating",
        "thumbsUpCount": "helpful_count", "at": "review_date",
    })

    df["sentiment_score"] = df["review_text"].apply(score_sentiment)
    df["sentiment_label"] = df["sentiment_score"].apply(classify_sentiment)
    df["app_slug"] = slug
    df["app_display_name"] = display_name

    out_path = os.path.join(out_dir, "reviews.csv")
    df.to_csv(out_path, index=False)
    print(f"  Saved {len(df)} reviews to {out_path}")
    print(f"  Avg rating: {df['rating'].mean():.2f} | "
          f"% negative: {(df['sentiment_label'] == 'negative').mean() * 100:.1f}%")


def main():
    for slug, config in APPS.items():
        process_app(slug, config["app_id"], config["display_name"])

    print("\nAll apps processed. Run the dashboard to see the comparison view.")


if __name__ == "__main__":
    main()
