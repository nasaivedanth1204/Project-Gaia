from abc import ABC, abstractmethod
from typing import Any, Dict


class IClassificationEngine(ABC):
    @abstractmethod
    def classify(self, taxonomy: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]: ...
