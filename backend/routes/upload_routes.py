from fastapi import APIRouter, Depends, File, UploadFile

from controllers.upload_controller import UploadController
from dependencies import get_upload_controller
from schemas.upload_schemas import UploadResponse

router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse, summary="Upload an eDNA dataset (FASTA/CSV/TXT)")
async def upload_dataset(
    file: UploadFile = File(...),
    controller: UploadController = Depends(get_upload_controller),
):
    result = await controller.upload(file)
    return {
        "sample_id": result["sample_id"],
        "filename": result["filename"],
        "file_type": result["file_type"],
        "sequence_count": len(result["sequences"]),
        "sequences": result["sequences"],
        "status": result["status"],
    }
