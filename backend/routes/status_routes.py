from fastapi import APIRouter, Depends

from controllers.status_controller import StatusController
from dependencies import get_status_controller

router = APIRouter(tags=["Status"])


@router.get("/status", summary="Overall backend/engine status")
def engine_status(controller: StatusController = Depends(get_status_controller)):
    return controller.engine_status()


@router.get("/status/{sample_id}", summary="Pipeline status for a specific sample")
def sample_status(sample_id: str, controller: StatusController = Depends(get_status_controller)):
    return controller.sample_status(sample_id)


@router.get("/history", summary="History of aggregated predictions")
def prediction_history(controller: StatusController = Depends(get_status_controller)):
    return controller.history()
