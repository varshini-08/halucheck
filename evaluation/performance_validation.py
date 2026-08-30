"""Controlled cold/warm performance validation without regenerating responses."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from .halu_eval_loader import load_halueval
from .profile_pipeline import profile
from services.analysis_service import HaluCheckPipeline
from verification.verification_pipeline import VerificationPipeline

def run(dataset, sample_index=0, output="results/performance/final_validation.json"):
    sample=list(load_halueval(str(dataset)))[sample_index]
    # Both passes use the same original response and question. Process caches
    # are intentionally retained between passes to measure warm behavior.
    pipeline = HaluCheckPipeline(verification_pipeline=VerificationPipeline())
    cold=profile(sample.response, sample.query, pipeline=pipeline)
    warm=profile(sample.response, sample.query, pipeline=pipeline)
    result={"sample_id":sample.sample_id,"dataset":str(dataset),"cold":cold,"warm":warm,"prediction_consistency":cold["predicted_label"] == warm["predicted_label"],"note":"Measured in one process; model caches remain warm for the second pass."}
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(result,indent=2),encoding="utf-8"); return result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--dataset",required=True); p.add_argument("--sample-index",type=int,default=0); p.add_argument("--output",default="results/performance/final_validation.json"); a=p.parse_args(); print(json.dumps(run(a.dataset,a.sample_index,a.output),indent=2))
if __name__=="__main__": main()
