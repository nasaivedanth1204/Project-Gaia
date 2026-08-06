from typing import Any, Dict

from interfaces.classification_engine import IClassificationEngine
from interfaces.data_repository import IDataRepository
from models.enums import PipelineStage
from utils.exceptions import SampleNotFoundError, StageNotCompletedError


class ClassificationService:
    def __init__(self, repository: IDataRepository, classification_engine: IClassificationEngine) -> None:
        self._repository = repository
        self._classification_engine = classification_engine

    def classify(self, sample_id: str) -> Dict[str, Any]:
        sample = self._repository.get_sample(sample_id)
        if not sample:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")

        identified = self._repository.get_stage_result(sample_id, PipelineStage.IDENTIFIED.value)
        if not identified:
            raise StageNotCompletedError("Sample must be identified before classification.")

        preprocessed = self._repository.get_stage_result(sample_id, PipelineStage.PREPROCESSED.value) or {}
        feature_lookup = {
            seq["sequence_id"]: seq["features"] for seq in preprocessed.get("processed_sequences", [])
        }

        results = []
        for taxonomy in identified["results"]:
            features = feature_lookup.get(taxonomy["sequence_id"], {})
            classification = self._classification_engine.classify(taxonomy, features)
            results.append({"sequence_id": taxonomy["sequence_id"], **classification})

        result_data = {"sample_id": sample_id, "results": results}
        self._repository.save_stage_result(sample_id, PipelineStage.CLASSIFIED.value, result_data)
        self._repository.update_sample_status(sample_id, PipelineStage.CLASSIFIED.value)
        return result_data
