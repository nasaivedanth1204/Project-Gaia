# Project Gaia — eDNA Biodiversity Backend (SIH Prototype)

Backend processing engine for **"Identifying Taxonomy and Assessing Biodiversity
from eDNA Datasets."** This is a hackathon prototype: it demonstrates a
complete workflow from an uploaded eDNA dataset to a biodiversity assessment,
using placeholder scientific logic wherever a real algorithm/model/database
would normally be required.

There is intentionally **no auth, no persistent database, and no
deployment tooling** in this codebase — see "Explicit non-goals" below. A
prototype UI does exist (`../frontend/`, served at `/ui`): a scientific
application shell (sidebar navigation, restrained forest-green/off-white
palette, semantic color for status only) over eight pages — Dashboard,
Samples, Analysis, Taxonomy, Biodiversity, Conservation, Risk Assessment,
History. Analysis embeds the live upload-through-analyze pipeline
described next; every other page reads the synthetic Gaia dataset via the
Explore API below.

## Quick start

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs
See [`../docs/API.md`](../docs/API.md) for endpoint documentation and
example requests/responses, and [`../frontend/`](../frontend/) for the UI
this backend serves at `/ui`.

## Two parallel demonstrations

This backend runs **two separate things off the same repository**, not
one pipeline pretending to be two:

1. **Live pipeline** (`/upload` ... `/analyze`) — processes one uploaded
   sample end-to-end through the placeholder engines below. Nothing here
   changed when the Gaia data model was added.

   ```
   Upload -> Validation -> Sequence Extraction -> Cleaning -> Preprocessing
          -> Taxonomic Identification -> Classification -> Biodiversity Assessment
          -> Confidence Calculation -> JSON Response
   ```

2. **Explore API** (`/organisms`, `/dashboard/summary`, ...) — read-only
   access to the synthetic Gaia dataset (`data/seed/*.json`, ~1,178
   records), loaded into the repository at startup. This is the fuller
   workflow the problem statement describes:

   ```
   eDNA Sample -> Sample Metadata -> Sequence Validation -> Preprocessing
       -> Organism Identification -> Taxonomic Classification
       -> Terrain / Ecosystem / Biosphere
       -> Biodiversity Assessment -> Population Assessment
       -> Habitat Assessment -> Threat Assessment -> Conservation Analysis
       -> Extinction Risk -> Gaia Risk Score -> Final Analysis -> Dashboard
   ```

Both share one `IDataRepository` instance (see `dependencies.py::get_repository`)
so an uploaded sample and the seeded dataset coexist without collision —
uploaded-sample storage and seed-collection storage use disjoint internal
keys. `/status` reports counts from both.

Each pipeline stage / explore endpoint has its own module, service, and
(where useful) interface, so any single one can be swapped out without
touching the others.

## Directory structure

```
backend/
    app.py                  FastAPI app, mounts all routers
    dependencies.py         Dependency-injection wiring (repository, engines, services, controllers)
    routes/                 One APIRouter per endpoint group -> calls a controller
    controllers/            Thin HTTP layer: calls a service, translates exceptions to HTTPException
    services/               Orchestration: one service per pipeline stage
    interfaces/             Abstract base classes every engine/repository implements
    models/                 Internal domain dataclasses (Sample, enums)
    schemas/                Pydantic request/response models
    storage/                In-memory IDataRepository implementation
    preprocessing/          Module 2: cleaning / noise removal / normalization / markers / features
    identification/         Module 3: taxonomy engine + hierarchical template
    classification/         Module 4: species category engine + enum
    assessment/             Module 5 & 6: biodiversity metrics + ecological assessment templates
    confidence/             Module 7: confidence scoring + levels
    aggregation/            Module 8: combines per-stage output into the final response
    utils/                  Validators, parsers, id generation, logging, exceptions

    services/explore_service.py      Read-side queries + aggregation over the Gaia data model
    controllers/explore_controller.py  Thin HTTP layer for the Explore API
    routes/explore_routes.py         /biospheres ... /dashboard/summary (see docs/API.md)
    assessment/risk_engine.py        Gaia Prototype Risk Score (re-exports scripts/gaia_seed/risk.py)
    storage/seed_loader.py           Loads data/seed/*.json into any IDataRepository
```

## Why the architecture looks like this

**The database is not finalized**, so nothing is coupled to a specific
persistence technology. Every read/write goes through `IDataRepository`
(`interfaces/data_repository.py`):

```python
class IDataRepository(ABC):
    def save_sample(self, sample_id, sample_data) -> None: ...
    def get_sample(self, sample_id) -> Optional[dict]: ...
    def save_stage_result(self, sample_id, stage, data) -> None: ...
    def get_stage_result(self, sample_id, stage) -> Optional[dict]: ...
    def save_prediction(self, sample_id, prediction) -> None: ...
    def get_prediction(self, sample_id) -> Optional[dict]: ...
    def get_history(self) -> list[dict]: ...
    def list_samples(self) -> list[str]: ...
```

`storage/in_memory_repository.py` is the only implementation today — plain
Python dicts, no external service required. **To add a real database**,
write a new class that implements `IDataRepository` (e.g.
`MongoRepository`, `PostgresRepository`) and swap the single line in
`dependencies.py::get_repository()`. Nothing in `services/`, `controllers/`,
or `routes/` needs to change.

**The biological algorithms are not built yet.** Every place a real
ML model, reference database, or bioinformatics tool (BLAST, Kraken2, a
trained classifier, etc.) would plug in is marked with a `# TODO:` comment
and implemented with a clearly-labeled placeholder in the meantime:

| Module | File | Placeholder behavior | Replace with |
|---|---|---|---|
| Preprocessing | `preprocessing/sequence_processor.py` | Regex-based cleaning, static primer patterns, k-mer-free feature stats | Real QC/trimming, primer/marker detection via alignment or HMMs, k-mer/embedding features |
| Taxonomic ID | `identification/taxonomy_engine.py`, `taxonomy_reference.py` | Deterministic hash into a 5-entry example taxonomy template | BLAST / Kraken2 / a trained sequence classifier against a real reference DB |
| Classification | `classification/classification_engine.py` | Kingdom-name string lookup | ML model trained on habitat/lineage features |
| Biodiversity metrics | `assessment/biodiversity_metrics.py` | Standard Shannon/Simpson/evenness formulas over placeholder species calls | Same formulas, but over real, validated species-abundance data (optionally rarefaction/Chao1) |
| Ecological assessment | `assessment/ecological_assessment.py` | Fixed richness thresholds | Expert-defined rules, invasive/endangered species reference lookups |
| Confidence | `confidence/confidence_engine.py` | Weighted average of placeholder inputs | Calibrated confidence from the real classifier's output probabilities |

## Where to plug in real components later

1. **Database** — implement `IDataRepository` in a new file under
   `storage/`, wire it in `dependencies.py::get_repository()`.
2. **ML taxonomy / classification models** — implement `ITaxonomyEngine` /
   `IClassificationEngine` in new classes, wire them in `dependencies.py`.
   The rest of the pipeline (services, routes, response shape) is
   unaffected because it only depends on the interfaces.
3. **Frontend** — this repo now ships a prototype UI (`../frontend/`,
   served at `/ui`), but nothing about the API assumes that particular
   client. Every endpoint returns plain JSON; a different UI can consume
   the same routes unchanged.
4. **Auth** — none exists. If added later, put it in FastAPI middleware /
   route dependencies without touching the service layer.

## Explicit non-goals (per hackathon prototype scope)

No authentication, login, users, permissions, report generation,
notifications, Docker, or cloud deployment. The focus is the scientific
processing pipeline, the Gaia data model, and a clean, swappable backend
architecture around both — not production styling or infrastructure.

## API summary

**Live pipeline** (operates on an uploaded sample):

| Method | Path | Purpose |
|---|---|---|
| POST | `/upload` | Validate + parse a FASTA/CSV/TXT file, store the sample |
| POST | `/preprocess` | Clean/normalize sequences, detect markers, extract features |
| POST | `/identify` | Placeholder taxonomic identification |
| POST | `/classify` | Placeholder ecological category classification |
| POST | `/assess` | Biodiversity metrics + ecological assessment |
| POST | `/analyze` | Runs the entire pipeline end-to-end, returns the aggregated result |
| GET | `/status` | Engine status — sample/prediction counts *and* seed dataset counts |
| GET | `/status/{sample_id}` | Pipeline status for one sample |
| GET | `/history` | All aggregated predictions produced so far |

**Explore API** (read-only, over the synthetic Gaia dataset in `data/seed/`):

| Method | Path | Purpose |
|---|---|---|
| GET | `/biospheres` `/biomes` `/terrains` `/ecosystems` `/locations` `/sampling-sites` | Environment hierarchy |
| GET | `/organisms` `/organisms/{id}` | List/filter or fetch one organism (`?kingdom=` `?habitat_type=` `?native_status=`) |
| GET | `/taxonomy` | Taxonomic records (`?kingdom=`) |
| GET | `/samples` `/samples/{id}` `/identifications` | Seed-side samples and identifications |
| GET | `/biodiversity/metrics` `/biodiversity/assessments` | Diversity indices and ecological findings (`?sample_id=`) |
| GET | `/population` `/population/{organism_id}` `/population/{organism_id}/timeseries` | Population assessments (bulk list, one, or its 2020-2026 timeseries) |
| GET | `/habitat` `/habitat/{organism_id}` | Habitat loss/quality/fragmentation (bulk list or one) |
| GET | `/threats` `/threats?organism_id=` `/threats?ecosystem_id=` | Threat records |
| GET | `/conservation` `/conservation/{organism_id}` | Conservation status (deliberately Unknown/Data Deficient — see `data/README.md`) |
| GET | `/risk` `/risk/{organism_id}` | Gaia Prototype Risk Score — `/risk/{id}` recomputes **live** via `GaiaRiskEngine`, not just echoed from the seed |
| GET | `/species/{organism_id}` | Full risk profile: organism + taxonomy + population + habitat + threats + conservation + risk, in one call |
| GET | `/analysis` `/analysis/{id}` | Seed-side aggregated analysis records |
| GET | `/dashboard/summary` | Totals, risk/biodiversity/kingdom/conservation distributions, top 10 highest-risk species |

Full request/response examples: [`../docs/API.md`](../docs/API.md).
