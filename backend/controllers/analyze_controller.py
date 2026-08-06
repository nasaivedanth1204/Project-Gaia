from typing import Any, Dict

from fastapi import HTTPException, status

from services.analysis_service import AnalysisService
from utils.exceptions import SampleNotFoundError, StageNotCompletedError


class AnalyzeController:
    def __init__(self, service: AnalysisService) -> None:
        self._service = service

    def analyze(self, sample_id: str) -> Dict[str, Any]:
        try:
            return self._service.analyze(sample_id)
        except SampleNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        except StageNotCompletedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
