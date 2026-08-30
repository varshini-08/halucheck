"""Configurable claim routing and transparent evidence fusion helpers."""
from dataclasses import dataclass
import re
from typing import Iterable

@dataclass(frozen=True)
class EvidenceScore:
    source: str
    score: float
    reliability: float
    relevance: float
    nli_confidence: float
    similarity: float

RELIABILITY = {"government": .95, "who": .95, "nasa": .95, "noaa": .95, "world_bank": .92, "un_data": .92, "pubmed": .92, "crossref": .88, "openalex": .86, "wikidata": .85, "wikipedia": .75, "local_knowledge": .70, "news": .72, "google_factcheck": .80, "britannica": .84}

def classify_claim(claim: str) -> str:
    text = claim.lower()
    if re.search(r"\b(cancer|disease|diabetes|malaria|treatment|medical|health|mortality)\b", text): return "MEDICAL"
    if re.search(r"\b(gdp|population|poverty|inflation|economic|income|development)\b", text): return "STATISTICS"
    if re.search(r"\b(nasa|planet|space|astronomy|climate|weather|ocean|temperature)\b", text): return "SCIENCE"
    if re.search(r"\b(law|legal|government|president|minister|election|policy)\b", text): return "GOVERNMENT"
    if re.search(r"\b(study|research|paper|journal|doi|university)\b", text): return "ACADEMIC"
    if re.search(r"\b(today|yesterday|breaking|recent|last night)\b", text): return "CURRENT_EVENT"
    return "GENERAL_FACT"

ROUTES = {"MEDICAL": ("who", "pubmed", "local_knowledge", "wikipedia"), "STATISTICS": ("world_bank", "un_data", "government", "local_knowledge", "wikipedia"), "SCIENCE": ("nasa", "noaa", "pubmed", "local_knowledge", "wikipedia"), "GOVERNMENT": ("government", "un_data", "wikidata", "local_knowledge", "wikipedia"), "ACADEMIC": ("crossref", "openalex", "pubmed", "wikipedia"), "CURRENT_EVENT": ("news", "google_factcheck", "government", "wikipedia"), "GENERAL_FACT": ("wikidata", "government", "local_knowledge", "wikipedia")}

def route_claim(claim: str) -> tuple[str, ...]: return ROUTES.get(classify_claim(claim), ROUTES["GENERAL_FACT"])

def score_evidence(source: str, relevance: float, similarity: float, nli_confidence: float) -> EvidenceScore:
    reliability = RELIABILITY.get(source.lower().replace(" ", "_"), .60)
    final = max(0.0, min(1.0, reliability * max(0.0, relevance) * max(0.0, similarity) * max(0.0, nli_confidence)))
    return EvidenceScore(source, final, reliability, relevance, nli_confidence, similarity)

def fuse_scores(scores: Iterable[EvidenceScore]) -> float:
    """Independent agreement raises confidence without double-counting duplicates."""
    items = list(scores)
    if not items: return 0.0
    unique = {item.source: item for item in items}
    combined = 1.0
    for item in unique.values(): combined *= 1.0 - item.score
    return max(0.0, min(1.0, 1.0 - combined))
