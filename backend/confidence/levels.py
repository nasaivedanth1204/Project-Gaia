from enum import Enum


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "Very High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNKNOWN = "Unknown"


def level_from_score(score: float) -> ConfidenceLevel:
    if score >= 0.9:
        return ConfidenceLevel.VERY_HIGH
    if score >= 0.75:
        return ConfidenceLevel.HIGH
    if score >= 0.5:
        return ConfidenceLevel.MEDIUM
    if score > 0:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNKNOWN
