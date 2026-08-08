#!/usr/bin/env python3
"""Load data/seed/*.json into a repository and print a summary.

    python scripts/seed_database.py

Uses the in-memory IDataRepository implementation today. Swap the
`InMemoryRepository()` line below for a real database-backed
implementation once one exists — everything else in this script is
written against the IDataRepository interface and needs no change.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

# backend/'s modules use flat imports (from interfaces..., from storage...)
# that resolve relative to backend/ itself — the same way `uvicorn app:app`
# already runs it from that directory. Prepending it here lets this script
# import those modules from anywhere in the repo.
sys.path.insert(0, str(BACKEND_DIR))

from storage.in_memory_repository import InMemoryRepository  # noqa: E402
from storage.seed_loader import SeedNotFoundError, seed_repository  # noqa: E402


def main() -> int:
    repository = InMemoryRepository()
    try:
        counts = seed_repository(repository)
    except SeedNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Seeded {len(counts)} collections into {type(repository).__name__}:\n")
    width = max(len(c) for c in counts)
    for collection, count in sorted(counts.items()):
        print(f"  {collection:<{width}}  {count:>5}")
    print(f"\n  {'TOTAL':<{width}}  {sum(counts.values()):>5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
