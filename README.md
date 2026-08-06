# Project-Gaia
Project Gaia is an AI-powered platform for eDNA taxonomy identification and biodiversity.

## Backend prototype

`backend/` contains an SIH hackathon prototype of the backend processing
engine: upload -> validation -> preprocessing -> taxonomic identification
-> classification -> biodiversity assessment -> confidence scoring -> JSON
response. It's a FastAPI service with a database-agnostic in-memory
repository and placeholder biological logic marked with `# TODO` where a
real ML model or reference database belongs. See `backend/README.md` for
setup and architecture, and `backend/docs/API.md` for endpoint
documentation and example requests/responses.
