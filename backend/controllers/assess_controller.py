from typing import Any, Dict

from fastapi import HTTPException, status

from services.assessment_service import AssessmentService
from utils.exceptions import SampleNotFoundError, StageNotCompletedError


class AssessController:
    def __init__(self, service: AssessmentService) -> None:
        self._service = service

    def assess(self, sample_id: str) -> Dict[str, Any]:
        try:
            return self._service.assess(sample_id)
        except SampleNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        except StageNotCompletedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
