"""Portable snapshot checks and material invalidation."""

import copy
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import yaml


_SUPPORTED = ("0.2.0", "0.2.1", "0.2.2", "0.2.3", "0.2.4")
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


def _items(value):
    return value if isinstance(value, list) else []


def _observation_date(value):
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        if len(value) == 10:
            date.fromisoformat(value)
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _legacy_report(doc, supported):
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
        for item in _items(brief.get("unresolved")):
            if not isinstance(item, dict) or not {"field", "clarification_status", "impact"} <= set(item):
                gaps.append("brief.unresolved.item")
                break
            if (item.get("clarification_status") == "user_skipped" and
                (not isinstance(item.get("field"), str) or brief.get(item["field"]) is not None)):
                gaps.append("silent_default")
    skipped = [
        item["field"]
        for item in _items(brief.get("unresolved"))
        if isinstance(item, dict) and item.get("clarification_status") == "user_skipped"
        and isinstance(item.get("field"), str)
    ]
    return {
        "compatible": not gaps,
        "gaps": gaps,
        "slot_count": len(doc["presented_candidate_ids"]) if isinstance(doc.get("presented_candidate_ids"), list) else 0,
        "veto": brief.get("veto") if isinstance(brief.get("veto"), list) else [],
        "selected_id": doc.get("selected_id"),
        "do_not_reask": skipped,
    }


STAGES = ("brief", "discovery", "verification", "decision_review", "selection",
          "planning", "operational_review", "publish")
STATUSES = ("draft", "running", "needs_input", "ready", "partial", "failed", "cancelled")
BRIEF_FIELDS = ("origins", "return_to", "dates", "duration", "party", "accommodation",
                "budget", "veto", "hard_constraints", "soft_preferences",
                "effort_tolerance", "assumptions", "unresolved", "intake_round",
                "intake_outcome")
DIMENSIONS = ("fit", "value", "logistics", "comfort", "novelty", "flexibility")


def evidence_records(value):
    """Current writer/reader shape is a list; accept legacy maps on delta."""
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def _strict_gaps(doc):
    gaps = []
    def check(condition, name):
        if not condition and name not in gaps:
            gaps.append(name)
    for key in (*_REQUIRED, "status", "preset", "candidates", "withdrawn_candidate_ids",
                "selected_id", "selection_user_basis", "evidence", "critic_results",
                "invalidation", "requires_revalidation", "artifacts"):
        check(key in doc, key)
    check(isinstance(doc.get("run_id"), str) and
          bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}_[a-z0-9-]+_\d{2}", doc.get("run_id", ""))), "run_id")
    check(isinstance(doc.get("revision"), str) and
          bool(re.fullmatch(r"r\d{2,}", doc.get("revision", ""))), "revision")
    check(doc.get("method_version") == "0.2.4", "method_version")
    check(doc.get("stage") in STAGES, "stage")
    check(doc.get("status") in STATUSES, "status")
    check(type(doc.get("selection_cycle")) is int and doc["selection_cycle"] >= 1, "selection_cycle")
    brief = doc.get("brief") if isinstance(doc.get("brief"), dict) else {}
    check(isinstance(doc.get("brief"), dict), "brief")
    for key in BRIEF_FIELDS:
        check(key in brief, "brief." + key)
    for key in ("veto", "hard_constraints", "assumptions", "unresolved"):
        check(isinstance(brief.get(key), list), "brief." + key)
    for key in ("origins", "return_to", "dates", "duration", "party", "accommodation",
                "soft_preferences", "effort_tolerance"):
        check(brief.get(key) is None or isinstance(brief.get(key), (str, list, dict)), "brief." + key)
    check(brief.get("intake_round") in ("not_offered", "offered", "closed"), "brief.intake_round")
    check(brief.get("intake_outcome") in ("not_offered", "offered", "sufficient", "answered", "skipped"),
          "brief.intake_outcome")
    for item in brief.get("unresolved") if isinstance(brief.get("unresolved"), list) else []:
        valid = (isinstance(item, dict) and isinstance(item.get("field"), str)
                 and bool(item["field"]) and isinstance(item.get("impact"), str) and bool(item["impact"])
                 and item.get("clarification_status") in ("needs_input", "offered_once", "user_skipped"))
        check(valid, "brief.unresolved.item")
        if valid and item["clarification_status"] == "user_skipped":
            check(item["field"] in brief and brief[item["field"]] is None, "silent_default")
    check(isinstance(brief.get("budget"), dict) and
          all(key in brief.get("budget", {}) for key in
              ("scope", "currency", "target_amount", "hard_cap", "included_categories", "reserve_policy")),
          "brief.budget")
    if isinstance(brief.get("budget"), dict):
        budget = brief["budget"]
        check(budget.get("scope") in ("whole_party", "per_person"), "brief.budget.scope")
        check(isinstance(budget.get("currency"), str) and bool(budget["currency"]), "brief.budget.currency")
        check(isinstance(budget.get("included_categories"), list), "brief.budget.included_categories")
        for key in ("target_amount", "hard_cap"):
            try:
                amount = budget.get(key)
                check(amount is None or (type(amount) is not bool and Decimal(str(amount)).is_finite()
                                        and Decimal(str(amount)) >= 0), "brief.budget." + key)
            except (InvalidOperation, ValueError, TypeError):
                check(False, "brief.budget." + key)
    for item in brief.get("hard_constraints") if isinstance(brief.get("hard_constraints"), list) else []:
        check(isinstance(item, dict) and all(key in item for key in
              ("id", "requirement", "origin", "applicability", "must_pass")) and
              item.get("origin") in ("user", "policy") and type(item.get("must_pass")) is bool,
              "brief.hard_constraints.item")
    check(doc.get("preset") in ("balanced", "relax", "explore", "smart_value", "group", "custom"), "preset")
    weights = doc.get("weights")
    valid_weights = isinstance(weights, dict) and set(weights) == set(DIMENSIONS)
    if valid_weights:
        try:
            numbers = [Decimal(str(weights[name])) for name in DIMENSIONS]
            valid_weights = (all(type(weights[name]) is not bool for name in DIMENSIONS)
                             and all(n.is_finite() and 0 <= n <= 100 for n in numbers)
                             and sum(numbers) == 100)
        except (InvalidOperation, ValueError, TypeError):
            valid_weights = False
    check(valid_weights, "weights")
    presented = doc.get("presented_candidate_ids")
    ids_valid = (isinstance(presented, list) and all(isinstance(i, str) and i for i in presented))
    check(ids_valid and len(presented) <= 5 and len(set(presented)) == len(presented),
          "presented_candidate_ids")
    presented = presented if ids_valid else []
    withdrawn = doc.get("withdrawn_candidate_ids")
    check(isinstance(withdrawn, list) and all(isinstance(i, str) and i in presented for i in withdrawn)
          and len(set(withdrawn)) == len(withdrawn), "withdrawn_candidate_ids")
    withdrawn = withdrawn if isinstance(withdrawn, list) else []
    candidates = doc.get("candidates")
    check(isinstance(candidates, list), "candidates")
    candidates = candidates if isinstance(candidates, list) else []
    candidate_ids = [c.get("candidate_id") for c in candidates if isinstance(c, dict)]
    check(len(candidate_ids) == len(candidates) and candidate_ids == presented, "candidates.history")
    evidence = doc.get("evidence")
    check(isinstance(evidence, list), "evidence")
    evidence = evidence if isinstance(evidence, list) else []
    eids = []
    for item in evidence:
        valid = isinstance(item, dict) and all(key in item for key in
                 ("evidence_id", "title", "claim", "value", "source_url", "authority",
                  "observed_at", "applies_to", "evidence_kind", "freshness", "limitation"))
        check(valid, "evidence.item")
        if not valid:
            continue
        for key in ("title", "claim", "authority", "limitation"):
            check(isinstance(item[key], str), "evidence." + key)
        for key in ("title", "claim", "authority"):
            check(isinstance(item[key], str) and bool(item[key].strip()), "evidence." + key)
        check(item["source_url"] is None or isinstance(item["source_url"], str), "evidence.source_url")
        check(isinstance(item["evidence_id"], str) and bool(item["evidence_id"]), "evidence.id")
        eids.append(item["evidence_id"])
        check(item["evidence_kind"] in ("primary_fact", "observed_offer", "cached_price",
                                      "estimate", "anecdote", "user_report"), "evidence.kind")
        check(item["freshness"] in ("current_for_scope", "stale", "unknown"), "evidence.freshness")
        check(_observation_date(item["observed_at"]), "evidence.observed_at")
        check(item["freshness"] != "current_for_scope" or item["observed_at"] is not None, "evidence.current_observation")
        check(isinstance(item["applies_to"], (dict, str)) and bool(item["applies_to"]), "evidence.scope")
    check(all(isinstance(i, str) for i in eids) and len(set(str(i) for i in eids)) == len(eids),
          "evidence.ids")
    def refs(value, path):
        check(isinstance(value, list) and all(isinstance(i, str) and i in eids for i in value), path)
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        check(isinstance(candidate.get("concept"), str) and bool(candidate["concept"]), "candidate.concept")
        refs(candidate.get("evidence_ids"), "candidate.evidence_ids")
        check(candidate.get("gate") in ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"), "candidate.gate")
    selected = doc.get("selected_id")
    check(selected is None or (isinstance(selected, str) and selected in presented and
                               selected not in withdrawn), "selected_id")
    if selected is not None:
        check(isinstance(doc.get("selection_user_basis"), str) and bool(doc["selection_user_basis"].strip()),
              "selection_user_basis")
        from enotcheck.selection import resolve_selection
        choice = resolve_selection(str(doc.get("selection_user_basis") or ""), presented,
                                   brief_revision=doc.get("revision"))
        check(choice["plan_allowed"] and choice["selected_id"] == selected, "selection_user_basis.explicit")
    if doc.get("stage") in ("planning", "operational_review", "publish"):
        check(selected is not None and selected in presented, "selection_required")
        check(brief.get("intake_round") == "closed", "intake_closed")
    critics = doc.get("critic_results")
    check(isinstance(critics, list), "critic_results")
    critics = critics if isinstance(critics, list) else []
    which = []
    for critic in critics:
        valid = isinstance(critic, dict) and type(critic.get("which")) is int and critic.get("which") in (1, 2)
        check(valid and critic.get("status") in ("PASS", "REPAIR", "PARTIAL") and
              isinstance(critic.get("summary"), str) and isinstance(critic.get("findings"), list),
              "critic_results.item")
        if valid:
            which.append(critic["which"])
            refs(critic.get("evidence_ids"), "critic.evidence_ids")
            for finding in critic.get("findings") if isinstance(critic.get("findings"), list) else []:
                if not isinstance(finding, dict):
                    check(False, "critic.finding")
                    continue
                refs(finding.get("evidence_ids"), "critic.finding.evidence_ids")
    check(len(set(which)) == len(which), "critic_results.duplicate")
    if doc.get("stage") in ("selection", "planning", "operational_review", "publish"):
        check(1 in which, "critic_1_required")
    check(type(doc.get("requires_revalidation")) is bool, "requires_revalidation")
    check(isinstance(doc.get("invalidation"), list) and
          all(isinstance(i, str) for i in doc.get("invalidation", [])), "invalidation")
    check(isinstance(doc.get("artifacts"), list), "artifacts")
    final = doc.get("stage") == "publish" and doc.get("status") == "ready"
    if final:
        check(doc.get("next_action") is None, "completion.next_action")
        check(2 in which, "critic_2_required")
        check(doc.get("requires_revalidation") is False, "completion.revalidation")
        check(not doc.get("invalidation"), "completion.invalidation")
        check(not any(c.get("gate") == "FAIL" for c in candidates
                      if isinstance(c, dict) and c.get("candidate_id") == selected),
              "completion.hard_fail")
        receipt = doc.get("delivery") or {}
        check(isinstance(receipt, dict) and receipt.get("checked") is True and
              receipt.get("mode") in ("files", "text_in_chat"), "completion.delivery")
    else:
        check(isinstance(doc.get("next_action"), str) and bool(doc["next_action"].strip()), "next_action")
    return gaps


def validate_snapshot(doc, supported=_SUPPORTED):
    if not isinstance(doc, dict):
        return {"compatible": False, "readable": False, "full_integrity": False,
                "gaps": ["snapshot.mapping"], "slot_count": 0, "veto": [], "selected_id": None,
                "do_not_reask": []}
    if doc.get("method_version") != "0.2.4":
        report = _legacy_report(doc, supported)
        report.update(readable=True, full_integrity=False, legacy=True,
                      integrity_gaps=_strict_gaps(doc))
        return report
    gaps = _strict_gaps(doc)
    brief = doc.get("brief") if isinstance(doc.get("brief"), dict) else {}
    return {"compatible": not gaps, "readable": True, "full_integrity": not gaps,
            "legacy": False, "gaps": gaps,
            "slot_count": len(doc["presented_candidate_ids"]) if isinstance(doc.get("presented_candidate_ids"), list) else 0,
            "veto": brief.get("veto") if isinstance(brief.get("veto"), list) else [],
            "selected_id": doc.get("selected_id"),
            "do_not_reask": [item["field"] for item in _items(brief.get("unresolved"))
                            if isinstance(item, dict) and item.get("clarification_status") == "user_skipped"
                            and isinstance(item.get("field"), str)]}


def serialize_snapshot(doc):
    """Emit accepted state, then validate the actual serialized product."""
    report = validate_snapshot(doc)
    if not report["compatible"]:
        raise ValueError("snapshot: " + ", ".join(report["gaps"]))
    text = ("# Продолжение\n\n" + _CONTINUATION_RULES + "\n\n```yaml\n" +
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False) + "```\n")
    reread = read_snapshot(text)
    if not validate_snapshot(reread)["compatible"] or reread != doc:
        raise ValueError("serialized snapshot changed accepted state")
    return text


_CONTINUATION_RULES = """Прочитайте сохранённый план ниже. Адресный вопрос не запускает новый подбор или общую анкету. Пропущенное `user_skipped` не спрашивать снова. При изменении дат сохраняйте выбранный вариант и прежние пожелания; зависимые цены, наличие, рейсы, правила и бюджет требуют повторной проверки. Старые `observed_at` не менять без нового чтения источника.

При записи следующего снимка сохраняйте машинные имена полей и типы. `stage`: brief, discovery, verification, decision_review, selection, planning, operational_review, publish. `status`: draft, running, needs_input, ready, partial, failed, cancelled. Перепроверка выбранной поездки: planning/running и конкретный `next_action`; delivery.checked=false, requires_revalidation=true. Завершённая согласованная доставка: publish/ready, next_action=null; это не бронь.

`invalidation` — список строк, подробные пояснения можно дать рядом в Markdown. `freshness` у Evidence: current_for_scope, stale, unknown. Ссылка на свидетельство — существующий evidence_id; поле типа — evidence_kind. `brief.unresolved` — список объектов с field, clarification_status (needs_input, offered_once, user_skipped) и impact. Пропущенное поле присутствует в brief со значением null. Не заменять эти машинные значения русскими или новыми enum; пояснения пишите отдельно. Не сочинять IDs, веса, результаты критиков или историю. Все три файла и ZIP прежней ревизии становятся историческими после изменения дат; их готовность не переносится автоматически."""


def read_snapshot(text):
    match = re.search(r"(?ms)^```yaml\s*\n(.*?)^```\s*$", text)
    if not match:
        return _read_legacy_export(text)
    doc = yaml.safe_load(match.group(1))
    if not isinstance(doc, dict):
        raise ValueError("snapshot requires a mapping")
    return doc


def _read_legacy_export(text):
    """Read only the historical renderer's known Markdown shape, no invented IDs."""
    if not text.startswith("# Продолжение") or "\nrun_id:" not in text:
        raise ValueError("unrecognized snapshot format; retain text for assisted recovery")
    doc, brief = {}, {}
    section = "header"
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:]
            continue
        if section in ("Evidence", "Critics"):
            doc.setdefault("legacy_" + section.lower() + "_text", "")
            doc["legacy_" + section.lower() + "_text"] += line + "\n"
            continue
        if section == "Brief" and line.startswith("- ") and " | " in line:
            parts = line[2:].split(" | ", 2)
            if len(parts) == 3:
                brief.setdefault("unresolved", []).append(dict(zip(
                    ("field", "clarification_status", "impact"), parts)))
            continue
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not match:
            continue
        key, raw = match.groups()
        target = brief if section == "Brief" else doc
        if raw == "не передано":
            continue
        value = None if raw in ("None", "null", "не задано") else raw
        if key in ("veto", "assumptions", "presented_candidate_ids", "withdrawn_candidate_ids", "invalidation", "artifacts"):
            value = [] if raw in ("нет", "") else raw.split(", ")
        elif key in ("selection_cycle",) and raw.isdigit():
            value = int(raw)
        elif key == "requires_revalidation" and raw in ("True", "False"):
            value = raw == "True"
        elif key == "unresolved":
            value = []
        target[key] = value
    doc["brief"] = brief
    return doc


def apply_delta(state, kind):
    updated = copy.deepcopy(state)
    updated["invalidation"] = list(_AFFECTED[kind])
    material = kind in ("dates", "party")
    updated["recheck_pending"] = material
    updated["requires_revalidation"] = bool(updated.get("selected_id")) and material
    if material:
        for item in evidence_records(updated.get("evidence")):
            item["freshness"] = "stale"
    if updated.get("method_version") == "0.2.4":
        updated["stage"] = "planning" if updated.get("selected_id") else "discovery"
        updated["status"] = "running"
        updated["next_action"] = ("recheck " if material else "update ") + ", ".join(_AFFECTED[kind])
        updated["delivery"] = None
    return updated
