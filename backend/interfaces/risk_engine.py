from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IRiskEngine(ABC):
    @abstractmethod
    def score(
        self,
        population: Dict[str, Any],
        habitat: Optional[Dict[str, Any]] = None,
        threats: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Compute the Gaia Prototype Risk Score and its explanation."""
