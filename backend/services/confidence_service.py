from typing import Any, Dict

from confidence.confidence_engine import PlaceholderConfidenceEngine


class ConfidenceService:
    def __init__(self, confidence_engine: PlaceholderConfidenceEngine) -> None:
        self._confidence_engine = confidence_engine

    def calculate_for_sequence(self, taxonomy: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        sequence_quality = features.get("completeness", 0.5)
        feature_completeness = 1.0 if features else 0.0
        return self._confidence_engine.calculate(taxonomy, sequence_quality, feature_completeness)
