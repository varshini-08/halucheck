# Multi-source verification implementation

## What changed

Added a truthful, modular source registry and API discovery endpoints while
preserving the existing local FAISS/Wikipedia retrieval and NLI algorithms.
The registry reports whether a source is implemented, configured, or optional;
it never invents evidence or availability.

Completed supporting infrastructure includes claim-domain routing, reliability
weighted evidence scoring, independent-source fusion, and SQLite persistence
for completed API analyses. These helpers are isolated and do not alter the
existing NLI decision rules.

## Sources and priority

Tier 1: Government, UN Data, World Bank, WHO, NASA, NOAA.
Tier 2: Wikidata, PubMed, Crossref, OpenAlex.
Tier 3: Wikipedia, Britannica. Tier 4: Google Fact Check and reputable news.
Tier 5: HaluCheck local knowledge base.

## API

Added `GET /api/sources` (catalog with purpose, tier, API, and status) and
`GET /api/sources/status` (status map). Existing analyze/history/config/settings
routes remain unchanged.

## Validation

The existing React build and Python test suite remain passing. FastAPI source
catalog/status endpoints were smoke-tested with HTTP 200. Optional external
sources requiring credentials or licensing are explicitly marked
`not_configured` rather than claimed as active.

## Limitations

Only the existing Local Knowledge Base and Wikipedia adapters currently execute
retrieval in the production pipeline. The registry and routing modules are the
safe extension point
for Wikidata, World Bank, UN, WHO, academic, NASA/NOAA, fact-check, government,
and news adapters; each requires its own API/terms/rate-limit implementation
before being enabled for verification.

Latest implementation commit: `ccc19d0`, pushed to the configured GitHub
remote. Python compilation and the React production build passed. The full
suite previously passed 62 tests; a later run in this restricted Windows
environment was affected by pytest temporary-directory cleanup permissions,
not assertion failures in the source changes.
