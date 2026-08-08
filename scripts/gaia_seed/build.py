"""Deterministic builder for the Gaia synthetic seed database.

Everything is generated from a fixed RNG seed so the dataset is
reproducible: regenerating produces byte-identical output unless the
reference tables or this builder change.

Referential integrity is guaranteed *by construction* — every foreign key
is taken from an already-built collection rather than being written by
hand and hoped to match.

PROVENANCE CONTRACT
-------------------
Every record carries the flags that let a consumer tell synthetic data
apart from real data:

    is_synthetic        record is generated, not observed
    is_mock             sequence is generated, not sequenced
    is_mock_prediction  identification came from a placeholder, not a model
    source_type         Synthetic | Calculated | ML Model | External Database
    source              free-text provenance

Values described as "Calculated" really are computed from other records in
this dataset (e.g. Shannon index from the generated identifications). They
are still synthetic in the sense that their *inputs* are synthetic.
"""

import math
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List

from . import MODEL_VERSION, SEED_VERSION, SYNTHETIC_SOURCE
from .reference import (
    BIOMES,
    BIOSPHERES,
    ECOSYSTEMS,
    KINGDOM_MARKERS,
    LOCATIONS,
    ORGANISM_SPECS,
    SAMPLING_SITES,
    SCENARIOS,
    TERRAINS,
    THREAT_CATALOGUE,
    UNLINKED_TAXA,
)

RNG_SEED = 20260808
ASSESSMENT_DATE = "2026-08-08"
TIMESERIES_YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

SYNTH = {"is_synthetic": True, "source": SYNTHETIC_SOURCE, "source_type": "Synthetic"}


def _calc(note: str) -> Dict[str, Any]:
    """Provenance block for a value genuinely computed from seed records."""
    return {"is_synthetic": True, "source": note, "source_type": "Calculated"}


def _sid(prefix: str, n: int) -> str:
    return f"{prefix}-{n:03d}"


class SeedBuilder:
    def __init__(self, seed: int = RNG_SEED) -> None:
        self.rng = random.Random(seed)
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        # scenario -> set of organism keys / site ids
        self.scn = {k: set(v) for k, v in SCENARIOS.items()}

    # -- helpers ---------------------------------------------------------
    def in_scn(self, name: str, key: str) -> bool:
        return key in self.scn.get(name, set())

    def pick(self, seq):
        return self.rng.choice(seq)

    def rnd(self, lo, hi, nd=2):
        return round(self.rng.uniform(lo, hi), nd)

    # =====================================================================
    # Environment spine
    # =====================================================================
    def build_environment(self) -> None:
        self.data["biospheres"] = [
            {
                "biosphere_id": bid,
                "name": name,
                "description": desc,
                "environment_type": env,
                **SYNTH,
            }
            for bid, name, desc, env in BIOSPHERES
        ]

        self.data["biomes"] = [
            {
                "biome_id": mid,
                "biosphere_id": bios,
                "name": name,
                "description": desc,
                "climate_type": climate,
                "typical_temperature_range_c": temp,
                "typical_precipitation_range_mm": precip,
                **SYNTH,
            }
            for mid, bios, name, desc, climate, temp, precip in BIOMES
        ]

        self.data["terrains"] = [
            {
                "terrain_id": tid,
                "name": name,
                "description": desc,
                "environment_type": env,
                "climate_type": climate,
                "typical_temperature_range_c": temp,
                "typical_humidity_range_pct": hum,
                "typical_altitude_range_m": alt,
                "typical_salinity_range_psu": sal,
                "parent_biome_id": biome,
                **SYNTH,
            }
            for tid, name, desc, env, climate, temp, hum, alt, sal, biome in TERRAINS
        ]

        self.data["ecosystems"] = [
            {
                "ecosystem_id": eid,
                "biome_id": biome,
                "terrain_id": terrain,
                "biosphere_id": bios,
                "name": name,
                "description": desc,
                "ecosystem_type": etype,
                "climate": climate,
                "typical_conditions": self._typical_conditions(etype),
                **SYNTH,
            }
            for eid, biome, terrain, bios, name, desc, etype, climate in ECOSYSTEMS
        ]

        self.data["locations"] = [
            {
                "location_id": lid,
                "country": country,
                "state": state,
                "region": region,
                "latitude": lat,
                "longitude": lon,
                "elevation_m": elev,
                "climate_zone": czone,
                "terrain_id": terrain,
                "ecosystem_id": eco,
                "note": (
                    "Synthetic sampling region. Coordinates are a plausible "
                    "regional centroid, not a recorded sampling campaign."
                ),
                **SYNTH,
            }
            for lid, country, state, region, lat, lon, elev, czone, terrain, eco in LOCATIONS
        ]

        self.data["sampling_sites"] = [
            {
                "site_id": sid,
                "location_id": loc,
                "terrain_id": terrain,
                "ecosystem_id": eco,
                "name": name,
                "sampling_method": method,
                "sample_medium": medium,
                "water_or_soil_type": wst,
                "depth_m": depth,
                "season": season,
                "synthetic_flag": True,
                **SYNTH,
            }
            for sid, loc, terrain, eco, name, method, medium, wst, depth, season in SAMPLING_SITES
        ]

    @staticmethod
    def _typical_conditions(etype: str) -> Dict[str, str]:
        return {
            "Terrestrial": {"moisture": "Soil-moisture limited", "light": "Canopy dependent"},
            "Freshwater": {"flow": "Variable", "oxygen": "Generally well oxygenated"},
            "Marine": {"salinity": "Stable marine", "pressure": "Depth dependent"},
            "Transitional": {"salinity": "Strongly variable", "tidal": "Tidally driven"},
            "Anthropogenic": {"disturbance": "Frequent", "nutrients": "Often elevated"},
        }.get(etype, {"regime": "Variable"})

    # =====================================================================
    # Taxonomy + organisms
    # =====================================================================
    def build_taxonomy_and_organisms(self) -> None:
        taxonomy: List[Dict[str, Any]] = []
        organisms: List[Dict[str, Any]] = []
        self.tax_by_key: Dict[str, str] = {}
        self.org_by_key: Dict[str, Dict[str, Any]] = {}

        for i, spec in enumerate(ORGANISM_SPECS, start=1):
            (key, kingdom, phylum, klass, order, family, genus, species, common,
             habitat, pref_eco, trophic, functional, native, sensitivity) = spec

            tax_id = _sid("TAX", i)
            taxonomy.append({
                "taxonomy_id": tax_id,
                "kingdom": kingdom,
                "phylum": phylum,
                "class": klass,
                "order": order,
                "family": family,
                "genus": genus,
                "species": species,
                "common_name": common,
                "taxonomic_rank": "Species",
                "name_source": "Real scientific name; associated observations are synthetic.",
                **SYNTH,
            })
            self.tax_by_key[key] = tax_id

            org_id = _sid("ORG", i)
            org = {
                "organism_id": org_id,
                "taxonomy_id": tax_id,
                "scientific_name": species,
                "common_name": common,
                "kingdom": kingdom,
                "habitat_type": habitat,
                "preferred_ecosystem": pref_eco,
                "trophic_level": trophic,
                "functional_group": functional,
                "native_status": native,
                "environmental_sensitivity": sensitivity,
                # Never fabricate an official status. Section 26.
                "conservation_status_reference": "Unknown",
                **SYNTH,
            }
            organisms.append(org)
            self.org_by_key[key] = org

        # Species-level taxonomy present in the reference set but not yet
        # characterised as a Gaia organism record.
        for j, (kingdom, phylum, klass, order, family, genus, species, common) in enumerate(
            UNLINKED_TAXA, start=len(ORGANISM_SPECS) + 1
        ):
            taxonomy.append({
                "taxonomy_id": _sid("TAX", j),
                "kingdom": kingdom,
                "phylum": phylum,
                "class": klass,
                "order": order,
                "family": family,
                "genus": genus,
                "species": species,
                "common_name": common,
                "taxonomic_rank": "Species",
                "name_source": "Real scientific name; no organism record assessed yet.",
                **SYNTH,
            })

        self.data["taxonomy"] = taxonomy
        self.data["organisms"] = organisms

    def build_classifications(self) -> None:
        """Multi-dimensional classification (spec section 16)."""
        rows = []
        eco_by_id = {e["ecosystem_id"]: e for e in self.data["ecosystems"]}
        for i, (key, org) in enumerate(self.org_by_key.items(), start=1):
            eco = eco_by_id[org["preferred_ecosystem"]]
            rows.append({
                "classification_id": _sid("CLS", i),
                "organism_id": org["organism_id"],
                "taxonomic_classification": {
                    "taxonomy_id": org["taxonomy_id"],
                    "scientific_name": org["scientific_name"],
                },
                "biological_kingdom": org["kingdom"],
                "habitat_classification": org["habitat_type"],
                "terrain_id": eco["terrain_id"],
                "ecosystem_id": eco["ecosystem_id"],
                "biosphere_id": eco["biosphere_id"],
                "trophic_level": org["trophic_level"],
                "functional_group": org["functional_group"],
                "conservation_category": "Unknown",
                "native_status": org["native_status"],
                "environmental_sensitivity": org["environmental_sensitivity"],
                "detection_confidence": (
                    "Low" if self.in_scn("S10_low_detection_confidence", key) else
                    self.pick(["Medium", "High", "Very High"])
                ),
                "potential_invasive": self.in_scn("S16_potential_invasive", key),
                **SYNTH,
            })
        self.data["classifications"] = rows

    # =====================================================================
    # Environmental conditions + samples + sequences
    # =====================================================================
    def build_environmental_conditions(self) -> None:
        """Only populate parameters that are meaningful for the medium.

        Irrelevant parameters stay null rather than being filled with noise
        (spec section 11).
        """
        rows = []
        for i, site in enumerate(self.data["sampling_sites"], start=1):
            medium = site["sample_medium"]
            terrain = next(t for t in self.data["terrains"] if t["terrain_id"] == site["terrain_id"])
            env = terrain["environment_type"]

            cond = {
                "environmental_condition_id": _sid("ENV", i),
                "site_id": site["site_id"],
                "temperature_c": None, "ph": None, "salinity_psu": None,
                "dissolved_oxygen_mg_l": None, "turbidity_ntu": None,
                "humidity_pct": None, "soil_moisture_pct": None,
                "water_depth_m": None, "elevation_m": None,
                "conductivity_us_cm": None, "nutrient_level": None,
                "measured_parameters": [],
            }

            def setp(field, value):
                cond[field] = value
                cond["measured_parameters"].append(field)

            tlo, thi = terrain["typical_temperature_range_c"]
            setp("temperature_c", self.rnd(tlo, thi, 1))

            if medium in ("Marine water", "Brackish water"):
                slo, shi = terrain["typical_salinity_range_psu"] or [30, 35]
                setp("salinity_psu", self.rnd(slo, shi, 1))
                setp("dissolved_oxygen_mg_l", self.rnd(4.5, 8.0, 2))
                setp("ph", self.rnd(7.8, 8.3, 2))
                setp("water_depth_m", site["depth_m"])
                setp("turbidity_ntu", self.rnd(0.5, 12.0, 1))
            elif medium == "Freshwater":
                setp("ph", self.rnd(6.2, 8.4, 2))
                setp("dissolved_oxygen_mg_l", self.rnd(5.0, 11.0, 2))
                setp("turbidity_ntu", self.rnd(1.0, 60.0, 1))
                setp("conductivity_us_cm", self.rnd(40, 900, 0))
                setp("water_depth_m", site["depth_m"])
            elif medium == "Soil":
                setp("soil_moisture_pct", self.rnd(2, 45, 1))
                setp("ph", self.rnd(4.8, 8.6, 2))
                if terrain["typical_humidity_range_pct"]:
                    hlo, hhi = terrain["typical_humidity_range_pct"]
                    setp("humidity_pct", self.rnd(hlo, hhi, 1))
            elif medium == "Sediment":
                setp("ph", self.rnd(6.5, 8.2, 2))
                setp("water_depth_m", site["depth_m"])
                if terrain["typical_salinity_range_psu"]:
                    slo, shi = terrain["typical_salinity_range_psu"]
                    setp("salinity_psu", self.rnd(slo, shi, 1))
                setp("nutrient_level", self.pick(["Low", "Moderate", "High"]))
            elif medium == "Biofilm":
                setp("ph", self.rnd(6.5, 8.0, 2))
                setp("dissolved_oxygen_mg_l", self.rnd(6.0, 10.5, 2))

            if env == "Terrestrial" and terrain["typical_humidity_range_pct"]:
                if cond["humidity_pct"] is None:
                    hlo, hhi = terrain["typical_humidity_range_pct"]
                    setp("humidity_pct", self.rnd(hlo, hhi, 1))

            loc = next(l for l in self.data["locations"] if l["location_id"] == site["location_id"])
            setp("elevation_m", loc["elevation_m"])
            if cond["nutrient_level"] is None:
                setp("nutrient_level", self.pick(["Low", "Moderate", "High"]))

            cond.update(SYNTH)
            rows.append(cond)
        self.data["environmental_conditions"] = rows

    def build_samples(self) -> None:
        """~34 samples spread across all sites, some sites sampled twice."""
        env_by_site = {c["site_id"]: c for c in self.data["environmental_conditions"]}
        sites = self.data["sampling_sites"]
        plan = list(sites) + [sites[i] for i in (0, 6, 8, 12, 13, 16, 18, 20, 7, 21, 3, 9)]

        rows = []
        for i, site in enumerate(plan, start=1):
            eco = next(e for e in self.data["ecosystems"] if e["ecosystem_id"] == site["ecosystem_id"])
            low_quality = self.in_scn("S13_low_biodiversity", site["site_id"]) and i % 3 == 0

            if eco["ecosystem_type"] in ("Marine", "Transitional"):
                marker = self.pick(["COI", "18S", "16S", "12S"])
            elif site["sample_medium"] in ("Soil", "Sediment"):
                marker = self.pick(["16S", "ITS", "18S"])
            else:
                marker = self.pick(["COI", "16S", "18S", "rbcL"])

            seq_count = self.rng.randint(400, 1200) if not low_quality else self.rng.randint(35, 160)
            status = "Low Quality" if low_quality else self.pick(
                ["Analyzed", "Analyzed", "Analyzed", "Processed", "Processing", "Collected"]
            )
            rows.append({
                "sample_id": _sid("SMP", i),
                "site_id": site["site_id"],
                "sample_type": site["sample_medium"],
                "collection_date": f"202{self.rng.randint(4, 6)}-{self.rng.randint(1, 12):02d}-{self.rng.randint(1, 28):02d}",
                "season": site["season"],
                "marker_region": marker,
                "sequence_count": seq_count,
                "status": status,
                "environmental_condition_id": env_by_site[site["site_id"]]["environmental_condition_id"],
                **SYNTH,
            })
        self.data["samples"] = rows

    def _mock_sequence(self, length: int, gc_target: float) -> str:
        """Generate a clearly-labelled mock nucleotide string.

        This is random text over the DNA alphabet with a controlled GC
        fraction. It is NOT a barcode sequence and carries no biological
        signal — see is_mock / sequence_source on every record.
        """
        gc, at = "GC", "AT"
        return "".join(
            self.pick(gc) if self.rng.random() < gc_target else self.pick(at)
            for _ in range(length)
        )

    def build_sequences(self) -> None:
        """2-3 mock sequences per analysable sample."""
        rows = []
        n = 0
        self.seqs_by_sample = defaultdict(list)
        for sample in self.data["samples"]:
            if sample["status"] in ("Collected", "Processing"):
                continue
            count = 2 if sample["status"] == "Low Quality" else self.rng.randint(2, 4)
            for _ in range(count):
                n += 1
                low_q = sample["status"] == "Low Quality"
                length = self.rng.randint(90, 140) if low_q else self.rng.randint(150, 420)
                gc = self.rnd(0.34, 0.66, 3)
                quality = self.rnd(0.42, 0.68, 3) if low_q else self.rnd(0.78, 0.99, 3)
                rec = {
                    "sequence_id": _sid("SEQ", n),
                    "sample_id": sample["sample_id"],
                    "sequence": self._mock_sequence(length, gc),
                    "sequence_length": length,
                    "marker_region": sample["marker_region"],
                    "quality_score": quality,
                    "gc_content": gc,
                    "sequence_status": "Low Quality" if low_q else "Valid",
                    "is_mock": True,
                    "sequence_source": (
                        "Synthetic demonstration sequence - randomly generated over the "
                        "DNA alphabet. Not a real barcode and carries no biological signal."
                    ),
                    "is_synthetic": True,
                    "source_type": "Synthetic",
                }
                rows.append(rec)
                self.seqs_by_sample[sample["sample_id"]].append(rec)
        self.data["dna_sequences"] = rows

    # =====================================================================
    # Identification
    # =====================================================================
    def build_identifications(self) -> None:
        """Mock identifications linking sequences to organisms.

        Candidate organisms are restricted to those whose preferred
        ecosystem matches the sample's ecosystem, so the resulting dataset
        is ecologically coherent rather than uniformly random.
        """
        site_by_id = {s["site_id"]: s for s in self.data["sampling_sites"]}
        sample_by_id = {s["sample_id"]: s for s in self.data["samples"]}
        eco_by_id = {e["ecosystem_id"]: e for e in self.data["ecosystems"]}

        by_eco = defaultdict(list)
        for key, org in self.org_by_key.items():
            by_eco[org["preferred_ecosystem"]].append(key)
        by_type = defaultdict(list)
        for key, org in self.org_by_key.items():
            by_type[eco_by_id[org["preferred_ecosystem"]]["ecosystem_type"]].append(key)

        rows = []
        n = 0
        self.ids_by_sample = defaultdict(list)

        for sample in self.data["samples"]:
            seqs = self.seqs_by_sample.get(sample["sample_id"], [])
            if not seqs:
                continue
            site = site_by_id[sample["site_id"]]
            eco = eco_by_id[site["ecosystem_id"]]

            candidates = list(by_eco.get(eco["ecosystem_id"], []))
            candidates += by_type.get(eco["ecosystem_type"], [])
            if self.in_scn("S15_high_microbial_diversity", site["site_id"]):
                candidates += [k for k, o in self.org_by_key.items()
                               if o["kingdom"] in ("Bacteria", "Archaea", "Protista")] * 3
            if self.in_scn("S14_high_biodiversity", site["site_id"]):
                candidates += list(self.org_by_key.keys())
            if not candidates:
                candidates = list(self.org_by_key.keys())

            # Low-biodiversity sites draw from a deliberately narrow pool.
            if self.in_scn("S13_low_biodiversity", site["site_id"]):
                candidates = candidates[:3] or candidates

            for seq in seqs:
                n += 1
                key = self.pick(candidates)
                org = self.org_by_key[key]

                if seq["sequence_status"] == "Low Quality":
                    score = self.rnd(0.18, 0.44, 3)
                elif self.in_scn("S10_low_detection_confidence", key):
                    score = self.rnd(0.22, 0.48, 3)
                else:
                    score = self.rnd(0.55, 0.98, 3)

                # Rank degrades gracefully with confidence rather than
                # always asserting species level (spec section 45).
                if score >= 0.85:
                    rank = "Species"
                elif score >= 0.7:
                    rank = "Genus"
                elif score >= 0.5:
                    rank = "Family"
                else:
                    rank = "Order"

                rows.append({
                    "identification_id": _sid("IDN", n),
                    "analysis_id": None,  # linked in build_analysis_results
                    "sequence_id": seq["sequence_id"],
                    "sample_id": sample["sample_id"],
                    "predicted_organism_id": org["organism_id"],
                    "predicted_taxonomy_id": org["taxonomy_id"],
                    "taxonomic_rank": rank,
                    "confidence_score": score,
                    "confidence_level": confidence_level(score),
                    "identification_method": "Prototype Classifier",
                    "model_version": MODEL_VERSION,
                    "is_mock_prediction": True,
                    "is_synthetic": True,
                    "source_type": "ML Model",
                    "source": "Placeholder classifier - not a trained model.",
                })
                self.ids_by_sample[sample["sample_id"]].append(rows[-1])
        self.data["identifications"] = rows

    # =====================================================================
    # Biodiversity
    # =====================================================================
    def build_biodiversity(self) -> None:
        """Diversity indices genuinely computed from the identifications."""
        metrics, assessments = [], []
        org_name = {o["organism_id"]: o["scientific_name"] for o in self.data["organisms"]}
        org_kingdom = {o["organism_id"]: o["kingdom"] for o in self.data["organisms"]}
        site_by_id = {s["site_id"]: s for s in self.data["sampling_sites"]}

        m = a = 0
        for sample in self.data["samples"]:
            ids = self.ids_by_sample.get(sample["sample_id"], [])
            if not ids:
                continue
            m += 1
            counts = Counter(i["predicted_organism_id"] for i in ids)
            total = sum(counts.values())
            richness = len(counts)

            shannon = -sum((c / total) * math.log(c / total) for c in counts.values())
            simpson = 1 - sum((c / total) ** 2 for c in counts.values())
            evenness = shannon / math.log(richness) if richness > 1 else (1.0 if richness == 1 else 0.0)
            rare = [oid for oid, c in counts.items() if c == 1]
            kingdoms = {org_kingdom[oid] for oid in counts}

            if richness >= 8:
                category = "Very High"
            elif richness >= 6:
                category = "High"
            elif richness >= 4:
                category = "Moderate"
            elif richness >= 2:
                category = "Low"
            else:
                category = "Very Low"

            metric_id = _sid("BDM", m)
            metrics.append({
                "biodiversity_metric_id": metric_id,
                "sample_id": sample["sample_id"],
                "site_id": sample["site_id"],
                "species_richness": richness,
                "observed_species_count": richness,
                "shannon_index": round(shannon, 4),
                "simpson_index": round(simpson, 4),
                "pielou_evenness": round(evenness, 4),
                "dominant_species": [org_name[oid] for oid, _ in counts.most_common(3)],
                "rare_species_count": len(rare),
                "unique_species_count": richness,
                "taxonomic_diversity": {
                    "kingdoms_represented": sorted(kingdoms),
                    "kingdom_count": len(kingdoms),
                },
                "biodiversity_category": category,
                "total_identifications": total,
                "abundance_interpretation": "Relative molecular signal",
                "abundance_caveat": (
                    "Counts are sequence-derived detections, not organism counts. "
                    "eDNA read abundance is not calibrated to population abundance."
                ),
                **_calc("Computed from synthetic identification records in this seed set."),
            })

            # --- ecological assessments ---
            site = site_by_id[sample["site_id"]]
            findings = []
            if category in ("Very High", "High"):
                findings.append(("High biodiversity", "INFO",
                                 f"{richness} distinct taxa detected across {len(kingdoms)} kingdoms."))
            elif category == "Moderate":
                findings.append(("Moderate biodiversity", "INFO",
                                 f"{richness} distinct taxa detected in this synthetic sample."))
            else:
                findings.append(("Low biodiversity", "MEDIUM",
                                 f"Only {richness} distinct taxa detected; may indicate stress or limited sampling."))
            if len(rare):
                findings.append(("Rare species detected", "LOW",
                                 f"{len(rare)} taxa appear exactly once in this sample."))
            if len(kingdoms & {"Bacteria", "Archaea", "Protista"}) >= 2:
                findings.append(("Significant microbial diversity", "INFO",
                                 "Multiple microbial kingdoms represented in the detections."))
            low_conf = [i for i in ids if i["confidence_score"] < 0.5]
            if low_conf:
                findings.append(("Low identification confidence", "MEDIUM",
                                 f"{len(low_conf)} of {len(ids)} identifications fall below 0.5 confidence."))
            invasive = [i for i in ids
                        if self.in_scn("S16_potential_invasive", self._key_for_org(i["predicted_organism_id"]))]
            if invasive:
                findings.append(("Potential invasive species", "HIGH",
                                 "One or more detections correspond to taxa flagged as potentially invasive."))
            if sample["status"] == "Low Quality":
                findings.append(("Environmental stress indicator", "MEDIUM",
                                 "Low sequence yield and quality for this synthetic sample."))

            for title, severity, desc in findings:
                a += 1
                assessments.append({
                    "assessment_id": _sid("BDA", a),
                    "sample_id": sample["sample_id"],
                    "site_id": sample["site_id"],
                    "biodiversity_metric_id": metric_id,
                    "category": "Ecological",
                    "severity": severity,
                    "title": title,
                    "description": desc,
                    "confidence": round(
                        sum(i["confidence_score"] for i in ids) / len(ids), 3
                    ),
                    "generated_by": f"Gaia prototype assessment rules {MODEL_VERSION}",
                    "is_mock": True,
                    "is_synthetic": True,
                    "source_type": "Calculated",
                    "source": "Derived from synthetic identifications via threshold rules.",
                })

        self.data["biodiversity_metrics"] = metrics
        self.data["biodiversity_assessments"] = assessments

    def _key_for_org(self, organism_id: str) -> str:
        for key, org in self.org_by_key.items():
            if org["organism_id"] == organism_id:
                return key
        return ""

    # =====================================================================
    # Population / habitat / threats / conservation / risk
    # =====================================================================
    def build_population(self) -> None:
        pops, series = [], []
        p = t = 0
        for key, org in self.org_by_key.items():
            p += 1
            micro = org["kingdom"] in ("Bacteria", "Archaea", "Protista")

            # S12 takes priority: a "very high extinction risk" demo needs
            # every contributing component elevated, not just one.
            if self.in_scn("S11_data_deficient", key):
                trend, decline, conf = "Unknown", None, 0.2
            elif self.in_scn("S12_very_high_extinction_risk", key):
                trend, decline, conf = "Rapidly Declining", self.rnd(62, 85, 1), self.rnd(0.65, 0.85, 2)
            elif self.in_scn("S03_rapidly_declining", key):
                trend, decline, conf = "Rapidly Declining", self.rnd(55, 82, 1), self.rnd(0.6, 0.8, 2)
            elif self.in_scn("S02_declining", key) or self.in_scn("S06_high_habitat_loss", key):
                trend, decline, conf = "Declining", self.rnd(28, 52, 1), self.rnd(0.55, 0.78, 2)
            elif self.in_scn("S01_healthy_stable", key):
                trend, decline, conf = "Stable", self.rnd(0, 6, 1), self.rnd(0.6, 0.85, 2)
            elif micro:
                trend, decline, conf = "Unknown", None, 0.15
            else:
                trend, decline, conf = self.pick(["Stable", "Fluctuating", "Declining"]), self.rnd(0, 25, 1), self.rnd(0.4, 0.7, 2)

            if micro or self.in_scn("S09_high_detection_low_population_data", key):
                est = est_mat = pmin = pmax = None
                method = "Not estimated - eDNA detection only"
                interp = "Relative molecular signal"
            elif self.in_scn("S04_small_population", key):
                est_mat = self.rng.randint(90, 850)
                est = int(est_mat * self.rnd(1.3, 1.8, 2))
                pmin, pmax = int(est * 0.7), int(est * 1.4)
                method = "Synthetic prototype estimate"
                interp = "Prototype population estimate (not field-derived)"
            else:
                est_mat = self.rng.randint(1200, 48000)
                est = int(est_mat * self.rnd(1.4, 2.2, 2))
                pmin, pmax = int(est * 0.65), int(est * 1.5)
                method = "Synthetic prototype estimate"
                interp = "Prototype population estimate (not field-derived)"

            gen_len = None if micro else self.rnd(1.5, 22.0, 1)
            pops.append({
                "population_assessment_id": _sid("POP", p),
                "organism_id": org["organism_id"],
                "estimated_population": est,
                "estimated_mature_individuals": est_mat,
                "population_min": pmin,
                "population_max": pmax,
                "population_estimation_method": method,
                "population_confidence": conf,
                "population_trend": trend,
                "population_change_percent": (-decline if decline else decline),
                "population_change_period_years": None if decline is None else 10,
                "population_change_basis": (
                    "Synthetic trend assigned for prototype demonstration."
                    if decline is not None else "Insufficient synthetic data to infer a trend."
                ),
                "trend_confidence": conf,
                "generation_length_years": gen_len,
                "generations_assessed": None if gen_len is None else round(min(3.0, 30.0 / gen_len), 1),
                "population_decline_percent": decline,
                "abundance_interpretation": interp,
                "abundance_caveat": (
                    "eDNA sequence read counts are NOT interpreted as organism counts. "
                    "No validated ecological calibration is applied in this prototype."
                ),
                "geographic_range": self._range_block(key, micro),
                **SYNTH,
            })

            # timeseries for non-microbial organisms
            if micro:
                continue
            base_pop = est_mat or 5000
            base_hab = self.rnd(400, 90000, 0)
            annual = (decline or 0) / 100.0 / len(TIMESERIES_YEARS)
            for yi, year in enumerate(TIMESERIES_YEARS):
                t += 1
                factor = max(0.05, 1 - annual * yi)
                series.append({
                    "timeseries_id": _sid("PTS", t),
                    "organism_id": org["organism_id"],
                    "year": year,
                    "estimated_population": int(base_pop * factor * self.rnd(0.95, 1.05, 3)),
                    "estimated_mature_individuals": int(base_pop * factor * 0.62),
                    "habitat_area_km2": round(base_hab * max(0.1, 1 - annual * yi * 0.8), 1),
                    "observed_detections": self.rng.randint(0, 40),
                    "threat_level": self.pick(["LOW", "MODERATE", "HIGH", "VERY_HIGH"]),
                    **SYNTH,
                })

        self.data["population_assessments"] = pops
        self.data["population_timeseries"] = series

    def _range_block(self, key: str, micro: bool) -> Dict[str, Any]:
        if micro:
            return {
                "extent_of_occurrence_km2": None,
                "area_of_occupancy_km2": None,
                "number_of_locations": None,
                "number_of_subpopulations": None,
                "range_trend": "Unknown",
                "range_reduction_percent": None,
                "range_fragmentation": "Unknown",
            }
        very_high_risk = self.in_scn("S12_very_high_extinction_risk", key)
        restricted = self.in_scn("S05_restricted_range", key) or very_high_risk
        frag = ("Severe" if (self.in_scn("S07_severe_fragmentation", key) or very_high_risk)
                else self.pick(["None", "Low", "Moderate", "High"]))
        eoo = self.rnd(120, 4200, 0) if restricted else self.rnd(8000, 900000, 0)
        return {
            "extent_of_occurrence_km2": eoo,
            "area_of_occupancy_km2": round(eoo * self.rnd(0.05, 0.35, 3), 1),
            "number_of_locations": self.rng.randint(1, 6) if restricted else self.rng.randint(6, 40),
            "number_of_subpopulations": self.rng.randint(1, 4) if restricted else self.rng.randint(4, 25),
            "range_trend": self.pick(["Declining", "Stable", "Declining", "Unknown"]),
            "range_reduction_percent": self.rnd(58, 80, 1) if very_high_risk else self.rnd(0, 65, 1),
            "range_fragmentation": frag,
        }

    def build_habitat(self) -> None:
        rows = []
        h = 0
        for key, org in self.org_by_key.items():
            if org["kingdom"] in ("Bacteria", "Archaea"):
                continue
            h += 1
            high_loss = self.in_scn("S06_high_habitat_loss", key)
            very_high_risk = self.in_scn("S12_very_high_extinction_risk", key)
            hist = self.rnd(500, 120000, 0)
            if very_high_risk:
                loss = self.rnd(62, 85, 1)
            elif high_loss:
                loss = self.rnd(42, 78, 1)
            else:
                loss = self.rnd(2, 38, 1)
            frag = ("Severe" if self.in_scn("S07_severe_fragmentation", key)
                    else self.pick(["None", "Low", "Moderate", "High"]))
            rows.append({
                "habitat_assessment_id": _sid("HAB", h),
                "organism_id": org["organism_id"],
                "ecosystem_id": org["preferred_ecosystem"],
                "historical_habitat_area_km2": hist,
                "current_habitat_area_km2": round(hist * (1 - loss / 100), 1),
                "habitat_loss_percent": loss,
                "habitat_quality": (
                    "Severely degraded" if loss > 60 else
                    "Moderately degraded" if loss > 30 else
                    "Largely intact"
                ),
                "habitat_trend": (
                    "Rapidly Declining" if loss > 60 else
                    "Declining" if loss > 25 else
                    self.pick(["Stable", "Improving", "Stable"])
                ),
                "fragmentation": frag,
                "assessment_confidence": self.rnd(0.4, 0.85, 2),
                **SYNTH,
            })
        self.data["habitat_assessments"] = rows

    def build_threats(self) -> None:
        rows = []
        n = 0
        eco_by_id = {e["ecosystem_id"]: e for e in self.data["ecosystems"]}
        pool_by_type = {
            "Terrestrial": ["Habitat Loss", "Deforestation", "Agricultural Expansion", "Fire", "Hunting", "Human Disturbance"],
            "Freshwater": ["Pollution", "Water Extraction", "Habitat Loss", "Invasive Species", "Infrastructure Development"],
            "Marine": ["Overfishing", "Ocean Acidification", "Climate Change", "Pollution"],
            "Transitional": ["Habitat Loss", "Urban Expansion", "Pollution", "Climate Change"],
            "Anthropogenic": ["Pollution", "Urban Expansion", "Agricultural Expansion", "Invasive Species"],
        }
        for key, org in self.org_by_key.items():
            eco = eco_by_id[org["preferred_ecosystem"]]
            pool = pool_by_type.get(eco["ecosystem_type"], ["Unknown"])
            count = 4 if self.in_scn("S08_multiple_threats", key) else self.rng.randint(1, 3)
            chosen = self.rng.sample(pool, min(count, len(pool)))
            if self.in_scn("S08_multiple_threats", key) and "Climate Change" not in chosen:
                chosen.append("Climate Change")
            very_high_risk = self.in_scn("S12_very_high_extinction_risk", key)
            for name in chosen:
                n += 1
                scope = self.rnd(75, 98, 1) if very_high_risk else self.rnd(5, 98, 1)
                severity = ("Critical" if scope > 85 else "High" if scope > 55
                            else "Moderate" if scope > 25 else "Low")
                rows.append({
                    "threat_id": _sid("THR", n),
                    "organism_id": org["organism_id"],
                    "ecosystem_id": eco["ecosystem_id"],
                    "threat_name": name,
                    "threat_category": THREAT_CATALOGUE[name],
                    "timing": self.pick(["Ongoing", "Ongoing", "Future", "Past"]),
                    "scope_percent": scope,
                    "affected_population_percent": scope,
                    "scope_interpretation": scope_interpretation(scope),
                    "severity": severity,
                    "impact_confidence": self.rnd(0.35, 0.85, 2),
                    "description": (
                        f"Synthetic threat record: {name} affecting an estimated "
                        f"{scope}% of the modelled population of {org['scientific_name']}."
                    ),
                    "note": "Scope percentage does NOT map to an official conservation category.",
                    **SYNTH,
                })
        self.data["threat_assessments"] = rows

    def build_conservation(self) -> None:
        """Conservation status is deliberately NOT invented.

        No verified external source is wired in, so every record reports
        Unknown / Not Evaluated with is_verified=False (spec section 26).
        """
        status_rows, assess_rows = [], []
        for i, (key, org) in enumerate(self.org_by_key.items(), start=1):
            data_deficient = self.in_scn("S11_data_deficient", key)
            status_rows.append({
                "conservation_status_id": _sid("CST", i),
                "organism_id": org["organism_id"],
                "external_conservation_status": "Data Deficient" if data_deficient else "Unknown",
                "source": "No external conservation dataset connected in this prototype.",
                "source_type": "Unknown",
                "source_url": None,
                "assessment_date": None,
                "is_verified": False,
                "is_synthetic": True,
                "note": (
                    "Gaia does not assign official conservation categories. Populate this "
                    "from a verified external dataset before drawing any conclusion."
                ),
            })

            pop = next(p for p in self.data["population_assessments"]
                       if p["organism_id"] == org["organism_id"])
            hab = next((h for h in self.data["habitat_assessments"]
                        if h["organism_id"] == org["organism_id"]), None)
            threats = [t for t in self.data["threat_assessments"]
                       if t["organism_id"] == org["organism_id"]]

            assess_rows.append({
                "conservation_assessment_id": _sid("CSA", i),
                "organism_id": org["organism_id"],
                "conservation_status_id": _sid("CST", i),
                "criteria": self._criteria(pop, hab, threats),
                "prototype_risk_interpretation": (
                    "Insufficient synthetic evidence for an interpretation."
                    if data_deficient else
                    "Prototype interpretation only - derived from synthetic evidence, "
                    "not an IUCN assessment."
                ),
                "assessment_date": ASSESSMENT_DATE,
                "assessed_by": f"Gaia prototype criteria template {MODEL_VERSION}",
                "is_official_assessment": False,
                **SYNTH,
            })
        self.data["conservation_status"] = status_rows
        self.data["conservation_assessments"] = assess_rows

    def _criteria(self, pop, hab, threats) -> Dict[str, Any]:
        """IUCN-*inspired* criteria template. No category is assigned."""
        decline = pop.get("population_decline_percent")
        rng = pop.get("geographic_range", {})
        eoo = rng.get("extent_of_occurrence_km2")
        mature = pop.get("estimated_mature_individuals")
        return {
            "A_population_reduction": {
                "applicable": decline is not None,
                "evidence": (f"Synthetic population decline of {decline}% over "
                             f"{pop.get('population_change_period_years')} years."
                             if decline is not None else None),
                "value": decline,
                "confidence": pop.get("trend_confidence") if decline is not None else None,
            },
            "B_geographic_range": {
                "applicable": eoo is not None,
                "evidence": (f"Synthetic extent of occurrence {eoo} km2 with "
                             f"{rng.get('range_fragmentation')} fragmentation."
                             if eoo is not None else None),
                "value": eoo,
                "confidence": 0.6 if eoo is not None else None,
            },
            "C_small_population": {
                "applicable": mature is not None and mature < 10000,
                "evidence": (f"Synthetic mature population estimate of {mature} individuals."
                             if mature is not None and mature < 10000 else None),
                "value": mature if mature is not None and mature < 10000 else None,
                "confidence": pop.get("population_confidence") if mature else None,
            },
            "D_restricted_population": {
                "applicable": mature is not None and mature < 1000,
                "evidence": (f"Very small synthetic population ({mature} mature individuals)."
                             if mature is not None and mature < 1000 else None),
                "value": mature if mature is not None and mature < 1000 else None,
                "confidence": 0.55 if mature is not None and mature < 1000 else None,
            },
            "E_quantitative_analysis": {
                "applicable": False,
                "evidence": None,
                "value": None,
                "confidence": None,
                "note": "No population viability analysis is performed in this prototype.",
            },
        }

    # =====================================================================
    # Extinction risk + Gaia risk score
    # =====================================================================
    def build_extinction_risk(self, weights: Dict[str, float]) -> None:
        from .risk import compute_gaia_risk  # local import: shared with backend logic

        rows = []
        for i, (key, org) in enumerate(self.org_by_key.items(), start=1):
            pop = next(p for p in self.data["population_assessments"]
                       if p["organism_id"] == org["organism_id"])
            hab = next((h for h in self.data["habitat_assessments"]
                        if h["organism_id"] == org["organism_id"]), None)
            threats = [t for t in self.data["threat_assessments"]
                       if t["organism_id"] == org["organism_id"]]

            risk = compute_gaia_risk(pop, hab, threats, weights)
            deficient = self.in_scn("S11_data_deficient", key)

            if deficient:
                prob = None
                prob_conf = None
            elif self.in_scn("S12_very_high_extinction_risk", key):
                prob = self.rnd(0.42, 0.71, 3)
                prob_conf = self.rnd(0.5, 0.7, 2)
            else:
                prob = round(min(0.6, risk["gaia_risk_score"] / 400 + self.rnd(0, 0.06, 3)), 3)
                prob_conf = self.rnd(0.35, 0.7, 2)

            rows.append({
                "extinction_risk_assessment_id": _sid("EXT", i),
                "organism_id": org["organism_id"],
                "extinction_probability": prob,
                "extinction_probability_period_years": None if prob is None else 50,
                "extinction_model": "Synthetic Prototype Model",
                "extinction_probability_confidence": prob_conf,
                "risk_indicators": risk["risk_indicators"],
                "gaia_risk_score": risk["gaia_risk_score"],
                "risk_level": risk["risk_level"],
                "risk_confidence": risk["risk_confidence"],
                "score_components": risk["score_components"],
                "score_weights": weights,
                "explanation": risk["explanation"],
                "disclaimer": (
                    "Prototype synthetic estimate produced from synthetic inputs. This is "
                    "NOT a scientific prediction and must not be read as one. It is not an "
                    "IUCN category and not an official extinction probability."
                ),
                "is_synthetic": True,
                "source_type": "Calculated",
                "source": "Gaia prototype risk model over synthetic evidence.",
            })
        self.data["extinction_risk_assessments"] = rows

    # =====================================================================
    # Aggregated analysis results
    # =====================================================================
    def build_analysis_results(self) -> None:
        rows = []
        n = 0
        site_by_id = {s["site_id"]: s for s in self.data["sampling_sites"]}
        env_by_id = {e["environmental_condition_id"]: e for e in self.data["environmental_conditions"]}
        loc_by_id = {l["location_id"]: l for l in self.data["locations"]}
        eco_by_id = {e["ecosystem_id"]: e for e in self.data["ecosystems"]}
        metric_by_sample = {m["sample_id"]: m for m in self.data["biodiversity_metrics"]}

        for sample in self.data["samples"]:
            ids = self.ids_by_sample.get(sample["sample_id"], [])
            if not ids:
                continue
            n += 1
            analysis_id = _sid("ANL", n)
            for rec in ids:
                rec["analysis_id"] = analysis_id

            site = site_by_id[sample["site_id"]]
            loc = loc_by_id[site["location_id"]]
            eco = eco_by_id[site["ecosystem_id"]]
            metric = metric_by_sample[sample["sample_id"]]
            org_ids = sorted({i["predicted_organism_id"] for i in ids})
            confs = [i["confidence_score"] for i in ids]

            rows.append({
                "analysis_id": analysis_id,
                "sample_id": sample["sample_id"],
                "sample": {
                    "sample_id": sample["sample_id"],
                    "site_id": site["site_id"],
                    "site_name": site["name"],
                    "sample_type": sample["sample_type"],
                    "marker_region": sample["marker_region"],
                    "season": sample["season"],
                    "collection_date": sample["collection_date"],
                    "status": sample["status"],
                },
                "environment": {
                    "location_id": loc["location_id"],
                    "region": loc["region"],
                    "state": loc["state"],
                    "country": loc["country"],
                    "ecosystem_id": eco["ecosystem_id"],
                    "ecosystem_name": eco["name"],
                    "ecosystem_type": eco["ecosystem_type"],
                    "terrain_id": eco["terrain_id"],
                    "biome_id": eco["biome_id"],
                    "biosphere_id": eco["biosphere_id"],
                    "conditions": {
                        k: v for k, v in env_by_id[sample["environmental_condition_id"]].items()
                        if k in env_by_id[sample["environmental_condition_id"]]["measured_parameters"]
                    },
                },
                "identification_ids": [i["identification_id"] for i in ids],
                "organism_ids": org_ids,
                "biodiversity_metric_id": metric["biodiversity_metric_id"],
                "biodiversity_metrics": {
                    "species_richness": metric["species_richness"],
                    "shannon_index": metric["shannon_index"],
                    "simpson_index": metric["simpson_index"],
                    "pielou_evenness": metric["pielou_evenness"],
                    "biodiversity_category": metric["biodiversity_category"],
                },
                "ecological_assessment_ids": [
                    a["assessment_id"] for a in self.data["biodiversity_assessments"]
                    if a["sample_id"] == sample["sample_id"]
                ],
                "population_assessment_ids": [
                    p["population_assessment_id"] for p in self.data["population_assessments"]
                    if p["organism_id"] in org_ids
                ],
                "habitat_assessment_ids": [
                    h["habitat_assessment_id"] for h in self.data["habitat_assessments"]
                    if h["organism_id"] in org_ids
                ],
                "threat_assessment_ids": [
                    t["threat_id"] for t in self.data["threat_assessments"]
                    if t["organism_id"] in org_ids
                ],
                "conservation_assessment_ids": [
                    c["conservation_assessment_id"] for c in self.data["conservation_assessments"]
                    if c["organism_id"] in org_ids
                ],
                "extinction_risk_assessment_ids": [
                    e["extinction_risk_assessment_id"] for e in self.data["extinction_risk_assessments"]
                    if e["organism_id"] in org_ids
                ],
                "confidence": {
                    "mean_identification_confidence": round(sum(confs) / len(confs), 3),
                    "min_identification_confidence": round(min(confs), 3),
                    "max_identification_confidence": round(max(confs), 3),
                    "confidence_level": confidence_level(sum(confs) / len(confs)),
                    "low_confidence_count": sum(1 for c in confs if c < 0.5),
                },
                "metadata": {
                    "is_synthetic": True,
                    "model_version": MODEL_VERSION,
                    "seed_version": SEED_VERSION,
                    "generated_on": ASSESSMENT_DATE,
                    "source_type": "Calculated",
                    "disclaimer": (
                        "Aggregated from synthetic records. Not a real analysis result."
                    ),
                },
            })
        self.data["analysis_results"] = rows

    # =====================================================================
    def build_all(self, weights: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
        self.build_environment()
        self.build_taxonomy_and_organisms()
        self.build_classifications()
        self.build_environmental_conditions()
        self.build_samples()
        self.build_sequences()
        self.build_identifications()
        self.build_biodiversity()
        self.build_population()
        self.build_habitat()
        self.build_threats()
        self.build_conservation()
        self.build_extinction_risk(weights)
        self.build_analysis_results()
        return self.data


def confidence_level(score: float) -> str:
    if score >= 0.9:
        return "Very High"
    if score >= 0.75:
        return "High"
    if score >= 0.5:
        return "Medium"
    if score > 0:
        return "Low"
    return "Unknown"


def scope_interpretation(pct: float) -> str:
    if pct > 90:
        return "Whole Population"
    if pct >= 50:
        return "Majority"
    if pct >= 25:
        return "Moderate"
    return "Limited"
