from abc import ABC, abstractmethod
from typing import Any, Dict


class IConfidenceEngine(ABC):
    @abstractmethod
    def calculate(
        self,
        classification: Dict[str, Any],
        sequence_quality: float,
        feature_completeness: float,
    ) -> Dict[str, Any]: ...
