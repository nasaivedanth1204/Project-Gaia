from typing import Any, Dict, List

from assessment.templates import ASSESSMENT_TEMPLATES


class EcologicalAssessmentEngine:
    """Generates ecological assessment objects from computed metrics.

    TODO:
    Replace these threshold-based rules with a validated ecological model
    (expert-defined rules, invasive/endangered species reference
    databases, statistically grounded stress indicators).
    """

    RICHNESS_HIGH = 10
    RICHNESS_MEDIUM = 4
    CONFIDENCE_LOW_THRESHOLD = 0.5

    def generate(self, metrics: Dict[str, Any], confidence: float) -> List[Dict[str, str]]:
        assessments: List[Dict[str, str]] = []
        richness = metrics.get("species_richness", 0)

        if richness >= self.RICHNESS_HIGH:
            assessments.append(ASSESSMENT_TEMPLATES["HIGH_BIODIVERSITY"])
        elif richness >= self.RICHNESS_MEDIUM:
            assessments.append(ASSESSMENT_TEMPLATES["MEDIUM_BIODIVERSITY"])
        else:
            assessments.append(ASSESSMENT_TEMPLATES["LOW_BIODIVERSITY"])

        dominant = metrics.get("dominant_species") or []
        if richness and dominant and len(dominant) < max(1, richness // 3):
            assessments.append(ASSESSMENT_TEMPLATES["ENVIRONMENTAL_STRESS"])

        if metrics.get("rare_species"):
            assessments.append(ASSESSMENT_TEMPLATES["RARE_SPECIES"])

        if confidence < self.CONFIDENCE_LOW_THRESHOLD:
            assessments.append(ASSESSMENT_TEMPLATES["LOW_CONFIDENCE"])

        # TODO:
        # Cross-reference identified species against invasive and
        # endangered species reference lists to append INVASIVE_SPECIES /
        # ENDANGERED_SPECIES assessments.

        return assessments
