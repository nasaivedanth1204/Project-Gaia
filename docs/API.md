# API Documentation

Base URL (local dev): `http://127.0.0.1:8000`

All request/response bodies are JSON except `/upload`, which takes a
`multipart/form-data` file. Every example below was captured from a live
run of this backend.

---

## POST /upload

Validates and parses an uploaded FASTA / CSV / TXT file, extracts
sequences, and stores the sample. CSV files must have a `sequence` column
(optionally `id`/`header`); TXT files are one raw sequence per line.

**Request** (`multipart/form-data`)

```
file: sample.fasta
```

**Response** `200 OK`

```json
{
  "sample_id": "sample_4d2088ac9c2a",
  "filename": "sample.fasta",
  "file_type": "fasta",
  "sequence_count": 4,
  "sequences": [
    {
      "sequence_id": "seq_9d121a74b0fc",
      "header": "read1",
      "sequence": "AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCAGGCCTAACACATGCAAGTCGAACG",
      "length": 61
    }
  ],
  "status": "uploaded"
}
```

**Validation error** `400 Bad Request`

```json
{
  "detail": {
    "message": "Validation failed for uploaded file.",
    "errors": ["FASTA content must start with a header line beginning with '>'."]
  }
}
```

---

## POST /preprocess

Runs `clean_sequence -> remove_noise -> normalize_sequence -> detect_markers
-> extract_features` over every sequence in the sample.

**Request**

```json
{ "sample_id": "sample_4d2088ac9c2a" }
```

**Response** `200 OK`

```json
{
  "sample_id": "sample_4d2088ac9c2a",
  "status": "preprocessed",
  "processed_sequences": [
    {
      "sequence_id": "seq_9d121a74b0fc",
      "original_sequence": "AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCAGGCCTAACACATGCAAGTCGAACG",
      "processed_sequence": "AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCAGGCCTAACACATGCAAGTCGAACG",
      "markers_detected": ["16S"],
      "features": { "length": 61, "gc_content": 0.541, "n_count": 0, "completeness": 1.0 }
    }
  ]
}
```

**Errors**: `404` sample not found.

---

## POST /identify

Placeholder taxonomic identification (see `# TODO` in
`identification/taxonomy_engine.py` — replace with BLAST / Kraken2 / a
trained classifier). Requires the sample to have been preprocessed.

**Request**

```json
{ "sample_id": "sample_4d2088ac9c2a" }
```

**Response** `200 OK`

```json
{
  "sample_id": "sample_4d2088ac9c2a",
  "status": "identified",
  "results": [
    {
      "sequence_id": "seq_b548b2ac42d6",
      "kingdom": "Animalia",
      "phylum": "Chordata",
      "class": "Actinopterygii",
      "order": "Perciformes",
      "family": "Example_Family_A",
      "genus": "Example_Genus_A",
      "species": "Example_species_a",
      "confidence": 0.95
    }
  ]
}
```

**Errors**: `404` sample not found, `409` sample not yet preprocessed.

---

## POST /classify

Placeholder ecological category assignment (see `# TODO` in
`classification/classification_engine.py`). Requires identification to
have run first.

**Request**

```json
{ "sample_id": "sample_4d2088ac9c2a" }
```

**Response** `200 OK`

```json
{
  "sample_id": "sample_4d2088ac9c2a",
  "status": "classified",
  "results": [
    {
      "sequence_id": "seq_b548b2ac42d6",
      "category": "Animal",
      "kingdom_reference": "Animalia",
      "basis": "placeholder-kingdom-mapping"
    }
  ]
}
```

Categories come from `classification/categories.py::SpeciesCategory`:
`Marine, Freshwater, Terrestrial, Plant, Animal, Fungi, Protist, Bacteria,
Archaea, Unknown` — extend that enum (and its mapping) to add more.

**Errors**: `404` sample not found, `409` sample not yet identified.

---

## POST /assess

Computes biodiversity metrics (`assessment/biodiversity_metrics.py`) and
ecological assessment objects (`assessment/ecological_assessment.py`).
Requires identification to have run first.

**Request**

```json
{ "sample_id": "sample_4d2088ac9c2a" }
```

**Response** `200 OK`

```json
{
  "sample_id": "sample_4d2088ac9c2a",
  "status": "assessed",
  "metrics": {
    "species_richness": 2,
    "shannon_index": 0.5623,
    "simpson_index": 0.375,
    "evenness": 0.8112,
    "dominant_species": ["Unknown", "Example_species_a"],
    "rare_species": ["Example_species_a"]
  },
  "assessment": [
    {
      "title": "Low Biodiversity",
      "severity": "warning",
      "description": "The sample shows low species richness, which may indicate ecosystem stress."
    },
    {
      "title": "Rare Species Present",
      "severity": "info",
      "description": "One or more species were detected at very low abundance."
    }
  ]
}
```

Assessment templates (title/severity/description) live in
`assessment/templates.py::ASSESSMENT_TEMPLATES` — add new ones there and
reference them from `EcologicalAssessmentEngine.generate()`.

**Errors**: `404` sample not found, `409` sample not yet identified.

---

## POST /analyze

Runs preprocess -> identify -> classify -> assess -> confidence for every
sequence in one call, aggregates the result (`aggregation/result_aggregator.py`),
and stores it as the sample's prediction (retrievable later via `/history`).

**Request**

```json
{ "sample_id": "sample_af93fc68a909" }
```

**Response** `200 OK`

```json
{
  "sample_id": "sample_af93fc68a909",
  "status": "analyzed",
  "results": [
    {
      "sequence_id": "seq_67e45e1c4e79",
      "taxonomy": {
        "sequence_id": "seq_67e45e1c4e79",
        "kingdom": "Animalia",
        "phylum": "Chordata",
        "class": "Actinopterygii",
        "order": "Perciformes",
        "family": "Example_Family_A",
        "genus": "Example_Genus_A",
        "species": "Example_species_a",
        "confidence": 0.95
      },
      "classification": {
        "sequence_id": "seq_67e45e1c4e79",
        "category": "Animal",
        "kingdom_reference": "Animalia",
        "basis": "placeholder-kingdom-mapping"
      },
      "confidence": {
        "confidence": 0.975,
        "confidence_level": "Very High",
        "inputs": {
          "classification_confidence": 0.95,
          "sequence_quality": 1.0,
          "feature_completeness": 1.0
        }
      }
    }
  ],
  "metrics": {
    "species_richness": 2,
    "shannon_index": 0.5623,
    "simpson_index": 0.375,
    "evenness": 0.8112,
    "dominant_species": ["Unknown", "Example_species_a"],
    "rare_species": ["Example_species_a"]
  },
  "assessment": [
    { "title": "Low Biodiversity", "severity": "warning", "description": "The sample shows low species richness, which may indicate ecosystem stress." },
    { "title": "Rare Species Present", "severity": "info", "description": "One or more species were detected at very low abundance." }
  ]
}
```

Confidence levels come from `confidence/levels.py::ConfidenceLevel`:
`Very High, High, Medium, Low, Unknown`.

**Errors**: `404` sample not found.

---

## GET /status

Overall engine status — live-pipeline counts plus the seed dataset loaded
at startup (see the Explore API section below).

```json
{
  "status": "operational",
  "total_samples": 1,
  "total_predictions": 1,
  "seed_dataset": {
    "loaded": true,
    "collection_count": 23,
    "record_count": 1178,
    "collections": {
      "organisms": 49,
      "extinction_risk_assessments": 49,
      "threat_assessments": 117
    }
  }
}
```

(`collections` is truncated above for brevity — the real response lists
all 23.)

## GET /status/{sample_id}

Per-sample pipeline status.

```json
{
  "sample_id": "sample_af93fc68a909",
  "filename": "sample.fasta",
  "file_type": "fasta",
  "status": "analyzed",
  "sequence_count": 4,
  "uploaded_at": "2026-08-06T12:32:29.737795+00:00"
}
```

**Errors**: `404` sample not found.

## GET /history

Returns every aggregated prediction produced by `/analyze` so far (a list
of the object shown in the `/analyze` response above).

---

# Explore API

Read-only access to the synthetic Gaia dataset (`data/seed/*.json`,
loaded into the repository at startup — see `backend/dependencies.py`).
**Nothing under this section is a real observation** — see
`data/README.md` for the full provenance model. Every example below was
captured from a live run.

## GET /organisms

Filterable by `kingdom`, `habitat_type`, `native_status`.

```
GET /organisms?kingdom=Bacteria
```

```json
[
  { "organism_id": "ORG-036", "scientific_name": "Nitrosomonas europaea", "common_name": "Ammonia-oxidising Bacterium", "kingdom": "Bacteria", "habitat_type": "Freshwater", "preferred_ecosystem": "ECO-008", "trophic_level": "Microbial Decomposer", "functional_group": "Microbial Decomposer", "native_status": "Native", "environmental_sensitivity": "Moderate", "conservation_status_reference": "Unknown", "is_synthetic": true, "source": "Synthetic demonstration data", "source_type": "Synthetic" }
]
```

**Errors** (on `GET /organisms/{organism_id}`): `404` if the organism does not exist.

## GET /risk/{organism_id}

Recomputes the Gaia Prototype Risk Score **live** from the organism's
current population/habitat/threat records via `GaiaRiskEngine` — it does
not just echo the value baked into the seed file at generation time.

```json
{
  "gaia_risk_score": 85,
  "risk_level": "Critical Risk",
  "risk_confidence": 1.0,
  "score_components": {
    "population_decline": 22.77,
    "population_size": 12.75,
    "habitat_loss": 12.58,
    "range_restriction": 15.0,
    "threat_pressure": 21.8
  },
  "risk_indicators": {
    "population_decline": "VERY_HIGH", "population_size": "HIGH",
    "geographic_range": "VERY_HIGH", "habitat_loss": "HIGH",
    "fragmentation": "LOW", "threat_pressure": "VERY_HIGH"
  },
  "explanation": [
    "Population trend indicates severe decline (75.9% in the synthetic record).",
    "The estimated mature population is very small, which raises risk independently of trend.",
    "Significant habitat reduction is present in the synthetic dataset (62.9% lost).",
    "The recorded population is geographically fragmented (severe fragmentation).",
    "Multiple ongoing environmental pressures are present (Climate Change, Deforestation, Habitat Loss, Human Disturbance, Hunting)."
  ],
  "score_name": "Gaia Prototype Risk Score",
  "score_disclaimer": "Prototype heuristic over synthetic evidence. Not an IUCN score and not an official extinction risk assessment."
}
```

Every statement in `explanation` cites the specific evidence that produced
it — see `scripts/gaia_seed/risk.py::explain_risk`. A component missing
evidence lowers `risk_confidence` rather than being dropped from the score
(see the design note in that file — this fixed a real bug where thin
evidence could otherwise spike the score to 100).

**Errors**: `404` if the organism has no population assessment.

## GET /species/{organism_id}

The full risk-profile object — organism, taxonomy, population, habitat,
threats, conservation, and a live risk score, in one call. This is what
the frontend's species detail panel calls.

```json
{
  "organism": { "organism_id": "ORG-006", "scientific_name": "Ardeotis nigriceps", "common_name": "Great Indian Bustard", "kingdom": "Animalia", "...": "..." },
  "taxonomy": { "kingdom": "Animalia", "phylum": "Chordata", "class": "Aves", "order": "Otidiformes", "family": "Otididae", "genus": "Ardeotis", "species": "Ardeotis nigriceps" },
  "population": { "population_trend": "Rapidly Declining", "population_decline_percent": 75.9, "estimated_mature_individuals": 134, "population_confidence": 0.72, "...": "..." },
  "population_timeseries": [ { "year": 2020, "estimated_population": 344, "...": "..." } ],
  "habitat": { "habitat_loss_percent": 62.9, "habitat_trend": "Rapidly Declining", "fragmentation": "Low", "...": "..." },
  "threats": [ { "threat_name": "Deforestation", "severity": "High" }, { "threat_name": "Climate Change", "severity": "High" } ],
  "conservation": { "status": { "external_conservation_status": "Unknown", "is_verified": false } },
  "risk": { "gaia_risk_score": 85, "risk_level": "Critical Risk" },
  "assessment": { "type": "prototype_risk_assessment", "is_synthetic": true }
}
```

## GET /dashboard/summary

Aggregate view over the whole dataset — the terminal "Dashboard" node in
the extended Gaia workflow.

```json
{
  "totals": { "organisms": 49, "samples": 34, "threat_assessments": 117, "...": "... (23 collections)" },
  "risk_level_distribution": { "Low Risk": 22, "Moderate Risk": 14, "Minimal Risk": 10, "Very High Risk": 2, "Critical Risk": 1 },
  "biodiversity_category_distribution": { "Low": 17, "Moderate": 4, "Very Low": 1 },
  "kingdom_distribution": { "Animalia": 23, "Plantae": 10, "Bacteria": 5, "Fungi": 4, "Protista": 4, "Archaea": 3 },
  "conservation_status_distribution": { "Unknown": 46, "Data Deficient": 3 },
  "top_risk_species": [
    { "organism_id": "ORG-006", "scientific_name": "Ardeotis nigriceps", "common_name": "Great Indian Bustard", "gaia_risk_score": 85, "risk_level": "Critical Risk" }
  ],
  "is_synthetic": true,
  "disclaimer": "All figures summarize the synthetic Gaia seed dataset. None represent real field observations."
}
```

Every other Explore endpoint (`/biospheres`, `/biomes`, `/terrains`,
`/ecosystems`, `/locations`, `/sampling-sites`, `/taxonomy`, `/samples`,
`/identifications`, `/biodiversity/metrics`, `/biodiversity/assessments`,
`/population/{id}/timeseries`, `/threats`, `/conservation`, `/analysis`)
returns the record shape documented in `data/README.md`'s relationship
table and `data/schemas/`, filtered by whichever query parameters are
listed in `backend/README.md`'s API summary.

---

## Interactive docs

FastAPI auto-generates OpenAPI/Swagger docs at `/docs` and ReDoc at
`/redoc` once the server is running.
