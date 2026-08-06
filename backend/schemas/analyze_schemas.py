from typing import Any, Dict, List

from pydantic import BaseModel

from schemas.assessment_schemas import BiodiversityMetrics, EcologicalAssessment
from schemas.confidence_schemas import ConfidenceResult


class SequenceAnalysisResult(BaseModel):
    sequence_id: str
    taxonomy: Dict[str, Any]
    classification: Dict[str, Any]
    confidence: ConfidenceResult


class AnalyzeResponse(BaseModel):
    sample_id: str
    status: str
    results: List[SequenceAnalysisResult]
    metrics: BiodiversityMetrics
    assessment: List[EcologicalAssessment]
