from typing import Any, Dict

from pydantic import BaseModel


class ConfidenceResult(BaseModel):
    confidence: float
    confidence_level: str
    inputs: Dict[str, Any]
