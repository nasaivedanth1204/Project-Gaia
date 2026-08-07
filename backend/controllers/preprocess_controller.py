from typing import Any, Dict

from fastapi import HTTPException, status

from services.preprocessing_service import PreprocessingService
from utils.exceptions import SampleNotFoundError


class PreprocessController:
    def __init__(self, service: PreprocessingService) -> None:
        self._service = service

    def preprocess(self, sample_id: str) -> Dict[str, Any]:
        try:
            return self._service.preprocess(sample_id)
        except SampleNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
