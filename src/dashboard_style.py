"""
Shared visual styling for the dashboard, using Aadrika's Hive brand palette
(Black, Cream, Cobalt Blue, Coral) for consistency across her portfolio work.

Import and call inject_style() at the top of app.py and every page.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    color: #0A0A0A !important;
    letter-spacing: -0.01em;
}

h1 {
    font-size: 2.6rem !important;
    border-bottom: 3px solid #E85A4F;
    padding-bottom: 0.4rem;
    display: inline-block;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E8E4DA;
    border-left: 4px solid #1E3A8A;
    border-radius: 6px;
    padding: 1rem 1.2rem;
}

div[data-testid="stMetricValue"] {
    font-family: 'Fraunces', serif !important;
    font-weight: 700 !important;
    color: #1E3A8A !important;
}

div[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #6B6B6B !important;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0A0A0A;
}
section[data-testid="stSidebar"] * {
    color: #FDFBF7 !important;
}
section[data-testid="stSidebar"] a {
    color: #F4F1EA !important;
}

/* Buttons */
.stButton > button {
    background-color: #1E3A8A;
    color: #FDFBF7;
    border: none;
    border-radius: 4px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.stButton > button:hover {
    background-color: #E85A4F;
    color: #FFFFFF;
}

/* Dividers */
hr {
    border-color: #E8E4DA !important;
}

/* Captions */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #6B6B6B !important;
}
</style>
"""


def inject_style():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)