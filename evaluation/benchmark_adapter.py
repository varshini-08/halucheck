from dataclasses import dataclass
from .halu_eval_loader import HaluEvalSample

@dataclass(frozen=True)
class BenchmarkInput:
    sample_id: str
    question: str
    response: str
    expected_label: str

def adapt(sample: HaluEvalSample) -> BenchmarkInput:
    return BenchmarkInput(sample.sample_id, sample.query, sample.response, "hallucination" if sample.hallucination else "no_hallucination")
