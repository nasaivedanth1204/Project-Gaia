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

## 2026-08-08 (rework: connect the Gaia data model to the running app)

- Audited the existing app before changing anything: the seed database
  from the previous session (23 collections, ~1,178 records) validated
  and existed on disk, but the running FastAPI app never loaded it —
  `dependencies.py::get_repository()` returned a fresh, unseeded
  repository, so there was zero API surface for organisms, ecosystems,
  population, threats, conservation, or the Gaia Risk Score. The
  frontend had no UI for any of it either. That gap was the actual work.
- Wired `get_repository()` to seed itself from `data/seed/` on creation
  (graceful no-op if seed files are absent). The live upload pipeline and
  the Gaia dataset now share one repository instance — uploaded-sample
  storage and seed-collection storage use disjoint internal keys, so
  neither can collide with the other. Verified both together via
  `/status` (reports sample/prediction counts and seed collection counts)
  and by running the old upload->analyze flow unchanged after the wiring.
- Added a read-only **Explore API** on top of the existing layered
  pattern (`services/explore_service.py` -> `explore_controller.py` ->
  `explore_routes.py`, wired into the existing `dependencies.py`/`app.py`):
  environment hierarchy, organisms/taxonomy (filterable), samples/
  identifications, biodiversity metrics/assessments, population (+
  timeseries), habitat, threats, conservation, and two composite
  endpoints — `/species/{id}` (full risk profile in one call) and
  `/dashboard/summary` (totals + distributions + top-10 highest-risk
  species). `/risk/{id}` and `/species/{id}` recompute the Gaia Prototype
  Risk Score **live** via `GaiaRiskEngine` rather than only echoing the
  seed value, proving the engine is a real callable component.
- Extended `frontend/index.html` (not rebuilt) with tab navigation:
  **Biodiversity Dashboard** (new, now the default view — summary tiles,
  CSS distribution bars for risk/biodiversity/kingdom/conservation,
  a filterable/searchable 49-species table, click-through detail panel
  with population/habitat/threats/conservation/risk explanation) and
  **Live Pipeline** (the existing upload flow, unchanged).
- Caught and fixed a real display bug during review: the species detail
  title inherited the site's uppercase heading style, which reads badly
  for scientific names (should be italic, not caps) — fixed with a
  targeted override.
- Verified end-to-end in a headless browser: dashboard loads by default
  and matches the API exactly (top risk species Ardeotis nigriceps score
  85 "Critical Risk", 49/49 species, 4 distribution panels); kingdom and
  risk-level filters and free-text search all work; species detail loads
  live data including the microbial edge case (`habitat: null` renders
  "Not assessed" instead of crashing); tab switching works both ways and
  the old Live Pipeline demo still completes with zero regressions; zero
  JS errors; no horizontal overflow at mobile width (390px).
- Updated `backend/README.md` (fixed stale "no frontend"/"no dashboards"
  claims, added the Explore API to the module map and API summary),
  `docs/API.md` (new Explore API section with live-captured examples),
  `data/README.md` (fixed a stale claim that the live pipeline and seed
  dataset were "two parallel demonstrations" — they now share one
  repository), and the root `README.md` (updated workflow diagram and
  repository layout description).

## 2026-08-08 (frontend reorganization: scientific IA + visual system)

- Reworked `frontend/index.html` from a 2-tab dashboard into a full
  application shell per the requested information architecture: sidebar
  navigation across 8 pages (Dashboard, Samples, Analysis, Taxonomy,
  Biodiversity, Conservation, Risk Assessment, History), each with a
  single clear purpose and progressive disclosure (primary info visible,
  secondary info one click away) rather than dumping every field at once.
- Replaced the dark neon theme with a restrained scientific palette:
  deep forest green sidebar, off-white content, slate text; color used
  only to carry meaning (positive/warning/critical/neutral/info), never
  decoration. No gradients, no glassmorphism, no giant marketing headings.
- Reused rather than rebuilt: the upload/6-stage-pipeline flow now lives
  inside the Analysis page (restyled, logic untouched); the species
  detail/risk-explanation rendering patterns from the previous dashboard
  became the basis for the new speciesMiniCard/risk-breakdown components.
- Added two small backend endpoints (`GET /population`, `GET /habitat`,
  bulk list) mirroring the existing `/risk` and `/conservation` bulk-list
  pattern — needed so the Conservation table can join client-side without
  49 individual requests.
- Built genuinely reusable component functions (not files, since this is
  still a single-file app by design): metricCard, statusBadge,
  confidenceBadge, riskBadge, conservationBadge, trendBadge,
  severityBadge, sectionHeader classes, emptyState/loadingState/errorBox,
  distributionList, speciesMiniCard, a collapsible taxonomyTree (kingdom
  through species via native `<details>`), and a unified
  renderAnalysisDetail() that handles both the seed analysis_results
  shape and the live /analyze pipeline shape in one function.
- Every "unknown" case renders honestly (`Unknown` / `Not assessed` /
  `Insufficient data`), never a fabricated number — verified directly:
  the Conservation table shows real "Not assessed" habitat cells for
  bacteria/archaea with no habitat_assessments record, and the Risk page
  shows "Insufficient data" per-factor (not a zero-length bar, which
  would misleadingly look like "no risk") when a component has no
  supporting evidence.
- Caught and fixed three real bugs during review, each verified against
  actual rendered output rather than just re-reading the code:
  1. `/risk/{id}` and `/species/{id}` never included `score_weights` in
     their response (only the seed-generation code added that field), so
     every risk-factor bar silently showed "Insufficient data" even with
     full evidence. Fixed at the shared source
     (`scripts/gaia_seed/risk.py::compute_gaia_risk`) so the seed
     generator and the live backend cannot drift apart again; regenerated
     and re-validated the seed data (still 0 errors/0 warnings).
  2. Risk factor bars were invisible: `.tone-critical` etc. were defined
     once for badges (pale tint background) and reused verbatim as a
     bar-fill class, so bars rendered in a near-invisible tint instead of
     a solid color. Added dedicated `.risk-bar-fill.tone-*` rules.
  3. The "Use Demo Dataset" button's text became invisible on hover: the
     generic `.btn:hover` rule set a dark background while
     `.btn.secondary:hover` only overrode text color to the same dark
     shade, making text and background match. Also found a mobile-only
     layout bug the same session: the sidebar's `flex: 0 0 210px` sizing
     stopped applying once `position: fixed` took over at narrow widths,
     so it computed to ~385px wide instead of 210px — "off-canvas" at
     `left: -210px` still left most of it covering the page and
     intercepting clicks on the menu toggle. Fixed both with explicit
     values instead of relying on cross-context inheritance.
  4. Also fixed two taxonomic-convention slips: a species name inherited
     a section heading's uppercase styling in the Risk detail panel, and
     a `.sci-name` italic rule was accidentally scoped to `td.sci-name`
     only, so the same species names in the Biodiversity page's
     "Frequently Dominant Species" list rendered upright instead of
     italic.
  5. The unified analysis-detail renderer assumes the seed and live
     pipeline shapes share field names for biodiversity metrics; verified
     the live shape (from `/analyze`) actually shares `species_richness`/
     `shannon_index`/`simpson_index` but lacks `biodiversity_category`/
     `pielou_evenness` — confirmed this degrades to an honest "—" rather
     than crashing or fabricating a value.
- Verified end-to-end in a headless browser after every fix: all 8 pages
  load with real data (49 organisms, 34 samples, 22 analyses, 117
  threats); every drill-down works (sample -> identifications ->
  biodiversity -> conservation -> risk; taxonomy tree -> species panel;
  conservation row -> population/habitat/threats; risk row -> score
  breakdown with bars and evidence-citing explanation); the live upload
  flow still completes and appears in History; keyboard Tab+Enter
  navigates the sidebar; zero JS errors throughout; zero horizontal
  overflow at 390px mobile width; mobile sidebar toggle confirmed
  actually functional after the width fix.
