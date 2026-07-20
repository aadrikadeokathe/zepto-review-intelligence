"""
Clusters negative reviews into topics using TF-IDF + KMeans.
This replaces manually reading hundreds of reviews to guess themes —
the clustering surfaces them automatically. Standard technique, well
short of "deep ML," but it's the piece that makes this read as more
than a sentiment counter.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.cluster import KMeans

INPUT_PATH = "data/reviews_scored.csv"
OUTPUT_PATH = "data/reviews_clustered.csv"
N_CLUSTERS = 6  # tune this after a first look at the results


def main():
    df = pd.read_csv(INPUT_PATH)

    # Focus clustering on negative reviews — that's where the actionable
    # product problems live. Positive reviews rarely need a "fix."
    negative_df = df[df["sentiment_label"] == "negative"].copy()
    negative_df = negative_df.dropna(subset=["review_text"])

    # Generic negative-intensity words that dominate TF-IDF without naming a
    # specific problem (e.g. "worst", "bad") get added to stopwords, so
    # clusters surface actual complaint topics instead of just anger level.
    custom_stopwords = list(ENGLISH_STOP_WORDS) + [
        "bad", "worst", "experience", "app", "zepto", "service",
        "used", "use", "using", "really", "just", "very",
    ]

    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words=custom_stopwords,
        ngram_range=(1, 2),  # captures phrases like "delivery time", not just single words
        min_df=5,
    )
    tfidf_matrix = vectorizer.fit_transform(negative_df["review_text"])

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    negative_df["topic_cluster"] = kmeans.fit_predict(tfidf_matrix)

    # Print top terms per cluster so you can manually label them
    # (e.g. cluster 3 -> "delivery delays")
    terms = vectorizer.get_feature_names_out()
    print("Top terms per cluster:\n")
    for i in range(N_CLUSTERS):
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[-10:][::-1]
        top_terms = [terms[idx] for idx in top_indices]
        cluster_size = (negative_df["topic_cluster"] == i).sum()
        print(f"Cluster {i} ({cluster_size} reviews): {', '.join(top_terms)}")

    negative_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved clustered reviews to {OUTPUT_PATH}")
    print("\nNext step: manually label each cluster based on its top terms "
          "(e.g. Cluster 0 = 'refund issues') — edit CLUSTER_LABELS in app.py")


if __name__ == "__main__":
    main()