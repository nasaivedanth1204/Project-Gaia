"""Gaia Prototype Risk Score — backend entry point.

The scoring logic lives in scripts/gaia_seed/risk.py because the seed
generator needs it too, and duplicating it would let the generated
dataset and the running backend drift apart. This module vendors that
logic into the backend package namespace and exposes it behind an
interface, so the rest of the backend never reaches into scripts/.

IMPORTANT: this is a PROTOTYPE heuristic. It is not an IUCN score and
does not produce an official conservation category.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from interfaces.risk_engine import IRiskEngine

_RISK_MODULE_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "gaia_seed" / "risk.py"
)


def _load_shared_risk_module():
    """Import scripts/gaia_seed/risk.py without importing the whole package.

    Loading it by path avoids putting scripts/ on sys.path for the whole
    application, which would leak generator-only modules into the backend.
    """
    if "gaia_shared_risk" in sys.modules:
        return sys.modules["gaia_shared_risk"]
    spec = importlib.util.spec_from_file_location("gaia_shared_risk", _RISK_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load shared risk module from {_RISK_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["gaia_shared_risk"] = module
    spec.loader.exec_module(module)
    return module


_risk = _load_shared_risk_module()

DEFAULT_WEIGHTS: Dict[str, float] = _risk.DEFAULT_WEIGHTS
compute_gaia_risk = _risk.compute_gaia_risk
explain_risk = _risk.explain_risk


class GaiaRiskEngine(IRiskEngine):
    """Computes the explainable Gaia Prototype Risk Score.

    TODO:
    Replace the weighted heuristic with a calibrated model once real
    population, habitat and threat data are available. The interface and
    the score_components contract should stay the same so consumers do
    not have to change.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        self._weights = {**DEFAULT_WEIGHTS, **(weights or {})}
        total = sum(self._weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Risk weights must sum to 1.0, got {total}")

    @property
    def weights(self) -> Dict[str, float]:
        return dict(self._weights)

    def score(
        self,
        population: Dict[str, Any],
        habitat: Optional[Dict[str, Any]] = None,
        threats: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        return compute_gaia_risk(population, habitat, threats or [], self._weights)
