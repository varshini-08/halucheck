"""Product-focused rendering of HaluCheck verification results."""
from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Iterable

import streamlit as st

if TYPE_CHECKING:
    from services.analysis_service import AnalysisResult


def _badge(label: str) -> str:
    display_label, icon, bg, color, border = _display_result(label)
    return (
        f'<span class="verification-badge" style="background:{bg};color:{color};'
        f'border-color:{border}"><span aria-hidden="true">{icon}</span> '
        f'{escape(display_label)}</span>'
    )


def _display_result(label: str) -> tuple[str, str, str, str, str]:
    """Map raw NLI output to presentation-only verification language."""
    return {
        "SUPPORTED": ("Correct", "\u2705", "#dcfce7", "#166534", "#16a34a"),
        "CONTRADICTED": ("Wrong", "\u274c", "#fee2e2", "#991b1b", "#dc2626"),
        "NEUTRAL": ("Needs Verification", "\u26a0", "#ffedd5", "#9a3412", "#ea580c"),
    }[label]


def _render_text(text: str) -> str:
    return escape(text or "").replace("\n", "<br>")



_LABEL_PRIORITY = {"SUPPORTED": 1, "NEUTRAL": 2, "CONTRADICTED": 3}


def _severity(contradicted: int, fact_count: int, confidence: float) -> str:
    """Return a transparent response-level severity heuristic."""
    if not fact_count:
        return "Unknown"
    contradiction_rate = contradicted / fact_count
    if contradiction_rate >= 0.5 or (contradicted and confidence >= 0.85):
        return "High"
    if contradicted:
        return "Medium"
    return "Low"


def _verified_response_html(response: str, facts: Iterable, verified: Iterable) -> str:
    """Render the original response with fact-level verification highlights.

    Atomic facts normally retain their character offsets from the generated
    response. Some extractor rules deliberately rewrite a clause to make it
    self-contained; for those facts, highlight the original source sentence
    rather than altering the LLM's wording.
    """
    response = response or ""
    facts_by_text: dict[str, list] = {}
    for fact in facts:
        facts_by_text.setdefault(fact.fact_text, []).append(fact)

    intervals: list[tuple[int, int, str]] = []
    for item in verified:
        matching_facts = facts_by_text.get(item.fact, [])
        fact = matching_facts.pop(0) if matching_facts else None
        if not fact:
            continue

        start, end = fact.start_position, fact.end_position
        if response[start:end].strip() != item.fact.strip():
            sentence = fact.source_sentence.strip()
            start = response.find(sentence)
            end = start + len(sentence) if start >= 0 else -1
        if 0 <= start < end <= len(response):
            intervals.append((start, end, item.label))

    # A contradiction takes precedence over neutral and support where fact
    # spans overlap, so an important warning is never obscured.
    labels: list[str | None] = [None] * len(response)
    for start, end, label in intervals:
        for position in range(start, end):
            current = labels[position]
            if current is None or _LABEL_PRIORITY[label] >= _LABEL_PRIORITY[current]:
                labels[position] = label

    if not response:
        return ""
    chunks: list[str] = []
    start = 0
    active_label = labels[0]
    for position in range(1, len(response) + 1):
        label = labels[position] if position < len(response) else object()
        if label != active_label:
            text = escape(response[start:position])
            if active_label:
                chunks.append(f'<span class="verified-response__fact {active_label.lower()}">{text}</span>')
            else:
                chunks.append(text)
            start = position
            active_label = label if position < len(response) else None
    return "".join(chunks)

def _summary_card(column, label: str, value: str | int, style: str, icon: str) -> None:
    with column:
        st.markdown(
            f'<div class="summary-card {style}"><div class="summary-icon">{icon}</div><div class="summary-label">{escape(label)}</div><div class="summary-value">{escape(str(value))}</div></div>',
            unsafe_allow_html=True,
        )


def render_analysis(
    analysis: "AnalysisResult",
    question: str = "",
    pipeline_seconds: float = 0.0,
    ui_log: Iterable[str] = (),
) -> None:
    verified = analysis.verifications
    supported = sum(x.label == "SUPPORTED" for x in verified)
    contradicted = sum(x.label == "CONTRADICTED" for x in verified)
    neutral = sum(x.label == "NEUTRAL" for x in verified)
    hallucinations = sum(x.hallucination for x in verified)
    confidence = sum(x.confidence for x in verified) / len(verified) if verified else 0.0
    fact_count = len(analysis.facts)
    hallucination_percentage = hallucinations / fact_count if fact_count else 0.0
    severity = _severity(hallucinations, fact_count, confidence)
    timings = analysis.comparison.get("timings", {})
    retrieval_mode = analysis.comparison.get("retrieval_mode", "Unknown")
    evidence_count = analysis.comparison.get("evidence_count", sum(len(item.retrieved_evidence) for item in analysis.retrievals))

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Question</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="body-card">{_render_text(question)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-kicker" style="margin-top:1.2rem;">LLM Response</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="body-card">{_render_text(analysis.response)}</div>', unsafe_allow_html=True)

    if verified and supported == len(verified):
        reliability, verdict_style = "Fully Verified", "verified"
    elif verified and supported > contradicted + neutral:
        reliability, verdict_style = "Mostly Verified", "verified"
    elif contradicted:
        reliability, verdict_style = "Verification Failed", "failed"
    elif supported:
        reliability, verdict_style = "Partially Verified", "needs-review"
    else:
        reliability, verdict_style = "Unable to Verify", "needs-review"

    st.markdown('<div class="section-kicker" style="margin-top:1.2rem;">Final Verified Response</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="verification-legend"><span class="supported">Green = Correct</span><span class="contradicted">Red = Wrong</span><span class="neutral">Orange = Needs Verification</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="verified-response">{_verified_response_html(analysis.response, analysis.facts, verified)}</div>',
        unsafe_allow_html=True,
    )
    if analysis.comparison.get("retrieval_error"):
        st.info("Verification highlights are unavailable because evidence retrieval did not complete. Details are available below.")
    elif analysis.comparison.get("verification_error"):
        st.info("Verification highlights are unavailable because fact verification did not complete. Details are available below.")
    elif not verified:
        st.info("No factual statements were identified for verification.")

    st.markdown('<div class="section-kicker" style="margin-top:1.2rem;">Verification Summary</div>', unsafe_allow_html=True)
    cols = st.columns(8)
    _summary_card(cols[0], "Total Facts", fact_count, "confidence", "#")
    _summary_card(cols[1], "Correct Facts", supported, "supported", "\u2705")
    _summary_card(cols[2], "Wrong Facts", contradicted, "contradicted", "\u274c")
    _summary_card(cols[3], "Needs Verification", neutral, "neutral", "\u26a0")
    _summary_card(cols[4], "Overall Confidence", f"{confidence:.0%}", "confidence", "\u25c9")
    _summary_card(cols[5], "Hallucination", f"{hallucination_percentage:.0%}", "failed" if hallucinations else "confidence", "!")
    _summary_card(cols[6], "Severity", severity, "failed" if severity == "High" else "needs-review" if severity == "Medium" else "confidence", "!")
    _summary_card(cols[7], "Final Verdict", reliability, verdict_style, "\u2713" if verdict_style == "verified" else "\u26a0")

    st.caption(
        f"Evidence: {evidence_count} | Retrieval: {retrieval_mode} | "
        f"Processing: {pipeline_seconds:.2f}s | "
        f"Extraction: {timings.get('extraction_seconds', 0.0):.2f}s | "
        f"Entities: {timings.get('entity_seconds', 0.0):.2f}s | "
        f"Retrieval: {timings.get('retrieval_seconds', 0.0):.2f}s | "
        f"NLI: {timings.get('verification_seconds', 0.0):.2f}s"
    )

    with st.expander("Developer Details", expanded=False):
        st.markdown("**Individual verification cards**")
        if analysis.comparison.get("retrieval_error"):
            st.warning(f"Evidence retrieval is temporarily unavailable: {analysis.comparison['retrieval_error']}")
        elif analysis.comparison.get("verification_error"):
            st.error(f"Verification failed: {analysis.comparison['verification_error']}")
        elif not verified:
            st.info("No factual statements were identified for verification.")

        for index, item in enumerate(verified, 1):
            with st.expander(f"{index}. {item.fact}", expanded=False):
                st.markdown(
                    f'<div class="fact-card {item.label.lower()}"><div class="fact-head"><div class="fact-title">{escape(item.fact)}</div>{_badge(item.label)}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="fact-meta"><div class="chip">Verification Confidence</div><div class="confidence-bar"><div style="width:{int(max(6, min(100, item.confidence * 100)))}%"></div></div><div class="confidence-text">{item.confidence:.0%}</div></div>',
                    unsafe_allow_html=True,
                )
                st.caption("This is the NLI model's confidence in its decision, not the factual correctness of the claim.")
                st.caption(item.reason)
                if not item.evidence_verifications:
                    st.info("No relevant evidence found for this fact.")
                for result in item.evidence_verifications:
                    evidence = result.evidence
                    source = "Wikipedia" if evidence.source == "wikipedia" else "Local Knowledge Base"
                    with st.container(border=True):
                        st.markdown(
                            f'<div class="evidence-card"><div class="evidence-title">Evidence</div><div class="fact-meta"><span class="chip secondary">{escape(source)}</span><span class="chip secondary">Similarity {evidence.score:.0%}</span></div><div class="evidence-body">{_render_text(evidence.content)}</div></div>',
                            unsafe_allow_html=True,
                        )
                        if evidence.url:
                            st.link_button("Open source", evidence.url)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("**Atomic facts and named entities**")
        for fact in analysis.facts:
            st.write(f"â€¢ {fact.fact_text}")
        entity_text = ", ".join(
            f"{entity['text']} ({entity['label']})" for fact in analysis.facts for entity in fact.entities
        ) or "No named entities"
        st.caption(entity_text)
        st.markdown("**Top-k documents, similarity scores, and NLI probabilities**")
        for item in verified:
            st.write(f"â€¢ {item.fact} â€” {item.label}")
            for result in item.evidence_verifications:
                evidence = result.evidence
                st.caption(f"{evidence.source.title()} Â· {evidence.title} Â· similarity {evidence.score:.3f}")
                probabilities = " Â· ".join(
                    f"{key}: {value:.3f}" for key, value in result.result.probabilities.items()
                )
                st.caption(f"NLI label: {result.result.label} Â· {probabilities}")
                if evidence.url:
                    st.caption(evidence.url)
        st.markdown("**Performance**")
        perf_cols = st.columns(4)
        perf_cols[0].metric("Total Time", f"{pipeline_seconds:.2f}s")
        perf_cols[1].metric("Retrieval", f"{timings.get('retrieval_seconds', 0.0):.2f}s")
        perf_cols[2].metric("Wikipedia", f"{timings.get('wikipedia_search_seconds', 0.0) + timings.get('wikipedia_article_seconds', 0.0):.2f}s")
        perf_cols[3].metric("NLI", f"{timings.get('verification_seconds', 0.0):.2f}s")
        st.markdown("**Processing logs**")
        log_entries = list(ui_log)
        if log_entries:
            for entry in log_entries:
                st.caption(entry)
        else:
            st.caption("No UI activity has been recorded for this report.")
    st.markdown('<div class="footer-actions">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.button("Export PDF", disabled=True, use_container_width=True)
    col2.button("Export JSON", disabled=True, use_container_width=True)
    col3.button("Export CSV", disabled=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
