from fastapi import APIRouter, Depends

from controllers.analyze_controller import AnalyzeController
from dependencies import get_analyze_controller
from schemas.common import SampleRequest

router = APIRouter(tags=["Analysis"])


@router.post("/analyze", summary="Run the full pipeline end-to-end and return the aggregated result")
def analyze_sample(
    request: SampleRequest,
    controller: AnalyzeController = Depends(get_analyze_controller),
):
    return controller.analyze(request.sample_id)
