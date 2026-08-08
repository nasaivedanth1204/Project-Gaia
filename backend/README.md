# Project Gaia — eDNA Biodiversity Backend (SIH Prototype)

Backend processing engine for **"Identifying Taxonomy and Assessing Biodiversity
from eDNA Datasets."** This is a hackathon prototype: it demonstrates a
complete workflow from an uploaded eDNA dataset to a biodiversity assessment,
using placeholder scientific logic wherever a real algorithm/model/database
would normally be required.

There is intentionally **no frontend, no auth, no persistent database, and
no deployment tooling** in this codebase — see "Explicit non-goals" below.

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

## Workflow

```
Upload -> Validation -> Sequence Extraction -> Cleaning -> Preprocessing
       -> Taxonomic Identification -> Classification -> Biodiversity Assessment
       -> Confidence Calculation -> JSON Response
```

Each arrow is a pipeline stage with its own module, service, and (where
useful) interface, so any single stage can be swapped out without touching
the others.

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
3. **Frontend** — none of this repo assumes a particular client. Every
   endpoint returns plain JSON; consume it from whatever UI is built later.
4. **Auth** — none exists. If added later, put it in FastAPI middleware /
   route dependencies without touching the service layer.

## Explicit non-goals (per hackathon prototype scope)

No authentication, login, users, permissions, dashboards, report
generation, notifications, Docker, or cloud deployment. No frontend pages
or styling. The focus is exclusively the scientific processing pipeline
and a clean, swappable backend architecture around it.

## API summary

| Method | Path | Purpose |
|---|---|---|
| POST | `/upload` | Validate + parse a FASTA/CSV/TXT file, store the sample |
| POST | `/preprocess` | Clean/normalize sequences, detect markers, extract features |
| POST | `/identify` | Placeholder taxonomic identification |
| POST | `/classify` | Placeholder ecological category classification |
| POST | `/assess` | Biodiversity metrics + ecological assessment |
| POST | `/analyze` | Runs the entire pipeline end-to-end, returns the aggregated result |
| GET | `/status` | Engine-level status (sample/prediction counts) |
| GET | `/status/{sample_id}` | Pipeline status for one sample |
| GET | `/history` | All aggregated predictions produced so far |

Full request/response examples: [`../docs/API.md`](../docs/API.md).
