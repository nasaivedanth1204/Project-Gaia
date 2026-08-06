from typing import Any, Dict, List

from pydantic import BaseModel


class ProcessedSequence(BaseModel):
    sequence_id: str
    original_sequence: str
    processed_sequence: str
    markers_detected: List[str]
    features: Dict[str, Any]


class PreprocessResponse(BaseModel):
    sample_id: str
    status: str
    processed_sequences: List[ProcessedSequence]
