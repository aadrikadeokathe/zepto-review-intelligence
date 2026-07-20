# Zepto Review Intelligence

**[Live Dashboard](https://zepto-review-intelligence-ghywgev87orc5kcvqkuywu.streamlit.app/)** · **[GitHub Repo](https://github.com/aadrikadeokathe/zepto-review-intelligence)**

A product-analytics project that mines quick-commerce app reviews to surface real user pain points, benchmarks Zepto against its competitors, and turns findings into a prioritized, quantified business recommendation — the way a PM would actually present it to leadership.

Built by **Aadrika Deokathe**.

---

## What this project does

Most "review analysis" projects stop at a sentiment chart. This one goes further: it identifies *why* Zepto has a real competitive sentiment problem, quantifies what it's likely costing the business, ranks what to fix first, and packages the whole thing into a one-page executive memo — the actual deliverable a PM would produce, not just the analysis behind it.

**Headline finding:** Zepto's negative review rate is **29.7%**, roughly **2.6x higher** than Blinkit (11.5%) and Swiggy Instamart (11.4%), based on independently scraped and analyzed reviews across all three platforms.

## Pipeline

1. **Scrape** — pulls real Play Store reviews (`google-play-scraper`, no API key needed)
2. **Sentiment scoring** — VADER, with rating/sentiment mismatch detection
3. **Topic clustering** — TF-IDF + KMeans surfaces 5 distinct, actionable complaint themes from negative reviews
4. **Human evaluation** — manual labeling of a stratified sample, scored against VADER using Cohen's Kappa (not just raw accuracy — see note below on why that distinction matters)
5. **AI-generated summaries** — an LLM (Gemini) summarizes each complaint cluster and proposes a fix, evaluated against human judgment rather than taken at face value
6. **Multi-app comparison** — the same pipeline run across Zepto, Blinkit, and Instamart for competitive benchmarking
7. **RICE prioritization** — interactive simulator scoring each pain point on Reach (real data) x Impact x Confidence / Effort (adjustable)
8. **Revenue-at-risk model** — scenario-based estimate (conservative/moderate/aggressive) of annual revenue at risk, built on Zepto's real, publicly reported scale (~900K orders/day, ~Rs 500 AOV), not on review sentiment applied naively to the full user base
9. **Executive memo** — a one-page strategy document tying findings 1-8 into a single recommendation

## Key finding: the Kappa paradox

An early version of the human-evaluation step returned Cohen's Kappa = 0.000 despite 88% raw agreement — a real, diagnosable statistical artifact caused by sampling only from an already-negative-filtered dataset (near-zero class variety collapses Kappa toward zero regardless of true agreement quality). Re-sampling across the full sentiment range fixed this and surfaced a genuine, moderate Kappa (0.50) — along with a specific, evidenced finding: VADER systematically under-detects sentiment in short, informally-punctuated reviews, defaulting to "neutral" where a human reader identifies clear sentiment.

## Repository structure

```
├── app.py                          # Main dashboard (headline metrics, Zepto deep-dive)
├── pages/
│   ├── 1_Compare_Apps.py          # Zepto vs Blinkit vs Instamart benchmarking
│   └── 2_RICE_Prioritization.py   # Interactive RICE scoring simulator
├── src/
│   ├── scrape_reviews.py          # Zepto-specific scraper (main deep-dive)
│   ├── scrape_multi_app.py        # Multi-app scraper for comparison view
│   ├── db_setup.py                # SQLite loading + core SQL aggregations
│   ├── sentiment_analysis.py      # VADER scoring
│   ├── topic_clustering.py        # TF-IDF + KMeans complaint clustering
│   ├── create_labeling_sample.py  # Stratified sample generator for human eval
│   ├── evaluate_labeling.py       # Accuracy + Cohen's Kappa calculation
│   ├── ai_summary.py              # LLM-generated cluster summaries (Gemini)
│   └── revenue_impact_model.py    # Scenario-based revenue-at-risk estimation
├── data/                           # Scraped reviews, scored data, cluster outputs
├── requirements.txt
└── Zepto_Strategy_Memo.docx        # The final one-page executive deliverable
```

## Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set your Gemini API key (free, no card required, from aistudio.google.com):
```bash
export GEMINI_API_KEY=your_key_here
```

## Run order

```bash
python src/scrape_reviews.py
python src/db_setup.py
python src/sentiment_analysis.py
python src/topic_clustering.py
python src/create_labeling_sample.py   # then manually label data/labeling_sample.csv
python src/evaluate_labeling.py
python src/ai_summary.py
python src/scrape_multi_app.py         # for the comparison view
python src/revenue_impact_model.py
streamlit run app.py
```

## Methodology notes (things I deliberately got right, not by accident)

- **Reviewer sentiment != population dissatisfaction.** The revenue model explicitly does NOT apply the 29.7% review-negativity rate directly to Zepto's full user base — reviewers are a self-selected, negativity-skewed sample. Dissatisfaction and churn are instead modeled as separate, clearly-labeled assumption ranges.
- **Ranges over false precision.** Every estimate (revenue impact, RICE scores) is presented as a scenario range, not a single confident number.
- **Benchmarked against real competitors**, not a hypothetical zero-complaints baseline — the target is closing the gap to Blinkit/Instamart's actual sentiment rate, not eliminating all complaints.

## Live links

- **Dashboard:** https://zepto-review-intelligence-ghywgev87orc5kcvqkuywu.streamlit.app/
- **Full code:** https://github.com/aadrikadeokathe/zepto-review-intelligence
