# eDNA Datasets

This directory contains all datasets and reference databases used in the project **"AI-Based Taxonomy Identification and Biodiversity Assessment from eDNA Datasets."**

## Folder Structure

```
data/
│
├── accessions.txt          # SRA run accessions (manifest, tracked in git)
├── .gitignore              # keeps the large files below out of git
│
├── raw/
│   ├── SRR17137384.fastq
│   ├── SRR37879006.fastq
│   ├── SRR38080555.fastq
│   ├── SRR39683131.fastq
│   ├── SRR39742893.fastq
│   ├── SRR39848019.fastq
│   ├── SRR39993450.fastq
│   └── SRR39993451.fastq
│
├── references/
│   ├── BOLD_Public.fasta
│   ├── mitofishdb.fa
│   ├── SILVA.fasta
│   └── UNITE.fasta
│
├── taxonomy/
│   ├── names.dmp
│   ├── nodes.dmp
│   └── merged.dmp
│
└── metadata/
    └── SRA_RunInfo.xlsx
```

---

## Folder Description

### raw/

Contains raw environmental DNA (eDNA) sequencing datasets downloaded from the NCBI Sequence Read Archive (SRA).

**File Format**

- FASTQ
- FASTQ.GZ

These files are the primary input for taxonomy identification and biodiversity analysis.

---

### references/

Contains reference databases used for taxonomic classification.

| Database | Purpose |
|----------|---------|
| BOLD | Animal COI reference sequences |
| SILVA | 16S/18S rRNA reference database |
| MitoFish | Fish mitochondrial reference database |
| UNITE | Fungal ITS reference database |

---

### taxonomy/

Contains taxonomy files downloaded from the NCBI Taxonomy database.

| File | Description |
|------|-------------|
| names.dmp | Scientific names |
| nodes.dmp | Taxonomic hierarchy |
| merged.dmp | Merged taxonomy IDs |

These files are required for mapping sequence classifications to biological taxonomy.

---

### metadata/

Contains metadata associated with each sequencing run.

Example information includes:

- Run ID
- BioProject
- BioSample
- Organism
- Sequencing Platform
- Instrument
- Library Strategy
- Library Layout
- Number of Reads
- Number of Bases
- Publication Date

---

## Data Sources

- NCBI Sequence Read Archive (SRA)
- NCBI Taxonomy
- BOLD Systems
- SILVA Database
- MitoFish
- UNITE Database

---

## Workflow

```
Raw FASTQ Files
        │
        ▼
Quality Control
        │
        ▼
Sequence Filtering
        │
        ▼
Taxonomic Classification
        │
        ▼
Biodiversity Assessment
        │
        ▼
Machine Learning Analysis
        │
        ▼
Visualization Dashboard
```

---

## Note

Large datasets and reference databases may exceed GitHub's file size limits. For public repositories, it is recommended to exclude large files using `.gitignore` and provide download instructions in the main project README.

### Status of this directory

That recommendation is now enforced by `data/.gitignore`, which excludes
`raw/`, `references/`, `taxonomy/`, and common sequence formats. GitHub
hard-rejects any file over 100 MB, and git retains every version of a
file forever — so a large file committed once bloats the repository
permanently, even after deletion.

**Tracked here:** `accessions.txt`, `metadata/`, and this README.
**Not tracked:** everything under `raw/`, `references/`, and `taxonomy/` —
download those to your local disk before running the pipeline.

---
---

# Gaia Synthetic Seed Database

Everything above this line describes the **real** dataset plan (SRA reads,
reference databases, NCBI taxonomy). Everything below describes a
**separate, synthetic** dataset that lives in `data/seed/` and exists so
Gaia's backend, API, and eventual frontend have realistic, fully
interconnected demonstration data to run against *before* the real
pipeline above is wired up.

## 1. What this represents — and what it does not

`data/seed/*.json` is a **deterministically generated, entirely synthetic**
dataset covering the full Gaia workflow: environment hierarchy → sampling
→ eDNA sequences → taxonomic identification → classification →
biodiversity metrics → population/habitat/threat assessment →
conservation status → extinction risk → a Gaia Prototype Risk Score.

**None of it is a real scientific observation.** Specifically:

- No organism was actually detected at any location in this dataset.
- No DNA sequence is a real barcode — sequences are randomly generated
  over the nucleotide alphabet with a controlled length and GC content,
  and carry no biological signal.
- No population estimate, extinction probability, or conservation status
  is a real figure. They are prototype heuristics computed from synthetic
  inputs, for demonstrating the pipeline's shape.
- Taxonomic **names** (kingdom → species) are real scientific names, used
  so the hierarchy and cross-references behave realistically — but the
  fact that a record for *Panthera tigris* exists here says nothing about
  a real tiger, real population, or real location.

Every record carries the flags that make this explicit and machine-checkable:

| Flag | Meaning | Where |
|---|---|---|
| `is_synthetic: true` | Generated record, not observed | every collection |
| `is_mock: true` | Sequence is generated text, not a real barcode | `dna_sequences` |
| `is_mock_prediction: true` | Identification came from a placeholder, not a trained model | `identifications` |
| `source_type` | `Synthetic` \| `Calculated` \| `ML Model` \| `External Database` \| `Unknown` | most collections |
| `source` | Free-text provenance note | most collections |

`Calculated` means a value really was computed from other records in this
dataset (e.g. the Shannon index is genuinely computed from the generated
identifications) — it is still synthetic in the sense that its *inputs*
are synthetic, and it must not be read as a real ecological measurement.

## 2. Collections and relationships

Twenty-three collections in `data/seed/`, following the chain in the
task spec:

```
Biosphere → Biome → Terrain → Ecosystem → Location → Sampling Site
    → Sample → DNA Sequence → Identification → Organism → Taxonomy

Organism → Population Assessment → Population Timeseries
    → Habitat Assessment → Threat Assessment → Geographic Range
    → Conservation Status / Conservation Assessment
    → Extinction Risk Assessment (Gaia Prototype Risk Score)
```

`analysis_results` aggregates one record per sample: the sample,
environment, identifications, biodiversity metrics, and links (by ID) to
every assessment produced from it — mirroring the JSON shape the backend
already returns from `/analyze`.

Referential integrity is enforced by construction (every foreign key is
drawn from an already-built collection, never hand-typed) and checked by
`scripts/validate_seed_data.py` before anything can be loaded.

Sixteen named scenarios (healthy/stable, declining, rapidly declining,
small population, restricted range, high habitat loss, severe
fragmentation, multiple threats, high-detection/low-population-data, low
confidence, data deficient, very-high extinction risk, low/high
biodiversity, high microbial diversity, potential invasive) are pinned to
specific organisms and sites in `scripts/gaia_seed/reference.py::SCENARIOS`
so the dataset always has a concrete example of each, rather than hoping
random generation produces one.

## 3. How to seed the database

```bash
# 1. Regenerate data/seed/*.json (deterministic — same seed, same output)
python scripts/generate_seed_data.py

# 2. Load into a running repository (in-memory today; any IDataRepository later)
python scripts/seed_database.py
```

`scripts/seed_database.py` is a thin runner — `backend/`'s modules use
flat imports (`from interfaces...`) that resolve relative to `backend/`
itself (that's how `uvicorn app:app` already runs it), so loading them
from a script anywhere else means putting `backend/` on `sys.path` first.
To do this from your own code:

```python
import sys
sys.path.insert(0, "backend")  # or run from inside backend/
from storage.in_memory_repository import InMemoryRepository
from storage.seed_loader import seed_repository

repo = InMemoryRepository()
print(seed_repository(repo))
```

`generate_seed_data.py` runs the same validation as step 2 before writing
anything, so a broken generator never produces committed output.

## 4. How to validate the data

```bash
python scripts/validate_seed_data.py           # errors only
python scripts/validate_seed_data.py --strict   # also fail on warnings
```

Checks include: duplicate IDs, dangling foreign keys, taxonomy rank
completeness, confidence/probability/percentage range checks, negative
population/habitat values, invalid enums (trends, severities,
fragmentation, conservation categories), missing `is_synthetic` /
`is_mock` / `is_mock_prediction` flags, coordinate bounds, and a guard
against ever asserting an official conservation status without
verification (unverified records must read `Unknown` / `Not Evaluated` /
`Data Deficient` — see `scripts/gaia_seed/validate.py::_check_conservation`).

## 5. How to query the data

Once loaded into a repository, every documented query in the spec works
against the generic accessors:

```python
# organisms belonging to a kingdom
repo.list_records("organisms", {"kingdom": "Animalia"})

# low-confidence identifications
[i for i in repo.list_records("identifications") if i["confidence_score"] < 0.5]

# organisms with population decline > 30%
[p for p in repo.list_records("population_assessments")
 if (p.get("population_decline_percent") or 0) > 30]

# high Gaia Risk Score organisms
[e for e in repo.list_records("extinction_risk_assessments")
 if (e.get("gaia_risk_score") or 0) >= 70]

# a specific organism / analysis / assessment by id
repo.get_organism(organism_id)
repo.get_analysis(analysis_id)
repo.get_assessment(assessment_id)
```

`list_records(collection, filters, limit)` takes exact-match filters
(a filter value may be a list for membership, e.g. `{"population_trend":
["Declining", "Rapidly Declining"]}`), which covers every filter query
named in the spec without bespoke query code per entity.

## 6. Gaia Prototype Risk Score

`extinction_risk_assessments[*].gaia_risk_score` (0-100) is computed by
`scripts/gaia_seed/risk.py::compute_gaia_risk` — the same function the
backend calls live via `backend/assessment/risk_engine.py`, so the seed
data and a fresh computation can never drift apart. It is explicitly
**not** called an IUCN score. Weights live in `data/seed/risk_weights.json`
and must sum to 1.0; every score comes with `score_components` (per-factor
contribution), `risk_confidence` (fraction of the weight actually backed
by evidence), and a plain-language `explanation` that cites the specific
evidence behind each statement.

A component with no supporting evidence contributes nothing to the score
rather than being dropped from the denominator — otherwise a single thin
data point (e.g. one threat record on an otherwise-undocumented organism)
could spike the score to 100. Missing evidence lowers `risk_confidence`,
never inflates the score.

## 7. Mapping to Gaia's analysis pipeline

| Pipeline stage (backend/) | Seed collection(s) |
|---|---|
| Upload / Sequence Extraction | `samples`, `dna_sequences` |
| Taxonomic Identification | `identifications`, `taxonomy` |
| Classification | `classifications`, `organisms` |
| Biodiversity Assessment | `biodiversity_metrics`, `biodiversity_assessments` |
| (new) Population Assessment | `population_assessments`, `population_timeseries` |
| (new) Habitat Assessment | `habitat_assessments` |
| (new) Threat Assessment | `threat_assessments` |
| (new) Conservation Analysis | `conservation_status`, `conservation_assessments` |
| (new) Extinction-Risk Analysis | `extinction_risk_assessments` |
| Result Aggregator | `analysis_results` |
| Dashboard | `GET /dashboard/summary` (see `backend/services/explore_service.py`) |

The live `backend/` pipeline (upload → preprocess → identify → classify →
assess → analyze) and this seed database share **one repository
instance** (`dependencies.py::get_repository`), loaded from `data/seed/`
at startup — they are not separate systems. The live pipeline processes
an uploaded FASTA end-to-end with placeholder engines and writes into its
own sample/prediction storage; the seed database pre-populates the richer
collections the live pipeline doesn't compute yet (population / habitat /
threat / conservation / risk). The **Explore API**
(`backend/routes/explore_routes.py`) reads the seed collections directly —
`/organisms`, `/risk/{id}`, `/species/{id}`, `/dashboard/summary`, etc. —
and is what the frontend's Biodiversity Dashboard calls. Extending the
live pipeline to write its own results into these same collections (so an
uploaded sample gets a population/habitat/threat/risk assessment too,
not just biodiversity metrics) remains the natural next step.

## 8. Replacing synthetic data with real data

| Field / collection | Currently | Should eventually come from |
|---|---|---|
| `taxonomy.*` (ranks, common names) | Real names, hand-curated | An external taxonomy database (NCBI Taxonomy, GBIF, Catalogue of Life) |
| `dna_sequences.sequence` | Randomly generated text | Real sequenced reads (`data/raw/*.fastq`, see above) |
| `identifications.predicted_*`, `confidence_score` | Placeholder classifier | A trained ML taxonomy classifier (BLAST / Kraken2 / custom model) |
| `biodiversity_metrics.*` | Calculated, but from synthetic identifications | Same formulas, computed from real identification output |
| `population_assessments.estimated_*` | Synthetic prototype estimate | Field survey data, camera-trap/transect studies, or a validated eDNA-to-abundance calibration (currently explicitly absent — see `abundance_interpretation`) |
| `habitat_assessments.*` | Synthetic prototype estimate | Remote-sensing land-cover change analysis (e.g. Global Forest Watch, satellite time series) |
| `threat_assessments.*` | Synthetic, rule-assigned | Expert assessment or a threat-classification model over real habitat/land-use data |
| `conservation_status.external_conservation_status` | `Unknown` / `Data Deficient` by design | IUCN Red List API, national conservation datasets (e.g. WII, ZSI for India) |
| `extinction_risk_assessments.gaia_risk_score` | Prototype heuristic (this repo) | Stays a Gaia-specific score, but recalibrated once the inputs above are real; still not a substitute for an IUCN assessment |
| `locations.*` (coordinates) | Plausible regional centroids | Real sampling-site GPS coordinates |

## 9. Regenerating or extending the dataset

- Reference tables (biospheres/biomes/terrains/ecosystems/locations/sites/
  taxonomy/organisms/scenarios) live in `scripts/gaia_seed/reference.py` —
  edit these to add new organisms, sites, or scenarios.
- Derived records (samples, sequences, identifications, metrics,
  assessments, risk scores) are generated by `scripts/gaia_seed/build.py`
  from a fixed RNG seed — regenerating after a reference-table edit
  produces a fresh, still-valid dataset.
- Run `python scripts/generate_seed_data.py` after any change; it
  validates before writing and reports per-collection counts.
