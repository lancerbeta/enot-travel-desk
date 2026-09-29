"""Weighted score. Unknown dimensions stay an interval; zero weight is not a score."""

from decimal import Decimal


def _decimal(value):
    return Decimal(str(value))


def evaluate_score(weights, scores, hard_gates=None):
    parsed = {name: _decimal(value) for name, value in weights.items()}
    if sum(parsed.values()) != Decimal(100):
        raise ValueError("weights must sum to 100")
    known = Decimal(0)
    missing = Decimal(0)
    for name, weight in parsed.items():
        if weight == 0:
            continue
        raw = scores.get(name)
        if raw is None:
            missing += weight
            continue
        score = _decimal(raw)
        doubled = score * 2
        if score < 0 or score > 5 or doubled != doubled.to_integral_value():
            raise ValueError(f"score {name} is outside 0–5 step 0.5")
        known += weight * score / Decimal(5)
    failed = any(status == "FAIL" for status in (hard_gates or {}).values())
    exact = missing == 0
    return {
        "point": known if exact else None,
        "low": known,
        "high": known + missing,
        "exact": exact,
        "gate_override": "FAIL" if failed else None,
        "rank_may_override_fail": False,
    }


def sensitivity(weights, scores):
    parsed = {name: _decimal(value) for name, value in weights.items()}
    nonzero = [name for name, weight in parsed.items() if weight != 0]
    if len(nonzero) < 2:
        return {
            "claimed": False,
            "reason": "single_nonzero_weight",
            "scenarios": [],
        }
    scenarios = []
    for name in nonzero:
        for sign in (Decimal("0.2"), Decimal("-0.2")):
            shifted = dict(parsed)
            shifted[name] = shifted[name] * (Decimal(1) + sign)
            if shifted[name] <= 0 or shifted[name] >= 100:
                scenarios.append({"weight": name, "delta": str(sign), "valid": False})
                continue
            others = [item for item in nonzero if item != name]
            pool = sum(shifted[item] for item in others)
            target_rest = Decimal(100) - shifted[name]
            running = Decimal(0)
            for index, item in enumerate(others):
                if index == len(others) - 1:
                    shifted[item] = target_rest - running
                else:
                    piece = (shifted[item] / pool * target_rest).quantize(Decimal("0.0001"))
                    shifted[item] = piece
                    running += piece
            scored = evaluate_score(shifted, scores)
            scenarios.append(
                {
                    "weight": name,
                    "delta": str(sign),
                    "valid": True,
                    "low": scored["low"],
                    "high": scored["high"],
                }
            )
    return {"claimed": True, "reason": "tool_verified", "scenarios": scenarios}
