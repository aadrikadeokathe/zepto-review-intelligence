"""
Scrapes Zepto's Play Store reviews using google-play-scraper.
No API key or auth required.

Zepto's Play Store app ID: com.zeptoconsumerapp
(Verify this is still correct by searching Zepto on Play Store and
checking the URL — it'll look like play.google.com/store/apps/details?id=XXXX)
"""

import pandas as pd
from google_play_scraper import Sort, reviews

APP_ID = "com.zeptoconsumerapp"
TARGET_COUNT = 4000
OUTPUT_PATH = "data/raw_reviews.csv"


def scrape_reviews(app_id: str, target_count: int) -> pd.DataFrame:
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
        print(f"Scraped {len(all_reviews)} reviews so far...")

        if continuation_token is None:
            break

    return pd.DataFrame(all_reviews)


def main():
    df = scrape_reviews(APP_ID, TARGET_COUNT)

    # Keep only the columns we actually need
    keep_cols = ["reviewId", "userName", "content", "score", "thumbsUpCount", "at"]
    df = df[[c for c in keep_cols if c in df.columns]]
    df = df.rename(columns={
        "content": "review_text",
        "score": "rating",
        "thumbsUpCount": "helpful_count",
        "at": "review_date",
    })

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} reviews to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
