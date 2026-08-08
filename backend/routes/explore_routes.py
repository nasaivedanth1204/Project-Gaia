"""Read-only API surface over the synthetic Gaia data model.

Everything here reads from the seed dataset (data/seed/*.json), loaded
into the shared repository at startup — see dependencies.py::get_repository.
It is entirely separate from the live single-sample pipeline
(/upload ... /analyze), which continues to operate unchanged.
"""

from typing import Optional

from fastapi import APIRouter, Depends

from controllers.explore_controller import ExploreController
from dependencies import get_explore_controller

router = APIRouter(tags=["Explore"])


# -- Environment hierarchy ------------------------------------------------

@router.get("/biospheres")
def list_biospheres(controller: ExploreController = Depends(get_explore_controller)):
    return controller.list_reference("biospheres")


@router.get("/biomes")
def list_biomes(
    biosphere_id: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_reference("biomes", biosphere_id=biosphere_id)


@router.get("/terrains")
def list_terrains(controller: ExploreController = Depends(get_explore_controller)):
    return controller.list_reference("terrains")


@router.get("/ecosystems")
def list_ecosystems(
    ecosystem_type: Optional[str] = None,
    biosphere_id: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_reference("ecosystems", ecosystem_type=ecosystem_type, biosphere_id=biosphere_id)


@router.get("/locations")
def list_locations(
    state: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_reference("locations", state=state)


@router.get("/sampling-sites")
def list_sampling_sites(
    ecosystem_id: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_reference("sampling_sites", ecosystem_id=ecosystem_id)


# -- Organisms / taxonomy -------------------------------------------------

@router.get("/organisms")
def list_organisms(
    kingdom: Optional[str] = None,
    habitat_type: Optional[str] = None,
    native_status: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_organisms(kingdom=kingdom, habitat_type=habitat_type, native_status=native_status)


@router.get("/organisms/{organism_id}")
def get_organism(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_organism(organism_id)


@router.get("/taxonomy")
def list_taxonomy(
    kingdom: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_taxonomy(kingdom)


# -- Samples / identifications --------------------------------------------

@router.get("/samples")
def list_samples(controller: ExploreController = Depends(get_explore_controller)):
    return controller.list_samples()


@router.get("/samples/{sample_id}")
def get_sample(sample_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_sample(sample_id)


@router.get("/identifications")
def list_identifications(
    sample_id: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_identifications(sample_id)


# -- Biodiversity ----------------------------------------------------------

@router.get("/biodiversity/metrics")
def list_biodiversity_metrics(
    sample_id: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_biodiversity_metrics(sample_id)


@router.get("/biodiversity/assessments")
def list_biodiversity_assessments(
    sample_id: Optional[str] = None,
    severity: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_biodiversity_assessments(sample_id, severity)


# -- Population / habitat / threats / conservation / risk ------------------

@router.get("/population/{organism_id}")
def get_population(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_population(organism_id)


@router.get("/population/{organism_id}/timeseries")
def get_population_timeseries(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_population_timeseries(organism_id)


@router.get("/habitat/{organism_id}")
def get_habitat(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_habitat(organism_id)


@router.get("/threats")
def list_threats(
    organism_id: Optional[str] = None,
    ecosystem_id: Optional[str] = None,
    controller: ExploreController = Depends(get_explore_controller),
):
    return controller.list_threats(organism_id, ecosystem_id)


@router.get("/conservation")
def list_conservation_status(controller: ExploreController = Depends(get_explore_controller)):
    return controller.list_conservation_status()


@router.get("/conservation/{organism_id}")
def get_conservation(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_conservation(organism_id)


@router.get("/risk")
def list_risk_assessments(controller: ExploreController = Depends(get_explore_controller)):
    return controller.list_risk_assessments()


@router.get("/risk/{organism_id}")
def get_risk(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_risk(organism_id)


@router.get("/species/{organism_id}")
def get_species_profile(organism_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_species_profile(organism_id)


# -- Analysis / dashboard ---------------------------------------------------

@router.get("/analysis")
def list_analyses(controller: ExploreController = Depends(get_explore_controller)):
    return controller.list_analyses()


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str, controller: ExploreController = Depends(get_explore_controller)):
    return controller.get_analysis(analysis_id)


@router.get("/dashboard/summary")
def dashboard_summary(controller: ExploreController = Depends(get_explore_controller)):
    return controller.dashboard_summary()
