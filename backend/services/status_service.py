from typing import Any, Dict, List

from interfaces.data_repository import IDataRepository
from utils.exceptions import SampleNotFoundError


class StatusService:
    def __init__(self, repository: IDataRepository) -> None:
        self._repository = repository

    def get_engine_status(self) -> Dict[str, Any]:
        collections = self._repository.list_collections()
        return {
            "status": "operational",
            "total_samples": len(self._repository.list_samples()),
            "total_predictions": len(self._repository.get_history()),
            "seed_dataset": {
                "loaded": bool(collections),
                "collection_count": len(collections),
                "record_count": sum(self._repository.count_records(c) for c in collections),
                "collections": {
                    c: self._repository.count_records(c) for c in collections
                },
            },
        }

    def get_sample_status(self, sample_id: str) -> Dict[str, Any]:
        sample = self._repository.get_sample(sample_id)
        if not sample:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")
        return {
            "sample_id": sample["sample_id"],
            "filename": sample["filename"],
            "file_type": sample["file_type"],
            "status": sample["status"],
            "sequence_count": len(sample["sequences"]),
            "uploaded_at": sample["uploaded_at"],
        }

    def get_history(self) -> List[Dict[str, Any]]:
        return self._repository.get_history()
