from fastapi import APIRouter, Depends

from controllers.identify_controller import IdentifyController
from dependencies import get_identify_controller
from schemas.common import SampleRequest

router = APIRouter(tags=["Identification"])


@router.post("/identify", summary="Run taxonomic identification on a preprocessed sample")
def identify_sample(
    request: SampleRequest,
    controller: IdentifyController = Depends(get_identify_controller),
):
    result = controller.identify(request.sample_id)
    return {"sample_id": result["sample_id"], "status": "identified", "results": result["results"]}
