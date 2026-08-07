from typing import Any, Dict

from interfaces.data_repository import IDataRepository
from interfaces.taxonomy_engine import ITaxonomyEngine
from models.enums import PipelineStage
from utils.exceptions import SampleNotFoundError, StageNotCompletedError


class IdentificationService:
    def __init__(self, repository: IDataRepository, taxonomy_engine: ITaxonomyEngine) -> None:
        self._repository = repository
        self._taxonomy_engine = taxonomy_engine

    def identify(self, sample_id: str) -> Dict[str, Any]:
        sample = self._repository.get_sample(sample_id)
        if not sample:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")

        preprocessed = self._repository.get_stage_result(sample_id, PipelineStage.PREPROCESSED.value)
        if not preprocessed:
            raise StageNotCompletedError("Sample must be preprocessed before identification.")

        results = []
        for record in preprocessed["processed_sequences"]:
            taxonomy = self._taxonomy_engine.identify(record["processed_sequence"], record["features"])
            results.append({"sequence_id": record["sequence_id"], **taxonomy})

        result_data = {"sample_id": sample_id, "results": results}
        self._repository.save_stage_result(sample_id, PipelineStage.IDENTIFIED.value, result_data)
        self._repository.update_sample_status(sample_id, PipelineStage.IDENTIFIED.value)
        return result_data
