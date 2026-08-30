"""Create measured performance artifacts from benchmark prediction JSON."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from .performance import summarize_timings

def generate_performance(predictions, output="results/performance"):
    rows=json.loads(Path(predictions).read_text(encoding="utf-8")); summary=summarize_timings([r["processing_time_seconds"] for r in rows]); result={"source":str(predictions),"total_processing":summary,"components":"not instrumented in source run"}
    out=Path(output); out.mkdir(parents=True,exist_ok=True); (out/"performance.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    with (out/"performance.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(summary)); w.writeheader(); w.writerow(summary)
    (out/"performance_report.md").write_text("# Performance Report\n\nMeasured from benchmark prediction timings; component timings are not reported unless instrumented.\n\n```json\n"+json.dumps(result,indent=2)+"\n```\n",encoding="utf-8"); return result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--predictions",required=True); p.add_argument("--output",default="results/performance"); a=p.parse_args(); print(json.dumps(generate_performance(a.predictions,a.output),indent=2))
if __name__=="__main__": main()
