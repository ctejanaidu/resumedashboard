# app.py — Streamlit resume dashboard (dark-only, styled & animated)

import json
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# -------------------- Data loader (safe + cached) --------------------
@st.cache_data
def load_resume() -> dict:
    """
    Load resume_data.json next to app.py. If missing/invalid, return a safe
    structure so CI imports and the app still render.
    """
    p = Path(__file__).parent / "resume_data.json"
    try:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass

    # Fallback so CI or fresh clones don't crash
    return {
        "profile": {
            "name": "Your Name",
            "title": "Data Scientist / Data Engineer",
            "location": "City, ST",
            "email": "",
            "linkedin": "",
            "portfolio": "",
            "publication": "",
            "phone": "",
            "summary": "Sample summary (fallback used because resume_data.json not found).",
        },
        "kpis": [],
        "skills": {},
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }


# -------------------- Helpers --------------------
def role_bucket(role: str) -> str:
    """Map free-form role titles into fixed buckets for color and legend."""
    r = (role or "").lower()
    if "analyst" in r:
        return "Data Analyst"
    if "engineer" in r:
        return "Data Engineer"
    if "scientist" in r:
        return "Data Scientist"
    if "master" in r or "education" in r or "university" in r:
        return "Education"
    return "Data Scientist"  # sensible default


# Fixed color map (tailwind-ish hexes)
COLOR_MAP = {
    "Data Analyst":  "#ef4444",  # red
    "Data Scientist": "#f59e0b",  # yellow
    "Data Engineer": "#22c55e",   # green
    "Education":     "#38bdf8",   # sky blue
}

ACCENT_ORANGE = "#f59e0b"
BG_DARK = "#0b1220"
FG_DARK = "#e5e7eb"
MUTED_BORDER = "rgba(255,255,255,0.1)"
SOFT_PANEL = "rgba(255,255,255,0.04)"


# -------------------- Main UI --------------------
def main() -> None:
    # ---- Page Config (first Streamlit call) ----
    st.set_page_config(
        page_title="Teja Naidu Chintha — Resume Dashboard",
        page_icon="📊",
        layout="wide",
    )

    data = load_resume()

    # ---- Global Styles (dark-only + animations + controls) ----
    st.markdown(
        f"""
        <style>
        html, body, .main {{
            background-color: {BG_DARK};
            color: {FG_DARK};
        }}

        /* Smooth fade-in on sections */
        @keyframes fadeIn {{
          from {{ opacity: 0; transform: translateY(4px); }}
          to   {{ opacity: 1; transform: translateY(0);   }}
        }}

        .fade-in {{ animation: fadeIn .5s ease both; }}

        .metric-box {{
            border: 1px solid {MUTED_BORDER};
            background: {SOFT_PANEL};
            padding: 18px;
            border-radius: 16px;
        }}
        .chip {{
            display: inline-block;
            padding: 6px 10px;
            margin: 4px 6px 0 0;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.15);
            background: rgba(255,255,255,0.06);
            font-size: 0.9rem;
        }}
        .section-title {{
            font-weight: 800;
            font-size: 1.32rem;  /* ~10% larger */
            letter-spacing: .02em;
            margin: 4px 0 10px 0;
            color: {ACCENT_ORANGE};   /* orange subheading */
            text-transform: uppercase;
        }}
        .subtle {{ opacity: 0.8; }}

        /* Fancy card hover glow */
        .soft-card {{
            border: 1px solid {MUTED_BORDER};
            background: {SOFT_PANEL};
            padding: 18px;
            border-radius: 18px;
            transition: box-shadow .25s ease, transform .25s ease;
        }}
        .soft-card:hover {{
            box-shadow: 0 10px 24px rgba(0,0,0,.35), 0 0 0 1px rgba(245,158,11,.28);
            transform: translateY(-2px);
        }}

        /* Custom details/summary (our colored expanders) */
        details.custom-expander {{
            border: 1px solid {MUTED_BORDER};
            border-radius: 12px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.02);
        }}
        details.custom-expander > summary {{
            cursor: pointer;
            list-style: none;   /* removes default disclosure triangle */
            padding: 10px 14px;
            font-weight: 700;
            font-size: 1.05rem;  /* larger header text */
            border-radius: 12px;
            color: {FG_DARK};
        }}
        details.custom-expander[open] {{
            background: rgba(255,255,255,0.03);
        }}
        details.custom-expander .expander-body {{
            padding: 12px 16px 14px 16px;
            font-size: 0.98rem;
        }}

        a, a:visited {{ color: {ACCENT_ORANGE}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; opacity: 0.95; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header ----
    left, right = st.columns([0.75, 0.25], gap="large")

    # Energetic, business-elegant summary (override JSON)
    summary_text = (
        "I design data products that move the needle. From **real-time fraud defenses** at bank scale "
        "to **forecasting systems** that guide millions in spend, I build ML pipelines that are fast, "
        "observable, and production-ready. My toolbox blends **GenAI**, **MLOps on Databricks/Spark/Airflow**, "
        "and **streaming architectures** that turn signals into decisions. I care about crisp dashboards, "
        "tight feedback loops, and measurable business lift."
    )

    with left:
        st.markdown(
            f"<h1 style='margin-bottom:2px'>{data['profile']['name']}</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='subtle'>{data['profile']['title']} • {data['profile']['location']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='soft-card fade-in'>{summary_text}</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-title fade-in'>Contact</div>", unsafe_allow_html=True)
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

    # ---- Highlights ----
    st.markdown("<div class='section-title fade-in'>Highlights</div>", unsafe_allow_html=True)
    kpis = data.get("kpis") or [
        {"label": "Experience", "value": "4 yrs"},
        {"label": "Domains", "value": "Finance, Healthcare"},
        {"label": "Models Deployed", "value": "Fraud, Forecasting, NLP"},
        {"label": "Platform Strength", "value": "MLOps • Databricks • Streaming"},
    ]
    kpi_cols = st.columns(len(kpis))
    for col, k in zip(kpi_cols, kpis):
        with col:
            st.markdown(
                f"<div class='metric-box fade-in'><div class='subtle'>{k['label']}</div>"
                f"<h2 style='margin:0'>{k['value']}</h2></div>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ---- Skills ----
    st.markdown("<div class='section-title fade-in'>Skills Matrix</div>", unsafe_allow_html=True)

    OPTIONS = [
        "All", "Languages", "ML & AI", "LLM & GenAI",
        "Vector & Retrieval", "Data Processing", "Cloud & MLOps", "Viz & Communication"
    ]
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

        # Simple skills frequency bar
        skill_counts = [{"Category": k, "Count": len(v)} for k, v in data["skills"].items()]
        if skill_counts:
            df_skills = pd.DataFrame(skill_counts).sort_values("Count", ascending=True)
            fig_skills = px.bar(
                df_skills, x="Count", y="Category", orientation="h",
                title="Skill Coverage by Category"
            )
            st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.caption("No skills defined yet.")

    st.divider()

    # ---- Experience Timeline ----
    st.markdown("<div class='section-title fade-in'>Experience Timeline</div>", unsafe_allow_html=True)

    exp_rows = []
    for e in data.get("experience", []):
        exp_rows.append({
            "Company": e.get("company", ""),
            "Role": e.get("role", ""),
            "Bucket": role_bucket(e.get("role", "")),
            "Start": pd.to_datetime(e.get("start")),
            "End": pd.to_datetime(e.get("end")),
            "Location": e.get("location", ""),
            "Bullets": " • ".join(e.get("bullets", [])[:3]) +
                       (" ..." if len(e.get("bullets", [])) > 3 else "")
        })

    # Inject Master's entry (no bullets)
    exp_rows.append({
        "Company": "Indiana University",
        "Role": "Master's in Data Science",
        "Bucket": "Education",
        "Start": pd.to_datetime("2022-08-01"),
        "End": pd.to_datetime("2024-05-31"),
        "Location": "Bloomington, IN",
        "Bullets": "",
    })

    df_exp = pd.DataFrame(exp_rows)

    if not df_exp.empty:
        fig_timeline = px.timeline(
            df_exp.sort_values("Start"),
            x_start="Start", x_end="End", y="Company", color="Bucket",
            hover_data=["Role", "Location", "Bullets"],
            title="Roles over Time",
            color_discrete_map=COLOR_MAP,
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Colored, larger-header "expanders" using HTML details/summary
        for _, row in df_exp.iterrows():
            header = f"{row['Role']} — {row['Company']} ({row['Location']})"
            tint = COLOR_MAP.get(row["Bucket"], ACCENT_ORANGE)
            body = ""
            if row["Bullets"]:
                items = [x.strip() for x in row["Bullets"].split("•") if x.strip()]
                if items:
                    body = "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
            st.markdown(
                f"""
                <details class="custom-expander fade-in">
                  <summary style="background:{tint}22; border:1px solid {tint}55;">
                    {header}
                  </summary>
                  <div class="expander-body">
                    {body if body else "<em>No additional details.</em>"}
                  </div>
                </details>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No experience entries yet.")

    st.divider()

    # ---- Projects ----
    st.markdown("<div class='section-title fade-in'>Projects & Publications</div>", unsafe_allow_html=True)
    if data.get("projects"):
        proj_tabs = st.tabs([p.get("name", f"Project {i+1}") for i, p in enumerate(data["projects"])])
        for tab, p in zip(proj_tabs, data["projects"]):
            with tab:
                st.markdown("#### Highlights")
                for h in p.get("highlights", []):
                    st.markdown(f"- {h}")
                if p.get("link"):
                    st.link_button("Open Link", p["link"], use_container_width=True)
    else:
        st.caption("No projects listed yet.")

    # ---- Demo plot (synthetic) ----
    st.markdown("<div class='section-title fade-in'>Demo: Fraud Model Uplift (Synthetic)</div>", unsafe_allow_html=True)
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
        color_discrete_sequence=["#ef4444", "#2563eb"]  # red, blue
    )
    st.plotly_chart(fig_demo, use_container_width=True)

    st.divider()

    # ---- Education & Certifications ----
    colA, colB = st.columns(2)
    with colA:
        st.markdown("<div class='section-title fade-in'>Education</div>", unsafe_allow_html=True)
        for ed in data.get("education", []):
            try:
                date = pd.to_datetime(ed.get("grad_date")).strftime("%b %Y")
            except Exception:
                date = ed.get("grad_date", "")
            st.markdown(f"**{ed.get('degree','')}**, {ed.get('school','')}  \n"
                        f"*{ed.get('location','')}* — {date}")

    with colB:
        st.markdown("<div class='section-title fade-in'>Certifications</div>", unsafe_allow_html=True)
        for c in data.get("certifications", []):
            st.markdown(f"- **{c.get('name','')}** ({c.get('year','')})")

    st.divider()

    # ---- Extras ----
    st.markdown("<div class='section-title fade-in'>Extras</div>", unsafe_allow_html=True)
    left, right = st.columns([0.6, 0.4])
    with left:
        st.markdown("**Pitch**")
        st.markdown(
            "> I build **useful AI**—the kind that ships, scales, and pays for itself. "
            "Give me raw data and an outcome; I’ll deliver a **measurable lift** with clean DAGs, "
            "tight monitoring, and dashboards an exec can love. If you need **fraud stopped, demand forecasted, "
            "or signals streaming into actions**, I’m your velocity edge."
        )

    with right:
        st.markdown("**Download Pack**")
        resume_path = Path(__file__).parent / "Teja_p.pdf"
        if resume_path.exists():
            resume_bytes = resume_path.read_bytes()
            st.download_button(
                "Download Teja_Resume.pdf",
                data=resume_bytes,
                file_name="Teja_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.caption("Teja_Resume.pdf not found in repository root.")

    st.caption("Built with Streamlit • Dark theme • Streamlit Community Cloud ready")


# -------------------- Entrypoint --------------------
if __name__ == "__main__":
    main()
