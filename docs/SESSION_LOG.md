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
- Reorganized the repository into `backend/ frontend/ data/ docs/`:
  - `Datasets/` -> `data/` (chose `data/` over lowercase `datasets/`
    deliberately — a case-only rename is unreliable on macOS/Windows
    checkouts).
  - `backend/docs/API.md` -> `docs/API.md`; this log -> `docs/SESSION_LOG.md`
    (`CLAUDE.md` updated to point at the new path).
  - Consolidated ignores into a root `.gitignore`, removed
    `backend/.gitignore`; `data/.gitignore` stays put since its rules are
    specific to that directory.
  - Deleted a stray 1-byte `DATASETS` file left at the repo root.
  - Rewrote the root `README.md` as a real entry point (layout map, quick
    start, doc index) and fixed every cross-reference the moves broke.
  - Left `backend/`'s Python module layout untouched on purpose — the flat
    imports work and repackaging them would risk a working demo for no
    functional gain. All moves recorded by git as renames, so history is
    preserved; re-verified the API and UI end-to-end afterwards.

## 2026-08-08 (later)

- Built a comprehensive synthetic seed database for the full Gaia data
  model: 23 interconnected collections (~1,178 records) covering the
  environment hierarchy (biosphere -> biome -> terrain -> ecosystem ->
  location -> sampling site), the biological chain (sample -> DNA
  sequence -> identification -> organism -> taxonomy), and the
  conservation chain (population -> habitat -> threats -> conservation
  status -> extinction risk -> Gaia Prototype Risk Score).
- Generator lives in `scripts/gaia_seed/` (reference.py = curated spine:
  real taxonomic names, India-focused locations, threat catalogue, and 16
  named risk/biodiversity scenarios pinned to specific organisms/sites;
  build.py = deterministic derivation of every other collection; risk.py =
  the Gaia Prototype Risk Score, shared with the backend so the two can't
  drift apart). Output: `data/seed/*.json`, regenerated via
  `scripts/generate_seed_data.py`.
- Every record carries provenance (`is_synthetic`, `is_mock`,
  `is_mock_prediction`, `source_type`, `source`); no record claims a real
  detection, and `conservation_status` deliberately reports Unknown/Data
  Deficient rather than inventing an official category.
- Caught and fixed a real scoring bug during review: normalizing the risk
  score only by the evidence present let a single thin data point (e.g.
  one threat record on an undocumented bacterium) spike the score to 100.
  Fixed so missing evidence lowers `risk_confidence` instead of inflating
  the score — verified against the actual generated data, not just
  reasoned about.
- Extended `IDataRepository` with generic `save_records/get_record/
  list_records/count_records/list_collections` plus named
  `save_organism/get_organism/save_analysis/get_analysis/save_assessment/
  get_assessment` accessors, implemented in `InMemoryRepository`. Existing
  sample-pipeline methods untouched.
- Added `backend/storage/seed_loader.py` (load seed JSON into any
  repository) and `backend/assessment/risk_engine.py` (`GaiaRiskEngine`,
  wraps the shared risk module behind `IRiskEngine`).
- Added `scripts/validate_seed_data.py` (16 rule families: duplicate IDs,
  dangling references, taxonomy completeness, confidence/percentage/
  probability ranges, enum validity, missing synthetic flags, coordinate
  bounds, sequence integrity) and `scripts/seed_database.py` (loads the
  seed into a repository and prints counts).
- Verified end-to-end: generation is deterministic and passes strict
  validation with 0 errors/0 warnings; every documented example query
  (marine samples, Animalia/Bacteria filters, low-confidence
  identifications, population decline >30%, high Gaia Risk Score, etc.)
  runs correctly against the loaded repository; the risk engine re-scores
  live from repository records and matches the seed; both new JSON
  schemas validate against every real generated record with 0 mismatches;
  the existing FastAPI backend still imports and boots cleanly.
- Documented the whole system in `data/README.md` (added as a new section
  below the existing real-dataset documentation, not a replacement for
  it) and `data/schemas/` (2 representative JSON Schemas + rationale for
  not duplicating all 23 as static schema files when
  `scripts/gaia_seed/validate.py` already encodes the real constraints
  exhaustively).
