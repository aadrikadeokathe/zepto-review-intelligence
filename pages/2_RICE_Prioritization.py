"""
RICE Prioritization Simulator — turns the 5 real Zepto complaint clusters
into an interactive prioritization exercise. Reach is pulled directly from
actual review counts (real data); Impact, Confidence, and Effort are set
via live sliders, and the ranking re-sorts instantly as you adjust them.

This is the artifact that shows PM thinking, not just data analysis —
it's literally how real roadmap prioritization debates happen.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="RICE Prioritization", layout="wide")
st.title("RICE Prioritization Simulator")
st.caption("Drag the sliders to score each pain point — the ranking updates live")

st.markdown("""
**RICE formula:** `Score = (Reach × Impact × Confidence) / Effort`

- **Reach**: how many users/reviews this issue actually affects (pulled from real data below)
- **Impact**: how much fixing this would improve the experience (1 = minimal, 3 = high)
- **Confidence**: how sure you are this is really the fix (as a %)
- **Effort**: estimated engineering effort, in person-weeks
""")

CLUSTERS = [
    {"id": 0, "name": "Refund & customer care friction", "reach": 134},
    {"id": 1, "name": "Poor customer support quality", "reach": 139},
    {"id": 2, "name": "Product quality & fulfillment issues", "reach": 604},
    {"id": 3, "name": "Delivery delays / late partners", "reach": 135},
    {"id": 5, "name": "Order cancellations", "reach": 147},
]

st.divider()
st.subheader("Score each pain point")

scores = []
cols = st.columns(len(CLUSTERS))

for col, cluster in zip(cols, CLUSTERS):
    with col:
        st.markdown(f"**{cluster['name']}**")
        st.caption(f"Reach: {cluster['reach']} reviews (real data)")
        impact = st.select_slider(
            "Impact", options=[0.25, 0.5, 1, 2, 3], value=1,
            key=f"impact_{cluster['id']}",
            help="0.25=minimal, 3=massive",
        )
        confidence = st.slider(
            "Confidence %", min_value=10, max_value=100, value=80, step=10,
            key=f"conf_{cluster['id']}",
        )
        effort = st.number_input(
            "Effort (person-weeks)", min_value=0.5, max_value=20.0, value=4.0, step=0.5,
            key=f"effort_{cluster['id']}",
        )

        rice_score = (cluster["reach"] * impact * (confidence / 100)) / effort
        scores.append({
            "Pain Point": cluster["name"],
            "Reach": cluster["reach"],
            "Impact": impact,
            "Confidence": f"{confidence}%",
            "Effort (weeks)": effort,
            "RICE Score": round(rice_score, 1),
        })

st.divider()
st.subheader("Live prioritization ranking")

scores_df = pd.DataFrame(scores).sort_values("RICE Score", ascending=False).reset_index(drop=True)
scores_df.index = scores_df.index + 1  # rank starting at 1

fig = px.bar(
    scores_df.sort_values("RICE Score"), x="RICE Score", y="Pain Point",
    orientation="h", title="Ranked by RICE Score (higher = fix first)",
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(scores_df, use_container_width=True)

st.info(
    f"**Top priority right now: {scores_df.iloc[0]['Pain Point']}** "
    f"(RICE Score: {scores_df.iloc[0]['RICE Score']}). "
    "Adjust the sliders above to reflect your own judgment on impact and effort — "
    "this is exactly the kind of debate that happens in real roadmap planning."
)

st.divider()
st.caption("Built by Aadrika Deokathe — Reach values are real review counts from the Zepto cluster analysis")
