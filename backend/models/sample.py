from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from models.enums import PipelineStage


@dataclass
class SequenceRecord:
    sequence_id: str
    header: str
    sequence: str
    length: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Sample:
    sample_id: str
    filename: str
    file_type: str
    sequences: List[Dict[str, Any]]
    uploaded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = PipelineStage.UPLOADED.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
