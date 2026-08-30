"""Run fixed-query GTR retrieval against the isolated paper index."""
from __future__ import annotations
import json, time
from pathlib import Path
from services.retriever import EvidenceRetriever

def main() -> int:
    queries = ["Paris is the capital of France.", "A coffee table holds art books.", "The Eiffel Tower is in Paris."]
    retriever = EvidenceRetriever(retrieval_mode="paper", offline=True, enable_wikipedia_fallback=False)
    rows=[]; failures=[]
    for query in queries:
        started=time.perf_counter()
        try:
            result=retriever.retrieve(query, top_k=2)
            rows.append({"query":query,"results":[{"title":e.title,"score":e.score,"evidence":e.content} for e in result.retrieved_evidence],"result_count":len(result.retrieved_evidence),"retrieval_latency_seconds":time.perf_counter()-started,"model":retriever.model_name,"retrieval_mode":"paper/GTR","index":"vector_db/gtr_base.index"})
        except Exception as exc:
            failures.append({"query":query,"error":f"{type(exc).__name__}: {exc}"})
    payload={"model":retriever.model_name,"index":"vector_db/gtr_base.index","metadata":"vector_db/gtr_base_metadata.pkl","dimension":768,"query_count":len(queries),"successful_queries":len(rows),"failures":failures,"average_retrieval_latency_seconds":sum(r["retrieval_latency_seconds"] for r in rows)/len(rows) if rows else None,"fallback_used":False,"gtr_network_access_attempted":False,"queries":rows}
    out=Path("results/final_validation"); out.mkdir(parents=True,exist_ok=True); (out/"gtr_offline_smoke.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    lines=["# Offline GTR Smoke Test","",f"- Model: `{payload['model']}`",f"- Dimension: {payload['dimension']}",f"- Queries: {payload['query_count']}",f"- Successful: {payload['successful_queries']}",f"- Failures: {len(failures)}",f"- Average retrieval latency: {payload['average_retrieval_latency_seconds']}","- Wikipedia fallback: disabled","- GTR network access attempted: false"]
    (out/"gtr_offline_smoke.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2)); return 0 if not failures else 1
if __name__ == "__main__": raise SystemExit(main())
