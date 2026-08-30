"""Legacy compatibility wrapper for entity detection and matching.

This module re-exports the current extraction and verification logic from the
modular packages while preserving backward compatibility for legacy imports.
"""

from extraction.entity_detection import EntityDetector
from verification.entity_matcher import EntityMatcher

__all__ = ["EntityDetector", "EntityMatcher"]
