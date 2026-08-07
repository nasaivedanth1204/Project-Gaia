from typing import List

from pydantic import BaseModel


class ClassificationResult(BaseModel):
    sequence_id: str
    category: str
    kingdom_reference: str
    basis: str


class ClassifyResponse(BaseModel):
    sample_id: str
    status: str
    results: List[ClassificationResult]
