"""Validation rules for the Gaia seed dataset.

Shared by validate_seed_data.py (standalone check) and seed_database.py
(pre-load gate), so data can never be loaded without passing the same
checks that CI would run.

Errors block loading. Warnings are reported but do not.
"""

from typing import Any, Dict, List, Tuple

Dataset = Dict[str, List[Dict[str, Any]]]

# collection -> primary key field
PRIMARY_KEYS = {
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

# (collection, field, target collection) — field may be missing/None only
# where explicitly allowed in OPTIONAL_REFS.
FOREIGN_KEYS = [
    ("biomes", "biosphere_id", "biospheres"),
    ("terrains", "parent_biome_id", "biomes"),
    ("ecosystems", "biome_id", "biomes"),
    ("ecosystems", "terrain_id", "terrains"),
    ("ecosystems", "biosphere_id", "biospheres"),
    ("locations", "terrain_id", "terrains"),
    ("locations", "ecosystem_id", "ecosystems"),
    ("sampling_sites", "location_id", "locations"),
    ("sampling_sites", "terrain_id", "terrains"),
    ("sampling_sites", "ecosystem_id", "ecosystems"),
    ("environmental_conditions", "site_id", "sampling_sites"),
    ("samples", "site_id", "sampling_sites"),
    ("samples", "environmental_condition_id", "environmental_conditions"),
    ("dna_sequences", "sample_id", "samples"),
    ("organisms", "taxonomy_id", "taxonomy"),
    ("classifications", "organism_id", "organisms"),
    ("classifications", "terrain_id", "terrains"),
    ("classifications", "ecosystem_id", "ecosystems"),
    ("classifications", "biosphere_id", "biospheres"),
    ("identifications", "sequence_id", "dna_sequences"),
    ("identifications", "sample_id", "samples"),
    ("identifications", "predicted_organism_id", "organisms"),
    ("identifications", "predicted_taxonomy_id", "taxonomy"),
    ("identifications", "analysis_id", "analysis_results"),
    ("biodiversity_metrics", "sample_id", "samples"),
    ("biodiversity_metrics", "site_id", "sampling_sites"),
    ("biodiversity_assessments", "sample_id", "samples"),
    ("biodiversity_assessments", "biodiversity_metric_id", "biodiversity_metrics"),
    ("population_assessments", "organism_id", "organisms"),
    ("population_timeseries", "organism_id", "organisms"),
    ("habitat_assessments", "organism_id", "organisms"),
    ("habitat_assessments", "ecosystem_id", "ecosystems"),
    ("threat_assessments", "organism_id", "organisms"),
    ("threat_assessments", "ecosystem_id", "ecosystems"),
    ("conservation_status", "organism_id", "organisms"),
    ("conservation_assessments", "organism_id", "organisms"),
    ("conservation_assessments", "conservation_status_id", "conservation_status"),
    ("extinction_risk_assessments", "organism_id", "organisms"),
    ("analysis_results", "sample_id", "samples"),
    ("analysis_results", "biodiversity_metric_id", "biodiversity_metrics"),
]

TAXONOMIC_RANKS = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]
VALID_KINGDOMS = {"Animalia", "Plantae", "Fungi", "Bacteria", "Archaea", "Protista"}
VALID_TRENDS = {"Increasing", "Stable", "Declining", "Rapidly Declining", "Fluctuating", "Unknown"}
VALID_HABITAT_TRENDS = {"Improving", "Stable", "Declining", "Rapidly Declining", "Unknown"}
VALID_SEVERITIES = {"Low", "Moderate", "High", "Critical"}
VALID_ASSESSMENT_SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_CONSERVATION = {
    "Least Concern", "Near Threatened", "Vulnerable", "Endangered",
    "Critically Endangered", "Extinct in the Wild", "Extinct",
    "Data Deficient", "Not Evaluated", "Unknown",
}
VALID_FRAGMENTATION = {"None", "Low", "Moderate", "High", "Severe", "Unknown"}
VALID_CONFIDENCE_LEVELS = {"Very High", "High", "Medium", "Low", "Unknown"}


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def _pct(v) -> bool:
    return v is None or (isinstance(v, (int, float)) and 0 <= v <= 100)


def _unit(v) -> bool:
    return v is None or (isinstance(v, (int, float)) and 0 <= v <= 1)


def validate(dataset: Dataset) -> Report:
    r = Report()
    _check_duplicates(dataset, r)
    index = {
        coll: {rec[PRIMARY_KEYS[coll]] for rec in rows}
        for coll, rows in dataset.items()
        if coll in PRIMARY_KEYS
    }
    _check_references(dataset, index, r)
    _check_synthetic_flags(dataset, r)
    _check_taxonomy(dataset, r)
    _check_confidence(dataset, r)
    _check_biodiversity(dataset, r)
    _check_population(dataset, r)
    _check_habitat(dataset, r)
    _check_threats(dataset, r)
    _check_conservation(dataset, r)
    _check_risk(dataset, r)
    _check_coordinates(dataset, r)
    _check_sequences(dataset, r)
    return r


def _check_duplicates(ds: Dataset, r: Report) -> None:
    for coll, rows in ds.items():
        pk = PRIMARY_KEYS.get(coll)
        if not pk:
            continue
        seen = set()
        for rec in rows:
            if pk not in rec:
                r.error(f"{coll}: record missing primary key '{pk}'")
                continue
            if rec[pk] in seen:
                r.error(f"{coll}: duplicate id '{rec[pk]}'")
            seen.add(rec[pk])


def _check_references(ds: Dataset, index: Dict[str, set], r: Report) -> None:
    for coll, field, target in FOREIGN_KEYS:
        for rec in ds.get(coll, []):
            value = rec.get(field)
            if value is None:
                r.error(f"{coll}[{rec.get(PRIMARY_KEYS[coll])}]: '{field}' is null "
                        f"but must reference {target}")
                continue
            if value not in index.get(target, set()):
                r.error(f"{coll}[{rec.get(PRIMARY_KEYS[coll])}]: '{field}'='{value}' "
                        f"not found in {target}")


def _check_synthetic_flags(ds: Dataset, r: Report) -> None:
    for coll, rows in ds.items():
        if coll not in PRIMARY_KEYS:
            continue
        for rec in rows:
            rid = rec.get(PRIMARY_KEYS[coll])
            if coll == "analysis_results":
                if not rec.get("metadata", {}).get("is_synthetic"):
                    r.error(f"analysis_results[{rid}]: metadata.is_synthetic must be true")
                continue
            if rec.get("is_synthetic") is not True:
                r.error(f"{coll}[{rid}]: missing 'is_synthetic': true")
    for rec in ds.get("dna_sequences", []):
        if rec.get("is_mock") is not True:
            r.error(f"dna_sequences[{rec.get('sequence_id')}]: missing 'is_mock': true")
    for rec in ds.get("identifications", []):
        if rec.get("is_mock_prediction") is not True:
            r.error(f"identifications[{rec.get('identification_id')}]: "
                    f"missing 'is_mock_prediction': true")


def _check_taxonomy(ds: Dataset, r: Report) -> None:
    for rec in ds.get("taxonomy", []):
        tid = rec.get("taxonomy_id")
        for rank in TAXONOMIC_RANKS:
            if not rec.get(rank):
                r.error(f"taxonomy[{tid}]: missing rank '{rank}'")
        if rec.get("kingdom") not in VALID_KINGDOMS:
            r.error(f"taxonomy[{tid}]: invalid kingdom '{rec.get('kingdom')}'")
        species, genus = rec.get("species", ""), rec.get("genus", "")
        if species and genus and not species.startswith(genus):
            r.warn(f"taxonomy[{tid}]: species '{species}' does not begin with genus '{genus}'")
    for rec in ds.get("organisms", []):
        if rec.get("kingdom") not in VALID_KINGDOMS:
            r.error(f"organisms[{rec.get('organism_id')}]: invalid kingdom")


def _check_confidence(ds: Dataset, r: Report) -> None:
    for rec in ds.get("identifications", []):
        rid = rec.get("identification_id")
        if not _unit(rec.get("confidence_score")):
            r.error(f"identifications[{rid}]: confidence_score outside 0-1")
        if rec.get("confidence_level") not in VALID_CONFIDENCE_LEVELS:
            r.error(f"identifications[{rid}]: invalid confidence_level")
    for rec in ds.get("biodiversity_assessments", []):
        if not _unit(rec.get("confidence")):
            r.error(f"biodiversity_assessments[{rec.get('assessment_id')}]: confidence outside 0-1")
        if rec.get("severity") not in VALID_ASSESSMENT_SEVERITIES:
            r.error(f"biodiversity_assessments[{rec.get('assessment_id')}]: invalid severity")


def _check_biodiversity(ds: Dataset, r: Report) -> None:
    for rec in ds.get("biodiversity_metrics", []):
        mid = rec.get("biodiversity_metric_id")
        if rec.get("species_richness", 0) < 0:
            r.error(f"biodiversity_metrics[{mid}]: negative species_richness")
        if not _unit(rec.get("simpson_index")):
            r.error(f"biodiversity_metrics[{mid}]: simpson_index outside 0-1")
        if not _unit(rec.get("pielou_evenness")):
            r.error(f"biodiversity_metrics[{mid}]: pielou_evenness outside 0-1")
        if (rec.get("shannon_index") or 0) < 0:
            r.error(f"biodiversity_metrics[{mid}]: negative shannon_index")
        if rec.get("abundance_interpretation") != "Relative molecular signal":
            r.error(f"biodiversity_metrics[{mid}]: abundance_interpretation must be "
                    f"'Relative molecular signal' (eDNA reads are not organism counts)")


def _check_population(ds: Dataset, r: Report) -> None:
    for rec in ds.get("population_assessments", []):
        pid = rec.get("population_assessment_id")
        if rec.get("population_trend") not in VALID_TRENDS:
            r.error(f"population_assessments[{pid}]: invalid population_trend")
        for field in ("estimated_population", "estimated_mature_individuals",
                      "population_min", "population_max"):
            v = rec.get(field)
            if v is not None and v < 0:
                r.error(f"population_assessments[{pid}]: negative {field}")
        if not _pct(rec.get("population_decline_percent")):
            r.error(f"population_assessments[{pid}]: population_decline_percent outside 0-100")
        if not _unit(rec.get("population_confidence")):
            r.error(f"population_assessments[{pid}]: population_confidence outside 0-1")
        lo, hi = rec.get("population_min"), rec.get("population_max")
        if lo is not None and hi is not None and lo > hi:
            r.error(f"population_assessments[{pid}]: population_min exceeds population_max")
        rng = rec.get("geographic_range") or {}
        if rng.get("range_fragmentation") not in VALID_FRAGMENTATION:
            r.error(f"population_assessments[{pid}]: invalid range_fragmentation")
        if not _pct(rng.get("range_reduction_percent")):
            r.error(f"population_assessments[{pid}]: range_reduction_percent outside 0-100")
        for field in ("extent_of_occurrence_km2", "area_of_occupancy_km2"):
            v = rng.get(field)
            if v is not None and v < 0:
                r.error(f"population_assessments[{pid}]: negative {field}")
        if rec.get("abundance_interpretation") == "Relative molecular signal" and \
                rec.get("estimated_population") is not None:
            r.error(f"population_assessments[{pid}]: record claims relative molecular signal "
                    f"but also asserts a population estimate")

    for rec in ds.get("population_timeseries", []):
        tid = rec.get("timeseries_id")
        if not (1900 <= rec.get("year", 0) <= 2100):
            r.error(f"population_timeseries[{tid}]: implausible year")
        for field in ("estimated_population", "estimated_mature_individuals",
                      "habitat_area_km2", "observed_detections"):
            v = rec.get(field)
            if v is not None and v < 0:
                r.error(f"population_timeseries[{tid}]: negative {field}")


def _check_habitat(ds: Dataset, r: Report) -> None:
    for rec in ds.get("habitat_assessments", []):
        hid = rec.get("habitat_assessment_id")
        for field in ("historical_habitat_area_km2", "current_habitat_area_km2"):
            v = rec.get(field)
            if v is not None and v < 0:
                r.error(f"habitat_assessments[{hid}]: negative {field}")
        if not _pct(rec.get("habitat_loss_percent")):
            r.error(f"habitat_assessments[{hid}]: habitat_loss_percent outside 0-100")
        if rec.get("habitat_trend") not in VALID_HABITAT_TRENDS:
            r.error(f"habitat_assessments[{hid}]: invalid habitat_trend")
        if rec.get("fragmentation") not in VALID_FRAGMENTATION:
            r.error(f"habitat_assessments[{hid}]: invalid fragmentation")
        hist, cur = rec.get("historical_habitat_area_km2"), rec.get("current_habitat_area_km2")
        if hist is not None and cur is not None and cur > hist:
            r.warn(f"habitat_assessments[{hid}]: current habitat exceeds historical")


def _check_threats(ds: Dataset, r: Report) -> None:
    for rec in ds.get("threat_assessments", []):
        tid = rec.get("threat_id")
        if rec.get("severity") not in VALID_SEVERITIES:
            r.error(f"threat_assessments[{tid}]: invalid severity '{rec.get('severity')}'")
        if not _pct(rec.get("scope_percent")):
            r.error(f"threat_assessments[{tid}]: scope_percent outside 0-100")
        if not _pct(rec.get("affected_population_percent")):
            r.error(f"threat_assessments[{tid}]: affected_population_percent outside 0-100")
        if not _unit(rec.get("impact_confidence")):
            r.error(f"threat_assessments[{tid}]: impact_confidence outside 0-1")


def _check_conservation(ds: Dataset, r: Report) -> None:
    for rec in ds.get("conservation_status", []):
        cid = rec.get("conservation_status_id")
        status = rec.get("external_conservation_status")
        if status not in VALID_CONSERVATION:
            r.error(f"conservation_status[{cid}]: invalid status '{status}'")
        # Guard against fabricating official statuses (spec section 26).
        if status not in ("Unknown", "Not Evaluated", "Data Deficient") \
                and not rec.get("is_verified"):
            r.error(f"conservation_status[{cid}]: asserts '{status}' without verification. "
                    f"Unverified records must use Unknown / Not Evaluated / Data Deficient.")
        if rec.get("source_url") and "example" in str(rec["source_url"]):
            r.error(f"conservation_status[{cid}]: placeholder source_url invented")


def _check_risk(ds: Dataset, r: Report) -> None:
    for rec in ds.get("extinction_risk_assessments", []):
        eid = rec.get("extinction_risk_assessment_id")
        prob = rec.get("extinction_probability")
        if not _unit(prob):
            r.error(f"extinction_risk_assessments[{eid}]: extinction_probability outside 0-1")
        if not _unit(rec.get("extinction_probability_confidence")):
            r.error(f"extinction_risk_assessments[{eid}]: probability confidence outside 0-1")
        score = rec.get("gaia_risk_score")
        if score is not None and not (0 <= score <= 100):
            r.error(f"extinction_risk_assessments[{eid}]: gaia_risk_score outside 0-100")
        if not _unit(rec.get("risk_confidence")):
            r.error(f"extinction_risk_assessments[{eid}]: risk_confidence outside 0-1")
        if prob is not None and rec.get("extinction_probability_period_years") is None:
            r.error(f"extinction_risk_assessments[{eid}]: probability given without a period")
        if not rec.get("disclaimer"):
            r.error(f"extinction_risk_assessments[{eid}]: missing disclaimer")


def _check_coordinates(ds: Dataset, r: Report) -> None:
    for rec in ds.get("locations", []):
        lid = rec.get("location_id")
        lat, lon = rec.get("latitude"), rec.get("longitude")
        if lat is None or not (-90 <= lat <= 90):
            r.error(f"locations[{lid}]: latitude out of range")
        if lon is None or not (-180 <= lon <= 180):
            r.error(f"locations[{lid}]: longitude out of range")


def _check_sequences(ds: Dataset, r: Report) -> None:
    for rec in ds.get("dna_sequences", []):
        sid = rec.get("sequence_id")
        seq = rec.get("sequence", "")
        if set(seq) - set("ACGTN"):
            r.error(f"dna_sequences[{sid}]: sequence contains non-DNA characters")
        if len(seq) != rec.get("sequence_length"):
            r.error(f"dna_sequences[{sid}]: sequence_length does not match sequence")
        if not _unit(rec.get("quality_score")):
            r.error(f"dna_sequences[{sid}]: quality_score outside 0-1")
        if not _unit(rec.get("gc_content")):
            r.error(f"dna_sequences[{sid}]: gc_content outside 0-1")


def summarize(ds: Dataset) -> List[Tuple[str, int]]:
    return sorted((coll, len(rows)) for coll, rows in ds.items())
