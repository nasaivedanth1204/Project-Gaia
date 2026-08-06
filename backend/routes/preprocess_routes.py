from fastapi import APIRouter, Depends

from controllers.preprocess_controller import PreprocessController
from dependencies import get_preprocess_controller
from schemas.common import SampleRequest
from schemas.preprocessing_schemas import PreprocessResponse

router = APIRouter(tags=["Preprocessing"])


@router.post("/preprocess", response_model=PreprocessResponse, summary="Clean, normalize and extract features from sequences")
def preprocess_sample(
    request: SampleRequest,
    controller: PreprocessController = Depends(get_preprocess_controller),
):
    result = controller.preprocess(request.sample_id)
    return {
        "sample_id": result["sample_id"],
        "status": "preprocessed",
        "processed_sequences": result["processed_sequences"],
    }
