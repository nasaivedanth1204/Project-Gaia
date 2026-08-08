"""Gaia Prototype Risk Score.

This is a PROTOTYPE scoring heuristic over synthetic evidence. It is
deliberately NOT called an IUCN score and does not produce an official
conservation category — see spec sections 27, 30 and 45.

The score is 0-100 and always explainable: every point is attributable to
a named component, and every component carries the evidence that produced
it. Weights are configuration (data/seed/risk_weights.json), not code.

The same function is re-exported by backend/assessment/risk_engine.py so
the seed generator and the running backend cannot drift apart.
"""

from typing import Any, Dict, List, Optional

DEFAULT_WEIGHTS = {
    "population_decline": 0.30,
    "population_size": 0.15,
    "habitat_loss": 0.20,
    "range_restriction": 0.15,
    "threat_pressure": 0.20,
}

RISK_LEVELS = [
    (85, "Critical Risk"),
    (70, "Very High Risk"),
    (55, "High Risk"),
    (35, "Moderate Risk"),
    (15, "Low Risk"),
    (0, "Minimal Risk"),
]

INDICATOR_LEVELS = [(75, "VERY_HIGH"), (50, "HIGH"), (25, "MODERATE"), (0, "LOW")]


def _indicator(value: Optional[float]) -> str:
    if value is None:
        return "UNKNOWN"
    for threshold, label in INDICATOR_LEVELS:
        if value >= threshold:
            return label
    return "LOW"


def _risk_level(score: Optional[float], confidence: float) -> str:
    if score is None or confidence < 0.2:
        return "Insufficient Data"
    for threshold, label in RISK_LEVELS:
        if score >= threshold:
            return label
    return "Minimal Risk"


def _population_size_pressure(mature: Optional[int]) -> Optional[float]:
    """Smaller populations imply higher risk. Returns 0-100 or None."""
    if mature is None:
        return None
    if mature < 250:
        return 100.0
    if mature < 1000:
        return 85.0
    if mature < 2500:
        return 70.0
    if mature < 10000:
        return 45.0
    if mature < 50000:
        return 25.0
    return 10.0


def compute_gaia_risk(
    population: Dict[str, Any],
    habitat: Optional[Dict[str, Any]],
    threats: List[Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Compute the Gaia Prototype Risk Score from assessment records.

    Components that have no supporting evidence are excluded from the
    weighted average rather than being scored as zero — a species with no
    population data must not look 'safe' purely because data is missing.
    That is also why `risk_confidence` reports the fraction of the total
    weight that was actually backed by evidence.
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    rng = population.get("geographic_range") or {}

    decline = population.get("population_decline_percent")
    mature = population.get("estimated_mature_individuals")
    habitat_loss = habitat.get("habitat_loss_percent") if habitat else None
    range_reduction = rng.get("range_reduction_percent")
    fragmentation = rng.get("range_fragmentation")

    frag_bonus = {"Severe": 25.0, "High": 15.0, "Moderate": 7.0}.get(fragmentation, 0.0)
    range_pressure = None
    if range_reduction is not None:
        range_pressure = min(100.0, range_reduction + frag_bonus)

    if threats:
        sev_map = {"Critical": 100.0, "High": 75.0, "Moderate": 45.0, "Low": 20.0}
        scored = [sev_map.get(t.get("severity"), 20.0) for t in threats]
        # Mean severity, nudged upward when several threats act together.
        threat_pressure = min(100.0, sum(scored) / len(scored) + 5.0 * (len(threats) - 1))
    else:
        threat_pressure = None

    raw = {
        "population_decline": decline,
        "population_size": _population_size_pressure(mature),
        "habitat_loss": habitat_loss,
        "range_restriction": range_pressure,
        "threat_pressure": threat_pressure,
    }

    # Missing components contribute 0, not "no penalty and no credit": if a
    # component were instead dropped from the denominator (re-normalising
    # over only the evidence present), a single thin data point could
    # single-handedly drive the score to 100 — e.g. one "Critical" threat
    # record on an otherwise-undocumented organism. Absence of evidence
    # must pull the score down, never inflate it. risk_confidence (evidence
    # weight actually observed, out of total weight) is what flags that the
    # score rests on incomplete evidence — the score itself stays honest.
    components: Dict[str, float] = {}
    evidence_weight = 0.0
    weighted_total = 0.0
    for name, value in raw.items():
        weight = w.get(name, 0.0)
        if value is None:
            continue
        contribution = value * weight
        components[name] = round(contribution, 2)
        weighted_total += contribution
        evidence_weight += weight

    if evidence_weight == 0:
        score: Optional[int] = None
        confidence = 0.0
    else:
        score = int(round(min(100.0, weighted_total)))
        confidence = round(evidence_weight / sum(w.values()), 2)

    indicators = {
        "population_decline": _indicator(decline),
        "population_size": _indicator(raw["population_size"]),
        "geographic_range": _indicator(range_pressure),
        "habitat_loss": _indicator(habitat_loss),
        "fragmentation": (
            "UNKNOWN" if fragmentation in (None, "Unknown")
            else {"Severe": "VERY_HIGH", "High": "HIGH",
                  "Moderate": "MODERATE", "Low": "LOW", "None": "LOW"}[fragmentation]
        ),
        "threat_pressure": _indicator(threat_pressure),
    }

    return {
        "gaia_risk_score": score,
        "risk_level": _risk_level(score, confidence),
        "risk_confidence": confidence,
        "score_components": components,
        "risk_indicators": indicators,
        "explanation": explain_risk(raw, indicators, threats, fragmentation, score),
        "score_name": "Gaia Prototype Risk Score",
        "score_disclaimer": (
            "Prototype heuristic over synthetic evidence. Not an IUCN score "
            "and not an official extinction risk assessment."
        ),
    }


def explain_risk(
    raw: Dict[str, Optional[float]],
    indicators: Dict[str, str],
    threats: List[Dict[str, Any]],
    fragmentation: Optional[str],
    score: Optional[int],
) -> List[str]:
    """Turn indicators into statements that cite their own evidence.

    Every sentence references the value that produced it. Nothing is
    asserted that is not present in the input records (spec section 34).
    """
    lines: List[str] = []

    decline = raw["population_decline"]
    if decline is None:
        lines.append("No population trend evidence is available, so decline could not be assessed.")
    elif decline >= 50:
        lines.append(f"Population trend indicates severe decline ({decline}% in the synthetic record).")
    elif decline >= 25:
        lines.append(f"Population trend indicates sustained decline ({decline}% in the synthetic record).")
    elif decline > 5:
        lines.append(f"Population shows a modest decline ({decline}% in the synthetic record).")
    else:
        lines.append("Population appears stable in the synthetic record.")

    size = raw["population_size"]
    if size is None:
        lines.append("No population size estimate is available; eDNA detection alone does not "
                     "provide one.")
    elif size >= 85:
        lines.append("The estimated mature population is very small, which raises risk independently "
                     "of trend.")
    elif size >= 45:
        lines.append("The estimated mature population is small enough to be a contributing risk factor.")

    loss = raw["habitat_loss"]
    if loss is not None and loss >= 40:
        lines.append(f"Significant habitat reduction is present in the synthetic dataset ({loss}% lost).")
    elif loss is not None and loss >= 20:
        lines.append(f"Moderate habitat reduction is recorded ({loss}% lost).")

    if fragmentation in ("Severe", "High"):
        lines.append(f"The recorded population is geographically fragmented ({fragmentation.lower()} "
                     "fragmentation).")

    if threats:
        names = ", ".join(sorted({t["threat_name"] for t in threats}))
        if len(threats) >= 3:
            lines.append(f"Multiple ongoing environmental pressures are present ({names}).")
        else:
            lines.append(f"Environmental pressure recorded from: {names}.")
    else:
        lines.append("No threat records are associated with this organism in the synthetic dataset.")

    unknowns = [k for k, v in indicators.items() if v == "UNKNOWN"]
    if unknowns:
        lines.append("Evidence is missing for: " + ", ".join(sorted(unknowns)) +
                     ". The score is computed only from the evidence that exists.")

    if score is None:
        lines.append("Insufficient evidence to produce a Gaia Prototype Risk Score.")

    return lines
