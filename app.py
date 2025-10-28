import json
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------- Data loader --------------------
@st.cache_data
def load_resume() -> dict:
    p = Path(__file__).parent / "resume_data.json"
    try:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {"profile": {}, "kpis": [], "skills": {}, "experience": [], "projects": [], "education": [], "certifications": []}

# -------------------- Main --------------------
def main() -> None:
    st.set_page_config(
        page_title="Teja Naidu Chintha — Resume Dashboard",
        page_icon="📊",
        layout="wide",
    )

    data = load_resume()

    # ---- Force Dark Mode ----
    primary_color = "#f97316"  # orange
    secondary_color = "#22d3ee"
    bg = "#0b1220"
    fg = "#e5e7eb"

    st.markdown(
        f"""
        <style>
        .main {{ background-color: {bg}; color: {fg}; }}
        .metric-box {{
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.04);
            padding: 16px; border-radius: 16px;
        }}
        .chip {{
            display: inline-block; padding: 6px 10px; margin: 4px 6px 0 0;
            border-radius: 999px; border: 1px solid rgba(255,255,255,0.15);
            background: rgba(255,255,255,0.06); font-size: 0.85rem;
        }}
        .section-title {{
            font-weight: 800; font-size: 1.32rem; letter-spacing: .02em;
            margin: 0 0 10px 0; color: {primary_color}; text-transform: uppercase;
            animation: fadein 1s ease-in;
        }}
        @keyframes fadein {{
            from {{opacity: 0; transform: translateY(8px);}}
            to {{opacity: 1; transform: translateY(0);}}
        }}
        .subtle {{ opacity: 0.75; }}
        .soft-card:hover {{
            box-shadow: 0 10px 24px rgba(0,0,0,.35), 
                        0 0 0 1px rgba(249,115,22,.55); /* orange hover glow */
            transform: translateY(-2px);
        }}
        /* Expander header font + color */
        div.streamlit-expanderHeader {{
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: {fg};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header ----
    left, right = st.columns([0.8, 0.2], gap="large")
    with left:
        st.markdown(f"<h1 style='margin-bottom:0'>{data['profile'].get('name','Teja Naidu Chintha')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='subtle'>{data['profile'].get('title','Data Scientist')} • {data['profile'].get('location','Plano, TX')}</div>", unsafe_allow_html=True)

        # Captivating professional summary (override)
        st.write(
            "Dynamic Data Scientist with 4+ years of experience turning complex data into clear, "
            "strategic insights. Proven success in **fraud detection, forecasting, GenAI, and scalable "
            "MLOps pipelines** that power decisions in **finance and healthcare**. Skilled in Spark, "
            "Databricks, Airflow, and real-time streaming systems — I design solutions that don’t just "
            "predict outcomes, but reshape how teams act on them."
        )

    with right:
        st.markdown("### 📇 Contact")
        if data["profile"].get("email"):
            st.write(f"📧 [{data['profile']['email']}]({data['profile']['email']})")
        if data["profile"].get("linkedin"):
            st.write(f"🔗 [LinkedIn]({data['profile']['linkedin']})")
        if data["profile"].get("portfolio"):
            st.write(f"📊 [Tableau Portfolio]({data['profile']['portfolio']})")
        if data["profile"].get("publication"):
            st.write(f"📚 [Publication]({data['profile']['publication']})")
        if data["profile"].get("location"):
            st.write(f"📍 {data['profile']['location']}")
        if data["profile"].get("phone"):
            st.write(f"📞 {data['profile']['phone']}")

    st.divider()

    # ---- KPIs ----
    st.markdown("<div class='section-title'>Highlights</div>", unsafe_allow_html=True)
    kpis = [
        {"label": "Experience", "value": "4 yrs"},
        {"label": "Domains", "value": "Finance, Healthcare"},
        {"label": "Models Deployed", "value": "Fraud, Forecasting, GenAI, NLP"},
        {"label": "Strengths", "value": "Spark • Databricks • MLOps • Streaming Pipelines"},
    ]
    kpi_cols = st.columns(len(kpis))
    for col, k in zip(kpi_cols, kpis):
        with col:
            st.markdown(f"<div class='metric-box'><div class='subtle'>{k['label']}</div><h2 style='margin:0'>{k['value']}</h2></div>", unsafe_allow_html=True)

    st.divider()

    # ---- Skills ----
    st.markdown("<div class='section-title'>Skills Matrix</div>", unsafe_allow_html=True)
    OPTIONS = ["All", "Languages", "ML & AI", "LLM & GenAI", "Vector & Retrieval", "Data Processing", "Cloud & MLOps", "Viz & Communication"]
    try:
        view = st.segmented_control("View", options=OPTIONS)
    except AttributeError:
        view = st.radio("View", OPTIONS, horizontal=True)
    view = view or "All"

    def chip_line(items):
        return " ".join(f"<span class='chip'>{item}</span>" for item in items)

    if data.get("skills"):
        if view == "All":
            for k, v in data["skills"].items():
                st.markdown(f"**{k}**  " + chip_line(v), unsafe_allow_html=True)
        else:
            st.markdown(chip_line(data["skills"].get(view, [])), unsafe_allow_html=True)

    st.divider()

    # ---- Experience Timeline ----
    st.markdown("<div class='section-title'>Experience Timeline</div>", unsafe_allow_html=True)

    exp_data = data.get("experience", [])
    exp_data.append({
        "company": "Indiana University",
        "role": "Master's in Data Science",
        "start": "2022-08-01",
        "end": "2024-05-01",
        "location": "Bloomington, IN",
        "bullets": []
    })

    df_exp = pd.DataFrame([
        {
            "Company": e.get("company", ""),
            "Role": e.get("role", ""),
            "Start": pd.to_datetime(e.get("start")),
            "End": pd.to_datetime(e.get("end")),
            "Location": e.get("location", ""),
            "Bullets": " • ".join(e.get("bullets", [])[:3])
        }
        for e in exp_data
    ])

    color_map = {"Data Scientist": "red", "Data Scientist / Data Science Engineer II": "yellow",
                 "Data Analyst": "green", "Master's in Data Science": "skyblue"}

    fig_timeline = px.timeline(
        df_exp.sort_values("Start"),
        x_start="Start", x_end="End", y="Company", color="Role",
        color_discrete_map=color_map,
        hover_data=["Location", "Bullets"],
        title="Roles over Time"
    )
    fig_timeline.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_timeline, use_container_width=True)

    for e in exp_data:
        with st.expander(f"{e.get('role')} — {e.get('company')} ({e.get('location')})"):
            for b in e.get("bullets", []):
                st.markdown(f"- {b}")

    st.divider()

    # ---- Demo plot ----
    st.markdown("##### Demo: Fraud Model Uplift (Synthetic)")
    np.random.seed(7)
    roc_baseline = np.clip(np.linspace(0.5, 0.8, 50) + np.random.normal(0, .015, 50), 0, 1)
    roc_new = np.clip(np.linspace(0.85, 0.99, 50) + np.random.normal(0, .01, 50), 0, 1)
    df_demo = pd.DataFrame({
        "Threshold": np.linspace(0, 1, 50),
        "Baseline ROC-AUC (~0.61→0.82)": roc_baseline,
        "New Model ROC-AUC (~0.92→0.99)": roc_new
    })
    fig_demo = px.line(
        df_demo, x="Threshold", y=df_demo.columns[1:],
        title="ROC-AUC Trend (Illustrative)",
        color_discrete_sequence=["red", "blue"]
    )
    st.plotly_chart(fig_demo, use_container_width=True)

    st.divider()

    # ---- Extras ----
    st.markdown("<div class='section-title'>Extras</div>", unsafe_allow_html=True)
    left, right = st.columns([0.6, 0.4])
    with left:
        st.markdown("**Pitch**")
        st.write(
            "I don’t just analyze data — I turn it into an **engine for decision-making**. "
            "From fraud models that save millions, to forecasting systems that guide investment, "
            "to MLOps pipelines that scale reliably, I thrive at the intersection of AI and impact. "
            "Every dataset tells a story — I make sure it’s one executives can act on."
        )
    with right:
        st.markdown("**Download Pack**")
        with open("Teja_p.pdf", "rb") as f:
            st.download_button("📄 Download Teja_Resume.pdf", f, file_name="Teja_Resume.pdf")

    st.caption("Built with Streamlit • Fully Dark Mode • Made to be shared")

if __name__ == "__main__":
    main()
