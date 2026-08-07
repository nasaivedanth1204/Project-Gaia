from typing import List

from pydantic import BaseModel


class BiodiversityMetrics(BaseModel):
    species_richness: int
    shannon_index: float
    simpson_index: float
    evenness: float
    dominant_species: List[str]
    rare_species: List[str]


class EcologicalAssessment(BaseModel):
    title: str
    severity: str
    description: str


class AssessResponse(BaseModel):
    sample_id: str
    status: str
    metrics: BiodiversityMetrics
    assessment: List[EcologicalAssessment]
