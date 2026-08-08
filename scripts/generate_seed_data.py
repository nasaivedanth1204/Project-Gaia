#!/usr/bin/env python3
"""Generate the Gaia synthetic seed database into data/seed/*.json.

    python scripts/generate_seed_data.py [--out data/seed] [--seed 20260808]

Deterministic: the same seed produces byte-identical output. Regenerate
after editing scripts/gaia_seed/reference.py or build.py, then re-run
scripts/validate_seed_data.py.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gaia_seed.build import RNG_SEED, SeedBuilder  # noqa: E402
from gaia_seed.risk import DEFAULT_WEIGHTS  # noqa: E402
from gaia_seed.validate import summarize, validate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO_ROOT / "data" / "seed"),
                    help="output directory for the JSON collections")
    ap.add_argument("--seed", type=int, default=RNG_SEED, help="RNG seed")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    weights_path = out / "risk_weights.json"
    if weights_path.exists():
        weights = {
            k: v for k, v in json.loads(weights_path.read_text()).items()
            if not k.startswith("_")
        }
    else:
        weights = dict(DEFAULT_WEIGHTS)

    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        print(f"ERROR: risk weights sum to {total}, expected 1.0", file=sys.stderr)
        return 2

    print(f"Generating Gaia seed data (seed={args.seed}) ...")
    dataset = SeedBuilder(args.seed).build_all(weights)

    weights_path.write_text(json.dumps({
        "_comment": (
            "Weights for the Gaia Prototype Risk Score. Must sum to 1.0. "
            "This is a prototype heuristic, not an IUCN or official scoring system."
        ),
        **weights,
    }, indent=2) + "\n")

    for collection, rows in dataset.items():
        (out / f"{collection}.json").write_text(json.dumps(rows, indent=2) + "\n")

    print(f"\nWrote {len(dataset) + 1} files to {out}\n")
    width = max(len(c) for c in dataset)
    for collection, count in summarize(dataset):
        print(f"  {collection:<{width}}  {count:>5}")
    print(f"\n  {'TOTAL RECORDS':<{width}}  {sum(len(r) for r in dataset.values()):>5}")

    report = validate(dataset)
    print()
    if report.errors:
        print(f"VALIDATION FAILED: {len(report.errors)} error(s)")
        for err in report.errors[:20]:
            print(f"  ERROR  {err}")
        return 1
    print("Validation passed.")
    for warn in report.warnings[:10]:
        print(f"  WARN   {warn}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
