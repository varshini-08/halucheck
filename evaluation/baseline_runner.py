"""Run opt-in baseline evaluations on a fixed HaluEval sample set.

SelfCheck requires multiple sampled responses; the official general dataset has
one response per record, so default mode reports this as unavailable rather than
silently fabricating samples. LLM judging is opt-in and uses GROQ_API_KEY only.
"""
from __future__ import annotations
import argparse, json, random, time, csv, statistics
from pathlib import Path
from .halu_eval_loader import load_halueval
from .metrics import calculate_metrics
from .baselines import SelfCheckNLIBaseline, BaselineUnavailable
from .llm_baseline import LLMJudge

def run_selfcheck(dataset_path, limit=50, seed=42, output="results/selfcheck_nli"):
    samples=list(load_halueval(str(dataset_path))); random.Random(seed).shuffle(samples); samples=samples[:limit]
    rows=[]
    for sample in samples:
        started=time.perf_counter()
        try:
            # general_data has no stochastic response pool; do not duplicate it.
            raise BaselineUnavailable("HaluEval general_data.json provides one response per sample; response sampling is disabled.")
        except Exception as exc:
            rows.append({"sample_id":sample.sample_id,"expected_label":"hallucination" if sample.hallucination else "no_hallucination","predicted_label":"unavailable","error":str(exc),"latency_seconds":time.perf_counter()-started})
    result={"mode":"available_responses_only","evaluated_samples":len(rows),"successful_samples":0,"failed_samples":len(rows),"metrics":None,"rows":rows}
    out=Path(output); out.mkdir(parents=True,exist_ok=True); (out/"predictions.json").write_text(json.dumps(result,indent=2),encoding="utf-8"); (out/"metrics.json").write_text(json.dumps({"status":"not_run","reason":result["rows"][0]["error"] if rows else "no samples"},indent=2),encoding="utf-8"); return result

def run_llm_judge(dataset_path, limit=50, seed=42, output="results/llm_baseline", provider="groq"):
    samples=list(load_halueval(str(dataset_path))); random.Random(seed).shuffle(samples); samples=samples[:limit]; judge=LLMJudge(provider=provider); rows=[]
    for sample in samples:
        started=time.perf_counter(); error=None; predicted="error"; raw=""
        retry_attempts = 0
        while True:
            try:
                judged=judge.evaluate(sample.query,sample.response); predicted=judged.label; raw=judged.raw_response
                break
            except Exception as exc:
                error=str(exc)
                retryable = provider == "gemini" and ("429" in error or "RESOURCE_EXHAUSTED" in error or "timeout" in error.lower() or "ConnectError" in error)
                if not retryable or retry_attempts >= 3:
                    break
                retry_attempts += 1
                time.sleep(min(2 ** retry_attempts, 8))
        rows.append({"sample_id":sample.sample_id,"provider":provider,"model":judge.model,"expected_label":"hallucination" if sample.hallucination else "no_hallucination","predicted_label":predicted,"latency_seconds":time.perf_counter()-started,"raw_response":raw,"error":error,"retry_attempts":retry_attempts})
    valid=[r for r in rows if r["predicted_label"] in {"hallucination","no_hallucination"}]; metrics=calculate_metrics([r["expected_label"] for r in valid],[r["predicted_label"] for r in valid]); metrics.update({"evaluated_samples":len(rows),"failed_samples":len(rows)-len(valid),"api_calls":len(rows)})
    latencies=[r["latency_seconds"] for r in rows]
    metrics.update({"provider": provider, "model": judge.model, "seed": seed, "dataset": str(dataset_path), "retry_policy": "up to 3 retries with exponential backoff for transient Gemini/network errors", "total_retry_attempts": sum(r.get("retry_attempts", 0) for r in rows), "average_latency_seconds": statistics.mean(latencies) if latencies else None, "min_latency_seconds": min(latencies) if latencies else None, "max_latency_seconds": max(latencies) if latencies else None})
    out=Path(output); out.mkdir(parents=True,exist_ok=True); (out/"predictions.json").write_text(json.dumps(rows,indent=2),encoding="utf-8"); (out/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    if rows:
        with (out/"predictions.csv").open("w", newline="", encoding="utf-8") as handle:
            writer=csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (out/"baseline_report.md").write_text("# LLM-as-Judge Baseline\n\n" + json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return metrics

def main():
    p=argparse.ArgumentParser(); p.add_argument("--dataset",required=True); p.add_argument("--samples",type=int,default=10); p.add_argument("--seed",type=int,default=42); p.add_argument("--baseline",choices=("selfcheck","llm"),required=True); p.add_argument("--provider",choices=("groq","gemini"),default="groq"); a=p.parse_args(); run_selfcheck(a.dataset,a.samples,a.seed) if a.baseline=="selfcheck" else run_llm_judge(a.dataset,a.samples,a.seed, output=f"results/baselines/llm_{a.provider}", provider=a.provider)
if __name__ == "__main__": main()
