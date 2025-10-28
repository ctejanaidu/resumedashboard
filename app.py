# app.py — dark-only resume dashboard with orange accent and improved styling

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

    # ---- Colors / Theme (dark only) ----
    # global accent (orange-500)
    ACCENT = "#f97316"
    PRIMARY = ACCENT
    SECONDARY = "#f59e0b"  # a lighter orange for subtle effects
    BG = "#0b1220"
    FG = "#e5e7eb"

    # Role color map for timeline & expander headers
    ROLE_COLORS = {
        "Data Scientist": "#22c55e",              # green
        "Data Analyst": "#ef4444",                # red
        "Data Scientist / Data Science Engineer II": "#eab308",  # yellow
        "Master's in Data Science": "#38bdf8",    # sky blue
    }

    # ---- Global CSS ----
    st.markdown(
        f"""
        <style>
        :root {{
            --accent: {ACCENT};
            --accent-soft: {SECONDARY};
            --fg: {FG};
            --bg: {BG};
        }}
        html, body, .main {{
            background-color: var(--bg) !important;
            color: var(--fg) !important;
        }}

        /* Section titles (bigger + orange) */
        .section-title {{
            font-weight: 900;
            font-size: 1.32rem; /* ~10% bump */
            letter-spacing: .02em;
            margin: 0 0 10px 0;
            color: var(--accent);
            text-transform: uppercase;
            animation: fadeIn .6s ease-in-out both;
        }}

        /* Soft cards & metrics */
        .metric-box {{
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
            padding: 16px; border-radius: 16px;
        }}
        .chip {{
            display: inline-block; padding: 6px 10px; margin: 4px 6px 0 0;
            border-radius: 999px; border: 1px solid rgba(255,255,255,0.15);
            background: rgba(255,255,255,0.06); font-size: 0.95rem;
        }}
        .subtle {{ opacity: 0.75; }}

        /* Links */
        a, a:visited {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ color: var(--accent); text-decoration: underline; opacity: 0.95; }}

        /* Orange hover glow for interactive blocks */
        .hover-glow:hover {{
            box-shadow: 0 0 0 2px var(--accent) inset, 0 0 18px rgba(249,115,22,.35);
            transition: box-shadow .18s ease-in-out, transform .18s ease-in-out;
            transform: translateY(-1px);
        }}

        /* --- Streamlit control accent overrides (orange everywhere) --- */

        /* Tabs active underline + color */
        div[role="tablist"] > div[aria-selected="true"] {{
            color: var(--accent) !important;
            border-bottom: 3px solid var(--accent) !important;
        }}
        div[role="tablist"] > div:hover {{
            color: var(--accent) !important;
        }}

        /* Segmented control selected & hover */
        button[aria-pressed="true"] {{
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }}
        button[role="tab"]:hover,
        button[aria-pressed="true"]:hover {{
            box-shadow: 0 0 0 1px var(--accent) inset;
        }}

        /* Radios/checkboxes sliders and focus rings */
        input[type="radio"]:checked + div, input[type="checkbox"]:checked + div {{
            border-color: var(--accent) !important;
        }}
        *:focus-visible {{
            outline: none !important;
            box-shadow: 0 0 0 2px var(--accent) !important;
        }}

        /* Expanders: larger header text; we tint header in Python via style attr.
           This rule bumps size and sets default hover to accent if not tinted. */
        details > summary {{
            font-size: 1.04rem;  /* larger placeholder text */
            padding: 12px 14px;
        }}
        details > summary:hover {{
            color: var(--accent);
        }}
        /* expander caret color on hover/open */
        details[open] > summary svg, details > summary:hover svg {{
            color: var(--accent) !important;
            fill: var(--accent) !important;
        }}

        /* Buttons (e.g., link_button) hover -> orange */
        .stButton button:hover {{
            border-color: var(--accent) !important;
            color: var(--accent) !important;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header ----
    left, right = st.columns([0.8, 0.2], gap="large")
    with left:
        st.markdown(
            f"<h1 style='margin-bottom:0' class='hover-glow'>{data['profile']['name']}</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='subtle'>{data['profile']['title']} • {data['profile']['location']}</div>",
            unsafe_allow_html=True,
        )

        # Energetic, business, elegant summary (override JSON)
        summary = (
            "I build decision-grade ML systems that **ship**. From fraud defenses that recover revenue "
            "to forecasting pipelines that steer multi-million-dollar plans, my work turns noisy data into "
            "live, reliable products. I move fast—with discipline—across Python, Spark, Databricks, "
            "and Airflow, wrapping it all in clean MLOps so models stay accurate in production. "
            "Finance & healthcare are my home turf; experimentation and measurable lift are my language."
        )
        st.write(summary)

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

    # ---- KPIs (Highlights) ----
    st.markdown("<div class='section-title'>Highlights</div>", unsafe_allow_html=True)
    if data.get("kpis"):
        kpi_cols = st.columns(len(data["kpis"]))
        for col, k in zip(kpi_cols, data["kpis"]):
            with col:
                st.markdown(
                    f"<div class='metric-box hover-glow'><div class='subtle'>{k['label']}</div>"
                    f"<h2 style='margin:0'>{k['value']}</h2></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No KPIs defined yet.")

    st.divider()

    # ---- Skills ----
    st.markdown("<div class='section-title'>Skills Matrix</div>", unsafe_allow_html=True)

    OPTIONS = [
        "All", "Languages", "ML & AI", "LLM & GenAI",
        "Vector & Retrieval", "Data Processing", "Cloud & MLOps", "Viz & Communication"
    ]

    # segmented control fallback
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

        # Skills frequency bar
        skill_counts = [{"Category": k, "Count": len(v)} for k, v in data["skills"].items()]
        if skill_counts:
            df_skills = pd.DataFrame(skill_counts).sort_values("Count", ascending=True)
            fig_skills = px.bar(
                df_skills, x="Count", y="Category", orientation="h",
                title="Skill Coverage by Category", color_discrete_sequence=[ACCENT]
            )
            fig_skills.update_layout(
                plot_bgcolor=BG, paper_bgcolor=BG, font_color=FG,
                hoverlabel=dict(bgcolor=ACCENT)
            )
            st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.caption("No skills defined yet.")

    st.divider()

    # ---- Experience Timeline ----
    st.markdown("<div class='section-title'>Experience Timeline</div>", unsafe_allow_html=True)

    def color_for_role(role: str) -> str:
        if not role:
            return ACCENT
        # try exact match, else find by startswith for safety
        for key, val in ROLE_COLORS.items():
            if role.strip().lower().startswith(key.lower()):
                return val
        return ACCENT

    rows = []
    for e in data.get("experience", []):
        rows.append(
            {
                "Company": e.get("company", ""),
                "Role": e.get("role", ""),
                "Start": pd.to_datetime(e.get("start")),
                "End": pd.to_datetime(e.get("end")),
                "Location": e.get("location", ""),
                "Bullets": " • ".join(e.get("bullets", [])[:3]) +
                           (" ..." if len(e.get("bullets", [])) > 3 else ""),
                "Color": color_for_role(e.get("role", "")),
            }
        )

    # Add Master's band (Aug 2022 – May 2024)
    rows.append({
        "Company": "Indiana University",
        "Role": "Master's in Data Science",
        "Start": pd.to_datetime("2022-08-01"),
        "End": pd.to_datetime("2024-05-31"),
        "Location": "Bloomington, IN",
        "Bullets": "",
        "Color": ROLE_COLORS["Master's in Data Science"],
    })

    if rows:
        df_exp = pd.DataFrame(rows).sort_values("Start")
        fig_timeline = px.timeline(
            df_exp,
            x_start="Start", x_end="End", y="Company", color="Role",
            hover_data=["Location", "Bullets"], color_discrete_map={
                r: c for r, c in ROLE_COLORS.items()
            }
        )
        # y reversed for Gantt feel
        fig_timeline.update_yaxes(autorange="reversed")
        # Dark theme + orange hover
        fig_timeline.update_layout(
            plot_bgcolor=BG, paper_bgcolor=BG, font_color=FG,
            hoverlabel=dict(bgcolor=ACCENT)
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Expandable details with header tinted to role color (header only)
        for e in rows:
            role = e["Role"]
            hdr_color = e["Color"]
            header_style = (
                f"background: rgba(255,255,255,0.04); "
                f"border: 1px solid rgba(255,255,255,0.08); "
                f"border-left: 5px solid {hdr_color}; "
                f"border-radius: 10px; margin-bottom: 10px;"
            )
            label = f"{role} — {e['Company']} ({e['Location']})"
            with st.expander(f":orange[{label}]", expanded=False):
                # inject header background via small HTML (header only look)
                st.markdown(f"<div style='{header_style}'></div>", unsafe_allow_html=True)
                if e["Bullets"]:
                    for b in e["Bullets"].split(" • "):
                        st.markdown(f"- {b}")
                else:
                    st.markdown("_No additional notes for this entry._")
    else:
        st.caption("No experience entries yet.")

    st.divider()

    # ---- Projects & Publications (tabs) ----
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
    # enforce red + blue series as requested; hover bubble orange
    fig_demo = px.line(
        df_demo, x="Threshold", y=df_demo.columns[1:],
        title="ROC-AUC Trend (Illustrative)",
        color_discrete_sequence=["#ef4444", "#3b82f6"]  # red, blue
    )
    fig_demo.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG, font_color=FG,
        hoverlabel=dict(bgcolor=ACCENT)
    )
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
            st.markdown(
                f"**{ed.get('degree','')}**, {ed.get('school','')}  \n"
                f"*{ed.get('location','')}* — {date}"
            )

    with colB:
        st.markdown("<div class='section-title'>Certifications</div>", unsafe_allow_html=True)
        for c in data.get("certifications", []):
            st.markdown(f"- **{c.get('name','')}** ({c.get('year','')})")

    st.divider()

    # ---- Extras ----
    st.markdown("<div class='section-title'>Extras</div>", unsafe_allow_html=True)
    left, right = st.columns([0.62, 0.38])
    with left:
        st.markdown("**Pitch**")
        st.write(
            "Give me noisy logs, messy telemetry, or a warehouse that hasn’t been touched in months—"
            "I’ll ship a pipeline that your business can *bet on*. My edge: battle-tested MLOps, "
            "streaming when it matters, and an obsession with measurable lift. If you need fraud caught sooner, "
            "forecasts that hold up in production, or GenAI that actually improves workflow speed, "
            "I’m the person you want in the room."
        )

    with right:
        st.markdown("**Download Pack**")
        resume_path = Path(__file__).parent / "Teja_p.pdf"
        if resume_path.exists():
            st.download_button(
                "Download Teja_Resume.pdf",
                data=resume_path.read_bytes(),
                file_name="Teja_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.caption("Resume file not found yet (upload Teja_p.pdf to the repo root).")

    st.caption("Built with Streamlit • Dark mode only • Orange accent everywhere • Deployed on Streamlit Community Cloud")


# -------------------- Only run UI when executed directly --------------------
if __name__ == "__main__":
    main()
