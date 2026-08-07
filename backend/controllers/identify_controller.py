from typing import Any, Dict

from fastapi import HTTPException, status

from services.identification_service import IdentificationService
from utils.exceptions import SampleNotFoundError, StageNotCompletedError


class IdentifyController:
    def __init__(self, service: IdentificationService) -> None:
        self._service = service

    def identify(self, sample_id: str) -> Dict[str, Any]:
        try:
            return self._service.identify(sample_id)
        except SampleNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        except StageNotCompletedError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
