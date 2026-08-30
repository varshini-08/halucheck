"""Services package for HaluCheck.

Imports are lazy so retrieval utilities can be used by the index builder without
loading the optional UI and NLP dependencies.
"""

__all__ = ["AnalysisResult", "HaluCheckPipeline", "LLMService", "LLMServiceException"]


def __getattr__(name: str):
    if name in {"AnalysisResult", "HaluCheckPipeline"}:
        from .analysis_service import AnalysisResult, HaluCheckPipeline
        return {"AnalysisResult": AnalysisResult, "HaluCheckPipeline": HaluCheckPipeline}[name]
    if name in {"LLMService", "LLMServiceException"}:
        from .llm_service import LLMService, LLMServiceException
        return {"LLMService": LLMService, "LLMServiceException": LLMServiceException}[name]
    raise AttributeError(name)
