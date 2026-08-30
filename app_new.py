"""Legacy prototype interface (not the production entrypoint).

Run ``python -m streamlit run app.py`` for the current dark dashboard. This
file is retained only for historical comparison and must not be used to
validate the production UI.
"""
from __future__ import annotations

import os
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
def get_llm_service(api_key: str) -> LLMService:
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
            [data-testid="stSidebar"] {{background:{surface}; border-right:1px solid {border}; min-width:300px;}}
            .block-container {{max-width:1220px; padding:1.5rem 1.2rem 3rem;}}
            .app-shell {{display:flex; flex-direction:column; gap:1.1rem;}}
            .hero-card, .input-card, .welcome-card, .result-card, .summary-card, .process-card, .verdict-card, .performance-card {{
                background:{surface}; border:1px solid {border}; border-radius:24px; box-shadow:0 12px 30px rgba(15,23,42,.08);
            }}
            .hero-card {{padding:2rem 2rem 1.7rem; margin-bottom:.4rem;}}
            .input-card {{padding:1.2rem 1.2rem 1.1rem; margin-bottom:.3rem;}}
            .welcome-card {{padding:2rem;}}
            .result-card {{padding:1.2rem 1.2rem 1.4rem; margin-top:.4rem;}}
            .process-card {{padding:1.2rem 1.2rem 1rem; margin-top:.6rem;}}
            .verdict-card {{padding:1.2rem 1.3rem; margin-top:1.2rem;}}
            .performance-card {{padding:1rem 1.1rem; margin-top:1rem;}}
            .summary-card {{padding:1rem 1rem 1.05rem; min-height:120px; border-top:4px solid {accent};}}
            .summary-card.supported {{border-top-color:{success};}}
            .summary-card.contradicted {{border-top-color:{danger};}}
            .summary-card.neutral {{border-top-color:{warning};}}
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
            .section-kicker {{color:{accent}; font-size:.74rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem;}}
            .section-title {{font-size:1.35rem; font-weight:800; margin-bottom:.3rem;}}
            .section-subtitle {{font-size:.95rem; color:{muted}; line-height:1.6; margin-bottom:.7rem;}}
            .hero-title {{font-size:2.6rem; font-weight:800; letter-spacing:-.03em; line-height:1.08; margin:.2rem 0 .55rem;}}
            .hero-subtitle {{font-size:1.05rem; color:{muted}; line-height:1.65; max-width:760px;}}
            .chip {{display:inline-block; padding:.3rem .65rem; border-radius:999px; background:#dbeafe; color:{accent}; font-size:.77rem; font-weight:700;}}
            .chip.secondary {{background:{card}; color:{text}; border:1px solid {border};}}
            .body-card {{padding:1rem 1.1rem; border-radius:18px; background:{card}; border:1px solid {border}; color:{text}; line-height:1.7; white-space:pre-wrap; max-height:320px; overflow:auto;}}
            .welcome-card .body-card {{max-height:none;}}
            .process-list {{display:flex; flex-direction:column; gap:.55rem; margin-top:.75rem;}}
            .process-item {{display:flex; align-items:center; gap:.7rem; padding:.6rem .75rem; border-radius:12px; background:{card}; color:{muted}; border:1px solid {border};}}
            .process-item.done {{color:{text}; border-color:{accent};}}
            .process-badge {{display:inline-flex; align-items:center; justify-content:center; width:1.55rem; height:1.55rem; border-radius:999px; background:{accent}; color:white; font-weight:800;}}
            .process-item.done .process-badge {{background:{success};}}
            .summary-value {{font-size:1.7rem; font-weight:800; margin-top:.35rem;}}
            .summary-label {{font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:{muted};}}
            .summary-icon {{font-size:1rem; margin-bottom:.25rem;}}
            .fact-card {{border:1px solid {border}; border-radius:18px; padding:1rem 1rem .85rem; background:{card}; margin-top:.8rem;}}
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
            .sidebar-brand {{padding:1rem .4rem 0;}}
            .sidebar-brand .title {{font-size:1.35rem; font-weight:800; letter-spacing:-.02em;}}
            .sidebar-brand .subtitle {{font-size:.9rem; color:{muted}; margin-top:.2rem; line-height:1.45;}}
            .stButton>button {{background:{accent}; color:white; border:0; border-radius:12px; min-height:2.95rem; font-weight:700;}}
            .stButton>button:hover {{background:#1d4ed8; border:0;}}
            .stButton>button:disabled {{background:#94a3b8; color:#e2e8f0;}}
            .streamlit-expanderHeader {{border-radius:14px; padding:.7rem .85rem; background:{card}; border:1px solid {border};}}
            .streamlit-expanderContent {{padding-top:.45rem;}}
            .footer-actions {{display:flex; gap:.75rem; flex-wrap:wrap; margin-top:1rem;}}
            @media (max-width: 920px) {{.hero-title {{font-size:2.1rem;}} [data-testid="stSidebar"] {{min-width:250px;}}}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div class="title">HaluCheck</div><div class="subtitle">Explainable Hallucination Detection</div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("### AI Model")
        st.selectbox("Large Language Model", ["Groq"], index=0, disabled=True)
        st.checkbox("Gemini (Coming Soon)", value=False, disabled=True)
        st.caption("Coming Soon")
        st.divider()
        st.markdown("### Retrieval")
        st.checkbox("Local Knowledge Base", value=True, disabled=True)
        st.checkbox("Wikipedia API", value=True, disabled=True)
        st.divider()
        st.markdown("### Verification")
        st.caption("DeBERTa-v3 MNLI")
        st.divider()
        theme = st.selectbox("Theme", ["System", "Light", "Dark"])
        st.divider()
        st.markdown("### About")
        st.caption("Version 1.0")
        st.caption("Author: HaluCheck Team")
        st.caption("Research Project")
        st.caption("Kongu Engineering College")
        return theme


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
        icon = "✓" if done else "•"
        state_class = "done" if done else ""
        lines.append(
            f'<div class="process-item {state_class}"><span class="process-badge">{icon}</span><span>{step}</span></div>'
        )
    area.markdown(
        '<div class="process-card"><div class="section-kicker">Verification in progress</div><div class="process-list">' + "".join(lines) + "</div></div>",
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="HaluCheck", page_icon="✓", layout="wide", initial_sidebar_state="expanded")

theme = render_sidebar()
apply_theme(theme)

st.markdown('<div class="app-shell">', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-card"><div class="section-kicker">AI verification workspace</div><div class="hero-title">HaluCheck</div><div class="hero-subtitle">Verify whether an AI response is factually correct using hybrid retrieval and natural language inference.</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="input-card"><div class="section-title">Ask a factual question</div><div class="section-subtitle">The workflow is simple: question, response, evidence, verification, and a final decision.</div>',
    unsafe_allow_html=True,
)
question = st.text_area(
    "Question",
    placeholder="Ask a factual question...\n\nExamples\nWho invented Python?\nWho is the Prime Minister of India?\nWhen was NASA founded?",
    height=150,
    label_visibility="collapsed",
)
clicked = st.button("Verify Response", type="primary", disabled=not question.strip(), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if clicked:
    st.session_state["analysis"] = None
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        st.error("Groq API key not configured.")
    else:
        progress = st.empty()
        processing_view(progress, 0)
        try:
            started = perf_counter()
            response = get_llm_service(api_key).generate_response(question)
            processing_view(progress, 1)
            analysis = get_pipeline().analyse(
                response,
                question=question,
                progress_callback=lambda _: processing_view(progress, 4),
            )
            processing_view(progress, 6)
            st.session_state["latest_question"] = question
            st.session_state["analysis"] = analysis
            st.session_state["pipeline_seconds"] = perf_counter() - started
        except LLMServiceException as exc:
            st.error(str(exc))
        except Exception:
            st.error("Unable to analyse this response. Please try again.")

if analysis := st.session_state.get("analysis"):
    dashboard.render_analysis(analysis, st.session_state.get("latest_question", ""), st.session_state.get("pipeline_seconds", 0.0))
else:
    st.markdown(
        '<div class="welcome-card"><div class="section-kicker">Welcome to HaluCheck</div><div class="section-title">This application verifies whether an AI response is factually correct.</div><div class="section-subtitle">How it works</div><div class="body-card">1. AI generates a response.<br>2. Facts are extracted.<br>3. Evidence is retrieved.<br>4. Each fact is verified.<br>5. A final report is generated.</div><div class="section-subtitle" style="margin-top:1rem;">Start by asking a factual question above.</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
