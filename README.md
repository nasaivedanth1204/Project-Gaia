# Project-Gaia
Project Gaia is an AI-powered platform for eDNA taxonomy identification and biodiversity.

## Running the prototype

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open **http://127.0.0.1:8000/ui** for the analysis UI, or
`/docs` for the interactive API reference. The UI has a *Use Demo
Dataset* button, so you can run the full pipeline without supplying a
file of your own.

## Backend prototype

`backend/` contains an SIH hackathon prototype of the backend processing
engine: upload -> validation -> preprocessing -> taxonomic identification
-> classification -> biodiversity assessment -> confidence scoring -> JSON
response. It's a FastAPI service with a database-agnostic in-memory
repository and placeholder biological logic marked with `# TODO` where a
real ML model or reference database belongs. See `backend/README.md` for
setup and architecture, and `backend/docs/API.md` for endpoint
documentation and example requests/responses.
