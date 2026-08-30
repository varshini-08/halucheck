# Data Flow

The question is sent to FastAPI; provider credentials remain server-side. The generated answer becomes atomic facts. Each fact is routed to relevant adapters, transformed into normalized `Evidence`, ranked and filtered, then paired with the fact for NLI. The resulting classifications and metrics are persisted without credentials and returned to React.
