"""Source metadata and availability checks.

This registry is deliberately separate from the existing retrieval pipeline;
it provides truthful capability/status information without fabricating evidence.
Sources requiring credentials are reported as not_configured until configured.
"""
from dataclasses import asdict, dataclass
import os

@dataclass(frozen=True)
class SourceSpec:
    name: str
    display_name: str
    purpose: str
    tier: int
    api: str
    env_key: str | None = None
    implemented: bool = False

SOURCES = [
    SourceSpec("local_knowledge", "Local Knowledge Base", "FAISS evidence", 5, "internal", implemented=True),
    SourceSpec("wikipedia", "Wikipedia", "General reference", 3, "Wikipedia API", implemented=True),
    SourceSpec("wikidata", "Wikidata", "Structured entities and relationships", 2, "SPARQL", implemented=False),
    SourceSpec("google_factcheck", "Google Fact Check", "Published fact checks", 4, "Fact Check Tools API", "GOOGLE_FACT_CHECK_API_KEY"),
    SourceSpec("world_bank", "World Bank", "Economic and development indicators", 1, "Indicators API", implemented=False),
    SourceSpec("un_data", "UN Data", "International statistics", 1, "UN Data API", implemented=False),
    SourceSpec("who", "WHO", "Health and public-health data", 1, "WHO API", implemented=False),
    SourceSpec("pubmed", "PubMed", "Biomedical literature", 2, "NCBI E-utilities", implemented=False),
    SourceSpec("crossref", "Crossref", "Academic publication metadata", 2, "Crossref API", implemented=False),
    SourceSpec("openalex", "OpenAlex", "Scholarly discovery", 2, "OpenAlex API", implemented=False),
    SourceSpec("nasa", "NASA", "Space and astronomy", 1, "NASA APIs", "NASA_API_KEY", implemented=False),
    SourceSpec("noaa", "NOAA", "Weather and climate", 1, "NOAA APIs", "NOAA_API_TOKEN", implemented=False),
    SourceSpec("government", "Government", "Official government sources", 1, "Configurable registry", implemented=False),
    SourceSpec("news", "Reuters/AP", "Current events", 4, "Configurable news APIs", implemented=False),
    SourceSpec("britannica", "Britannica", "Reference material", 3, "Optional/licensed", implemented=False),
]

def source_status(spec: SourceSpec) -> str:
    if spec.implemented:
        return "available"
    if spec.env_key and os.getenv(spec.env_key, "").strip():
        return "configured_optional"
    return "not_configured"

def source_catalog() -> list[dict]:
    return [{**asdict(spec), "status": source_status(spec)} for spec in SOURCES]
