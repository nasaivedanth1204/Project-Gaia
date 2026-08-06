from typing import List, Optional

from pydantic import BaseModel


class SampleRequest(BaseModel):
    sample_id: str


class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[List[str]] = None


class StatusResponse(BaseModel):
    status: str
    total_samples: int
    total_predictions: int
    version: str = "0.1.0-prototype"


class SampleStatusResponse(BaseModel):
    sample_id: str
    filename: str
    file_type: str
    status: str
    sequence_count: int
    uploaded_at: str
