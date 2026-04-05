"""
Multimodal Clinical Query Router — Streamlit UI
Clean light theme, production-grade oncology informatics interface.
"""

import json
import os
from typing import Any

import streamlit as st

st.set_page_config(
    page_title="Clinical Query Router",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f7f8fc;
    color: #1a1f36;
}
.stApp { background-color: #f7f8fc; }

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e8eaf0;
}

/* KPI cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 10px;
    padding: 18px 20px;
    margin: 4px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.kpi-label {
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #8792a2;
    margin-bottom: 6px;
    font-family: 'DM Mono', monospace;
}
.kpi-value {
    font-size: 28px;
    font-weight: 600;
    color: #1a1f36;
    font-family: 'DM Sans', sans-serif;
    line-height: 1;
}
.kpi-sub {
    font-size: 11px;
    color: #8792a2;
    margin-top: 4px;
}

/* Modality badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    font-family: 'DM Mono', monospace;
}
.badge-TEXT    { background: #e6f9f0; color: #0e7a4a; }
.badge-LABS    { background: #e8f0fe; color: #1a56db; }
.badge-GENOMIC { background: #f3e8ff; color: #7c3aed; }
.badge-FUSED   { background: #fff3e0; color: #c05e00; }

/* Answer block */
.answer-block {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-left: 4px solid #1a56db;
    border-radius: 0 10px 10px 0;
    padding: 20px 24px;
    font-size: 14px;
    line-height: 1.75;
    color: #1a1f36;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* Evidence cards */
.evidence-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
    color: #4a5568;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.evidence-pid { color: #1a56db; font-weight: 500; }
.evidence-flag { color: #e53e3e; font-weight: 600; }

/* Section headers */
.section-hdr {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8792a2;
    margin: 20px 0 10px 0;
    font-family: 'DM Mono', monospace;
    padding-bottom: 6px;
    border-bottom: 1px solid #e8eaf0;
}

/* Routing panel */
.routing-panel {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.routing-reasoning {
    font-size: 13px;
    color: #4a5568;
    margin-top: 10px;
    line-height: 1.6;
}

/* Latency chips */
.chip {
    display: inline-block;
    background: #f0f2f8;
    border: 1px solid #e8eaf0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    font-family: 'DM Mono', monospace;
    color: #4a5568;
    margin: 3px 4px 3px 0;
}
.chip b { color: #1a1f36; }

/* Modality grid cards */
.mod-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: border-color 0.2s;
}
.mod-card.active { border-width: 2px; }

/* Streamlit overrides */
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
header[data-testid="stHeader"] { background: transparent; }

.stTextInput input {
    background: #ffffff !important;
    border: 1px solid #d1d9e6 !important;
    border-radius: 8px !important;
    color: #1a1f36 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #1a56db !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.1) !important;
}

.stButton > button {
    background: #1a56db !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #1648c0 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 2px solid #e8eaf0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8792a2;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #1a56db !important;
    border-bottom: 2px solid #1a56db !important;
}

div[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e8eaf0 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Init ───────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_pipeline():
    if not os.path.exists("data/clinical_notes.json"):
        from scripts.generate_data import main as gen_main
        gen_main()
    from src.pipeline import run_query
    return run_query


@st.cache_resource(show_spinner=False)
def warmup_chroma():
    from src.retrievers import _get_chroma
    _get_chroma()


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="padding: 4px 0 24px 0;">
  <div style="font-size: 20px; font-weight: 600; color: #1a1f36; line-height: 1.2;">
    Clinical Query Router
  </div>
  <div style="font-size: 12px; color: #8792a2; margin-top: 4px;">
    Multimodal oncology RAG · 4 modalities
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">SAMPLE QUERIES</div>', unsafe_allow_html=True)

    examples = {
        "🧬 Genomic": [
            "Which patients have EGFR L858R mutations?",
            "Find all KRAS G12C positive patients",
            "Show MSI-H patients with TMB-High status",
        ],
        "🔬 Labs": [
            "Which patients have CRP above 10 mg/L?",
            "Find patients with hemoglobin below 9 g/dL",
            "Show patients with LDH above 400",
        ],
        "📋 Clinical Notes": [
            "Find notes documenting grade 3 neutropenia",
            "Which patients were referred to palliative care?",
            "Summarize treatment response in NSCLC patients",
        ],
        "🔀 Cross-Modal": [
            "Which EGFR patients have CRP above 10 and documented progression?",
            "Find KRAS G12C patients with elevated LDH and progressive disease",
            "Show MSI-H patients with CRP flagged HIGH and pembrolizumab response",
        ],
    }

    selected_query = None
    for group, queries in examples.items():
        with st.expander(group, expanded=False):
            for q in queries:
                if st.button(q, key=f"q_{hash(q)}", use_container_width=True):
                    selected_query = q

    st.markdown('<div class="section-hdr" style="margin-top:24px;">API KEY</div>', unsafe_allow_html=True)
    groq_key = st.text_input(
        "Groq API Key",
        label_visibility="collapsed",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        placeholder="gsk_... (free at console.groq.com)",
    )
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    st.markdown("""
<div style="margin-top: 24px; background: #f7f8fc; border: 1px solid #e8eaf0;
            border-radius: 8px; padding: 14px; font-size: 11px; color: #8792a2;
            font-family: 'DM Mono', monospace; line-height: 1.8;">
  <div style="color: #4a5568; font-weight: 500; margin-bottom: 6px;">TECH STACK</div>
  ChromaDB · cosine similarity<br>
  Pandas · structured lab filter<br>
  Groq · llama-3.3-70b-versatile<br>
  LLM-as-judge · faithfulness eval<br>
  25 patients · 8 visits/patient
</div>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding-bottom: 24px; border-bottom: 1px solid #e8eaf0; margin-bottom: 28px;">
  <h1 style="font-size: 26px; font-weight: 600; color: #1a1f36; margin: 0 0 6px 0;">
    Multimodal Clinical Query Router
  </h1>
  <p style="color: #8792a2; font-size: 13px; margin: 0; max-width: 580px; line-height: 1.6;">
    Routes natural language oncology questions to the right retrieval modality —
    clinical notes, lab time-series, genomic profiles, or cross-modal joins —
    and generates grounded answers with faithfulness scoring.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Query input ────────────────────────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])
with col_q:
    query_val = selected_query or st.session_state.get("last_query", "")
    query_input = st.text_input(
        "Query",
        label_visibility="collapsed",
        value=query_val,
        placeholder="Ask a clinical question — e.g. 'Which EGFR patients have CRP above 10?'",
        key="query_field",
    )
with col_btn:
    run_btn = st.button("Run Query", use_container_width=True)

# ── History state ──────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Execute ────────────────────────────────────────────────────────────────
MODALITY_COLORS = {
    "TEXT": "#0e7a4a",
    "LABS": "#1a56db",
    "GENOMIC": "#7c3aed",
    "FUSED": "#c05e00",
}

if (run_btn or selected_query) and query_input.strip():
    if not os.getenv("GROQ_API_KEY"):
        st.warning("Add your Groq API key in the sidebar to enable answer generation.")
        st.stop()

    with st.spinner("Routing query and retrieving evidence…"):
        run_query = init_pipeline()
        warmup_chroma()
        result = run_query(query_input.strip(), top_k=6)

    st.session_state.history.insert(0, result)
    st.session_state.last_query = query_input.strip()

    r = result["routing"]
    f = result["faithfulness"]
    lat = result["latency_ms"]
    mc = MODALITY_COLORS.get(r["modality"], "#1a1f36")

    # ── KPI row ────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">MODALITY</div>
  <div class="kpi-value" style="color:{mc}; font-size:22px;">{r['modality']}</div>
  <div class="kpi-sub">confidence {r['confidence']:.2f}</div>
</div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">RECORDS RETRIEVED</div>
  <div class="kpi-value">{result['evidence_used']}</div>
  <div class="kpi-sub">across data sources</div>
</div>""", unsafe_allow_html=True)

    with k3:
        gs = f["grounding_score"]
        gc = "#0e7a4a" if gs >= 0.75 else ("#d97706" if gs >= 0.5 else "#dc2626")
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">GROUNDING SCORE</div>
  <div class="kpi-value" style="color:{gc};">{gs:.2f}</div>
  <div class="kpi-sub">faithfulness to evidence</div>
</div>""", unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">TOTAL LATENCY</div>
  <div class="kpi-value">{lat['total']}<span style="font-size:14px;color:#8792a2;">ms</span></div>
  <div class="kpi-sub">end-to-end</div>
</div>""", unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab_ans, tab_route, tab_evid, tab_faith = st.tabs(["Answer", "Routing", "Evidence", "Faithfulness"])

    with tab_ans:
        st.markdown('<div class="section-hdr">GENERATED ANSWER</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="answer-block">{result["answer"].replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-hdr">PIPELINE LATENCY</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div>
  <span class="chip">Route <b>{lat['routing']}ms</b></span>
  <span class="chip">Retrieve <b>{lat['retrieval']}ms</b></span>
  <span class="chip">Generate <b>{lat['generation']}ms</b></span>
  <span class="chip">Total <b>{lat['total']}ms</b></span>
</div>""", unsafe_allow_html=True)

    with tab_route:
        st.markdown('<div class="section-hdr">ROUTING DECISION</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="routing-panel">
  <span class="badge badge-{r['modality']}">{r['modality']}</span>
  <span style="margin-left:10px; font-size:13px; color:#8792a2;">
    confidence {r['confidence']:.3f}
  </span>
  <div class="routing-reasoning">{r['reasoning']}</div>
</div>""", unsafe_allow_html=True)

        if r.get("filters"):
            st.markdown('<div class="section-hdr">EXTRACTED FILTERS</div>', unsafe_allow_html=True)
            st.json(r["filters"])

        st.markdown('<div class="section-hdr">MODALITY REFERENCE</div>', unsafe_allow_html=True)
        mod_info = {
            "TEXT": ("Clinical Notes", "ChromaDB cosine similarity", "#0e7a4a", "#e6f9f0"),
            "LABS": ("Lab Time-Series", "Pandas structured filter", "#1a56db", "#e8f0fe"),
            "GENOMIC": ("NGS Profiles", "Gene/variant exact match", "#7c3aed", "#f3e8ff"),
            "FUSED": ("Cross-Modal Join", "Patient-ID join across sources", "#c05e00", "#fff3e0"),
        }
        cols = st.columns(4)
        for i, (mod, (label, desc, color, bg)) in enumerate(mod_info.items()):
            active = mod == r["modality"]
            border = f"2px solid {color}" if active else "1px solid #e8eaf0"
            with cols[i]:
                st.markdown(f"""
<div style="background:{bg if active else '#fff'}; border:{border}; border-radius:10px;
            padding:14px; text-align:center; opacity:{'1' if active else '0.6'};">
  <div style="font-size:11px; color:{color}; font-weight:600; margin-bottom:4px;">{mod}</div>
  <div style="font-size:12px; color:#1a1f36; font-weight:500;">{label}</div>
  <div style="font-size:11px; color:#8792a2; margin-top:4px; line-height:1.4;">{desc}</div>
</div>""", unsafe_allow_html=True)

    with tab_evid:
        modality = r["modality"]
        retrieved = result["retrieved"]
        st.markdown(f'<div class="section-hdr">RETRIEVED RECORDS — {modality}</div>', unsafe_allow_html=True)

        if not retrieved:
            st.info("No records retrieved.")
        elif modality == "FUSED":
            for rec in retrieved[:8]:
                pid = rec.get("patient_id", "?")
                sources = ", ".join(rec.get("sources", []))
                lines = [f"<span class='evidence-pid'>{pid}</span> · sources: {sources}"]
                if "genomic" in rec:
                    g = rec["genomic"]
                    lines.append(f"genomic: {g['primary_alteration']} | {g.get('cancer_type','')} | TMB {g.get('tmb_score','')} {g.get('tmb_class','')} | MSI {g.get('msi_status','')}")
                if "labs" in rec:
                    snap = rec["labs"].get("snapshot", {})
                    snap_str = "  ".join(f"{k}={v}" for k, v in snap.items() if v is not None)
                    flag = rec["labs"].get("flag", "")
                    flag_html = f" <span class='evidence-flag'>⚑ {flag}</span>" if flag and flag not in ("NORMAL", "UNKNOWN", "") else ""
                    lines.append(f"labs: {snap_str}{flag_html}")
                if "notes" in rec:
                    lines.append(f"note: {rec['notes'].get('snippet','')[:200]}…")
                st.markdown(f'<div class="evidence-card">{"<br>".join(lines)}</div>', unsafe_allow_html=True)

        elif modality == "LABS":
            for rec in retrieved[:12]:
                snap = rec.get("snapshot", {})
                snap_str = "  ".join(f"{k}={v}" for k, v in snap.items() if v is not None)
                flag = rec.get("flag", "")
                flag_html = f"<span class='evidence-flag'> ⚑{flag}</span>" if flag and flag not in ("NORMAL", "UNKNOWN", "") else ""
                st.markdown(f"""
<div class="evidence-card">
  <span class='evidence-pid'>{rec.get('patient_id','?')}</span>
  · {rec.get('date','')} · visit {rec.get('visit','')}
  {flag_html}<br>
  {rec.get('metric','')} = {rec.get('value','')} | {snap_str}
</div>""", unsafe_allow_html=True)

        elif modality == "GENOMIC":
            for rec in retrieved[:10]:
                co = ", ".join(rec.get("co_alterations") or []) or "—"
                tmb_c = "#c05e00" if rec.get("tmb_class") == "TMB-High" else "#8792a2"
                msi_c = "#dc2626" if rec.get("msi_status") == "MSI-H" else "#8792a2"
                st.markdown(f"""
<div class="evidence-card">
  <span class='evidence-pid'>{rec.get('patient_id','?')}</span> · {rec.get('cancer_type','')}<br>
  primary: <b style="color:#1a1f36;">{rec.get('primary_alteration','')}</b> · co-alt: {co}<br>
  TMB <span style="color:{tmb_c};">{rec.get('tmb_score','')} ({rec.get('tmb_class','')})</span> ·
  MSI <span style="color:{msi_c};">{rec.get('msi_status','')}</span> ·
  PD-L1 TPS {rec.get('pdl1_tps','')}%
</div>""", unsafe_allow_html=True)

        else:  # TEXT
            for rec in retrieved[:5]:
                sc = rec.get("score", 0)
                sc_c = "#0e7a4a" if sc >= 0.75 else ("#d97706" if sc >= 0.5 else "#dc2626")
                st.markdown(f"""
<div class="evidence-card">
  <span class='evidence-pid'>{rec.get('patient_id','?')}</span>
  · {rec.get('date','')}
  · sim <span style="color:{sc_c};">{sc}</span><br>
  {rec.get('snippet','')[:350]}…
</div>""", unsafe_allow_html=True)

    with tab_faith:
        st.markdown('<div class="section-hdr">FAITHFULNESS EVALUATION</div>', unsafe_allow_html=True)

        scores = [
            ("Grounding Score", f["grounding_score"], "#1a56db", "Fraction of answer facts traceable to retrieved evidence"),
            ("Hallucination Risk", f["hallucination_risk"], "#dc2626", "Risk of fabricated data — lower is better"),
            ("Completeness", f["completeness"], "#0e7a4a", "Coverage of all aspects of the question"),
        ]
        for label, val, color, desc in scores:
            pct = int(val * 100)
            st.markdown(f"""
<div style="margin: 16px 0;">
  <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
    <span style="font-size:13px; font-weight:500; color:#1a1f36;">{label}</span>
    <span style="font-size:14px; font-weight:600; color:{color};">{val:.3f}</span>
  </div>
  <div style="background:#e8eaf0; border-radius:4px; height:6px;">
    <div style="width:{pct}%; background:{color}; height:100%; border-radius:4px;"></div>
  </div>
  <div style="font-size:11px; color:#8792a2; margin-top:4px;">{desc}</div>
</div>""", unsafe_allow_html=True)

        if f.get("flags"):
            st.markdown('<div class="section-hdr">FLAGS</div>', unsafe_allow_html=True)
            for flag in f["flags"]:
                st.markdown(f'<div style="font-size:12px; color:#dc2626; padding:4px 0;">⚑ {flag}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="margin-top:12px; padding:12px 16px; background:#e6f9f0; border-radius:8px;
            font-size:13px; color:#0e7a4a; font-weight:500;">
  ✓ No faithfulness flags raised
</div>""", unsafe_allow_html=True)

# ── Empty state ────────────────────────────────────────────────────────────
elif not st.session_state.get("history"):
    st.markdown("""
<div style="text-align:center; padding:60px 20px;">
  <div style="font-size:48px; margin-bottom:16px;">🧬</div>
  <div style="font-size:16px; font-weight:600; color:#1a1f36; margin-bottom:8px;">
    Ready to query
  </div>
  <div style="font-size:13px; color:#8792a2; max-width:400px; margin:0 auto; line-height:1.7;">
    Select a sample query from the sidebar or type your own clinical question above.
    The router will classify it, retrieve evidence, and generate a grounded answer.
  </div>
</div>""", unsafe_allow_html=True)

# ── History ────────────────────────────────────────────────────────────────
if len(st.session_state.get("history", [])) > 1:
    st.markdown('<div class="section-hdr" style="margin-top:40px;">RECENT QUERIES</div>', unsafe_allow_html=True)
    for prev in st.session_state.history[1:5]:
        pr = prev["routing"]
        mc = MODALITY_COLORS.get(pr["modality"], "#1a1f36")
        gs = prev["faithfulness"]["grounding_score"]
        st.markdown(f"""
<div style="display:flex; align-items:center; padding:10px 14px; background:#fff;
            border:1px solid #e8eaf0; border-radius:8px; margin:4px 0;">
  <span class="badge badge-{pr['modality']}" style="margin-right:12px; min-width:72px; text-align:center;">
    {pr['modality']}
  </span>
  <span style="font-size:13px; color:#1a1f36; flex:1;">{prev['query']}</span>
  <span style="font-size:11px; color:#8792a2; font-family:'DM Mono',monospace;">
    {gs:.2f} grounding
  </span>
</div>""", unsafe_allow_html=True)
