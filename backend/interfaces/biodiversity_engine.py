from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IBiodiversityEngine(ABC):
    @abstractmethod
    def calculate_species_richness(self, species: List[Dict[str, Any]]) -> int: ...

    @abstractmethod
    def calculate_shannon_index(self, species: List[Dict[str, Any]]) -> float: ...

    @abstractmethod
    def calculate_simpson_index(self, species: List[Dict[str, Any]]) -> float: ...

    @abstractmethod
    def calculate_evenness(self, species: List[Dict[str, Any]]) -> float: ...

    @abstractmethod
    def calculate_dominant_species(self, species: List[Dict[str, Any]]) -> List[str]: ...

    @abstractmethod
    def calculate_rare_species(self, species: List[Dict[str, Any]]) -> List[str]: ...
