"""
Compare Apps page — benchmarks Zepto against Blinkit and Swiggy Instamart
on rating, sentiment, and top complaint keywords.

Run scrape_multi_app.py first to generate the data this page reads.
"""

import os
import glob
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
from collections import Counter
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dashboard_style import inject_style

st.set_page_config(page_title="Compare Apps", layout="wide")
inject_style()
st.title("Quick-Commerce App Comparison")
st.caption("Benchmarking Zepto against competitors on review sentiment and complaint themes")

DATA_DIR = "data/apps"
STOPWORDS = set([
    "the", "and", "for", "with", "this", "that", "not", "you", "your", "was",
    "are", "have", "has", "app", "its", "but", "they", "them", "very", "just",
    "get", "got", "from", "when", "then", "now", "even", "all", "can", "will",
    "何", "is", "it", "to", "of", "a", "in", "on", "my", "me", "i",
])


@st.cache_data
def load_all_apps():
    app_dirs = glob.glob(os.path.join(DATA_DIR, "*"))
    frames = []
    for d in app_dirs:
        csv_path = os.path.join(d, "reviews.csv")
        if os.path.exists(csv_path):
            frames.append(pd.read_csv(csv_path))
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def top_complaint_words(texts: pd.Series, n=8) -> list[tuple[str, int]]:
    all_words = []
    for text in texts.dropna():
        words = re.findall(r"[a-zA-Z]+", str(text).lower())
        all_words.extend([w for w in words if w not in STOPWORDS and len(w) > 3])
    return Counter(all_words).most_common(n)


df = load_all_apps()

if df is None:
    st.error(
        "No app comparison data found. Run this first:\n\n"
        "python src/scrape_multi_app.py\n\n"
        "This scrapes Zepto, Blinkit, and Instamart reviews for side-by-side comparison."
    )
    st.stop()

apps_present = df["app_display_name"].unique().tolist()
st.info(f"Comparing: {', '.join(apps_present)} — {len(df):,} total reviews")

# --- Headline comparison metrics ---
st.subheader("Rating & sentiment by app")

summary = df.groupby("app_display_name").agg(
    avg_rating=("rating", "mean"),
    pct_negative=("sentiment_label", lambda x: (x == "negative").mean() * 100),
    total_reviews=("rating", "count"),
).reset_index().sort_values("pct_negative")

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(summary, x="app_display_name", y="avg_rating",
                 title="Average rating (out of 5)", color="app_display_name")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(summary, x="app_display_name", y="pct_negative",
                 title="% negative sentiment reviews", color="app_display_name")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(summary.style.format({"avg_rating": "{:.2f}", "pct_negative": "{:.1f}%"}), use_container_width=True)

st.divider()

# --- Top complaint words per app, side by side ---
st.subheader("Top complaint keywords by app")
st.caption("Most frequent words in negative reviews — a fast way to spot each app's biggest weakness")

cols = st.columns(len(apps_present))
for col, app_name in zip(cols, apps_present):
    with col:
        st.markdown(f"**{app_name}**")
        app_negative = df[(df["app_display_name"] == app_name) & (df["sentiment_label"] == "negative")]
        top_words = top_complaint_words(app_negative["review_text"])
        if top_words:
            words_df = pd.DataFrame(top_words, columns=["word", "count"])
            fig = px.bar(words_df, x="count", y="word", orientation="h")
            fig.update_layout(height=300, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Not enough negative reviews to analyze")

st.divider()
st.caption("Built by Aadrika Deokathe — data scraped independently per app, same pipeline as the main Zepto deep-dive")
