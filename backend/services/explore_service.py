"""Read-side service over the synthetic Gaia data model.

Everything here is a query or a derived computation against records
already sitting in the repository (via generic list_records/get_record) —
this service does not own a storage format of its own, so it stays valid
whatever IDataRepository implementation backs it later.

The one piece of real computation is risk scoring: /risk and /species
recompute the Gaia Prototype Risk Score live from the organism's current
population/habitat/threat records via IRiskEngine, rather than only ever
echoing back the value baked into the seed file. That is what proves the
risk engine is a real, callable component and not just seed-time output.
"""

from collections import Counter
from typing import Any, Dict, List, Optional

from interfaces.data_repository import IDataRepository
from interfaces.risk_engine import IRiskEngine
from utils.exceptions import SampleNotFoundError

REFERENCE_COLLECTIONS = [
    "biospheres", "biomes", "terrains", "ecosystems", "locations", "sampling_sites",
]

TOP_RISK_LIMIT = 10


class ExploreService:
    def __init__(self, repository: IDataRepository, risk_engine: IRiskEngine) -> None:
        self._repository = repository
        self._risk_engine = risk_engine

    # ------------------------------------------------------------------
    # Environment hierarchy
    # ------------------------------------------------------------------
    def list_reference(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if collection not in REFERENCE_COLLECTIONS:
            raise ValueError(f"Unknown reference collection '{collection}'")
        return self._repository.list_records(collection, self._clean(filters))

    # ------------------------------------------------------------------
    # Organisms / taxonomy
    # ------------------------------------------------------------------
    def list_organisms(
        self,
        kingdom: Optional[str] = None,
        habitat_type: Optional[str] = None,
        native_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filters = self._clean({
            "kingdom": kingdom, "habitat_type": habitat_type, "native_status": native_status,
        })
        return self._repository.list_records("organisms", filters)

    def get_organism(self, organism_id: str) -> Dict[str, Any]:
        organism = self._repository.get_organism(organism_id)
        if not organism:
            raise SampleNotFoundError(f"Organism '{organism_id}' was not found.")
        return organism

    def list_taxonomy(self, kingdom: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._repository.list_records("taxonomy", self._clean({"kingdom": kingdom}))

    # ------------------------------------------------------------------
    # Samples / sequences / identifications
    # ------------------------------------------------------------------
    def list_samples(self) -> List[Dict[str, Any]]:
        return self._repository.list_records("samples")

    def get_sample(self, sample_id: str) -> Dict[str, Any]:
        record = self._repository.get_record("samples", sample_id)
        if not record:
            raise SampleNotFoundError(f"Sample '{sample_id}' was not found.")
        return record

    def list_identifications(self, sample_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._repository.list_records("identifications", self._clean({"sample_id": sample_id}))

    # ------------------------------------------------------------------
    # Biodiversity
    # ------------------------------------------------------------------
    def list_biodiversity_metrics(self, sample_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._repository.list_records("biodiversity_metrics", self._clean({"sample_id": sample_id}))

    def list_biodiversity_assessments(
        self, sample_id: Optional[str] = None, severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filters = self._clean({"sample_id": sample_id, "severity": severity})
        return self._repository.list_records("biodiversity_assessments", filters)

    # ------------------------------------------------------------------
    # Population / habitat / threats / conservation
    # ------------------------------------------------------------------
    def get_population(self, organism_id: str) -> Dict[str, Any]:
        records = self._repository.list_records("population_assessments", {"organism_id": organism_id})
        if not records:
            raise SampleNotFoundError(f"No population assessment for organism '{organism_id}'.")
        return records[0]

    def get_population_timeseries(self, organism_id: str) -> List[Dict[str, Any]]:
        rows = self._repository.list_records("population_timeseries", {"organism_id": organism_id})
        return sorted(rows, key=lambda r: r["year"])

    def get_habitat(self, organism_id: str) -> Optional[Dict[str, Any]]:
        records = self._repository.list_records("habitat_assessments", {"organism_id": organism_id})
        return records[0] if records else None

    def list_threats(
        self, organism_id: Optional[str] = None, ecosystem_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filters = self._clean({"organism_id": organism_id, "ecosystem_id": ecosystem_id})
        return self._repository.list_records("threat_assessments", filters)

    def list_conservation_status(self) -> List[Dict[str, Any]]:
        return self._repository.list_records("conservation_status")

    def get_conservation(self, organism_id: str) -> Dict[str, Any]:
        status = self._repository.list_records("conservation_status", {"organism_id": organism_id})
        assessment = self._repository.list_records("conservation_assessments", {"organism_id": organism_id})
        if not status:
            raise SampleNotFoundError(f"No conservation record for organism '{organism_id}'.")
        return {
            "status": status[0],
            "assessment": assessment[0] if assessment else None,
        }

    # ------------------------------------------------------------------
    # Risk — computed live, not just echoed from the seed
    # ------------------------------------------------------------------
    def list_risk_assessments(self) -> List[Dict[str, Any]]:
        """Seed-side risk records, for bulk display (e.g. a species table).

        Use get_risk()/get_species_profile() instead when you need a score
        recomputed live from the organism's current records.
        """
        return self._repository.list_records("extinction_risk_assessments")

    def get_risk(self, organism_id: str) -> Dict[str, Any]:
        population = self.get_population(organism_id)
        habitat = self.get_habitat(organism_id)
        threats = self.list_threats(organism_id=organism_id)
        return self._risk_engine.score(population, habitat, threats)

    def get_species_profile(self, organism_id: str) -> Dict[str, Any]:
        """Assemble the full risk-profile object (organism + every linked
        assessment) in one call — the natural "click a species" payload.
        """
        organism = self.get_organism(organism_id)
        taxonomy = self._repository.get_record("taxonomy", organism["taxonomy_id"])
        population = self.get_population(organism_id)
        habitat = self.get_habitat(organism_id)
        threats = self.list_threats(organism_id=organism_id)
        conservation = self._safe(self.get_conservation, organism_id)
        risk = self._risk_engine.score(population, habitat, threats)
        timeseries = self.get_population_timeseries(organism_id)

        return {
            "organism": organism,
            "taxonomy": taxonomy,
            "population": population,
            "population_timeseries": timeseries,
            "habitat": habitat,
            "threats": threats,
            "conservation": conservation,
            "risk": risk,
            "assessment": {
                "type": "prototype_risk_assessment",
                "is_synthetic": True,
            },
        }

    @staticmethod
    def _safe(fn, *args):
        try:
            return fn(*args)
        except SampleNotFoundError:
            return None

    # ------------------------------------------------------------------
    # Analysis results (seed-side aggregated records)
    # ------------------------------------------------------------------
    def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        record = self._repository.get_analysis(analysis_id)
        if not record:
            raise SampleNotFoundError(f"Analysis '{analysis_id}' was not found.")
        return record

    def list_analyses(self) -> List[Dict[str, Any]]:
        return self._repository.list_records("analysis_results")

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def dashboard_summary(self) -> Dict[str, Any]:
        organisms = self._repository.list_records("organisms")
        metrics = self._repository.list_records("biodiversity_metrics")
        risks = self._repository.list_records("extinction_risk_assessments")
        conservation = self._repository.list_records("conservation_status")
        threats = self._repository.list_records("threat_assessments")

        risk_levels = Counter(r["risk_level"] for r in risks)
        biodiversity_categories = Counter(m["biodiversity_category"] for m in metrics)
        kingdoms = Counter(o["kingdom"] for o in organisms)
        conservation_statuses = Counter(c["external_conservation_status"] for c in conservation)
        threat_categories = Counter(t["threat_category"] for t in threats)

        scored = [r for r in risks if r.get("gaia_risk_score") is not None]
        top_risk = sorted(scored, key=lambda r: r["gaia_risk_score"], reverse=True)[:TOP_RISK_LIMIT]
        org_by_id = {o["organism_id"]: o for o in organisms}

        return {
            "totals": {
                collection: self._repository.count_records(collection)
                for collection in sorted(self._repository.list_collections())
            },
            "risk_level_distribution": dict(risk_levels),
            "biodiversity_category_distribution": dict(biodiversity_categories),
            "kingdom_distribution": dict(kingdoms),
            "conservation_status_distribution": dict(conservation_statuses),
            "threat_category_distribution": dict(threat_categories),
            "top_risk_species": [
                {
                    "organism_id": r["organism_id"],
                    "scientific_name": org_by_id.get(r["organism_id"], {}).get("scientific_name"),
                    "common_name": org_by_id.get(r["organism_id"], {}).get("common_name"),
                    "gaia_risk_score": r["gaia_risk_score"],
                    "risk_level": r["risk_level"],
                    "risk_confidence": r["risk_confidence"],
                }
                for r in top_risk
            ],
            "is_synthetic": True,
            "disclaimer": (
                "All figures summarize the synthetic Gaia seed dataset. "
                "None represent real field observations."
            ),
        }

    @staticmethod
    def _clean(filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not filters:
            return None
        cleaned = {k: v for k, v in filters.items() if v is not None}
        return cleaned or None
