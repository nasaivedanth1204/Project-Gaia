import math
from collections import Counter
from typing import Any, Dict, List

from interfaces.biodiversity_engine import IBiodiversityEngine


class PlaceholderBiodiversityEngine(IBiodiversityEngine):
    """Computes basic diversity metrics from a list of identified species.

    TODO:
    Replace with statistically robust implementations (rarefaction,
    Chao1 estimator, confidence-weighted abundance, etc.) once real
    species-abundance data from a validated model is available.
    """

    def calculate_species_richness(self, species: List[Dict[str, Any]]) -> int:
        return len({s.get("species", "Unknown") for s in species})

    def calculate_shannon_index(self, species: List[Dict[str, Any]]) -> float:
        counts = Counter(s.get("species", "Unknown") for s in species)
        total = sum(counts.values())
        if total == 0:
            return 0.0
        index = -sum((n / total) * math.log(n / total) for n in counts.values())
        return round(index, 4)

    def calculate_simpson_index(self, species: List[Dict[str, Any]]) -> float:
        counts = Counter(s.get("species", "Unknown") for s in species)
        total = sum(counts.values())
        if total == 0:
            return 0.0
        index = sum((n / total) ** 2 for n in counts.values())
        return round(1 - index, 4)

    def calculate_evenness(self, species: List[Dict[str, Any]]) -> float:
        richness = self.calculate_species_richness(species)
        if richness <= 1:
            return 1.0 if richness == 1 else 0.0
        shannon = self.calculate_shannon_index(species)
        return round(shannon / math.log(richness), 4)

    def calculate_dominant_species(self, species: List[Dict[str, Any]]) -> List[str]:
        counts = Counter(s.get("species", "Unknown") for s in species)
        return [name for name, _ in counts.most_common(3)]

    def calculate_rare_species(self, species: List[Dict[str, Any]]) -> List[str]:
        counts = Counter(s.get("species", "Unknown") for s in species)
        return [name for name, count in counts.items() if count == 1]

    def compute_all(self, species: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "species_richness": self.calculate_species_richness(species),
            "shannon_index": self.calculate_shannon_index(species),
            "simpson_index": self.calculate_simpson_index(species),
            "evenness": self.calculate_evenness(species),
            "dominant_species": self.calculate_dominant_species(species),
            "rare_species": self.calculate_rare_species(species),
        }
