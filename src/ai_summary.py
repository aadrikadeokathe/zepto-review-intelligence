"""
Sends a sample of reviews from each topic cluster to Gemini and asks it
to summarize the core complaint + suggest a fix.

Requires: GEMINI_API_KEY environment variable set.
Get a free key (no credit card) at aistudio.google.com.
"""

import os
import json
import pandas as pd
import google.generativeai as genai

INPUT_PATH = "data/reviews_clustered.csv"
OUTPUT_PATH = "data/ai_summary.txt"
SAMPLES_PER_CLUSTER = 15

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")


def summarize_cluster(cluster_id: int, sample_reviews: list[str]) -> dict:
    reviews_text = "\n".join(f"- {r}" for r in sample_reviews)

    prompt = f"""Here are user reviews from a single complaint cluster for a quick-commerce app:

{reviews_text}

Respond with ONLY valid JSON, no other text, no markdown code fences:
{{
  "cluster_theme": "short label for what this cluster is about",
  "summary": "2-3 sentence summary of the core complaint",
  "suggested_fix": "1-2 sentence product recommendation to address it"
}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"cluster_theme": "parse_error", "summary": text, "suggested_fix": ""}


def main():
    df = pd.read_csv(INPUT_PATH)
    results = []

    for cluster_id in sorted(df["topic_cluster"].unique()):
        cluster_reviews = df[df["topic_cluster"] == cluster_id]["review_text"].dropna()
        sample = cluster_reviews.sample(
            min(SAMPLES_PER_CLUSTER, len(cluster_reviews)), random_state=42
        ).tolist()

        print(f"Summarizing cluster {cluster_id} ({len(cluster_reviews)} reviews)...")
        summary = summarize_cluster(cluster_id, sample)
        summary["cluster_id"] = int(cluster_id)
        summary["review_count"] = len(cluster_reviews)
        results.append(summary)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved AI summaries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()