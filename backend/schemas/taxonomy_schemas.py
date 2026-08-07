from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TaxonomyResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sequence_id: str
    kingdom: str
    phylum: str
    class_: str = Field(alias="class")
    order: str
    family: str
    genus: str
    species: str
    confidence: float


class IdentifyResponse(BaseModel):
    sample_id: str
    status: str
    results: List[TaxonomyResult]
