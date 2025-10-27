# app.py — import-safe Streamlit app with segmented-control fallback

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


# -------------------- Main UI (wrapped so imports are safe) --------------------
def main() -> None:
    # ---- Page Config (first Streamlit call) ----
    st.set_page_config(
        page_title="Teja Naidu Chintha — Resume Dashboard",
        page_icon="📊",
        layout="wide",
    )

    data = load_resume()

    # ---- Theming Toggle ----
    st.sidebar.title("⚙️ Controls")
    dark_mode = st.sidebar.toggle("Dark mode", value=True)
    primary_color = "#4ade80" if dark_mode else "#2563eb"
    secondary_color = "#22d3ee" if dark_mode else "#7c3aed"
    bg = "#0b1220" if dark_mode else "#ffffff"
    fg = "#e5e7eb" if dark_mode else "#0f172a"

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
            font-weight: 800; font-size: 1.2rem; letter-spacing: .02em;
            margin: 0 0 8px 0; color: {primary_color}; text-transform: uppercase;
        }}
        .subtle {{ opacity: 0.75; }}
        .card {{
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(255,255,255,0.03);
            padding: 18px; border-radius: 18px; margin-bottom: 12px;
        }}
        a, a:visited {{ color: {secondary_color}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; opacity: 0.9; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header ----
    left, right = st.columns([0.8, 0.2], gap="large")
    with left:
        st.markdown(
            f"<h1 style='margin-bottom:0'>{data['profile']['name']}</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='subtle'>{data['profile']['title']} • {data['profile']['location']}</div>",
            unsafe_allow_html=True,
        )
        st.write(data["profile"]["summary"])

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
    if data.get("kpis"):
        kpi_cols = st.columns(len(data["kpis"]))
        for col, k in zip(kpi_cols, data["kpis"]):
            with col:
                st.markdown(
                    f"<div class='metric-box'><div class='subtle'>{k['label']}</div>"
                    f"<h2 style='margin:0'>{k['value']}</h2></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No KPIs defined yet.")

    st.divider()

    # ---- Skills ----
    st.markdown("<div class='section-title'>Skills Matrix</div>", unsafe_allow_html=True)

    OPTIONS = ["All", "Languages", "ML & AI", "LLM & GenAI",
               "Vector & Retrieval", "Data Processing", "Cloud & MLOps", "Viz & Communication"]

    try:
        view = st.segmented_control("View", options=OPTIONS)
    except AttributeError:
        view = st.radio("View", OPTIONS, horizontal=True)

    # Guard for CI / bare-mode: default to "All" if widget returns None
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
    st.markdown("<div class='section-title'>Experience Timeline</div>", unsafe_allow_html=True)

    if data.get("experience"):
        df_exp = pd.DataFrame([
            {
                "Company": e.get("company", ""),
                "Role": e.get("role", ""),
                "Start": pd.to_datetime(e.get("start")),
                "End": pd.to_datetime(e.get("end")),
                "Location": e.get("location", ""),
                "Bullets": " • ".join(e.get("bullets", [])[:3]) +
                           (" ..." if len(e.get("bullets", [])) > 3 else "")
            }
            for e in data["experience"]
        ])

        if not df_exp.empty:
            fig_timeline = px.timeline(
                df_exp.sort_values("Start"),
                x_start="Start", x_end="End", y="Company", color="Role",
                hover_data=["Location", "Bullets"],
                title="Roles over Time"
            )
            fig_timeline.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_timeline, use_container_width=True)

        # Expandable details
        for e in data["experience"]:
            with st.expander(f"{e.get('role','')} — {e.get('company','')} ({e.get('location','')})"):
                for b in e.get("bullets", []):
                    st.markdown(f"- {b}")
    else:
        st.caption("No experience entries yet.")

    st.divider()

    # ---- Projects ----
    st.markdown("<div class='section-title'>Projects & Publications</div>", unsafe_allow_html=True)
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
    st.markdown("##### Demo: Fraud Model Uplift (Synthetic)")
    np.random.seed(7)
    roc_baseline = np.clip(np.linspace(0.5, 0.8, 50) + np.random.normal(0, .015, 50), 0, 1)
    roc_new = np.clip(np.linspace(0.85, 0.99, 50) + np.random.normal(0, .01, 50), 0, 1)
    df_demo = pd.DataFrame({
        "Threshold": np.linspace(0, 1, 50),
        "Baseline ROC-AUC (~0.61→0.82)": roc_baseline,
        "New Model ROC-AUC (~0.92→0.99)": roc_new
    })
    fig_demo = px.line(df_demo, x="Threshold", y=df_demo.columns[1:], title="ROC-AUC Trend (Illustrative)")
    st.plotly_chart(fig_demo, use_container_width=True)

    st.divider()

    # ---- Education & Certifications ----
    colA, colB = st.columns(2)
    with colA:
        st.markdown("<div class='section-title'>Education</div>", unsafe_allow_html=True)
        for ed in data.get("education", []):
            try:
                date = pd.to_datetime(ed.get("grad_date")).strftime("%b %Y")
            except Exception:
                date = ed.get("grad_date", "")
            st.markdown(f"**{ed.get('degree','')}**, {ed.get('school','')}  \n"
                        f"*{ed.get('location','')}* — {date}")

    with colB:
        st.markdown("<div class='section-title'>Certifications</div>", unsafe_allow_html=True)
        for c in data.get("certifications", []):
            st.markdown(f"- **{c.get('name','')}** ({c.get('year','')})")

    st.divider()

    # ---- Extras ----
    st.markdown("<div class='section-title'>Extras</div>", unsafe_allow_html=True)
    left, right = st.columns([0.6, 0.4])
    with left:
        st.markdown("**Pitch**")
        st.write("I design dashboards that translate complex ML systems into crisp, "
                 "decision-grade visuals — from fraud scoring and anomaly triage to "
                 "experiment tracking and CI/CD health.")
    with right:
        st.markdown("**Download Pack**")
        data_bytes = json.dumps(data, indent=2).encode("utf-8")
        st.download_button("Download resume_data.json", data=data_bytes,
                           file_name="resume_data.json", mime="application/json")

    st.caption("Built with Streamlit • Toggle dark mode in the sidebar • Made to be deployed on Streamlit Community Cloud")


# -------------------- Only run UI when executed directly --------------------
if __name__ == "__main__":
    main()
