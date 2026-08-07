from typing import Any, Dict

from assessment.biodiversity_metrics import PlaceholderBiodiversityEngine
from assessment.ecological_assessment import EcologicalAssessmentEngine
from interfaces.data_repository import IDataRepository
from models.enums import PipelineStage
from utils.exceptions import SampleNotFoundError, StageNotCompletedError


class AssessmentService:
    def __init__(
        self,
        repository: IDataRepository,
        biodiversity_engine: PlaceholderBiodiversityEngine,
        ecological_engine: EcologicalAssessmentEngine,
    ) -> None:
        self._repository = repository
        self._biodiversity_engine = biodiversity_engine
        self._ecological_engine = ecological_engine

    def assess(self, sample_id: str) -> Dict[str, Any]:
        sample = self._repository.get_sample(sample_id)
        if not sample:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")

        identified = self._repository.get_stage_result(sample_id, PipelineStage.IDENTIFIED.value)
        if not identified:
            raise StageNotCompletedError("Sample must be identified before assessment.")

        species_list = identified["results"]
        metrics = self._biodiversity_engine.compute_all(species_list)

        avg_confidence = (
            sum(s.get("confidence", 0.0) for s in species_list) / len(species_list) if species_list else 0.0
        )
        assessment = self._ecological_engine.generate(metrics, avg_confidence)

        result_data = {"sample_id": sample_id, "metrics": metrics, "assessment": assessment}
        self._repository.save_stage_result(sample_id, PipelineStage.ASSESSED.value, result_data)
        self._repository.update_sample_status(sample_id, PipelineStage.ASSESSED.value)
        return result_data
