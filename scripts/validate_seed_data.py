#!/usr/bin/env python3
"""Validate the Gaia seed dataset in data/seed/.

    python scripts/validate_seed_data.py [--seed-dir data/seed] [--strict]

Exits non-zero if any error is found, so it can be used as a CI gate.
--strict also fails on warnings.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gaia_seed.validate import PRIMARY_KEYS, summarize, validate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_dataset(seed_dir: Path) -> dict:
    dataset = {}
    for collection in PRIMARY_KEYS:
        path = seed_dir / f"{collection}.json"
        if not path.exists():
            print(f"  MISSING  {path.name}", file=sys.stderr)
            continue
        dataset[collection] = json.loads(path.read_text())
    return dataset


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed-dir", default=str(REPO_ROOT / "data" / "seed"))
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    seed_dir = Path(args.seed_dir)
    if not seed_dir.is_dir():
        print(f"Seed directory not found: {seed_dir}", file=sys.stderr)
        print("Run: python scripts/generate_seed_data.py", file=sys.stderr)
        return 2

    dataset = load_dataset(seed_dir)
    if not dataset:
        print("No collections loaded.", file=sys.stderr)
        return 2

    weights_path = seed_dir / "risk_weights.json"
    if weights_path.exists():
        weights = {k: v for k, v in json.loads(weights_path.read_text()).items()
                   if not k.startswith("_")}
        total = sum(weights.values())
        if abs(total - 1.0) > 1e-6:
            print(f"ERROR  risk_weights.json sums to {total}, expected 1.0")
            return 1

    print(f"Validating {len(dataset)} collections in {seed_dir} ...\n")
    width = max(len(c) for c in dataset)
    for collection, count in summarize(dataset):
        print(f"  {collection:<{width}}  {count:>5}")
    print(f"\n  {'TOTAL':<{width}}  {sum(len(r) for r in dataset.values()):>5}\n")

    report = validate(dataset)
    for warn in report.warnings:
        print(f"  WARN   {warn}")
    for err in report.errors:
        print(f"  ERROR  {err}")

    print()
    if report.errors:
        print(f"FAILED — {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1
    if args.strict and report.warnings:
        print(f"FAILED (strict) — {len(report.warnings)} warning(s)")
        return 1
    print(f"PASSED — 0 errors, {len(report.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
