from abc import ABC, abstractmethod
from typing import Any, Dict


class ITaxonomyEngine(ABC):
    @abstractmethod
    def identify(self, sequence: str, features: Dict[str, Any]) -> Dict[str, Any]: ...
