"""
Scores each review's sentiment using VADER (rule-based, no training needed).
Flags rating/sentiment mismatches — these are often the most interesting
reviews (e.g. a 5-star review with negative text, or a 1-star review that's
actually about a delivery agent, not the product).
"""

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT_PATH = "data/raw_reviews.csv"
OUTPUT_PATH = "data/reviews_scored.csv"

analyzer = SentimentIntensityAnalyzer()


def score_sentiment(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return analyzer.polarity_scores(text)["compound"]  # range: -1 to 1


def classify_sentiment(compound_score: float) -> str:
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    return "neutral"


def main():
    df = pd.read_csv(INPUT_PATH)
    df["sentiment_score"] = df["review_text"].apply(score_sentiment)
    df["sentiment_label"] = df["sentiment_score"].apply(classify_sentiment)

    # Flag mismatches: high star rating but negative text, or vice versa
    df["is_mismatch"] = (
        ((df["rating"] >= 4) & (df["sentiment_label"] == "negative")) |
        ((df["rating"] <= 2) & (df["sentiment_label"] == "positive"))
    )

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Sentiment breakdown:\n{df['sentiment_label'].value_counts()}")
    print(f"\nMismatched reviews found: {df['is_mismatch'].sum()}")
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
