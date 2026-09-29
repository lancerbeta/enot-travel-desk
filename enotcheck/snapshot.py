"""Portable snapshot checks and material invalidation."""

import copy


_SUPPORTED = ("0.2.0", "0.2.1", "0.2.2", "0.2.3")
_BRIEF_022 = ("origins", "dates", "party", "budget", "veto", "assumptions", "unresolved")
_REQUIRED = (
    "run_id",
    "revision",
    "method_version",
    "stage",
    "brief",
    "weights",
    "selection_cycle",
    "presented_candidate_ids",
    "next_action",
)
_AFFECTED = {
    "dates": ["transport", "lodging", "events", "applicable_rules", "budget"],
    "party": ["quotas", "rooms", "costs", "conditions"],
    "weights": ["ranking"],
    "presentation": ["presentation_only"],
}


def validate_snapshot(doc, supported=_SUPPORTED):
    gaps = [key for key in _REQUIRED if key not in doc]
    brief = doc.get("brief") if isinstance(doc.get("brief"), dict) else {}
    if "veto" not in brief:
        gaps.append("brief.veto")
    version = doc.get("method_version")
    if version not in supported and "method_version" not in gaps:
        gaps.append("method_version")
    if version in ("0.2.2", "0.2.3"):
        for key in _BRIEF_022:
            if key not in brief:
                gaps.append(f"brief.{key}")
        if "status" not in doc:
            gaps.append("status")
        for item in brief.get("unresolved") or []:
            if not isinstance(item, dict) or not {"field", "clarification_status", "impact"} <= set(item):
                gaps.append("brief.unresolved.item")
                break
            if item.get("clarification_status") == "user_skipped" and brief.get(item.get("field")) is not None:
                gaps.append("silent_default")
    skipped = [
        item["field"]
        for item in brief.get("unresolved") or []
        if isinstance(item, dict) and item.get("clarification_status") == "user_skipped"
    ]
    return {
        "compatible": not gaps,
        "gaps": gaps,
        "slot_count": len(doc.get("presented_candidate_ids") or []),
        "veto": list(brief.get("veto") or []),
        "selected_id": doc.get("selected_id"),
        "do_not_reask": skipped,
    }


def apply_delta(state, kind):
    updated = copy.deepcopy(state)
    updated["invalidation"] = list(_AFFECTED[kind])
    material = kind in ("dates", "party")
    updated["recheck_pending"] = material
    updated["requires_revalidation"] = bool(updated.get("selected_id")) and material
    if material:
        for item in updated.get("evidence", {}).values():
            item["freshness"] = "stale"
    return updated
