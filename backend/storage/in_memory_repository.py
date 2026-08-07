from typing import Any, Dict, List, Optional

from interfaces.data_repository import IDataRepository


class InMemoryRepository(IDataRepository):
    """Dictionary-backed placeholder for IDataRepository.

    TODO:
    Replace with a real database-backed repository (MongoDB, PostgreSQL,
    etc.) once the schema is finalized. Callers only ever depend on
    IDataRepository, so the swap requires no changes outside this file
    and the dependency wiring in dependencies.py.
    """

    def __init__(self) -> None:
        self._samples: Dict[str, Dict[str, Any]] = {}
        self._stage_results: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._predictions: Dict[str, Dict[str, Any]] = {}

    def save_sample(self, sample_id: str, sample_data: Dict[str, Any]) -> None:
        self._samples[sample_id] = sample_data

    def get_sample(self, sample_id: str) -> Optional[Dict[str, Any]]:
        return self._samples.get(sample_id)

    def update_sample_status(self, sample_id: str, status: str) -> None:
        if sample_id in self._samples:
            self._samples[sample_id]["status"] = status

    def save_stage_result(self, sample_id: str, stage: str, data: Dict[str, Any]) -> None:
        self._stage_results.setdefault(sample_id, {})[stage] = data

    def get_stage_result(self, sample_id: str, stage: str) -> Optional[Dict[str, Any]]:
        return self._stage_results.get(sample_id, {}).get(stage)

    def save_prediction(self, sample_id: str, prediction: Dict[str, Any]) -> None:
        self._predictions[sample_id] = prediction

    def get_prediction(self, sample_id: str) -> Optional[Dict[str, Any]]:
        return self._predictions.get(sample_id)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._predictions.values())

    def list_samples(self) -> List[str]:
        return list(self._samples.keys())
