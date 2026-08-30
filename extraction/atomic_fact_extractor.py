"""Atomic fact extraction for HaluCheck.

This module turns LLM responses into semantically smaller atomic facts,
extracts entities from each fact, and prepares a structured fact-level
representation for downstream verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re

import spacy
import spacy.cli

from extraction.entity_detection import EntityDetector, load_spacy_model
from services.config import MAX_CLAIMS

CONJUNCTION_KEYWORDS = {"and", "but", "while", "whereas", "however"}
DATE_LABELS = {"DATE", "TIME"}
META_PREFIXES = ("the user asks", "the user wants", "they want", "provide ", "mention ", "explain ", "likely they mean", "the response should", "answer the question", "also mention")


@dataclass
class AtomicFact:
    fact_id: str
    fact_text: str
    source_sentence: str
    entities: List[Dict[str, Any]]
    start_position: int
    end_position: int


class AtomicFactExtractor:
    """Extracts atomic facts from LLM responses and enriches them with entities."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self.model_name = model_name
        self.entity_detector = EntityDetector(model_name=self.model_name)
        # Reuse the detector's process-wide cached model instead of loading it
        # once for sentence parsing and once again for entity detection.
        self.nlp = self.entity_detector.nlp

    def _load_model(self) -> spacy.language.Language:
        return load_spacy_model(self.model_name)

    def extract_atomic_facts(
        self,
        response_text: str,
        entity_types: Optional[List[str]] = None,
        max_facts: int = 10,
    ) -> List[AtomicFact]:
        """Extract up to ``max_facts`` complete, distinct factual statements."""
        if not response_text or not response_text.strip():
            return []

        document = self.nlp(response_text)
        atomic_facts: List[AtomicFact] = []
        fact_counter = 1

        for sentence_start, sentence_end, source_text in self._sentence_units(response_text, document):
            source_sentence = source_text.strip()
            if not source_sentence:
                continue

            clauses = self._complete_unique_clauses(self._split_sentence(source_sentence))
            if not clauses and self._is_complete_fact(source_sentence):
                clauses = [source_sentence]

            for clause in clauses:
                if max_facts >= 0 and len(atomic_facts) >= max_facts:
                    return atomic_facts
                clause_text = clause.strip()
                if not clause_text:
                    continue
                if self._is_meta_or_instruction(clause_text):
                    continue

                if self._is_duplicate_or_near_duplicate(
                    clause_text, [fact.fact_text for fact in atomic_facts]
                ):
                    continue

                entities = self.entity_detector.extract_entities(
                    clause_text,
                    entity_types=entity_types,
                )
                if self._is_derived_date_fact(source_sentence, clause_text):
                    # The subject is inherited from the founder-list sentence;
                    # keep the temporal entity that this derived fact isolates.
                    entities = [entity for entity in entities if entity["label"] in DATE_LABELS]

                start_position, end_position = self._find_clause_boundaries(
                    response_text,
                    clause_text,
                    sentence_start,
                    sentence_end,
                )

                atomic_facts.append(
                    AtomicFact(
                        fact_id=f"fact-{fact_counter}",
                        fact_text=clause_text,
                        source_sentence=source_sentence,
                        entities=entities,
                        start_position=start_position,
                        end_position=end_position,
                    )
                )
                fact_counter += 1

        return atomic_facts

    @staticmethod
    def _is_meta_or_instruction(text: str) -> bool:
        normalized = re.sub(r"^[\W_]+", "", text.strip().casefold())
        return normalized.startswith(META_PREFIXES) or normalized.endswith("?")

    def _sentence_units(
        self,
        response_text: str,
        document: spacy.tokens.Doc,
    ) -> List[tuple[int, int, str]]:
        """Keep numbered and bulleted response items as separate source units."""
        lines = response_text.splitlines(keepends=True)
        is_markdown_table = sum("|" in line for line in lines) >= 2
        is_list = len(lines) > 1 and all(
            not line.strip() or re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
            for line in lines
        )
        if is_markdown_table or is_list:
            units: List[tuple[int, int, str]] = []
            offset = 0
            for line in lines:
                content = line.rstrip("\r\n")
                cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", content).strip()
                if is_markdown_table:
                    if re.fullmatch(r"\s*[|:\-\s]+\s*", content):
                        cleaned = ""
                    else:
                        cleaned = " ".join(
                            re.sub(r"\*+", "", cell).strip()
                            for cell in content.strip().strip("|").split("|")
                            if cell.strip()
                        )
                if cleaned:
                    units.append((offset, offset + len(content), cleaned))
                offset += len(line)
            return units
        return [(sentence.start_char, sentence.end_char, sentence.text) for sentence in document.sents]

    def _complete_unique_clauses(self, clauses: List[str]) -> List[str]:
        """Keep complete propositions and collapse variants from one sentence."""
        complete = [clause.strip() for clause in clauses if self._is_complete_fact(clause)]
        unique: List[str] = []
        for clause in complete:
            if not self._is_duplicate_or_near_duplicate(clause, unique):
                unique.append(clause)
        return unique

    def _is_complete_fact(self, text: str) -> bool:
        """Require a subject, predicate, and predicate complement/object.

        This intentionally removes parser fragments produced while splitting a
        compound sentence. It accepts active, passive, and copular facts.
        """
        document = self.nlp(text.strip())
        if not document or not any(token.is_alpha or token.like_num for token in document):
            return False
        has_subject = any(token.dep_ in {"nsubj", "nsubjpass", "csubj", "expl"} for token in document)
        has_predicate = any(token.pos_ in {"VERB", "AUX"} for token in document)
        complement_dependencies = {"obj", "dobj", "iobj", "dative", "attr", "oprd", "acomp", "pobj", "xcomp", "ccomp"}
        has_complement = any(token.dep_ in complement_dependencies for token in document)
        return has_subject and has_predicate and has_complement

    def _is_duplicate_or_near_duplicate(self, candidate: str, existing: List[str]) -> bool:
        candidate_key, candidate_entities = self._fact_signature(candidate)
        for other in existing:
            other_key, other_entities = self._fact_signature(other)
            if candidate_key == other_key:
                return True
            # Do not merge facts with different named entities: the different
            # entity often carries the factual distinction (for example, two
            # separate founders). For matching entities, merge only near-
            # identical lexical variants created by the splitter.
            if candidate_entities != other_entities:
                continue
            union = candidate_key | other_key
            if union and len(candidate_key & other_key) / len(union) >= 0.85:
                return True
        return False

    def _fact_signature(self, text: str) -> tuple[set[str], frozenset[str]]:
        document = self.nlp(text)
        terms = {
            (token.lemma_ or token.text).lower()
            for token in document
            if not token.is_stop and not token.is_punct and (token.is_alpha or token.like_num)
        }
        entities = frozenset(entity.text.strip().lower() for entity in document.ents)
        return terms, entities

    def _is_derived_date_fact(self, source_sentence: str, clause_text: str) -> bool:
        """Identify the date-only fact derived from a multi-person ``by`` list."""
        source_document = self.nlp(source_sentence)
        people = [entity for entity in source_document.ents if entity.label_ == "PERSON"]
        clause_document = self.nlp(clause_text)
        has_date = any(entity.label_ in DATE_LABELS for entity in clause_document.ents)
        return len(people) >= 2 and " by " in source_sentence.lower() and has_date and " by " not in clause_text.lower()

    def _split_sentence(self, sentence: str) -> List[str]:
        if not sentence or len(sentence.split()) < 4:
            return [sentence.strip()]

        person_list_facts = self._split_person_list(sentence)
        if person_list_facts:
            return person_list_facts

        coordinated_facts = self._split_safe_coordination(sentence)
        if coordinated_facts:
            return coordinated_facts

        if not any(keyword in sentence.lower() for keyword in CONJUNCTION_KEYWORDS):
            return [sentence.strip()]

        document = self.nlp(sentence)
        candidates = []

        candidates.extend(self._split_date_clauses(document, sentence))

        unique_facts = self._deduplicate([candidate.strip() for candidate in candidates if candidate.strip()])
        if len(unique_facts) > 1:
            return unique_facts

        return [sentence.strip()]

    def _split_safe_coordination(self, sentence_text: str) -> List[str]:
        """Split coordinated verbs or direct objects without changing meaning."""
        document = self.nlp(sentence_text)
        root = next((token for token in document if token.dep_ == "ROOT" and token.pos_ in {"VERB", "AUX"}), None)
        subject = next((token for token in document if token.dep_ in {"nsubj", "nsubjpass", "csubj"} and token.head == root), None)
        if not root or not subject:
            return []
        subject_text = self._merge_subtree_text(subject)
        end = len(sentence_text.rstrip(".?! "))
        verb_conjuncts = [token for token in root.children if token.dep_ == "conj" and token.pos_ in {"VERB", "AUX"}]
        if verb_conjuncts:
            first_conj = min(verb_conjuncts, key=lambda token: token.idx)
            conjunction = next((token for token in document if token.dep_ == "cc" and token.idx < first_conj.idx and token.head == root), None)
            if conjunction:
                auxiliaries = [token for token in root.children if token.dep_ in {"aux", "auxpass", "neg"} and token.idx < root.idx]
                start = min([root.idx] + [token.idx for token in auxiliaries])
                facts = [self._normalize_text(f"{subject_text} {sentence_text[start:conjunction.idx].strip(' ,')}")]
                for index, verb in enumerate(verb_conjuncts):
                    next_verb = verb_conjuncts[index + 1].idx if index + 1 < len(verb_conjuncts) else end
                    predicate = sentence_text[verb.idx:next_verb].strip(" ,")
                    local_subject = next((token for token in verb.children if token.dep_ in {"nsubj", "nsubjpass", "csubj"}), None)
                    fact_subject = self._merge_subtree_text(local_subject) if local_subject else subject_text
                    inherited_auxiliary = next((token.text for token in auxiliaries if token.dep_ == "auxpass"), "")
                    if inherited_auxiliary and predicate and not predicate.startswith(inherited_auxiliary):
                        predicate = f"{inherited_auxiliary} {predicate}"
                    if predicate:
                        facts.append(self._normalize_text(f"{fact_subject} {predicate}"))
                return self._deduplicate(facts)
        direct_objects = [token for token in root.children if token.dep_ in {"obj", "dobj"}]
        if len(direct_objects) != 1:
            return []
        first_object = direct_objects[0]
        object_conjuncts = [token for token in first_object.children if token.dep_ == "conj"]
        if not object_conjuncts:
            return []
        auxiliaries = [token for token in root.children if token.dep_ in {"aux", "auxpass", "neg"} and token.idx < root.idx]
        start = min([root.idx] + [token.idx for token in auxiliaries])
        predicate = sentence_text[start:first_object.idx].strip()
        first_object_text = self._span_without_conjunctions(document[first_object.left_edge.i : first_object.right_edge.i + 1])
        object_texts = [first_object_text] + [self._merge_subtree_text(obj) for obj in object_conjuncts]
        facts = []
        for object_text in object_texts:
            if predicate.lower().endswith((" a", " an", " the")):
                article = predicate.rsplit(" ", 1)[-1].lower()
                if object_text.lower().startswith(article + " "):
                    object_text = object_text[len(article):].lstrip()
            facts.append(self._normalize_text(f"{subject_text} {predicate} {object_text}"))
        return self._deduplicate(facts)
    def _split_person_list(self, sentence: str) -> List[str]:
        """Split a coordinated list of people following ``by`` into facts.

        For example, ``Apple was founded by A, B and C in 1976`` becomes one
        founder fact per person plus a date fact.  The focused rule avoids the
        malformed fragments produced by splitting arbitrary dependency trees.
        """
        document = self.nlp(sentence)
        people = [entity for entity in document.ents if entity.label_ == "PERSON"]
        by_token = next((token for token in document if token.lower_ == "by"), None)
        if not by_token or len(people) < 2 or people[0].start <= by_token.i:
            return []

        prefix = sentence[: people[0].start_char].rstrip()
        if not prefix.lower().endswith("by"):
            return []

        facts = [self._normalize_text(f"{prefix} {person.text}") for person in people]
        date_entities = [entity for entity in document.ents if entity.label_ in DATE_LABELS]
        if date_entities:
            subject_predicate = sentence[: by_token.idx].strip()
            date = date_entities[-1].text.strip()
            if subject_predicate:
                facts.append(self._normalize_text(f"{subject_predicate} in {date}"))
        return self._deduplicate(facts)

    def _split_coordinate_phrases(
        self,
        sentence: spacy.tokens.Doc,
        sentence_text: str,
    ) -> List[str]:
        candidates: List[str] = []

        for token in sentence:
            if token.dep_ == "conj" and token.head is not token:
                coordinate_span = sentence[token.head.left_edge.i : token.right_edge.i + 1]
                if any(word.lower() in CONJUNCTION_KEYWORDS for word in coordinate_span.text.split()):
                    replacements = self._build_coordinate_replacements(sentence, coordinate_span)
                    for replacement in replacements:
                        candidate = sentence_text.replace(coordinate_span.text, replacement)
                        candidate = self._normalize_text(candidate)
                        if candidate and candidate != sentence_text:
                            candidates.append(candidate)

        return candidates

    def _split_date_clauses(
        self,
        sentence: spacy.tokens.Doc,
        sentence_text: str,
    ) -> List[str]:
        candidates: List[str] = []

        date_entities = [ent for ent in sentence.ents if ent.label_ in DATE_LABELS]
        if not date_entities:
            return candidates

        for date_entity in date_entities:
            reduced = self._remove_non_date_phrases(sentence, sentence_text, date_entity)
            if reduced and reduced != sentence_text:
                candidates.append(self._normalize_text(reduced))

        return candidates

    def _build_coordinate_replacements(
        self,
        sentence: spacy.tokens.Doc,
        coordinate_span: spacy.tokens.Span,
    ) -> List[str]:
        replacements: List[str] = []
        head_token = coordinate_span.root
        if not head_token:
            return replacements

        head_phrase = self._span_without_conjunctions(coordinate_span, keep_head=True)
        if head_phrase:
            replacements.append(head_phrase)

        for token in coordinate_span:
            if token.dep_ == "conj":
                replacements.append(self._merge_subtree_text(token))

        # Return deduplicated raw replacement phrases. Do not normalize here;
        # normalization is applied to the full candidate sentence later so that
        # punctuation is handled correctly and not inserted mid-sentence.
        return self._deduplicate([item.strip() for item in replacements if item])

    def _remove_non_date_phrases(
        self,
        sentence: spacy.tokens.Doc,
        sentence_text: str,
        date_entity: spacy.tokens.Span,
    ) -> str:
        segments = [sentence_text]

        for prep in [token for token in sentence if token.dep_ == "prep"]:
            prep_span = sentence[prep.left_edge.i : prep.right_edge.i + 1]
            if date_entity.start_char >= prep_span.start_char and date_entity.end_char <= prep_span.end_char:
                continue
            if any(
                ent.label_ in DATE_LABELS
                and ent.start_char >= prep_span.start_char
                and ent.end_char <= prep_span.end_char
                for ent in sentence.ents
            ):
                continue
            segments = [segment.replace(prep_span.text, "") for segment in segments]

        return segments[0]

    def _find_clause_boundaries(
        self,
        full_text: str,
        clause_text: str,
        sentence_start: int,
        sentence_end: int,
    ) -> tuple[int, int]:
        window = full_text[sentence_start:sentence_end]
        local_index = window.find(clause_text)
        if local_index >= 0:
            start = sentence_start + local_index
            return start, start + len(clause_text)
        return sentence_start, sentence_end

    @staticmethod
    def _merge_subtree_text(token: spacy.tokens.Token) -> str:
        return " ".join([t.text for t in sorted(token.subtree, key=lambda child: child.i)])

    @staticmethod
    def _span_without_conjunctions(span: spacy.tokens.Span, keep_head: bool = False) -> str:
        # Exclude coordinating conjunction tokens and the full subtrees
        # rooted at any conjunct tokens. If `keep_head` is True, ensure the
        # span root token is preserved even when it's otherwise filtered.
        conj_roots = [t for t in span if t.dep_ == "conj"]
        conj_subtree_idxs = set()
        for root in conj_roots:
            for t in root.subtree:
                conj_subtree_idxs.add(t.i)

        tokens: list[spacy.tokens.Token] = []
        for t in span:
            if t.dep_ == "cc":
                continue
            if t.i in conj_subtree_idxs:
                continue
            if keep_head and t == span.root:
                tokens.append(t)
                continue
            tokens.append(t)

        return " ".join([token.text for token in tokens]).strip()

    @staticmethod
    def _normalize_text(text: str) -> str:
        cleaned = " ".join(text.strip().split())
        # Repair duplicated possessives/terms introduced by dependency-span
        # reconstruction (for example, “Kepler's Kepler's laws”).
        cleaned = re.sub(r"\b([A-Za-z][A-Za-z'’-]*)\s+\1\b", r"\1", cleaned, flags=re.IGNORECASE)
        # spaCy token spans may space punctuation inside hyphenated modifiers.
        cleaned = re.sub(r"\s*-\s*", "-", cleaned)
        if cleaned and cleaned[-1] not in {".", "?", "!"}:
            cleaned = f"{cleaned}."
        return cleaned

    @staticmethod
    def _deduplicate(items: List[str]) -> List[str]:
        seen = set()
        unique = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique


class BaseFactExtractor:
    """Abstract base class for atomic fact extractors."""

    def extract_facts(self, text: str) -> List[str]:
        raise NotImplementedError


class SpacyFactExtractor(BaseFactExtractor):
    """Rule-based fact extractor using spaCy sentence segmentation."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self.model_name = model_name
        self.nlp = self._load_model()

    def _load_model(self) -> spacy.language.Language:
        try:
            return spacy.load(self.model_name)
        except OSError:
            spacy.cli.download(self.model_name)
            return spacy.load(self.model_name)

    def extract_facts(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        document = self.nlp(text)
        return [sent.text.strip() for sent in document.sents if sent.text.strip()]


class LLMFactExtractor(BaseFactExtractor):
    """Semantic fact extractor that utilizes an LLM provider."""

    def __init__(self, llm_provider: "BaseLLMProvider") -> None:
        self.llm_provider = llm_provider

    def extract_facts(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        system_prompt = (
            "You are a precise information extraction system. Decompose the input text into a list "
            "of simple, atomic, self-contained factual statements. Each statement must express exactly "
            "one core fact. Replace pronouns (he, she, it, they, etc.) with the specific entities they "
            "refer to so that each sentence can be understood independently. Return the list of facts "
            "format: one fact per line, prefixed by a dash (-). Do not include any numbering, "
            "introductory text, explanations, or conclusions."
        )
        prompt = f"Decompose the following text into atomic facts:\n\n{text}"
        try:
            response = self.llm_provider.generate_response(prompt, system_prompt=system_prompt)
        except Exception:
            fallback = SpacyFactExtractor()
            return fallback.extract_facts(text)

        facts: List[str] = []
        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("-") or line.startswith("*"):
                line = line[1:].strip()
            elif line[0].isdigit() and (line.startswith(tuple(f"{i}." for i in range(10))) or line.startswith(tuple(f"{i})" for i in range(10)))):
                line = line.split(maxsplit=1)[1].strip()
            if line:
                facts.append(line)
        return facts


class FactExtractorFactory:
    """Factory to instantiate atomic fact extractors."""

    @staticmethod
    def get_extractor(extractor_type: str, llm_provider: Optional["BaseLLMProvider"] = None) -> BaseFactExtractor:
        extractor_type = extractor_type.lower().strip()
        if extractor_type == "spacy":
            return SpacyFactExtractor()
        if extractor_type == "llm":
            if not llm_provider:
                raise ValueError("LLM provider must be provided for llm extractor.")
            return LLMFactExtractor(llm_provider)
        raise ValueError(f"Unsupported extractor type: {extractor_type}")








