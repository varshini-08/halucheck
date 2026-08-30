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


def _render_analysis_legacy(
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


# Screenshot-inspired presentation layer. Pipeline data and algorithms remain unchanged.
def _reference_donut(supported: int, contradicted: int, neutral: int) -> str:
    total = supported + contradicted + neutral
    if not total:
        return '<div class="hc-donut hc-donut-empty"><span>No data</span></div>'
    supported_end = supported / total * 100
    contradicted_end = supported_end + contradicted / total * 100
    center = supported / total * 100
    return (f'<div class="hc-donut" style="--supported:{supported_end:.2f}%;--contradicted:{contradicted_end:.2f}%">'
            f'<div class="hc-donut-hole"><strong>{center:.0f}%</strong><span>Supported</span></div></div>')


def render_analysis(analysis: "AnalysisResult", question: str = "", pipeline_seconds: float = 0.0, ui_log: Iterable[str] = ()) -> None:
    """Render actual analysis values in a compact professional dashboard."""
    import os
    verified = list(analysis.verifications)
    supported = sum(x.label == "SUPPORTED" for x in verified)
    contradicted = sum(x.label == "CONTRADICTED" for x in verified)
    neutral = sum(x.label == "NEUTRAL" for x in verified)
    facts = len(analysis.facts)
    hallucinations = sum(bool(x.hallucination) for x in verified)
    score = hallucinations / facts if facts else 0.0
    confidence = sum(x.confidence for x in verified) / len(verified) if verified else 0.0
    severity = _severity(hallucinations, facts, confidence)
    retrieval_mode = analysis.comparison.get("retrieval_mode", "Unknown")
    evidence_count = analysis.comparison.get("evidence_count", sum(len(x.retrieved_evidence) for x in analysis.retrievals))
    timings = analysis.comparison.get("timings", {})
    provider = st.session_state.get("selected_provider", os.environ.get("LLM_PROVIDER", "groq")).lower()
    model = os.environ.get("GEMINI_MODEL" if provider == "gemini" else "GROQ_MODEL", "gemini-3.6-flash" if provider == "gemini" else "openai/gpt-oss-20b")

    st.markdown('<div class="hc-page-heading"><div><div class="hc-eyebrow">AI verification workspace</div><h1>New Analysis</h1><p>Ask a factual question and verify the AI response</p></div><span class="hc-model-pill">● ' + escape(model) + '</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-question-card"><div class="hc-card-kicker">Your Question</div><div class="hc-question-text">' + _render_text(question) + '</div><div class="hc-card-help">Ask factual questions that can be verified against reliable sources</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-response-card"><div class="hc-response-head"><strong>AI Response</strong><span>● Model: ' + escape(model) + '</span></div><div class="hc-response-body">' + _render_text(analysis.response) + '</div></div>', unsafe_allow_html=True)

    cards = [("Hallucination Score", f"{score:.0%}", "Excellent" if not hallucinations else severity, "blue"), ("Claims Analyzed", facts, "Total claims extracted", "blue"), ("Supported", supported, f"{supported / facts:.0%}" if facts else "0%", "green"), ("Contradicted", contradicted, f"{contradicted / facts:.0%}" if facts else "0%", "red"), ("Neutral", neutral, f"{neutral / facts:.0%}" if facts else "0%", "amber"), ("Processing Time", f"{pipeline_seconds:.2f}s", "Total time taken", "blue")]
    st.markdown('<div class="hc-metrics">' + ''.join(f'<div class="hc-metric {tone}"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong><small>{escape(str(sub))}</small><i></i></div>' for label, value, sub, tone in cards) + '</div>', unsafe_allow_html=True)

    left, right = st.columns([2.2, 1], gap="large")
    with right:
        st.markdown('<div class="hc-side-card"><h3>Analysis Summary</h3>' + _reference_donut(supported, contradicted, neutral) + f'<div class="hc-legend"><span class="green">● Supported ({supported})</span><span class="red">● Contradicted ({contradicted})</span><span class="amber">● Neutral ({neutral})</span></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="hc-side-card"><h3 class="blue-text">Verification Details</h3><div class="hc-detail-row"><span>Retrieval Mode</span><b>' + escape(str(retrieval_mode)) + '</b></div><div class="hc-detail-row"><span>Verification Engine</span><b>DeBERTa-v3 MNLI</b></div><div class="hc-detail-row"><span>Evidence Sources</span><b>' + str(evidence_count) + '</b></div><div class="hc-detail-row"><span>Model Used</span><b>' + escape(model) + '</b></div><div class="hc-detail-row"><span>Analysis Time</span><b>' + f'{pipeline_seconds:.2f}s' + '</b></div></div>', unsafe_allow_html=True)
    with left:
        st.markdown('<div class="hc-section-title">Verification Results</div>', unsafe_allow_html=True)
        for index, item in enumerate(verified, 1):
            label, icon, bg, color, border = _display_result(item.label)
            evidence_html = []
            for result in item.evidence_verifications[:2]:
                evidence = result.evidence
                source = "Wikipedia" if evidence.source == "wikipedia" else "Local Knowledge Base"
                evidence_html.append('<div class="hc-evidence"><div><b>Evidence Found</b><span class="hc-source">' + escape(source) + '</span></div><p>' + _render_text(evidence.content) + '</p><small>NLI confidence <strong>' + f'{result.result.confidence:.1%}' + '</strong> · Similarity ' + f'{evidence.score:.1%}' + '</small></div>')
            if not evidence_html:
                evidence_html.append('<div class="hc-evidence"><p>No relevant evidence found for this fact.</p></div>')
            st.markdown('<div class="hc-claim-card"><div class="hc-claim-head"><div><small>Claim ' + str(index) + '</small><strong>' + _render_text(item.fact) + '</strong></div><span class="hc-badge" style="background:' + bg + ';color:' + color + ';border-color:' + border + '">' + icon + ' ' + escape(label) + '</span></div>' + ''.join(evidence_html) + '</div>', unsafe_allow_html=True)
    with st.expander("Developer Details", expanded=False):
        st.caption("Technical diagnostics, atomic facts, entities, probabilities, and processing logs")
        st.write({"facts": [fact.fact_text for fact in analysis.facts], "entities": [entity for fact in analysis.facts for entity in fact.entities], "timings": timings, "ui_log": list(ui_log)})

    # Historical dashboard is driven solely by completed analyses in this session.
    records = list(st.session_state.get("analysis_history", []))
    st.markdown('<div class="hc-dashboard"><h3>Verification Dashboard</h3>', unsafe_allow_html=True)
    if not records:
        st.caption("No historical analyses yet. Complete an analysis to populate this dashboard.")
    else:
        avg_score = sum(float(x.get("hallucination_score", 0.0)) for x in records) / len(records)
        avg_time = sum(float(x.get("processing_time", 0.0)) for x in records) / len(records)
        accuracy_proxy = sum(int(x.get("supported", 0)) for x in records) / max(1, sum(int(x.get("supported", 0)) + int(x.get("contradicted", 0)) + int(x.get("neutral", 0)) for x in records))
        st.markdown('<div class="hc-stat-grid"><div class="hc-stat"><span>Total Analyses</span><strong>' + str(len(records)) + '</strong></div><div class="hc-stat"><span>Avg Hallucination Score</span><strong>' + f'{avg_score:.1%}' + '</strong></div><div class="hc-stat"><span>Supported Share</span><strong>' + f'{accuracy_proxy:.1%}' + '</strong></div><div class="hc-stat"><span>Avg Response Time</span><strong>' + f'{avg_time:.2f}s' + '</strong></div></div>', unsafe_allow_html=True)
        trend_values = [max(0.02, min(1.0, float(x.get("hallucination_score", 0.0)))) for x in records[-12:]]
        bars = ''.join('<i style="height:' + f'{value * 100:.1f}' + '%"></i>' for value in trend_values)
        total_supported = sum(int(x.get("supported", 0)) for x in records)
        total_contradicted = sum(int(x.get("contradicted", 0)) for x in records)
        total_neutral = sum(int(x.get("neutral", 0)) for x in records)
        total_labels = max(1, total_supported + total_contradicted + total_neutral)
        distribution = '<div class="hc-distribution"><div class="hc-distribution-row"><i style="width:' + f'{total_supported / total_labels * 100:.1f}' + '%"></i><span>Supported ' + str(total_supported) + '</span></div><div class="hc-distribution-row red"><i style="width:' + f'{total_contradicted / total_labels * 100:.1f}' + '%"></i><span>Contradicted ' + str(total_contradicted) + '</span></div><div class="hc-distribution-row amber"><i style="width:' + f'{total_neutral / total_labels * 100:.1f}' + '%"></i><span>Neutral ' + str(total_neutral) + '</span></div></div>'
        st.markdown('<div class="hc-chart-row"><div class="hc-mini-chart"><b>Hallucination Score Trend</b><div class="hc-bars">' + bars + '</div></div><div class="hc-mini-chart"><b>Verification Results Distribution</b>' + distribution + '</div></div>', unsafe_allow_html=True)
        rows = ''.join('<tr><td>' + escape(str(x.get("question", ""))) + '</td><td>' + escape(str(x.get("provider", ""))) + '</td><td>' + f'{float(x.get("hallucination_score", 0.0)):.0%}' + '</td><td>' + ('Contradicted' if x.get("contradicted", 0) else 'Supported') + '</td><td>' + f'{float(x.get("processing_time", 0.0)):.2f}s' + '</td></tr>' for x in records[-8:][::-1])
        st.markdown('<b style="display:block;margin-top:.9rem;">Recent Analyses</b><table class="hc-recent"><thead><tr><th>Question</th><th>Provider</th><th>Hallucination</th><th>Status</th><th>Time</th></tr></thead><tbody>' + rows + '</tbody></table>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
