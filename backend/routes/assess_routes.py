from fastapi import APIRouter, Depends

from controllers.assess_controller import AssessController
from dependencies import get_assess_controller
from schemas.common import SampleRequest

router = APIRouter(tags=["Assessment"])


@router.post("/assess", summary="Compute biodiversity metrics and ecological assessment")
def assess_sample(
    request: SampleRequest,
    controller: AssessController = Depends(get_assess_controller),
):
    result = controller.assess(request.sample_id)
    return {
        "sample_id": result["sample_id"],
        "status": "assessed",
        "metrics": result["metrics"],
        "assessment": result["assessment"],
    }
