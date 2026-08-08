"""Load the synthetic seed database into any IDataRepository.

Deliberately depends only on the IDataRepository interface, so swapping
the in-memory store for MongoDB/PostgreSQL later requires no change here.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from interfaces.data_repository import IDataRepository

DEFAULT_SEED_DIR = Path(__file__).resolve().parents[2] / "data" / "seed"

# Load order follows the referential chain so a store that enforces
# foreign keys can accept the collections in sequence.
COLLECTION_ORDER: List[str] = [
    "biospheres",
    "biomes",
    "terrains",
    "ecosystems",
    "locations",
    "sampling_sites",
    "environmental_conditions",
    "samples",
    "dna_sequences",
    "taxonomy",
    "organisms",
    "classifications",
    "biodiversity_metrics",
    "analysis_results",
    "identifications",
    "biodiversity_assessments",
    "population_assessments",
    "population_timeseries",
    "habitat_assessments",
    "threat_assessments",
    "conservation_status",
    "conservation_assessments",
    "extinction_risk_assessments",
]


class SeedNotFoundError(FileNotFoundError):
    pass


def load_seed_files(seed_dir: Optional[Path] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Read every seed collection from disk."""
    directory = Path(seed_dir) if seed_dir else DEFAULT_SEED_DIR
    if not directory.is_dir():
        raise SeedNotFoundError(
            f"Seed directory not found: {directory}. "
            f"Run: python scripts/generate_seed_data.py"
        )
    dataset: Dict[str, List[Dict[str, Any]]] = {}
    for collection in COLLECTION_ORDER:
        path = directory / f"{collection}.json"
        if path.exists():
            dataset[collection] = json.loads(path.read_text())
    if not dataset:
        raise SeedNotFoundError(f"No seed collections found in {directory}")
    return dataset


def load_risk_weights(seed_dir: Optional[Path] = None) -> Dict[str, float]:
    """Read the configurable Gaia risk-score weights."""
    directory = Path(seed_dir) if seed_dir else DEFAULT_SEED_DIR
    path = directory / "risk_weights.json"
    if not path.exists():
        from assessment.risk_engine import DEFAULT_WEIGHTS
        return dict(DEFAULT_WEIGHTS)
    return {
        k: v for k, v in json.loads(path.read_text()).items()
        if not k.startswith("_")
    }


def seed_repository(
    repository: IDataRepository,
    seed_dir: Optional[Path] = None,
) -> Dict[str, int]:
    """Load the seed dataset into a repository. Returns per-collection counts."""
    dataset = load_seed_files(seed_dir)
    counts: Dict[str, int] = {}
    for collection in COLLECTION_ORDER:
        rows = dataset.get(collection)
        if rows is None:
            continue
        repository.save_records(collection, rows)
        counts[collection] = len(rows)
    return counts
