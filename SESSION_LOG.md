# Session Log

Running log of work done on this repo across Claude Code sessions. Each
entry is appended at the end of a session that made changes — see
`CLAUDE.md` for the standing instruction that keeps this current.

---

## 2026-08-06

- Built the full eDNA biodiversity backend prototype under `backend/`:
  FastAPI service implementing upload -> validation -> preprocessing ->
  taxonomic identification -> classification -> biodiversity assessment ->
  confidence scoring -> aggregation, per the SIH problem statement.
- Persistence abstracted behind `IDataRepository`, backed today by an
  in-memory implementation only (database not finalized).
- All domain-specific biology (taxonomy ID, classification, ecological
  assessment thresholds) implemented as placeholders with `# TODO`
  markers pointing to where real models/reference databases go.
- Smoke-tested the full pipeline end-to-end locally (upload through
  analyze, plus 400/404/409 error paths).
- Opened PR #1 (`claude/edna-biodiversity-backend-1pfvp2` -> `main`),
  currently a draft. No CI configured in the repo yet.
- Added `SESSION_LOG.md` (this file) and a `CLAUDE.md` instruction to
  keep it updated automatically going forward.

## 2026-08-07

- PR #1 merged to `main` (by repo owner via GitHub web UI).
- Noted external contributions from a teammate directly on `main`:
  `Datasets/readme.md` (documents a planned `raw/references/taxonomy/
  metadata` layout sourced from NCBI SRA, BOLD, SILVA, MitoFish, UNITE)
  and `Datasets/metadata/SRA_RunInfo.xlsx`.
- Added `Datasets/.gitignore` (excludes raw reads/reference DBs/taxonomy
  dumps — GB-scale files that must never be committed to git) and
  `Datasets/accessions.txt` (the 8 SRA run accessions already named in
  `Datasets/readme.md`, as a plain list other scripts/teammates can read).
- Decided against committing the team's actual dataset (hosted on Google
  Drive) to the repo: GitHub hard-caps files at 100 MB and git retains
  every version forever, so large files bloat the repo permanently even
  after deletion. Recommended downloading data directly to disk (e.g.
  `gdown`) and pointing the backend at the local path instead.

## 2026-08-08

- Added a prototype frontend at `frontend/index.html` — a single
  self-contained page (inline CSS/JS, no build step, no CDN assets) that
  drives the existing API: upload, live per-stage pipeline tracker,
  biodiversity metric tiles, ecological assessment cards, and a combined
  taxonomy / category / confidence table. Includes a built-in demo
  dataset button so the pipeline can be run without supplying a file.
- The stage tracker calls the real modular endpoints in sequence
  (`/preprocess` -> `/identify` -> `/classify` -> `/assess` -> `/analyze`)
  rather than faking progress, so the UI reflects the actual pipeline.
- Mounted the UI at `/ui` via `StaticFiles` in `backend/app.py` and added
  permissive CORS (flagged with a TODO to restrict before any real
  deployment) so the page also works when opened straight from disk.
- Verified in a headless browser: all 6 stages complete, tables/metrics/
  assessments populate, backend validation errors surface correctly and
  flag the failing stage, no JS errors, no horizontal overflow at mobile
  width.
