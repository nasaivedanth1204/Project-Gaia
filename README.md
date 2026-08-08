# Project Gaia

An AI-powered platform for **eDNA taxonomy identification and biodiversity
assessment** — built for the Smart India Hackathon problem statement
*"Identifying Taxonomy and Assessing Biodiversity from eDNA Datasets."*

The pipeline takes raw environmental DNA sequences and returns taxonomic
assignments, ecological categories, biodiversity metrics, and confidence
scores:

```
Upload -> Validation -> Preprocessing -> Taxonomic Identification
      -> Classification -> Biodiversity Assessment -> Confidence -> JSON
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
| http://127.0.0.1:8000/ui | Analysis UI — click **Use Demo Dataset** to run the pipeline with no input file |
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

The scientific pipeline, organized by concern — `routes/` → `controllers/`
→ `services/` → engines (`preprocessing/`, `identification/`,
`classification/`, `assessment/`, `confidence/`, `aggregation/`), wired
via `dependencies.py`. Persistence sits behind an `IDataRepository`
interface so the database can be chosen later, and all domain-specific
biology is a placeholder marked with `# TODO` where a real ML model or
reference database belongs.

### `frontend/`

One self-contained `index.html` — no build step, no npm, no external
assets. The backend mounts it at `/ui`.

### `data/`

Dataset **manifests**, not the datasets themselves. Raw reads and
reference databases are GB-scale and are excluded by `data/.gitignore` —
GitHub rejects files over 100 MB, and git retains every version forever.
Contributors download data to disk locally instead.

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
