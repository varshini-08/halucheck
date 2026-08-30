# Source integration report

| Source | Purpose | API | Authentication | Priority | Status |
|---|---|---|---|---:|---|
| Local Knowledge Base | FAISS evidence | Internal | None | 5 | Available |
| Wikipedia | General reference | Wikipedia API | None | 3 | Available |
| Wikidata | Structured entities | SPARQL | None | 2 | Extension point |
| Google Fact Check | Published fact checks | Fact Check Tools API | `GOOGLE_FACT_CHECK_API_KEY` | 4 | Optional/not configured |
| Government | Official facts/statistics | Configurable registry | Source-specific | 1 | Extension point |
| UN Data | International statistics | UN Data API | Usually none | 1 | Extension point |
| World Bank | Economic indicators | Indicators API | Usually none | 1 | Extension point |
| WHO | Health data | WHO API | Source-specific | 1 | Extension point |
| PubMed | Biomedical literature | NCBI E-utilities | Usually none | 2 | Extension point |
| Crossref | Publication metadata | Crossref API | Usually none | 2 | Extension point |
| OpenAlex | Scholarly discovery | OpenAlex API | Optional email | 2 | Extension point |
| NASA | Space/science | NASA APIs | `NASA_API_KEY` | 1 | Optional/not configured |
| NOAA | Weather/climate | NOAA APIs | `NOAA_API_TOKEN` | 1 | Optional/not configured |
| Britannica | Licensed reference | Optional/licensed | License required | 3 | Not enabled |
| Reuters/AP | Current events | Licensed/provider API | Provider-specific | 4 | Not enabled |

Source failures should be isolated when adapters are added; unavailable or
unconfigured sources must not block local/Wikipedia verification.
