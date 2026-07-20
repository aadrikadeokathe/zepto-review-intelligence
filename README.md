# Zepto Review Intelligence

A product-analytics project that mines Zepto's Play Store reviews to surface real user pain points, then uses an LLM to summarize findings and propose fixes — evaluated against a human (PM) recommendation.

**Why this exists:** most portfolio "teardowns" are opinion-based. This one grounds the teardown in actual user data — scraping, SQL, sentiment/topic analysis — then layers an AI-generated summary on top, which you evaluate and build on.

## Pipeline

1. `src/scrape_reviews.py` — pulls Zepto reviews from the Play Store (no API key needed)
2. `src/db_setup.py` — loads reviews into SQLite, runs core SQL aggregations
3. `src/sentiment_analysis.py` — scores each review (VADER), flags rating/sentiment mismatches
4. `src/topic_clustering.py` — TF-IDF + KMeans to auto-surface recurring complaint themes
5. `src/ai_summary.py` — sends top clusters to Claude API, gets an AI-generated pain-point summary + suggested fix
6. `app.py` — Streamlit dashboard tying it all together (sentiment trends, topic breakdown, AI summary vs. your own take)

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run order

```bash
python src/scrape_reviews.py       # -> data/raw_reviews.csv
python src/db_setup.py             # -> data/reviews.db (SQLite)
python src/sentiment_analysis.py   # -> data/reviews_scored.csv
python src/topic_clustering.py     # -> data/reviews_clustered.csv
python src/ai_summary.py           # -> data/ai_summary.txt (needs ANTHROPIC_API_KEY env var)
streamlit run app.py               # launches dashboard
```

## Notes on scope

- Target: 3,000–5,000 reviews is plenty. More isn't better here — you want clean signal, not scale for its own sake.
- `ANTHROPIC_API_KEY` needs to be set as an environment variable before running `ai_summary.py`. Get one at console.anthropic.com.
- This must be run on your own machine — Play Store scraping isn't reachable from this sandboxed environment, which is why these are handed to you as ready-to-run files rather than executed here.

## What the final writeup should cover (for your resume/portfolio piece)

- Top 3 pain points, with review evidence for each
- Whether the AI's summary matched your own read of the data (where it was right, where you'd correct it — this is the most interesting part, don't skip it)
- Your PM recommendation: what you'd build/fix, and how you'd measure whether it worked
