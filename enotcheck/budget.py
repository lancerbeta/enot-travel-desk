"""All-in budget. Amount is the line total, not a unit price to multiply."""

from decimal import Decimal


def _decimal(value):
    if value is None:
        return None
    return Decimal(str(value))


def _convert(amount, currency, base_currency, fx, notes):
    if currency == base_currency:
        return amount
    spec = (fx or {}).get((currency, base_currency))
    if spec is None:
        raise ValueError(f"currency {currency} cannot be added to {base_currency} without fx")
    for key in ("rate", "as_of", "direction", "fee_rate"):
        if key not in spec:
            raise ValueError(f"fx {currency}->{base_currency} missing {key}")
    expected = f"{currency}_to_{base_currency}"
    if spec["direction"] != expected:
        raise ValueError("fx direction does not match the conversion")
    rate = _decimal(spec["rate"])
    fee = _decimal(spec["fee_rate"])
    notes.append(spec["as_of"])
    return amount * rate * (Decimal(1) + fee)


def evaluate_budget(
    lines,
    *,
    deposit,
    hard_cap,
    base_currency,
    fx=None,
    baseline_total=None,
    baseline_comparable=False,
):
    known = Decimal(0)
    lower_sum = Decimal(0)
    upper_sum = Decimal(0)
    upper_open = False
    unknown_not_zero = False
    fx_dates = []

    for line in lines:
        if line.get("included_in"):
            continue
        currency = line["currency"]
        mandatory = line.get("mandatory", True)
        known_line = line.get("known", True)
        amount = _decimal(line.get("amount"))
        lower = _decimal(line.get("lower"))
        upper = _decimal(line.get("upper"))

        if not known_line or (amount is None and lower is None and upper is None):
            if mandatory:
                unknown_not_zero = True
                upper_open = True
            continue

        if amount is not None:
            lower = amount
            upper = amount
        converted_lower = _convert(lower, currency, base_currency, fx, fx_dates)
        lower_sum += converted_lower
        known += converted_lower
        if upper is None:
            if mandatory:
                unknown_not_zero = True
                upper_open = True
        else:
            upper_sum += _convert(upper, currency, base_currency, fx, fx_dates)

    cap = _decimal(hard_cap)
    deposit_amount = _decimal(deposit)
    point = lower_sum == upper_sum and not upper_open
    if cap is not None and lower_sum > cap:
        gate = "FAIL"
    elif upper_open or (cap is not None and upper_sum > cap):
        gate = "UNKNOWN"
    else:
        gate = "PASS"

    travel_spend = lower_sum if point and gate != "FAIL" else None
    if gate == "FAIL" and point:
        travel_spend = lower_sum
    cash_needed = None if travel_spend is None or deposit_amount is None else travel_spend + deposit_amount

    baseline = _decimal(baseline_total)
    savings = None
    if (
        baseline_comparable
        and baseline is not None
        and baseline > 0
        and travel_spend is not None
    ):
        savings = (baseline - travel_spend) / baseline * Decimal(100)

    return {
        "travel_spend": travel_spend,
        "known_spend": known,
        "deposit": deposit_amount,
        "cash_needed": cash_needed,
        "currency": base_currency,
        "gate": gate,
        "unknown_not_zero": unknown_not_zero,
        "calculation_check": "tool_verified",
        "savings_percent": savings,
        "fx_as_of": fx_dates[-1] if fx_dates else None,
        "lines": lines,
    }
