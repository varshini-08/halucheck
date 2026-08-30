"""Extraction layer for named entity recognition used by HaluCheck."""

import logging
from functools import lru_cache
from typing import Dict, List, Optional

import spacy
import spacy.cli

logger = logging.getLogger(__name__)

SUPPORTED_ENTITY_LABELS = ["PERSON", "ORG", "GPE", "DATE", "EVENT", "PRODUCT"]


@lru_cache(maxsize=None)
def load_spacy_model(model_name: str) -> spacy.language.Language:
    """Load each spaCy model once per Python process."""
    try:
        return spacy.load(model_name)
    except OSError:
        logger.warning("spaCy model %s not found. Downloading...", model_name)
        spacy.cli.download(model_name)
        return spacy.load(model_name)


class EntityDetector:
    """Extracts named entities from text using spaCy."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self.model_name = model_name
        self.nlp = self._load_model()

    def _load_model(self) -> spacy.language.Language:
        return load_spacy_model(self.model_name)

    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
    ) -> List[Dict[str, object]]:
        if not text or not text.strip():
            return []

        if entity_types is None:
            entity_types = SUPPORTED_ENTITY_LABELS

        document = self.nlp(text)
        entities: List[Dict[str, object]] = []

        for entity in document.ents:
            if entity.label_ not in entity_types:
                continue
            entities.append(
                {
                    "text": entity.text.strip(),
                    "label": entity.label_,
                    "sentence": entity.sent.text.strip(),
                    "start": entity.start_char,
                    "end": entity.end_char,
                }
            )

        return entities
