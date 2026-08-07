from typing import List

from pydantic import BaseModel


class SequenceRecordSchema(BaseModel):
    sequence_id: str
    header: str
    sequence: str
    length: int


class UploadResponse(BaseModel):
    sample_id: str
    filename: str
    file_type: str
    sequence_count: int
    sequences: List[SequenceRecordSchema]
    status: str
