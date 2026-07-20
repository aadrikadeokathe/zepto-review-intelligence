"""
Computes agreement metrics between VADER's automated sentiment labels and
your own manual labels.

Handles the two-part sample from create_labeling_sample.py:
- sentiment_check rows: used for the accuracy/Kappa calculation (has real
  variety across positive/negative/neutral, so Kappa is meaningful here)
- cluster_check rows: used only for the cluster-agreement percentage

Run this AFTER you've filled in human_sentiment (and agrees_with_cluster
for cluster_check rows) in data/labeling_sample.csv by hand.
"""

import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix

INPUT_PATH = "data/labeling_sample.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    df["human_sentiment"] = df["human_sentiment"].astype(str).str.lower().str.strip()
    df["vader_sentiment"] = df["vader_sentiment"].astype(str).str.lower().str.strip()

    if (df["human_sentiment"].isin(["", "nan"])).any():
        print("Some rows still have an empty human_sentiment column.")
        print("Finish labeling all rows in data/labeling_sample.csv before running this.")
        return

    # --- Sentiment accuracy/Kappa: use ONLY the sentiment_check subset ---
    sent_df = df[df["sample_type"] == "sentiment_check"]
    human = sent_df["human_sentiment"]
    vader = sent_df["vader_sentiment"]

    acc = accuracy_score(human, vader)
    kappa = cohen_kappa_score(human, vader)

    print(f"=== Sentiment agreement (n={len(sent_df)}, stratified across all classes) ===")
    print(f"Raw accuracy: {acc * 100:.1f}%")
    print(f"Cohen's Kappa: {kappa:.3f} — {interpret_kappa(kappa)}")
    print("(This sample spans positive/negative/neutral, so Kappa is meaningful here —")
    print(" unlike a negative-only sample, where Kappa collapses toward 0 regardless")
    print(" of real agreement quality, since there's no class variety for 'chance' to")
    print(" meaningfully differ from actual agreement. That's the kappa paradox.)")

    print("\n--- Confusion matrix (rows = your labels, columns = VADER's labels) ---")
    labels = sorted(set(human) | set(vader))
    cm = confusion_matrix(human, vader, labels=labels)
    print(pd.DataFrame(cm, index=labels, columns=labels))

    # --- Cluster agreement: use ONLY the cluster_check subset ---
    cluster_df = df[df["sample_type"] == "cluster_check"].copy()
    if len(cluster_df) > 0 and "agrees_with_cluster" in cluster_df.columns:
        cluster_df["agrees_with_cluster"] = cluster_df["agrees_with_cluster"].astype(str).str.lower().str.strip()
        valid = cluster_df[cluster_df["agrees_with_cluster"].isin(["yes", "no"])]
        if len(valid) > 0:
            agreement_rate = (valid["agrees_with_cluster"] == "yes").mean()
            print(f"\n=== Cluster assignment agreement (n={len(valid)}) ===")
            print(f"{agreement_rate * 100:.1f}% of reviews were judged to genuinely match their assigned topic cluster")

    # --- Disagreement examples, worth quoting in writeup ---
    disagreements = sent_df[sent_df["human_sentiment"] != sent_df["vader_sentiment"]]
    if len(disagreements) > 0:
        print(f"\n--- {len(disagreements)} sentiment disagreement cases ---")
        for _, row in disagreements.head(5).iterrows():
            print(f"\nReview: {row['review_text'][:150]}...")
            print(f"  VADER: {row['vader_sentiment']} | You: {row['human_sentiment']}")


def interpret_kappa(kappa: float) -> str:
    if kappa < 0.20:
        return "slight agreement"
    elif kappa < 0.40:
        return "fair agreement"
    elif kappa < 0.60:
        return "moderate agreement"
    elif kappa < 0.80:
        return "substantial agreement"
    else:
        return "almost perfect agreement"


if __name__ == "__main__":
    main()
