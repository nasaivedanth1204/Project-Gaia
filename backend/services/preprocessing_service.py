from typing import Any, Dict

from interfaces.data_repository import IDataRepository
from interfaces.preprocessing_engine import IPreprocessingEngine
from models.enums import PipelineStage
from utils.exceptions import SampleNotFoundError


class PreprocessingService:
    def __init__(self, repository: IDataRepository, preprocessor: IPreprocessingEngine) -> None:
        self._repository = repository
        self._preprocessor = preprocessor

    def preprocess(self, sample_id: str) -> Dict[str, Any]:
        sample = self._repository.get_sample(sample_id)
        if not sample:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")

        processed_sequences = []
        for record in sample["sequences"]:
            sequence = record["sequence"]
            cleaned = self._preprocessor.clean_sequence(sequence)
            denoised = self._preprocessor.remove_noise(cleaned)
            normalized = self._preprocessor.normalize_sequence(denoised)
            markers = self._preprocessor.detect_markers(normalized)
            features = self._preprocessor.extract_features(normalized)
            processed_sequences.append(
                {
                    "sequence_id": record["sequence_id"],
                    "original_sequence": sequence,
                    "processed_sequence": normalized,
                    "markers_detected": markers,
                    "features": features,
                }
            )

        result_data = {"sample_id": sample_id, "processed_sequences": processed_sequences}
        self._repository.save_stage_result(sample_id, PipelineStage.PREPROCESSED.value, result_data)
        self._repository.update_sample_status(sample_id, PipelineStage.PREPROCESSED.value)
        return result_data
