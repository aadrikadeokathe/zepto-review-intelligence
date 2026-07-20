"""
Streamlit dashboard for the Zepto Review Intelligence project.
Run with: streamlit run app.py

This is what you screen-share in interviews — a live, explorable version
of the analysis, not just a static report.
"""

import json
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Zepto Review Intelligence", layout="wide")

st.title("Zepto Review Intelligence")
st.caption("Mining Play Store reviews to surface real product pain points")

try:
    df = pd.read_csv("data/reviews_scored.csv")
except FileNotFoundError:
    st.error("Run the pipeline first: scrape_reviews.py → db_setup.py → sentiment_analysis.py → topic_clustering.py")
    st.stop()

df["review_date"] = pd.to_datetime(df["review_date"])

# --- Top-line metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total reviews", len(df))
col2.metric("Avg rating", round(df["rating"].mean(), 2))
col3.metric("% negative sentiment", f"{(df['sentiment_label'] == 'negative').mean() * 100:.1f}%")
col4.metric("Rating/sentiment mismatches", int(df["is_mismatch"].sum()))

st.divider()

# --- Rating & sentiment over time ---
left, right = st.columns(2)

with left:
    st.subheader("Rating distribution")
    fig = px.histogram(df, x="rating", nbins=5)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Avg rating over time")
    monthly = df.set_index("review_date").resample("M")["rating"].mean().reset_index()
    fig = px.line(monthly, x="review_date", y="rating")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Topic clusters ---
st.subheader("Complaint clusters")
try:
    clustered_df = pd.read_csv("data/reviews_clustered.csv")
    cluster_counts = clustered_df["topic_cluster"].value_counts().sort_index()
    fig = px.bar(
        x=[f"Cluster {i}" for i in cluster_counts.index],
        y=cluster_counts.values,
        labels={"x": "Cluster", "y": "Review count"},
    )
    st.plotly_chart(fig, use_container_width=True)
except FileNotFoundError:
    st.info("Run topic_clustering.py to see complaint clusters here.")

st.divider()

# --- AI-generated summaries ---
st.subheader("AI-generated pain point summaries")
try:
    with open("data/ai_summary.txt") as f:
        summaries = json.load(f)

    for s in summaries:
        with st.expander(f"Cluster {s['cluster_id']}: {s.get('cluster_theme', 'Unlabeled')} ({s['review_count']} reviews)"):
            st.write(f"**Summary:** {s.get('summary', '')}")
            st.write(f"**Suggested fix:** {s.get('suggested_fix', '')}")
            st.text_area(
                f"Your take — was the AI right? What would you correct?",
                key=f"eval_{s['cluster_id']}",
                height=80,
            )
except FileNotFoundError:
    st.info("Run ai_summary.py to see AI-generated summaries here.")

st.divider()
st.caption("Built by Aadrika Deokathe — full pipeline and code at github.com/aadrikadeokathe/zepto-review-intelligence")
