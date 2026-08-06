from typing import Any, Dict

from fastapi import UploadFile

from interfaces.data_repository import IDataRepository
from models.sample import Sample
from utils.id_generator import generate_id
from utils.parsers import parse_sequences
from utils.validators import ValidationError, validate_upload


class UploadService:
    def __init__(self, repository: IDataRepository) -> None:
        self._repository = repository

    async def handle_upload(self, file: UploadFile) -> Dict[str, Any]:
        raw_bytes = await file.read()
        content = raw_bytes.decode("utf-8", errors="replace")

        file_type = validate_upload(file.filename or "upload.txt", content)
        sequences = parse_sequences(file_type, content)

        if not sequences:
            raise ValidationError("No sequences could be extracted from the uploaded file.")

        sample = Sample(
            sample_id=generate_id("sample"),
            filename=file.filename or "unknown",
            file_type=file_type,
            sequences=sequences,
        )
        sample_data = sample.to_dict()
        self._repository.save_sample(sample.sample_id, sample_data)
        return sample_data
