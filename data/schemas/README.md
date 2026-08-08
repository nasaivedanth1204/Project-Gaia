# Seed Data Schemas

These are documentation schemas, not a runtime validation layer — the
authoritative checks live in `scripts/gaia_seed/validate.py` and run
against the actual generated data every time it's built (see the root
`data/README.md`, section 4).

Each file here is a JSON Schema (draft 2020-12) describing one seed
collection's record shape: required fields, enums, and numeric ranges.
They exist so a consumer (a future frontend, a future real database
migration) has a single place to check "what fields does an organism
record have" without reading the generator.

`organism.schema.json` and `extinction_risk_assessment.schema.json` are
provided as representative examples — one from the biological-identity
side of the model, one from the risk-assessment side. The remaining 21
collections follow the same field names documented in the root
`data/README.md` relationship table and in `scripts/gaia_seed/build.py`.
