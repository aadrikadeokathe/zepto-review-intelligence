"""
Creates a stratified random sample of reviews for manual labeling.

Two separate samples are created:
1. SENTIMENT sample — drawn from the FULL review set (all sentiments),
   stratified by sentiment_label, so there's real variety to check VADER
   against. Sampling only from already-negative-filtered data collapses
   Cohen's Kappa toward zero regardless of actual agreement quality
   (the "kappa paradox" — see evaluate_labeling.py for why).
2. CLUSTER sample — drawn from the clustered (negative-only) file, since
   clusters only exist for negative reviews. This checks whether each
   review actually matches its assigned topic.

Output: data/labeling_sample.csv — open in Excel/Sheets and fill in the
two empty columns by hand.
"""

import pandas as pd

SCORED_PATH = "data/reviews_scored.csv"
CLUSTERED_PATH = "data/reviews_clustered.csv"
OUTPUT_PATH = "data/labeling_sample.csv"
SENTIMENT_SAMPLES_PER_CLASS = 15  # x3 classes (pos/neg/neutral) = 45 reviews
CLUSTER_SAMPLES_PER_TOPIC = 5      # x6 clusters = 30 reviews


def main():
    scored_df = pd.read_csv(SCORED_PATH)
    clustered_df = pd.read_csv(CLUSTERED_PATH)

    # --- Sentiment sample: stratified across ALL sentiment classes ---
    sentiment_sample = (
        scored_df.groupby("sentiment_label", group_keys=False)
        .apply(lambda x: x.sample(min(SENTIMENT_SAMPLES_PER_CLASS, len(x)), random_state=7))
    )
    sentiment_sample = sentiment_sample[["review_text", "rating", "sentiment_label"]].copy()
    sentiment_sample = sentiment_sample.rename(columns={"sentiment_label": "vader_sentiment"})
    sentiment_sample["topic_cluster"] = ""  # not applicable for this half
    sentiment_sample["sample_type"] = "sentiment_check"

    # --- Cluster sample: stratified across topic clusters (negative-only) ---
    cluster_sample = (
        clustered_df.groupby("topic_cluster", group_keys=False)
        .apply(lambda x: x.sample(min(CLUSTER_SAMPLES_PER_TOPIC, len(x)), random_state=7))
    )
    cluster_sample = cluster_sample[["review_text", "rating", "sentiment_label", "topic_cluster"]].copy()
    cluster_sample = cluster_sample.rename(columns={"sentiment_label": "vader_sentiment"})
    cluster_sample["sample_type"] = "cluster_check"

    combined = pd.concat([sentiment_sample, cluster_sample], ignore_index=True)
    combined = combined.sample(frac=1, random_state=7).reset_index(drop=True)  # shuffle

    combined["human_sentiment"] = ""       # you type: positive / negative / neutral
    combined["agrees_with_cluster"] = ""   # you type: yes / no / n/a (n/a if topic_cluster is blank)

    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(combined)} reviews to {OUTPUT_PATH}")
    print(f"  - {len(sentiment_sample)} for sentiment check (spans positive/negative/neutral)")
    print(f"  - {len(cluster_sample)} for cluster check (negative reviews only)")
    print("\nFor rows where sample_type = 'sentiment_check': only fill human_sentiment, leave agrees_with_cluster blank or 'n/a'")
    print("For rows where sample_type = 'cluster_check': fill both columns")


if __name__ == "__main__":
    main()
