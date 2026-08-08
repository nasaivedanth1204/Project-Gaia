# Project Gaia

An AI-powered platform for **eDNA taxonomy identification and biodiversity
assessment** — built for the Smart India Hackathon problem statement
*"Identifying Taxonomy and Assessing Biodiversity from eDNA Datasets."*

The pipeline takes raw environmental DNA sequences and returns taxonomic
assignments, ecological categories, biodiversity metrics, and confidence
scores. It extends into a full conservation-assessment workflow —
terrain/ecosystem/biosphere, population, habitat, threats, conservation
status, extinction risk, and a Gaia Prototype Risk Score — over a
synthetic demonstration dataset (see `data/README.md`):

```
Upload -> Validation -> Preprocessing -> Taxonomic Identification
      -> Classification -> Terrain / Ecosystem / Biosphere
      -> Biodiversity Assessment -> Population -> Habitat -> Threats
      -> Conservation Analysis -> Extinction Risk -> Gaia Risk Score
      -> Final Analysis -> Dashboard
```

## Quick start

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

| URL | What |
|---|---|
| http://127.0.0.1:8000/ui | Two tabs: **Biodiversity Dashboard** (browse the synthetic dataset — species, risk scores, distributions) and **Live Pipeline** (upload a file, or click **Use Demo Dataset**, and watch it run) |
| http://127.0.0.1:8000/docs | Interactive OpenAPI reference |

## Repository layout

```
Project-Gaia/
├── backend/     FastAPI processing engine (see backend/README.md)
├── frontend/    Single-file prototype UI, served by the backend at /ui
├── data/        Dataset manifests & metadata (see data/README.md)
├── docs/        API reference and session history
└── CLAUDE.md    Standing instructions for Claude Code sessions
```

### `backend/`

Two things share one FastAPI app and one repository instance:

- **Live pipeline** (`routes/` → `controllers/` → `services/` → engines:
  `preprocessing/`, `identification/`, `classification/`, `assessment/`,
  `confidence/`, `aggregation/`) — processes one uploaded sample
  end-to-end. All domain-specific biology here is a placeholder marked
  with `# TODO` where a real ML model or reference database belongs.
- **Explore API** (`services/explore_service.py` → `explore_controller.py`
  → `explore_routes.py`) — read-only access to the synthetic Gaia dataset
  below, including a Gaia Prototype Risk Score computed live via
  `assessment/risk_engine.py`.

Persistence sits behind an `IDataRepository` interface (`dependencies.py`)
so the database can be chosen later without touching either side.

### `frontend/`

One self-contained `index.html` — no build step, no npm, no external
assets. The backend mounts it at `/ui`. Two tabs: Biodiversity Dashboard
(Explore API) and Live Pipeline (upload flow).

### `data/`

Two things: dataset **manifests** for the real eDNA data plan (raw reads
and reference databases are GB-scale and excluded by `data/.gitignore` —
GitHub rejects files over 100 MB, and git retains every version forever;
contributors download those to disk locally), and `data/seed/` — a
complete **synthetic** demonstration dataset (~1,178 interconnected
records: organisms, populations, threats, conservation status, risk
scores) that *is* committed, since it's the whole point of the demo. See
`data/README.md` for the critical distinction between the two.

## Documentation

| Document | Contents |
|---|---|
| [`backend/README.md`](backend/README.md) | Architecture, module map, where ML models and databases plug in |
| [`docs/API.md`](docs/API.md) | Every endpoint with example requests and responses |
| [`data/README.md`](data/README.md) | Dataset sources, structure, and workflow |
| [`docs/SESSION_LOG.md`](docs/SESSION_LOG.md) | Running history of changes |

## Status

Prototype. The full pipeline and API are implemented and working
end-to-end; the scientific engines are placeholders behind stable
interfaces, pending ML model integration.
