"""Hugging Face natural-language-inference adapter for Phase 3."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
import os
import traceback
from time import perf_counter
from typing import Any
from services.config import NLI_BATCH_SIZE, NLI_MAX_LENGTH, NLI_DEVICE

LOGGER = logging.getLogger(__name__)

# Prevent a Streamlit request from waiting indefinitely on an unavailable hub.
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "15")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "30")


class NLIVerificationError(RuntimeError):
    """Raised when the NLI model cannot produce a reliable result."""


@dataclass(frozen=True)
class NLIResult:
    label: str
    confidence: float
    probabilities: dict[str, float]


@lru_cache(maxsize=4)
def _load_model(model_name: str, offline: bool = False) -> tuple[Any, Any]:
    """Load tokenizer and model once per Python process."""
    try:
        if offline:
            # This also protects transformer subcomponents which may otherwise
            # query model metadata while resolving a locally cached tokenizer.
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        try:
            LOGGER.info("Loading NLI tokenizer from local cache: %s", model_name)
            print("Loading NLI tokenizer from local cache", flush=True)
            if offline:
                # Resolve a local filesystem snapshot first. Passing the hub ID
                # directly can make some tokenizer versions query model metadata
                # despite local_files_only=True.
                from huggingface_hub import snapshot_download
                local_path = snapshot_download(model_name, local_files_only=True)
            else:
                local_path = model_name
            tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
            LOGGER.info("Tokenizer loaded from local cache")
            print("Tokenizer loaded", flush=True)
            LOGGER.info("Loading NLI model from local cache: %s", model_name)
            print("Loading NLI model from local cache", flush=True)
            model = AutoModelForSequenceClassification.from_pretrained(local_path, local_files_only=True)
            LOGGER.info("Model loaded from local cache")
            print("Model loaded", flush=True)
        except Exception as local_exc:
            if offline:
                raise NLIVerificationError(
                    f"Offline NLI model unavailable in the local cache: {model_name}"
                ) from local_exc
            LOGGER.info("NLI model is not fully cached (%s); attempting Hugging Face download.", local_exc)
            print("NLI model is not fully cached; downloading with a 30-second timeout", flush=True)
            LOGGER.info("Loading NLI tokenizer from Hugging Face: %s", model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            LOGGER.info("Tokenizer downloaded and loaded")
            print("Tokenizer loaded", flush=True)
            LOGGER.info("Loading NLI model from Hugging Face: %s", model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            LOGGER.info("Model downloaded and loaded")
            print("Model loaded", flush=True)
        model.eval()
        return tokenizer, model
    except Exception as exc:
        LOGGER.exception("Unable to load NLI model '%s'", model_name)
        traceback.print_exc()
        raise NLIVerificationError(f"Unable to load NLI model '{model_name}': {exc}") from exc


class NLIVerifier:
    """Scores evidence (premise) against an atomic fact (hypothesis)."""

    def __init__(self, model_name: str = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli", offline: bool = False) -> None:
        self.model_name = model_name
        self.offline = bool(offline)
        self.last_timings: dict[str, float] = {
            "nli_load_seconds": 0.0,
            "nli_inference_seconds": 0.0,
            "nli_tokenization_seconds": 0.0,
        }

    def _resources(self) -> tuple[Any, Any]:
        cached = _load_model.cache_info().currsize > 0
        resources = _load_model(self.model_name, self.offline)
        LOGGER.info("NLI model %s: %s", "reused from memory" if cached else "initialized", self.model_name)
        return resources

    @staticmethod
    def _canonical_label(label: str) -> str:
        normalized = label.lower()
        if "entail" in normalized or "support" in normalized:
            return "SUPPORTED"
        if "contradict" in normalized:
            return "CONTRADICTED"
        return "NEUTRAL"

    @staticmethod
    def _result_from_probabilities(probabilities: list[float], model: Any) -> NLIResult:
        canonical_scores: dict[str, float] = {"SUPPORTED": 0.0, "CONTRADICTED": 0.0, "NEUTRAL": 0.0}
        for index, probability in enumerate(probabilities):
            label = NLIVerifier._canonical_label(str(model.config.id2label[index]))
            canonical_scores[label] = max(canonical_scores[label], float(probability))
        label = max(canonical_scores, key=canonical_scores.get)
        return NLIResult(label, canonical_scores[label], canonical_scores)

    def verify_many(self, pairs: list[tuple[str, str]], batch_size: int = NLI_BATCH_SIZE) -> list[NLIResult]:
        """Run independent NLI premise/hypothesis pairs in model batches."""
        if not pairs:
            return []
        if any(not premise.strip() or not hypothesis.strip() for premise, hypothesis in pairs):
            raise ValueError("Both evidence and an atomic fact are required for NLI verification.")
        try:
            import torch

            load_started = perf_counter()
            tokenizer, model = self._resources()
            if NLI_DEVICE == "cuda" and not torch.cuda.is_available():
                LOGGER.warning("NLI_DEVICE=cuda requested but CUDA is unavailable; using CPU")
            device = "cuda" if (NLI_DEVICE == "cuda" or (NLI_DEVICE == "auto" and torch.cuda.is_available())) else "cpu"
            LOGGER.info("NLI device: %s", device.upper())
            model.to(device)
            load_seconds = perf_counter() - load_started
            results: list[NLIResult] = []
            inference_started = perf_counter()
            tokenization_seconds = 0.0
            for offset in range(0, len(pairs), batch_size):
                batch = pairs[offset : offset + batch_size]
                premises, hypotheses = zip(*batch)
                tokenize_started = perf_counter()
                inputs = tokenizer(
                    list(premises),
                    list(hypotheses),
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=NLI_MAX_LENGTH,
                )
                tokenization_seconds += perf_counter() - tokenize_started
                inputs = {key: value.to(device) for key, value in inputs.items()}
                with torch.inference_mode():
                    rows = torch.softmax(model(**inputs).logits, dim=-1).tolist()
                results.extend(self._result_from_probabilities(row, model) for row in rows)
            self.last_timings = {
                "nli_load_seconds": load_seconds,
                "nli_inference_seconds": perf_counter() - inference_started,
                "nli_tokenization_seconds": tokenization_seconds,
            }
            return results
        except NLIVerificationError:
            raise
        except Exception as exc:
            LOGGER.exception("NLI batch inference failed")
            raise NLIVerificationError(f"NLI inference failed: {exc}") from exc

    def verify(self, premise: str, hypothesis: str) -> NLIResult:
        return self.verify_many([(premise, hypothesis)], batch_size=1)[0]

    def verify_fact(self, premise: str, hypothesis: str) -> str:
        return self.verify(premise, hypothesis).label
