"""One optional round; the LLM supplies material gaps, this seam persists them."""

import copy

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
        "intake_round": brief.get("intake_round", "closed"),
    }


def offer_intake(brief, useful_gaps, *, no_questions=False):
    """Offer only unknown fields. Gap relevance is decided by the travel actor.

    A rich brief can have useful fit gaps. There is no mandatory field quota.
    A closed round cannot reopen; material scope exceptions are addressed apart.
    """
    updated = copy.deepcopy(brief)
    if updated.get("intake_round") == "closed":
        return updated, []
    if updated.get("intake_round") == "offered":
        return updated, []
    skipped = set(resume_intake(updated)["do_not_reask"])
    questions = []
    unresolved = list(updated.get("unresolved") or [])
    for gap in useful_gaps:
        field = gap["field"]
        if updated.get(field) is not None or field in skipped:
            continue
        if any(item["field"] == field for item in questions):
            continue
        mark = record_unresolved(field, "offered_once", gap["impact"])
        questions.append({**mark, "question": gap["question"]})
        updated.setdefault(field, None)
        unresolved = [item for item in unresolved if item.get("field") != field]
        unresolved.append(mark)
    updated["unresolved"] = unresolved
    updated["intake_round"] = "offered" if questions else "closed"
    updated["intake_outcome"] = "offered" if questions else "sufficient"
    if no_questions:
        return close_intake(updated, {}, continue_as_is=True), []
    return updated, questions


def close_intake(brief, answers, *, continue_as_is=False):
    """A partial answer with continue closes the same round, preserving nulls."""
    updated = copy.deepcopy(brief)
    if updated.get("intake_round") == "closed":
        return updated
    offered = [item for item in updated.get("unresolved") or []
               if item.get("clarification_status") == "offered_once"]
    for item in offered:
        field = item["field"]
        if answers.get(field) is not None:
            updated[field] = answers[field]
            updated["unresolved"] = [mark for mark in updated["unresolved"]
                                     if mark.get("field") != field]
        else:
            updated = apply_skip(updated, field, item["impact"])
    updated["intake_round"] = "closed"
    updated["intake_outcome"] = "skipped" if continue_as_is and not answers else "answered"
    return updated
