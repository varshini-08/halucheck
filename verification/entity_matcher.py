"""Verification layer for entity matching and hallucination scoring."""

from typing import Dict, List, Any

from rapidfuzz import fuzz


class EntityMatcher:
    """Compares response entities against reference entities."""

    def __init__(
        self,
        similarity_threshold: float = 80.0,
        strict_label_matching: bool = True,
        type_matching: bool | None = None,
    ) -> None:
        if type_matching is not None:
            strict_label_matching = type_matching

        self.similarity_threshold = similarity_threshold
        self.strict_label_matching = strict_label_matching

    def compare_entities(
        self,
        source_entities: List[Dict[str, Any]],
        response_entities: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        matched: List[Dict[str, Any]] = []
        hallucinated: List[Dict[str, Any]] = []

        if not response_entities:
            return {
                "matched": [],
                "verified": [],
                "hallucinated": [],
                "score": 100.0,
                "factual_consistency_score": 100.0,
                "total": 0,
            }

        for response_entity in response_entities:
            best_match = self._find_best_match(response_entity, source_entities)
            result_entry = {
                "entity": response_entity,
                "best_match": best_match["entity"],
                "score": round(best_match["score"], 1),
                "similarity_score": round(best_match["score"], 1),
            }
            if best_match["score"] >= self.similarity_threshold:
                matched.append(result_entry)
            else:
                hallucinated.append(result_entry)

        total = len(response_entities)
        hallucinated_count = len(hallucinated)
        score = round(100.0 * (1.0 - hallucinated_count / total), 1)

        return {
            "matched": matched,
            "verified": matched,
            "hallucinated": hallucinated,
            "score": score,
            "factual_consistency_score": score,
            "total": total,
        }

    def compare_within_response(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Match each entity against the other entities in the response.

        This is deliberately evidence-free: it reports repeated/corroborated
        entities versus entities that need later retrieval verification.
        """
        matched: List[Dict[str, Any]] = []
        hallucinated: List[Dict[str, Any]] = []
        for index, entity in enumerate(entities):
            other_entities = entities[:index] + entities[index + 1:]
            best_match = self._find_best_match(entity, other_entities)
            entry = {
                "entity": entity,
                "best_match": best_match["entity"],
                "score": round(best_match["score"], 1),
                "similarity_score": round(best_match["score"], 1),
            }
            (matched if best_match["score"] >= self.similarity_threshold else hallucinated).append(entry)

        total = len(entities)
        score = round(100.0 * len(matched) / total, 1) if total else 100.0
        return {"matched": matched, "verified": matched, "hallucinated": hallucinated,
                "score": score, "factual_consistency_score": score, "total": total}

    def _find_best_match(
        self,
        response_entity: Dict[str, Any],
        source_entities: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        best_score = 0.0
        best_entity: Dict[str, Any] = {}

        for source_entity in source_entities:
            if self.strict_label_matching and source_entity["label"] != response_entity["label"]:
                continue

            source_text = source_entity["text"].strip().lower()
            response_text = response_entity["text"].strip().lower()

            if source_text == response_text:
                return {"entity": source_entity, "score": 100.0}

            if source_text in response_text or response_text in source_text:
                best_score = max(best_score, 95.0)
                best_entity = source_entity

            fuzzy_score = fuzz.token_sort_ratio(source_text, response_text)
            if fuzzy_score > best_score:
                best_score = float(fuzzy_score)
                best_entity = source_entity

        return {"entity": best_entity, "score": best_score}
