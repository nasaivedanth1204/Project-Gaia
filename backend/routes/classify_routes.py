from fastapi import APIRouter, Depends

from controllers.classify_controller import ClassifyController
from dependencies import get_classify_controller
from schemas.common import SampleRequest

router = APIRouter(tags=["Classification"])


@router.post("/classify", summary="Assign an ecological category to identified sequences")
def classify_sample(
    request: SampleRequest,
    controller: ClassifyController = Depends(get_classify_controller),
):
    result = controller.classify(request.sample_id)
    return {"sample_id": result["sample_id"], "status": "classified", "results": result["results"]}
