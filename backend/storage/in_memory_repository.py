from typing import Any, Dict, List, Optional

from interfaces.data_repository import IDataRepository


class InMemoryRepository(IDataRepository):
    """Dictionary-backed placeholder for IDataRepository.

    TODO:
    Replace with a real database-backed repository (MongoDB, PostgreSQL,
    etc.) once the schema is finalized. Callers only ever depend on
    IDataRepository, so the swap requires no changes outside this file
    and the dependency wiring in dependencies.py.
    """

    # Primary-key field for each seed collection, so records can be
    # indexed generically without the caller naming the key every time.
    PRIMARY_KEYS: Dict[str, str] = {
        "biospheres": "biosphere_id",
        "biomes": "biome_id",
        "terrains": "terrain_id",
        "ecosystems": "ecosystem_id",
        "locations": "location_id",
        "sampling_sites": "site_id",
        "environmental_conditions": "environmental_condition_id",
        "samples": "sample_id",
        "dna_sequences": "sequence_id",
        "taxonomy": "taxonomy_id",
        "organisms": "organism_id",
        "classifications": "classification_id",
        "identifications": "identification_id",
        "biodiversity_metrics": "biodiversity_metric_id",
        "biodiversity_assessments": "assessment_id",
        "population_assessments": "population_assessment_id",
        "population_timeseries": "timeseries_id",
        "habitat_assessments": "habitat_assessment_id",
        "threat_assessments": "threat_id",
        "conservation_status": "conservation_status_id",
        "conservation_assessments": "conservation_assessment_id",
        "extinction_risk_assessments": "extinction_risk_assessment_id",
        "analysis_results": "analysis_id",
    }

    def __init__(self) -> None:
        self._samples: Dict[str, Dict[str, Any]] = {}
        self._stage_results: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._predictions: Dict[str, Dict[str, Any]] = {}
        # collection -> {record_id: record}, insertion ordered
        self._collections: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def save_sample(self, sample_id: str, sample_data: Dict[str, Any]) -> None:
        self._samples[sample_id] = sample_data

    def get_sample(self, sample_id: str) -> Optional[Dict[str, Any]]:
        return self._samples.get(sample_id)

    def update_sample_status(self, sample_id: str, status: str) -> None:
        if sample_id in self._samples:
            self._samples[sample_id]["status"] = status

    def save_stage_result(self, sample_id: str, stage: str, data: Dict[str, Any]) -> None:
        self._stage_results.setdefault(sample_id, {})[stage] = data

    def get_stage_result(self, sample_id: str, stage: str) -> Optional[Dict[str, Any]]:
        return self._stage_results.get(sample_id, {}).get(stage)

    def save_prediction(self, sample_id: str, prediction: Dict[str, Any]) -> None:
        self._predictions[sample_id] = prediction

    def get_prediction(self, sample_id: str) -> Optional[Dict[str, Any]]:
        return self._predictions.get(sample_id)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._predictions.values())

    def list_samples(self) -> List[str]:
        return list(self._samples.keys())

    # ------------------------------------------------------------------
    # Reference / seed collections
    # ------------------------------------------------------------------

    def _key_field(self, collection: str) -> str:
        return self.PRIMARY_KEYS.get(collection, "id")

    def save_records(self, collection: str, records: List[Dict[str, Any]]) -> None:
        key = self._key_field(collection)
        self._collections[collection] = {
            rec[key]: rec for rec in records if key in rec
        }

    def upsert_record(self, collection: str, record: Dict[str, Any]) -> None:
        key = self._key_field(collection)
        if key not in record:
            raise KeyError(f"Record for '{collection}' is missing primary key '{key}'")
        self._collections.setdefault(collection, {})[record[key]] = record

    def get_record(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        return self._collections.get(collection, {}).get(record_id)

    def list_records(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        rows = list(self._collections.get(collection, {}).values())
        if filters:
            rows = [r for r in rows if self._matches(r, filters)]
        return rows[:limit] if limit is not None else rows

    @staticmethod
    def _matches(record: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for field, expected in filters.items():
            actual = record.get(field)
            if isinstance(expected, (list, tuple, set)):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True

    def count_records(self, collection: str) -> int:
        return len(self._collections.get(collection, {}))

    def list_collections(self) -> List[str]:
        return sorted(self._collections.keys())

    # -- named accessors -------------------------------------------------

    def save_organism(self, organism: Dict[str, Any]) -> None:
        self.upsert_record("organisms", organism)

    def get_organism(self, organism_id: str) -> Optional[Dict[str, Any]]:
        return self.get_record("organisms", organism_id)

    def save_analysis(self, analysis: Dict[str, Any]) -> None:
        self.upsert_record("analysis_results", analysis)

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        return self.get_record("analysis_results", analysis_id)

    def save_assessment(self, assessment: Dict[str, Any]) -> None:
        self.upsert_record("biodiversity_assessments", assessment)

    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        return self.get_record("biodiversity_assessments", assessment_id)
