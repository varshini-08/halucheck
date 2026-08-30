"""Product-style Streamlit interface for HaluCheck."""
from __future__ import annotations

import os
import traceback
from html import escape
from time import perf_counter

import streamlit as st

from services.analysis_service import HaluCheckPipeline
from services.llm_service import LLMService, LLMServiceException
from verification.verification_pipeline import VerificationPipeline
from visualization import dashboard


@st.cache_resource(show_spinner=False)
def get_pipeline() -> HaluCheckPipeline:
    return HaluCheckPipeline(verification_pipeline=VerificationPipeline())


@st.cache_resource(show_spinner=False)
def get_llm_service(api_key: str, provider: str) -> LLMService:
    # Provider selection is explicit; production defaults remain Groq.
    os.environ["LLM_PROVIDER"] = provider
    return LLMService(api_key=api_key)


def apply_theme(theme: str) -> None:
    dark = theme == "Dark"
    bg = "#0f172a" if dark else "#f5f7fb"
    surface = "#111827" if dark else "#ffffff"
    card = "#1f2937" if dark else "#f8fafc"
    text = "#f8fafc" if dark else "#111827"
    muted = "#94a3b8" if dark else "#64748b"
    border = "#334155" if dark else "#e2e8f0"
    accent = "#2563eb"
    success = "#16a34a"
    warning = "#ea580c"
    danger = "#dc2626"

    st.markdown(
        f"""
        <style>
            .stApp {{background:{bg}; color:{text};}}
            [data-testid="stSidebar"] {{background:#111827; border-right:1px solid #1f2937; min-width:290px;}}
            [data-testid="stSidebar"] * {{color:#e5e7eb;}}
            [data-testid="stSidebar"] [data-baseweb="select"] > div, [data-testid="stSidebar"] input {{background:#1f2937 !important; color:#f8fafc !important; border-color:#374151 !important;}}
            [data-testid="stSidebar"] .stButton>button {{background:#1f2937; border:1px solid #374151; color:#e5e7eb; min-height:2.35rem; text-align:left;}}
            [data-testid="stSidebar"] .stButton>button:hover {{background:#273449; border-color:#4b67a1;}}
            .block-container {{max-width:1220px; padding:1.5rem 1.2rem 3rem;}}
            .app-shell {{display:flex; flex-direction:column; gap:1.1rem;}}
            .hero-card, .input-card, .welcome-card, .result-card, .summary-card, .process-card, .verdict-card, .performance-card {{
                background:{surface}; border:1px solid {border}; border-radius:24px; box-shadow:0 12px 30px rgba(15,23,42,.08);
            }}
            .hero-card {{padding:1.2rem 1.5rem; margin-bottom:.4rem; display:flex; align-items:center; justify-content:space-between; gap:1rem;}}
            .input-card {{padding:1.2rem 1.2rem 1.1rem; margin-bottom:.3rem;}}
            .welcome-card {{padding:2rem;}}
            .result-card {{padding:1.2rem 1.2rem 1.4rem; margin-top:.4rem;}}
            .process-card {{padding:1.2rem 1.2rem 1rem; margin-top:.6rem;}}
            .verdict-card {{padding:1.2rem 1.3rem; margin-top:1.2rem;}}
            .performance-card {{padding:1rem 1.1rem; margin-top:1rem;}}
            .summary-card {{padding:1rem 1rem 1.05rem; min-height:120px; border-top:4px solid {accent};}}
            .summary-card.supported {{background:#f0fdf4; border-color:#86efac; border-top-color:{success};}}
            .summary-card.contradicted {{background:#fef2f2; border-color:#fca5a5; border-top-color:{danger};}}
            .summary-card.neutral {{background:#fff7ed; border-color:#fdba74; border-top-color:{warning};}}
            .summary-card.confidence {{border-top-color:{accent};}}
            .summary-card.verified {{background:#f0fdf4; border-color:#86efac; border-top-color:{success};}}
            .summary-card.failed {{background:#fef2f2; border-color:#fca5a5; border-top-color:{danger};}}
            .summary-card.needs-review {{background:#fff7ed; border-color:#fdba74; border-top-color:{warning};}}
            .summary-card.verified .summary-label, .summary-card.verified .summary-value {{color:#166534;}}
            .summary-card.failed .summary-label, .summary-card.failed .summary-value {{color:#991b1b;}}
            .summary-card.needs-review .summary-label, .summary-card.needs-review .summary-value {{color:#9a3412;}}
            .verification-legend {{display:flex; gap:.55rem; flex-wrap:wrap; margin-bottom:.7rem; font-size:.78rem; font-weight:700;}}
            .verification-legend span {{padding:.28rem .6rem; border-radius:999px;}}
            .verification-legend .supported {{background:#dcfce7; color:#166534;}}
            .verification-legend .contradicted {{background:#fee2e2; color:#991b1b;}}
            .verification-legend .neutral {{background:#ffedd5; color:#9a3412;}}
            .verified-response {{padding:1rem 1.1rem; border-radius:18px; background:{card}; border:1px solid {border}; color:{text}; line-height:1.9; white-space:pre-wrap;}}
            .verified-response__fact {{padding:.08rem .18rem; border-radius:.28rem; font-weight:600; box-decoration-break:clone; -webkit-box-decoration-break:clone;}}
            .verified-response__fact.supported {{background:#dcfce7; color:#166534;}}
            .verified-response__fact.contradicted {{background:#fee2e2; color:#991b1b;}}
            .verified-response__fact.neutral {{background:#ffedd5; color:#9a3412;}}
            .summary-card.supported .summary-label, .summary-card.supported .summary-value {{color:#166534;}}
            .summary-card.contradicted .summary-label, .summary-card.contradicted .summary-value {{color:#991b1b;}}
            .summary-card.neutral .summary-label, .summary-card.neutral .summary-value {{color:#9a3412;}}
            .section-kicker {{color:{accent}; font-size:.74rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem;}}
            .section-title {{font-size:1.35rem; font-weight:800; margin-bottom:.3rem;}}
            .section-subtitle {{font-size:.95rem; color:{muted}; line-height:1.6; margin-bottom:.7rem;}}
            .hero-title {{font-size:2.6rem; font-weight:800; letter-spacing:-.03em; line-height:1.08; margin:.2rem 0 .55rem;}}
            .hero-subtitle {{font-size:1.05rem; color:{muted}; line-height:1.65; max-width:760px;}}
            .header-model {{padding:.45rem .75rem; border-radius:12px; background:{card}; border:1px solid {border}; color:{muted}; font-size:.82rem; white-space:nowrap;}}
            .top-nav {{display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.8rem 1.1rem; background:{surface}; border:1px solid {border}; border-radius:18px; box-shadow:0 8px 24px rgba(15,23,42,.06);}}
            .top-nav__title {{font-weight:800; font-size:1.05rem; color:{text};}}
            .model-tabs {{display:flex; align-items:center; gap:.45rem; flex-wrap:wrap;}}
            .model-tab {{padding:.42rem .72rem; border:1px solid {border}; border-radius:10px; color:{muted}; font-size:.82rem; font-weight:700;}}
            .model-tab.active {{background:#dbeafe; border-color:#93c5fd; color:#1d4ed8;}}
            .top-nav__status {{font-size:.8rem; color:{muted};}}
            .chip {{display:inline-block; padding:.3rem .65rem; border-radius:999px; background:#dbeafe; color:{accent}; font-size:.77rem; font-weight:700;}}
            .chip.secondary {{background:{card}; color:{text}; border:1px solid {border};}}
            .body-card {{padding:1rem 1.1rem; border-radius:18px; background:{card}; border:1px solid {border}; color:{text}; line-height:1.7; white-space:pre-wrap; max-height:320px; overflow:auto;}}
            .welcome-card .body-card {{max-height:none;}}
            .process-list {{display:flex; flex-direction:column; gap:.55rem; margin-top:.75rem;}}
            .process-item {{display:flex; align-items:center; gap:.7rem; padding:.6rem .75rem; border-radius:12px; background:{card}; color:{muted}; border:1px solid {border};}}
            .process-item.done {{color:{text}; border-color:{accent};}}
            .process-badge {{display:inline-flex; flex:0 0 1.55rem; align-items:center; justify-content:center; width:1.55rem; height:1.55rem; overflow:hidden; line-height:1; border-radius:999px; background:{accent}; color:white; font-weight:800;}}
            .process-item.done .process-badge {{background:{success};}}
            .summary-value {{font-size:1.7rem; font-weight:800; margin-top:.35rem;}}
            .summary-label {{font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:{muted};}}
            .summary-icon {{font-size:1rem; margin-bottom:.25rem;}}
            .verification-badge {{display:inline-flex; align-items:center; gap:.28rem; border:1px solid; border-radius:999px; padding:.32rem .68rem; font-size:.75rem; font-weight:800; letter-spacing:.02em; white-space:nowrap;}}
            .fact-card {{border:1px solid {border}; border-radius:18px; padding:1rem 1rem .85rem; background:{card}; margin-top:.8rem;}}
            .fact-card.supported {{background:#f0fdf4; border-color:#86efac;}}
            .fact-card.contradicted {{background:#fef2f2; border-color:#fca5a5;}}
            .fact-card.neutral {{background:#fff7ed; border-color:#fdba74;}}
            .fact-head {{display:flex; justify-content:space-between; gap:1rem; align-items:center; flex-wrap:wrap; margin-bottom:.7rem;}}
            .fact-title {{font-weight:700; color:{text}; line-height:1.5;}}
            .fact-meta {{display:flex; gap:.55rem; align-items:center; flex-wrap:wrap; margin:.55rem 0 .7rem;}}
            .confidence-bar {{position:relative; height:8px; width:180px; max-width:100%; border-radius:999px; background:{border}; overflow:hidden;}}
            .confidence-bar > div {{height:100%; border-radius:999px; background:linear-gradient(90deg, {accent}, #60a5fa);}}
            .confidence-text {{font-size:.85rem; color:{muted};}}
            .evidence-card {{border:1px solid {border}; border-radius:16px; padding:.85rem .95rem; background:{surface}; margin-top:.6rem;}}
            .evidence-title {{font-weight:700; margin-bottom:.45rem; color:{text};}}
            .evidence-body {{color:{muted}; line-height:1.6; white-space:pre-wrap;}}
            .verdict-card .hero-title {{font-size:2rem; margin:.3rem 0 .25rem;}}
            .verdict-card.verified {{background:#f0fdf4; border-color:#86efac;}}
            .verdict-card.verified .hero-title {{color:#166534;}}
            .verdict-card.needs-review {{background:#fff7ed; border-color:#fdba74;}}
            .verdict-card.needs-review .hero-title {{color:#9a3412;}}
            .verdict-card.failed {{background:#fef2f2; border-color:#fca5a5;}}
            .verdict-card.failed .hero-title {{color:#991b1b;}}
            .sidebar-brand {{padding:1rem .4rem 0;}}
            .sidebar-brand .title {{font-size:1.35rem; font-weight:800; letter-spacing:-.02em;}}
            .sidebar-brand .subtitle {{font-size:.9rem; color:{muted}; margin-top:.2rem; line-height:1.45;}}
            .stButton>button {{background:{accent}; color:white; border:0; border-radius:12px; min-height:2.95rem; font-weight:700;}}
            .stButton>button:hover {{background:#1d4ed8; border:0;}}
            .stButton>button:disabled {{background:#94a3b8; color:#e2e8f0;}}
            .streamlit-expanderHeader {{border-radius:14px; padding:.7rem .85rem; background:{card}; border:1px solid {border};}}
            .streamlit-expanderContent {{padding-top:.45rem;}}
            .footer-actions {{display:flex; gap:.75rem; flex-wrap:wrap; margin-top:1rem;}}
            .hc-page-heading {{display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:.4rem 0 1rem;}}
            .hc-page-heading h1 {{font-size:2rem; margin:.1rem 0 .2rem; color:{text};}}
            .hc-page-heading p {{margin:0; color:{muted};}}
            .hc-eyebrow, .hc-card-kicker {{color:{accent}; font-size:.75rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase;}}
            .hc-model-pill {{background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; padding:.5rem .75rem; border-radius:999px; font-size:.8rem; font-weight:700;}}
            .hc-question-card, .hc-response-card, .hc-side-card, .hc-claim-card {{background:{surface}; border:1px solid {border}; border-radius:16px; box-shadow:0 8px 22px rgba(15,23,42,.06);}}
            .hc-question-card {{padding:1rem 1.1rem; margin-bottom:.8rem;}}
            .hc-question-text {{margin:.55rem 0 .3rem; padding:.75rem .85rem; border:1px solid {border}; border-radius:10px; color:{text}; background:{card};}}
            .hc-card-help {{font-size:.8rem; color:{muted};}}
            .hc-response-card {{padding:1rem 1.1rem; background:linear-gradient(120deg,#f0fdf4,#eff6ff); margin-bottom:.8rem;}}
            .hc-response-head {{display:flex; justify-content:space-between; gap:1rem; color:#166534; font-size:.85rem;}}
            .hc-response-head span {{font-size:.76rem; color:{muted};}}
            .hc-response-body {{margin-top:.65rem; padding:.8rem; border:1px solid #dbeafe; border-radius:10px; background:{surface}; color:{text}; line-height:1.65; white-space:pre-wrap; max-height:260px; overflow:auto;}}
            .hc-metrics {{display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.65rem; margin-bottom:1rem;}}
            .hc-metric {{padding:.85rem .75rem; background:{surface}; border:1px solid {border}; border-radius:14px; min-height:106px; display:flex; flex-direction:column; gap:.22rem;}}
            .hc-metric span {{font-size:.7rem; color:{muted}; font-weight:700; text-transform:uppercase; letter-spacing:.05em;}}
            .hc-metric strong {{font-size:1.45rem; color:{text};}}
            .hc-metric small {{font-size:.72rem; color:{muted};}}
            .hc-metric i {{height:4px; border-radius:10px; background:{accent}; margin-top:auto;}}
            .hc-metric.green i {{background:#22c55e;}} .hc-metric.red i {{background:#ef4444;}} .hc-metric.amber i {{background:#f59e0b;}}
            .hc-side-card {{padding:1rem; margin-bottom:.8rem;}} .hc-side-card h3 {{margin:0 0 .8rem; font-size:1rem; color:{text};}} .blue-text {{color:{accent} !important;}}
            .hc-donut {{width:150px; height:150px; border-radius:50%; margin:1rem auto; display:grid; place-items:center; background:conic-gradient(#22c55e 0 var(--supported), #ef4444 var(--supported) var(--contradicted), #f59e0b var(--contradicted) 100%);}}
            .hc-donut-hole {{width:104px; height:104px; border-radius:50%; background:{surface}; display:flex; flex-direction:column; align-items:center; justify-content:center; color:{text};}} .hc-donut-hole strong {{font-size:1.5rem;}} .hc-donut-hole span {{font-size:.75rem; color:{muted};}} .hc-donut-empty {{background:{border};}}
            .hc-legend {{display:flex; flex-direction:column; gap:.3rem; font-size:.75rem; color:{muted};}} .hc-legend .green {{color:#16a34a;}} .hc-legend .red {{color:#dc2626;}} .hc-legend .amber {{color:#d97706;}}
            .hc-detail-row {{display:flex; justify-content:space-between; gap:.75rem; padding:.5rem 0; border-bottom:1px solid {border}; font-size:.75rem; color:{muted};}} .hc-detail-row:last-child {{border-bottom:0;}} .hc-detail-row b {{color:{text}; text-align:right; max-width:58%; overflow-wrap:anywhere;}}
            .hc-section-title {{font-size:1.15rem; font-weight:800; color:{text}; margin:.2rem 0 .7rem;}} .hc-claim-card {{padding:.9rem; margin-bottom:.7rem;}} .hc-claim-head {{display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;}} .hc-claim-head small {{display:block; color:{muted}; font-size:.72rem;}} .hc-claim-head strong {{display:block; margin-top:.25rem; color:{text}; line-height:1.45;}} .hc-badge {{border:1px solid; border-radius:999px; padding:.3rem .55rem; font-size:.72rem; font-weight:800; white-space:nowrap;}} .hc-evidence {{margin-top:.75rem; padding:.7rem; background:{card}; border:1px solid {border}; border-radius:10px;}} .hc-evidence b {{color:{text}; font-size:.78rem;}} .hc-evidence p {{margin:.35rem 0; color:{muted}; line-height:1.5; font-size:.8rem;}} .hc-evidence small {{color:{muted};}} .hc-source {{float:right; color:{accent}; font-size:.7rem; font-weight:700;}}
            @media (max-width: 1050px) {{.hc-metrics {{grid-template-columns:repeat(3,minmax(0,1fr));}}}} @media (max-width: 640px) {{.hc-metrics {{grid-template-columns:repeat(2,minmax(0,1fr));}} .hc-page-heading {{align-items:flex-start; flex-direction:column;}}}}
            .hc-dashboard {{margin-top:1.1rem; padding:1rem; background:{surface}; border:1px solid {border}; border-radius:16px;}} .hc-dashboard h3 {{margin:0 0 .8rem; color:{text};}} .hc-stat-grid {{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.6rem;}} .hc-stat {{padding:.7rem; border:1px solid {border}; border-radius:10px; background:{card};}} .hc-stat span {{display:block; color:{muted}; font-size:.7rem;}} .hc-stat strong {{display:block; color:{text}; font-size:1.25rem; margin-top:.2rem;}} .hc-chart-row {{display:grid; grid-template-columns:1fr 1fr; gap:.7rem; margin-top:.8rem;}} .hc-mini-chart {{padding:.8rem; border:1px solid {border}; border-radius:10px; background:{card};}} .hc-bars {{height:90px; display:flex; align-items:flex-end; gap:4px; margin-top:.6rem;}} .hc-bars i {{flex:1; min-height:4px; background:{accent}; border-radius:4px 4px 0 0;}} .hc-distribution {{display:flex; flex-direction:column; gap:.45rem; margin-top:.7rem;}} .hc-distribution-row {{display:flex; align-items:center; gap:.5rem; font-size:.72rem; color:{muted};}} .hc-distribution-row i {{height:7px; border-radius:5px; background:#22c55e;}} .hc-distribution-row.red i {{background:#ef4444;}} .hc-distribution-row.amber i {{background:#f59e0b;}} .hc-recent {{width:100%; border-collapse:collapse; margin-top:.8rem; font-size:.72rem;}} .hc-recent th,.hc-recent td {{padding:.5rem; border-bottom:1px solid {border}; text-align:left; color:{muted};}} .hc-recent th {{color:{text};}}
            @media (max-width: 920px) {{.hero-title {{font-size:2.1rem;}} [data-testid="stSidebar"] {{min-width:250px;}}}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_question(question: str) -> None:
    """Load a previous question into the workspace without changing analysis logic."""
    st.session_state["question_input"] = question


def render_sidebar() -> tuple[str, str, str]:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div class="title">HaluCheck</div><div class="subtitle">Explainable Hallucination Detection</div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("### Connection")
        provider = st.selectbox("Large Language Model", ["Groq", "Gemini"], index=0 if os.environ.get("LLM_PROVIDER", "groq").lower() == "groq" else 1)
        env_name = "GEMINI_API_KEY" if provider == "Gemini" else "GROQ_API_KEY"
        api_key = st.text_input(
            f"{provider} API Key",
            value=os.environ.get(env_name, ""),
            type="password",
            help="Kept only for this browser session. The environment value remains supported.",
        ).strip()
        model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash") if provider == "Gemini" else os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
        st.caption(f"{provider} connected" if api_key else f"{provider} API key not configured")
        st.divider()
        st.markdown("### Retrieval")
        st.checkbox("Local Knowledge Base", value=True, disabled=True)
        st.checkbox("Wikipedia API", value=True, disabled=True)
        st.divider()
        st.markdown("### Evaluation Method")
        st.selectbox("Verification engine", ["DeBERTa-v3 MNLI"], index=0, disabled=True)
        st.divider()
        st.markdown("### Conversation History")
        history = st.session_state.get("conversation_history", [])
        if history:
            for index, item in enumerate(history[-5:][::-1]):
                st.button(item, key=f"history_{index}", use_container_width=True, on_click=load_question, args=(item,))
        else:
            st.caption("No verified questions yet.")
        st.divider()
        theme = st.selectbox("Theme", ["Dark"], index=0, disabled=True)
        st.divider()
        st.markdown("### About")
        st.caption("Version 1.0")
        st.caption("Author: HaluCheck Team")
        st.caption("Research Project")
        st.caption("Kongu Engineering College")
        return theme, api_key, provider.lower()


def processing_view(area, completed: int) -> None:
    steps = [
        "Generating AI response",
        "Extracting facts",
        "Searching knowledge base",
        "Searching Wikipedia",
        "Running verification",
        "Preparing report",
    ]
    lines = []
    for index, step in enumerate(steps):
        done = index < completed
        icon = "&#10003;" if done else "&#8226;"
        state_class = "done" if done else ""
        lines.append(
            f'<div class="process-item {state_class}"><span class="process-badge">{icon}</span><span>{step}</span></div>'
        )
    area.markdown(
        '<div class="process-card"><div class="section-kicker">Verification in progress</div><div class="process-list">' + "".join(lines) + "</div></div>",
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="HaluCheck", page_icon="âœ“", layout="wide", initial_sidebar_state="expanded")

theme, sidebar_api_key, selected_provider = render_sidebar()
apply_theme(theme)
st.session_state["selected_provider"] = selected_provider

active_model = (os.environ.get("GEMINI_MODEL", "gemini-3.6-flash") if selected_provider == "gemini" else os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")).strip()
st.markdown('<div class="app-shell">', unsafe_allow_html=True)
st.markdown(
    f'<div class="hc-page-heading"><div><div class="hc-eyebrow">AI verification workspace</div><h1>New Analysis</h1><p>Ask a factual question and verify the AI response</p></div><span class="hc-model-pill">● {escape(active_model)}</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="input-card"><div class="section-title">Your Question</div><div class="section-subtitle">Ask factual questions that can be verified against reliable sources.</div>',
    unsafe_allow_html=True,
)
question = st.text_area(
    "Question",
    placeholder="Ask a factual question...\n\nExamples\nWho invented Python?\nWho is the Prime Minister of India?\nWhen was NASA founded?",
    height=150,
    label_visibility="collapsed",
    key="question_input",
)
latest_question = st.session_state.get("latest_question", "")
action_cols = st.columns([3, 2])
clicked = action_cols[0].button("Analyze", type="primary", disabled=not question.strip(), use_container_width=True)
regenerate = action_cols[1].button("Regenerate Response", disabled=not latest_question, use_container_width=True, on_click=load_question, args=(latest_question,))
if regenerate:
    clicked = True
st.markdown("</div>", unsafe_allow_html=True)

if clicked:
    st.session_state["analysis"] = None
    ui_log = ["Question submitted"]
    st.session_state["ui_log"] = ui_log
    env_name = "GEMINI_API_KEY" if selected_provider == "gemini" else "GROQ_API_KEY"
    api_key = sidebar_api_key or os.environ.get(env_name, "").strip()
    if not api_key:
        st.error(f"{selected_provider.title()} API key not configured.")
    else:
        progress = st.empty()
        processing_view(progress, 0)
        try:
            started = perf_counter()
            response = get_llm_service(api_key, selected_provider).generate_response(question)
            ui_log.append("LLM response generated")
            processing_view(progress, 1)
            st.markdown('<div class="section-kicker" style="margin-top:1.2rem;">LLM Response</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="body-card">{escape(response).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            live_results = st.empty()
            live_items: list[str] = []

            def update_progress(message: str) -> None:
                ui_log.append(message)
                completed = 5 if message.startswith("Verifying") else 4
                processing_view(progress, completed)

            def show_verified_fact(item) -> None:
                display_label, icon, *_ = dashboard._display_result(item.label)
                live_items.append(
                    f'<div class="fact-card {item.label.lower()}"><div class="fact-head">'
                    f'<div class="fact-title">{escape(item.fact)}</div>'
                    f'{dashboard._badge(item.label)}</div></div>'
                )
                live_results.markdown(
                    '<div class="section-kicker" style="margin-top:1.2rem;">Verifying facts...</div>'
                    + "".join(live_items),
                    unsafe_allow_html=True,
                )

            analysis = get_pipeline().analyse(
                response,
                question=question,
                progress_callback=update_progress,
                verification_callback=show_verified_fact,
            )
            processing_view(progress, 6)
            st.session_state["latest_question"] = question
            st.session_state["analysis"] = analysis
            st.session_state["pipeline_seconds"] = perf_counter() - started
            ui_log.append("Verification report prepared")
            history = st.session_state.setdefault("conversation_history", [])
            if question not in history:
                history.append(question)
            # Keep structured history only for analyses that actually completed.
            # This powers the dashboard summary without introducing sample data.
            verified_items = list(analysis.verifications)
            hallucination_count = sum(bool(item.hallucination) for item in verified_items)
            fact_count = len(analysis.facts)
            analysis_history = st.session_state.setdefault("analysis_history", [])
            analysis_history.append({
                "question": question,
                "provider": selected_provider,
                "model": active_model,
                "hallucination_score": hallucination_count / fact_count if fact_count else 0.0,
                "supported": sum(item.label == "SUPPORTED" for item in verified_items),
                "contradicted": sum(item.label == "CONTRADICTED" for item in verified_items),
                "neutral": sum(item.label == "NEUTRAL" for item in verified_items),
                "processing_time": st.session_state["pipeline_seconds"],
                "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            })
        except LLMServiceException as exc:
            st.error(str(exc))
        except Exception as exc:
            # Do not hide pipeline failures: terminal and UI need the real error.
            traceback.print_exc()
            st.error(f"Unable to analyse this response: {exc}")
            st.exception(exc)

if analysis := st.session_state.get("analysis"):
    dashboard.render_analysis(
        analysis,
        st.session_state.get("latest_question", ""),
        st.session_state.get("pipeline_seconds", 0.0),
        st.session_state.get("ui_log", []),
    )
else:
    st.markdown('<div class="hc-empty-state"><strong>Ready to verify.</strong><span>Enter a factual question above to begin an analysis.</span></div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
