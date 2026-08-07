import zlib
from typing import Any, Dict

from identification.taxonomy_reference import TAXONOMY_TEMPLATE
from interfaces.taxonomy_engine import ITaxonomyEngine


class PlaceholderTaxonomyEngine(ITaxonomyEngine):
    """Skeletal taxonomy engine returning a hierarchical template result.

    TODO:
    Integrate ML classification model (e.g. BLAST / Kraken2 / a trained
    neural classifier) to derive real taxonomy from sequence + features.
    """

    def identify(self, sequence: str, features: Dict[str, Any]) -> Dict[str, Any]:
        index = zlib.crc32(sequence.encode("utf-8")) % len(TAXONOMY_TEMPLATE)
        template = TAXONOMY_TEMPLATE[index]
        completeness = features.get("completeness", 0.5)
        confidence = round(min(0.5 + completeness * 0.45, 0.99), 2)
        return {**template, "confidence": confidence}
