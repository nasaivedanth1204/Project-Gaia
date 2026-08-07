from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IPreprocessingEngine(ABC):
    @abstractmethod
    def clean_sequence(self, sequence: str) -> str: ...

    @abstractmethod
    def remove_noise(self, sequence: str) -> str: ...

    @abstractmethod
    def normalize_sequence(self, sequence: str) -> str: ...

    @abstractmethod
    def detect_markers(self, sequence: str) -> List[str]: ...

    @abstractmethod
    def extract_features(self, sequence: str) -> Dict[str, Any]: ...
