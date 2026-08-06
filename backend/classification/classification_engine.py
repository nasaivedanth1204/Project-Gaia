from typing import Any, Dict

from classification.categories import KINGDOM_CATEGORY_MAP, SpeciesCategory
from interfaces.classification_engine import IClassificationEngine


class PlaceholderClassificationEngine(IClassificationEngine):
    """Skeletal classification engine assigning a broad ecological category.

    TODO:
    Integrate a real ML classification model trained on habitat / lineage
    features to replace this rule-based placeholder.
    """

    def classify(self, taxonomy: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        kingdom = taxonomy.get("kingdom", "Unknown")
        category = KINGDOM_CATEGORY_MAP.get(kingdom, SpeciesCategory.UNKNOWN)
        return {
            "category": category.value,
            "kingdom_reference": kingdom,
            "basis": "placeholder-kingdom-mapping",
        }
