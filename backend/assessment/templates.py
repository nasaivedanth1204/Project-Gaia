from typing import Dict

# TODO:
# Move these into a configuration file / database table so titles,
# severities, and descriptions can be tuned without a code change.
ASSESSMENT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "HIGH_BIODIVERSITY": {
        "title": "High Biodiversity",
        "severity": "info",
        "description": "The sample shows a high level of species richness and evenness.",
    },
    "MEDIUM_BIODIVERSITY": {
        "title": "Medium Biodiversity",
        "severity": "info",
        "description": "The sample shows a moderate level of species diversity.",
    },
    "LOW_BIODIVERSITY": {
        "title": "Low Biodiversity",
        "severity": "warning",
        "description": "The sample shows low species richness, which may indicate ecosystem stress.",
    },
    "ENVIRONMENTAL_STRESS": {
        "title": "Potential Environmental Stress",
        "severity": "warning",
        "description": "Dominance of a few species suggests a potentially stressed environment.",
    },
    "INVASIVE_SPECIES": {
        "title": "Possible Invasive Species",
        "severity": "critical",
        "description": "One or more identified taxa match known invasive-species patterns.",
    },
    "RARE_SPECIES": {
        "title": "Rare Species Present",
        "severity": "info",
        "description": "One or more species were detected at very low abundance.",
    },
    "ENDANGERED_SPECIES": {
        "title": "Endangered Species Detected",
        "severity": "critical",
        "description": "One or more identified taxa match known endangered-species records.",
    },
    "LOW_CONFIDENCE": {
        "title": "Low Confidence Identification",
        "severity": "warning",
        "description": "Taxonomic identification confidence is below a reliable threshold.",
    },
}
