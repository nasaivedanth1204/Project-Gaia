from typing import Any, Dict

from fastapi import HTTPException, UploadFile, status

from services.upload_service import UploadService
from utils.exceptions import ValidationError


class UploadController:
    def __init__(self, service: UploadService) -> None:
        self._service = service

    async def upload(self, file: UploadFile) -> Dict[str, Any]:
        try:
            return await self._service.handle_upload(file)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": exc.message, "errors": exc.errors},
            )
