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

Overall engine status.

```json
{ "status": "operational", "total_samples": 2, "total_predictions": 1 }
```

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

## Interactive docs

FastAPI auto-generates OpenAPI/Swagger docs at `/docs` and ReDoc at
`/redoc` once the server is running.
