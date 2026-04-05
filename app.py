"""
Multimodal Clinical Query Router — Streamlit UI
Production-grade oncology informatics interface.
"""

import json
import os
import sys
import time
from typing import Any

import streamlit as st

# ── Page config must be first ──────────────────────────────────────────────
st.set_page_config(
    page_title="Clinical Query Router",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0a0d14;
    color: #c8d0e0;
}

.stApp { background-color: #0a0d14; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #1e2535;
}

/* Metric cards */
.metric-card {
    background: #111827;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 6px 0;
}
.metric-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 4px;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-value {
    font-size: 26px;
    font-weight: 600;
    color: #e2e8f0;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-sub {
    font-size: 11px;
    color: #4a90d9;
    margin-top: 2px;
    font-family: 'IBM Plex Mono', monospace;
}

/* Modality badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
}
.badge-TEXT    { background: #1a3a2a; color: #4ade80; border: 1px solid #166534; }
.badge-LABS    { background: #1a2a3a; color: #60a5fa; border: 1px solid #1e3a5f; }
.badge-GENOMIC { background: #2a1a3a; color: #c084fc; border: 1px solid #6b21a8; }
.badge-FUSED   { background: #3a2a1a; color: #fb923c; border: 1px solid #9a3412; }

/* Answer block */
.answer-block {
    background: #111827;
    border-left: 3px solid #4a90d9;
    border-radius: 0 8px 8px 0;
    padding: 18px 22px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.7;
    color: #d1d5db;
}

/* Score bar */
.score-row {
    display: flex;
    align-items: center;
    margin: 5px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
}
.score-label {
    width: 160px;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 10px;
}
.score-bar-bg {
    flex: 1;
    height: 5px;
    background: #1e2535;
    border-radius: 3px;
    margin: 0 10px;
}
.score-bar-fill {
    height: 100%;
    border-radius: 3px;
}
.score-num {
    width: 42px;
    text-align: right;
    color: #a0aec0;
}

/* Evidence record */
.evidence-record {
    background: #0d1117;
    border: 1px solid #1e2535;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 5px 0;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    color: #8899aa;
}
.evidence-pid {
    color: #4a90d9;
    font-weight: 500;
}
.evidence-flag {
    color: #f87171;
    font-weight: 600;
}

/* Section header */
.section-header {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4a5568;
    margin: 20px 0 8px 0;
    font-family: 'IBM Plex Mono', monospace;
    border-bottom: 1px solid #1e2535;
    padding-bottom: 6px;
}

/* Routing panel */
.routing-panel {
    background: #0d1117;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
}
.routing-reasoning {
    font-size: 12px;
    color: #718096;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.6;
    margin-top: 8px;
}

/* Latency chips */
.latency-chip {
    display: inline-block;
    background: #111827;
    border: 1px solid #1e2535;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    color: #718096;
    margin: 2px 4px 2px 0;
}
.latency-chip span { color: #a0aec0; font-weight: 500; }

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
header[data-testid="stHeader"] { background: transparent; }

/* Query input */
.stTextInput input {
    background: #111827 !important;
    border: 1px solid #1e2535 !important;
    color: #e2e8f0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    border-radius: 6px !important;
}
.stTextInput input:focus {
    border-color: #4a90d9 !important;
    box-shadow: 0 0 0 2px rgba(74,144,217,0.15) !important;
}

/* Button */
.stButton button {
    background: #1a3a5a !important;
    border: 1px solid #2a5a8a !important;
    color: #60a5fa !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 1px !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    transition: all 0.2s;
}
.stButton button:hover {
    background: #234875 !important;
    border-color: #4a90d9 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1e2535;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #4a5568;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 8px 16px;
    border-radius: 0;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #60a5fa !important;
    border-bottom: 2px solid #4a90d9 !important;
}

/* Divider */
hr { border-color: #1e2535; }

/* Select box */
.stSelectbox [data-baseweb="select"] {
    background: #111827 !important;
    border-color: #1e2535 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Bootstrap data & pipeline ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_pipeline():
    if not os.path.exists("data/clinical_notes.json"):
        from scripts.generate_data import main as gen_main
        gen_main()
    from src.pipeline import run_query
    return run_query


@st.cache_resource(show_spinner=False)
def warmup_chroma():
    """Pre-load ChromaDB to avoid cold-start on first query."""
    from src.retrievers import _get_chroma
    _get_chroma()


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
<div style="padding: 4px 0 20px 0;">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:3px;
              text-transform:uppercase; color:#4a5568; margin-bottom:4px;">
    TEMPUS AI ×
  </div>
  <div style="font-size:18px; font-weight:600; color:#e2e8f0; line-height:1.2;">
    Clinical Query<br>Router
  </div>
  <div style="font-size:11px; color:#4a5568; margin-top:4px; font-family:'IBM Plex Mono',monospace;">
    v1.0 · 4-modality RAG
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">SAMPLE QUERIES</div>', unsafe_allow_html=True)

    example_groups = {
        "🧬 Genomic": [
            "Which patients have EGFR L858R mutations?",
            "Find all KRAS G12C positive patients",
            "Show MSI-H patients with TMB-High status",
        ],
        "🔬 Labs": [
            "Which patients have CRP above 10 mg/L?",
            "Find patients with hemoglobin below 9 g/dL",
            "Show patients with LDH trending above 400",
        ],
        "📋 Clinical Notes": [
            "Find notes documenting grade 3 neutropenia",
            "Which patients were referred to palliative care?",
            "Summarize treatment response in NSCLC patients",
        ],
        "🔀 Cross-Modal": [
            "Which EGFR patients have CRP above 10 and documented progression?",
            "Find KRAS G12C patients with elevated LDH and progressive disease in notes",
            "Show MSI-H patients with CRP flagged HIGH and pembrolizumab response",
        ],
    }

    selected_query = None
    for group_name, queries in example_groups.items():
        with st.expander(group_name, expanded=False):
            for q in queries:
                if st.button(q, key=f"btn_{hash(q)}", use_container_width=True):
                    selected_query = q

    st.markdown('<div class="section-header">SYSTEM</div>', unsafe_allow_html=True)
    groq_key = st.text_input(
        "GROQ_API_KEY",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        placeholder="gsk_...",
        help="Get a free key at console.groq.com",
    )
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    st.markdown(
        """
<div style="margin-top:24px; padding:12px; background:#0d1117; border:1px solid #1e2535;
            border-radius:6px; font-size:11px; color:#4a5568; font-family:'IBM Plex Mono',monospace;">
  <div style="margin-bottom:6px; color:#718096;">ARCHITECTURE</div>
  ChromaDB · cosine similarity<br>
  Pandas · structured lab filter<br>
  Groq · llama-3.3-70b-versatile<br>
  LLM-as-judge · faithfulness<br>
  25 patients · 8 visits · 4 genes
</div>
""",
        unsafe_allow_html=True,
    )

# ── Main content ───────────────────────────────────────────────────────────
st.markdown(
    """
<div style="padding: 0 0 24px 0; border-bottom: 1px solid #1e2535; margin-bottom: 24px;">
  <div style="font-size:11px; font-family:'IBM Plex Mono',monospace; letter-spacing:2px;
              text-transform:uppercase; color:#4a5568; margin-bottom:6px;">
    MULTIMODAL ONCOLOGY INFORMATICS
  </div>
  <h1 style="font-size:28px; font-weight:600; color:#e2e8f0; margin:0; line-height:1.2;">
    Clinical Query Router
  </h1>
  <p style="color:#718096; font-size:13px; margin:8px 0 0 0; max-width:560px; line-height:1.6;">
    Routes natural language questions to the appropriate retrieval modality —
    clinical notes, lab time-series, genomic profiles, or cross-modal joins —
    then generates grounded answers with LLM-as-judge faithfulness scoring.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# Query input
col_input, col_btn = st.columns([5, 1])
with col_input:
    query_input = st.text_input(
        label="Query",
        label_visibility="collapsed",
        value=selected_query or st.session_state.get("last_query", ""),
        placeholder="Ask a clinical question, e.g. 'Which EGFR patients have CRP above 10?'",
        key="query_field",
    )
with col_btn:
    run_btn = st.button("▶  RUN", use_container_width=True)

# ── History ────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Run pipeline ───────────────────────────────────────────────────────────
if (run_btn or selected_query) and query_input.strip():
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠ Set your GROQ_API_KEY in the sidebar to enable answer generation.")
        st.stop()

    with st.spinner(""):
        run_query = init_pipeline()
        warmup_chroma()
        result = run_query(query_input.strip(), top_k=6)

    st.session_state.history.insert(0, result)
    st.session_state.last_query = query_input.strip()

    r = result["routing"]
    f = result["faithfulness"]
    lat = result["latency_ms"]

    # ── Top KPI row ────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    modality_colors = {
        "TEXT": "#4ade80", "LABS": "#60a5fa",
        "GENOMIC": "#c084fc", "FUSED": "#fb923c",
    }
    mc = modality_colors.get(r["modality"], "#e2e8f0")

    with k1:
        st.markdown(
            f"""<div class="metric-card">
              <div class="metric-label">MODALITY</div>
              <div class="metric-value" style="color:{mc}; font-size:22px;">{r['modality']}</div>
              <div class="metric-sub">conf {r['confidence']:.2f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""<div class="metric-card">
              <div class="metric-label">EVIDENCE</div>
              <div class="metric-value">{result['evidence_used']}</div>
              <div class="metric-sub">records retrieved</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k3:
        gs = f["grounding_score"]
        gs_color = "#4ade80" if gs >= 0.75 else ("#facc15" if gs >= 0.5 else "#f87171")
        st.markdown(
            f"""<div class="metric-card">
              <div class="metric-label">GROUNDING</div>
              <div class="metric-value" style="color:{gs_color};">{gs:.2f}</div>
              <div class="metric-sub">faithfulness score</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""<div class="metric-card">
              <div class="metric-label">LATENCY</div>
              <div class="metric-value">{lat['total']}<span style="font-size:14px; color:#4a5568;">ms</span></div>
              <div class="metric-sub">end-to-end</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Main tabs ──────────────────────────────────────────────────────────
    tab_answer, tab_routing, tab_evidence, tab_scores = st.tabs(
        ["ANSWER", "ROUTING", "EVIDENCE", "FAITHFULNESS"]
    )

    with tab_answer:
        st.markdown('<div class="section-header">GENERATED ANSWER</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="answer-block">{result["answer"].replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

        # Latency breakdown
        st.markdown('<div class="section-header">STAGE LATENCY</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div>
  <span class="latency-chip">Route <span>{lat['routing']}ms</span></span>
  <span class="latency-chip">Retrieve <span>{lat['retrieval']}ms</span></span>
  <span class="latency-chip">Generate <span>{lat['generation']}ms</span></span>
  <span class="latency-chip">Total <span>{lat['total']}ms</span></span>
</div>""",
            unsafe_allow_html=True,
        )

    with tab_routing:
        st.markdown('<div class="section-header">ROUTING DECISION</div>', unsafe_allow_html=True)
        badge_class = f"badge badge-{r['modality']}"
        st.markdown(
            f"""<div class="routing-panel">
              <span class="{badge_class}">{r['modality']}</span>
              <span style="margin-left:10px; font-size:13px; color:#a0aec0;">
                confidence {r['confidence']:.3f}
              </span>
              <div class="routing-reasoning">{r['reasoning']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        if r.get("filters"):
            st.markdown('<div class="section-header">EXTRACTED FILTERS</div>', unsafe_allow_html=True)
            st.json(r["filters"])

        # Modality guide
        st.markdown('<div class="section-header">MODALITY REFERENCE</div>', unsafe_allow_html=True)
        mod_info = {
            "TEXT": ("Clinical Notes", "ChromaDB cosine similarity over progress notes", "#4ade80"),
            "LABS": ("Lab Time-Series", "Pandas filter over CBC/CMP/tumor markers across visits", "#60a5fa"),
            "GENOMIC": ("NGS Profiles", "Exact/fuzzy match over FoundationOne CDx mutation reports", "#c084fc"),
            "FUSED": ("Cross-Modal Join", "Patient-ID join across notes + labs + genomics", "#fb923c"),
        }
        cols = st.columns(4)
        for i, (mod, (label, desc, color)) in enumerate(mod_info.items()):
            active = mod == r["modality"]
            border = f"2px solid {color}" if active else "1px solid #1e2535"
            with cols[i]:
                st.markdown(
                    f"""<div style="background:#0d1117; border:{border}; border-radius:8px;
                                   padding:12px; text-align:center; opacity:{'1' if active else '0.5'};">
                      <div style="font-size:10px; letter-spacing:2px; color:{color};
                                  font-family:'IBM Plex Mono',monospace; margin-bottom:4px;">{mod}</div>
                      <div style="font-size:12px; color:#e2e8f0; font-weight:500;">{label}</div>
                      <div style="font-size:11px; color:#4a5568; margin-top:4px; line-height:1.4;">{desc}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    with tab_evidence:
        st.markdown(
            f'<div class="section-header">RETRIEVED RECORDS — {r["modality"]}</div>',
            unsafe_allow_html=True,
        )

        modality = r["modality"]
        retrieved = result["retrieved"]

        if not retrieved:
            st.info("No records retrieved for this query.")
        elif modality == "FUSED":
            for rec in retrieved[:8]:
                pid = rec.get("patient_id", "?")
                sources = ", ".join(rec.get("sources", []))
                lines = [f"<span class='evidence-pid'>{pid}</span>  sources: {sources}"]
                if "genomic" in rec:
                    g = rec["genomic"]
                    lines.append(
                        f"  genomic: {g['primary_alteration']} | {g.get('cancer_type','')} | "
                        f"TMB {g.get('tmb_score','')} {g.get('tmb_class','')} | MSI {g.get('msi_status','')}"
                    )
                if "labs" in rec:
                    snap = rec["labs"].get("snapshot", {})
                    snap_str = "  ".join(f"{k}={v}" for k, v in snap.items() if v is not None)
                    flag = rec["labs"].get("flag", "")
                    flag_str = f" <span class='evidence-flag'>⚑{flag}</span>" if flag and flag not in ("NORMAL", "UNKNOWN", "") else ""
                    lines.append(f"  labs: {snap_str}{flag_str}")
                if "notes" in rec:
                    snippet = rec["notes"].get("snippet", "")[:200]
                    lines.append(f"  note: {snippet}…")
                st.markdown(
                    f'<div class="evidence-record">{"<br>".join(lines)}</div>',
                    unsafe_allow_html=True,
                )
        elif modality == "LABS":
            for rec in retrieved[:12]:
                snap = rec.get("snapshot", {})
                snap_str = "  ".join(f"{k}={v}" for k, v in snap.items() if v is not None)
                flag = rec.get("flag", "")
                flag_str = f"<span class='evidence-flag'>  ⚑{flag}</span>" if flag and flag not in ("NORMAL", "UNKNOWN", "") else ""
                st.markdown(
                    f"""<div class="evidence-record">
                      <span class='evidence-pid'>{rec.get('patient_id','?')}</span>
                      {rec.get('date','')}  visit {rec.get('visit','')}
                      {flag_str}<br>
                      {rec.get('metric','')}={rec.get('value','')} | {snap_str}
                    </div>""",
                    unsafe_allow_html=True,
                )
        elif modality == "GENOMIC":
            for rec in retrieved[:10]:
                co = ", ".join(rec.get("co_alterations") or []) or "—"
                tmb_color = "#fb923c" if rec.get("tmb_class") == "TMB-High" else "#8899aa"
                msi_color = "#fb923c" if rec.get("msi_status") == "MSI-H" else "#8899aa"
                st.markdown(
                    f"""<div class="evidence-record">
                      <span class='evidence-pid'>{rec.get('patient_id','?')}</span>
                      {rec.get('cancer_type','')}<br>
                      primary: <b style="color:#e2e8f0;">{rec.get('primary_alteration','')}</b>
                      co-alt: {co}<br>
                      TMB <span style="color:{tmb_color};">{rec.get('tmb_score','')} ({rec.get('tmb_class','')})</span>  |
                      MSI <span style="color:{msi_color};">{rec.get('msi_status','')}</span>  |
                      PD-L1 TPS {rec.get('pdl1_tps','')}%
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:  # TEXT
            for rec in retrieved[:5]:
                score_color = "#4ade80" if rec.get("score", 0) >= 0.75 else (
                    "#facc15" if rec.get("score", 0) >= 0.5 else "#f87171"
                )
                st.markdown(
                    f"""<div class="evidence-record">
                      <span class='evidence-pid'>{rec.get('patient_id','?')}</span>
                      {rec.get('date','')}
                      sim <span style="color:{score_color};">{rec.get('score','')}</span><br>
                      {rec.get('snippet','')[:350]}…
                    </div>""",
                    unsafe_allow_html=True,
                )

    with tab_scores:
        st.markdown('<div class="section-header">FAITHFULNESS EVALUATION</div>', unsafe_allow_html=True)

        scores_data = [
            ("GROUNDING SCORE", f["grounding_score"], "#4a90d9", "Fraction of answer facts traceable to evidence"),
            ("HALLUCINATION RISK", f["hallucination_risk"], "#f87171", "Risk of fabricated clinical data (lower = better)"),
            ("COMPLETENESS", f["completeness"], "#4ade80", "Coverage of all question aspects in the answer"),
        ]
        for label, val, color, desc in scores_data:
            pct = int(val * 100)
            st.markdown(
                f"""<div style="margin: 14px 0;">
                  <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span style="font-size:10px; letter-spacing:2px; color:#4a5568;
                                 font-family:'IBM Plex Mono',monospace;">{label}</span>
                    <span style="font-size:13px; color:{color}; font-family:'IBM Plex Mono',monospace;
                                 font-weight:600;">{val:.3f}</span>
                  </div>
                  <div style="background:#1e2535; border-radius:3px; height:6px;">
                    <div style="width:{pct}%; background:{color}; height:100%; border-radius:3px;
                                transition:width 0.4s;"></div>
                  </div>
                  <div style="font-size:11px; color:#4a5568; margin-top:3px;">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        if f.get("flags"):
            st.markdown('<div class="section-header">FLAGS</div>', unsafe_allow_html=True)
            for flag in f["flags"]:
                st.markdown(
                    f'<div style="font-size:12px; color:#f87171; font-family:\'IBM Plex Mono\',monospace; '
                    f'padding:4px 0;">⚑ {flag}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div style="font-size:12px; color:#4ade80; font-family:\'IBM Plex Mono\',monospace; '
                'padding:8px 0;">✓ No faithfulness flags raised</div>',
                unsafe_allow_html=True,
            )

# ── Empty state ────────────────────────────────────────────────────────────
elif not st.session_state.get("history"):
    st.markdown(
        """
<div style="text-align:center; padding:60px 20px; color:#4a5568;">
  <div style="font-size:40px; margin-bottom:16px;">🧬</div>
  <div style="font-size:14px; font-family:'IBM Plex Mono',monospace; letter-spacing:1px;
              margin-bottom:8px; color:#718096;">
    READY TO QUERY
  </div>
  <div style="font-size:13px; color:#4a5568; max-width:400px; margin:0 auto; line-height:1.7;">
    Select a sample query from the sidebar or type your own clinical question above.
    The router will classify it, retrieve evidence across modalities, and generate
    a grounded answer with faithfulness scoring.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# ── Query history (bottom) ────────────────────────────────────────────────
if len(st.session_state.get("history", [])) > 1:
    st.markdown('<div class="section-header" style="margin-top:40px;">QUERY HISTORY</div>', unsafe_allow_html=True)
    for prev in st.session_state.history[1:6]:
        r = prev["routing"]
        color = modality_colors.get(r["modality"], "#e2e8f0")
        st.markdown(
            f"""<div style="display:flex; align-items:center; padding:8px 12px;
                            background:#0d1117; border:1px solid #1e2535; border-radius:6px;
                            margin:4px 0; cursor:default;">
              <span style="font-size:10px; color:{color}; font-family:'IBM Plex Mono',monospace;
                           letter-spacing:1px; width:80px;">{r['modality']}</span>
              <span style="font-size:13px; color:#a0aec0; flex:1;">{prev['query']}</span>
              <span style="font-size:11px; color:#4a5568; font-family:'IBM Plex Mono',monospace;">
                {prev['faithfulness']['grounding_score']:.2f} grounding
              </span>
            </div>""",
            unsafe_allow_html=True,
        )
