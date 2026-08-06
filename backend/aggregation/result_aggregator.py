from typing import Any, Dict, List


class ResultAggregator:
    """Combines per-stage outputs into the final /analyze API response.

    TODO:
    Extend this once persistence is backed by a real database (e.g. to
    include historical comparisons, versioning, or provenance metadata).
    """

    def aggregate(
        self,
        sample_id: str,
        status: str,
        results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        assessment: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "sample_id": sample_id,
            "status": status,
            "results": results,
            "metrics": metrics,
            "assessment": assessment,
        }
