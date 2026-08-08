from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from services.explore_service import ExploreService
from utils.exceptions import SampleNotFoundError


class ExploreController:
    def __init__(self, service: ExploreService) -> None:
        self._service = service

    def _not_found(self, exc: SampleNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    def list_reference(self, collection: str, **filters) -> List[Dict[str, Any]]:
        try:
            return self._service.list_reference(collection, filters)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    def list_organisms(self, **filters) -> List[Dict[str, Any]]:
        return self._service.list_organisms(**filters)

    def get_organism(self, organism_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_organism(organism_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def list_taxonomy(self, kingdom: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._service.list_taxonomy(kingdom)

    def list_samples(self) -> List[Dict[str, Any]]:
        return self._service.list_samples()

    def get_sample(self, sample_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_sample(sample_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def list_identifications(self, sample_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._service.list_identifications(sample_id)

    def list_biodiversity_metrics(self, sample_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._service.list_biodiversity_metrics(sample_id)

    def list_biodiversity_assessments(
        self, sample_id: Optional[str] = None, severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self._service.list_biodiversity_assessments(sample_id, severity)

    def get_population(self, organism_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_population(organism_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def get_population_timeseries(self, organism_id: str) -> List[Dict[str, Any]]:
        return self._service.get_population_timeseries(organism_id)

    def get_habitat(self, organism_id: str) -> Optional[Dict[str, Any]]:
        return self._service.get_habitat(organism_id)

    def list_threats(
        self, organism_id: Optional[str] = None, ecosystem_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self._service.list_threats(organism_id, ecosystem_id)

    def list_conservation_status(self) -> List[Dict[str, Any]]:
        return self._service.list_conservation_status()

    def get_conservation(self, organism_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_conservation(organism_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def list_risk_assessments(self) -> List[Dict[str, Any]]:
        return self._service.list_risk_assessments()

    def get_risk(self, organism_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_risk(organism_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def get_species_profile(self, organism_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_species_profile(organism_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        try:
            return self._service.get_analysis(analysis_id)
        except SampleNotFoundError as exc:
            self._not_found(exc)

    def list_analyses(self) -> List[Dict[str, Any]]:
        return self._service.list_analyses()

    def dashboard_summary(self) -> Dict[str, Any]:
        return self._service.dashboard_summary()
