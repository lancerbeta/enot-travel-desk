"""Portable snapshot checks and material invalidation."""

import copy


_SUPPORTED = ("0.2.0", "0.2.1")
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
    return {
        "compatible": not gaps,
        "gaps": gaps,
        "slot_count": len(doc.get("presented_candidate_ids") or []),
        "veto": list(brief.get("veto") or []),
        "selected_id": doc.get("selected_id"),
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
