"""One-shot intake marks. A skipped field stays empty and is not asked again."""

_STATUSES = ("needs_input", "offered_once", "user_skipped")


def record_unresolved(field, status, impact):
    if status not in _STATUSES:
        raise ValueError(f"unknown clarification_status: {status}")
    if not field or not impact:
        raise ValueError("field and impact are required")
    return {
        "field": field,
        "clarification_status": status,
        "impact": impact,
    }


def apply_skip(brief, field, impact):
    updated = dict(brief)
    updated[field] = None
    kept = [
        item
        for item in list(updated.get("unresolved") or [])
        if not (isinstance(item, dict) and item.get("field") == field)
    ]
    kept.append(record_unresolved(field, "user_skipped", impact))
    updated["unresolved"] = kept
    return updated


def resume_intake(brief):
    skipped = []
    for item in brief.get("unresolved") or []:
        if isinstance(item, dict) and item.get("clarification_status") == "user_skipped":
            skipped.append(item["field"])
    return {
        "repeat_general_intake": False,
        "do_not_reask": skipped,
    }
