from typing import Any, Dict, List

from fastapi import HTTPException, status

from services.status_service import StatusService
from utils.exceptions import SampleNotFoundError


class StatusController:
    def __init__(self, service: StatusService) -> None:
        self._service = service

    def engine_status(self) -> Dict[str, Any]:
        return self._service.get_engine_status()

    def sample_status(self, sample_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_sample_status(sample_id)
        except SampleNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    def history(self) -> List[Dict[str, Any]]:
        return self._service.get_history()
