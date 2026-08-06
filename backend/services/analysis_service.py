from typing import Any, Dict

from aggregation.result_aggregator import ResultAggregator
from interfaces.data_repository import IDataRepository
from models.enums import PipelineStage
from services.assessment_service import AssessmentService
from services.classification_service import ClassificationService
from services.confidence_service import ConfidenceService
from services.identification_service import IdentificationService
from services.preprocessing_service import PreprocessingService
from utils.exceptions import SampleNotFoundError


class AnalysisService:
    """Orchestrates the full pipeline end-to-end for a single sample."""

    def __init__(
        self,
        repository: IDataRepository,
        preprocessing_service: PreprocessingService,
        identification_service: IdentificationService,
        classification_service: ClassificationService,
        assessment_service: AssessmentService,
        confidence_service: ConfidenceService,
        aggregator: ResultAggregator,
    ) -> None:
        self._repository = repository
        self._preprocessing_service = preprocessing_service
        self._identification_service = identification_service
        self._classification_service = classification_service
        self._assessment_service = assessment_service
        self._confidence_service = confidence_service
        self._aggregator = aggregator

    def analyze(self, sample_id: str) -> Dict[str, Any]:
        sample = self._repository.get_sample(sample_id)
        if not sample:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")

        preprocessed = self._preprocessing_service.preprocess(sample_id)
        identified = self._identification_service.identify(sample_id)
        classified = self._classification_service.classify(sample_id)
        assessed = self._assessment_service.assess(sample_id)

        feature_lookup = {
            seq["sequence_id"]: seq["features"] for seq in preprocessed["processed_sequences"]
        }
        classification_lookup = {c["sequence_id"]: c for c in classified["results"]}

        per_sequence_results = []
        for taxonomy in identified["results"]:
            sequence_id = taxonomy["sequence_id"]
            features = feature_lookup.get(sequence_id, {})
            confidence = self._confidence_service.calculate_for_sequence(taxonomy, features)
            per_sequence_results.append(
                {
                    "sequence_id": sequence_id,
                    "taxonomy": taxonomy,
                    "classification": classification_lookup.get(sequence_id, {}),
                    "confidence": confidence,
                }
            )

        aggregated = self._aggregator.aggregate(
            sample_id=sample_id,
            status=PipelineStage.ANALYZED.value,
            results=per_sequence_results,
            metrics=assessed["metrics"],
            assessment=assessed["assessment"],
        )

        self._repository.save_prediction(sample_id, aggregated)
        self._repository.update_sample_status(sample_id, PipelineStage.ANALYZED.value)
        return aggregated
