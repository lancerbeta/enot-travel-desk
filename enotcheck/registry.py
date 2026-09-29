"""Validate the source registry. It does not call providers."""

from pathlib import Path

import yaml

CORE_FAMILIES = (
    "air",
    "ground",
    "stays",
    "packages",
    "activities",
    "local_discovery",
    "official_rules",
    "maps",
)

_REQUIRED = (
    "id",
    "families",
    "roles",
    "authority_for",
    "never_proves",
    "access_modes",
    "access_requirements",
    "fallback",
    "documentary_status",
    "review_policy",
)

_BANNED_FACTS = (
    "live_price",
    "inventory",
    "schedule",
    "current_fare",
    "availability_quote",
)


def load_registry(path=None):
    target = Path(path) if path else Path(__file__).resolve().parents[1] / "config" / "sources.yaml"
    return yaml.safe_load(target.read_text(encoding="utf-8"))


def source_index(data):
    return {item["id"]: item for item in data["runtime_sources"]}


def validate_registry(data):
    errors = []
    sources = source_index(data)
    if len(sources) != len(data["runtime_sources"]):
        errors.append("duplicate runtime source id")
    research_ids = {item["id"] for item in data.get("research_register") or []}
    families = data.get("families") or {}
    for name in CORE_FAMILIES:
        spec = families.get(name)
        if not spec:
            errors.append(f"missing family {name}")
            continue
        for slot in ("baseline", "direct", "fallback"):
            source_id = spec.get(slot)
            if source_id not in sources:
                errors.append(f"{name}.{slot} missing {source_id}")
                continue
            if sources[source_id].get("optional"):
                errors.append(f"{name}.{slot} depends on an optional accelerator")
        for source_id in spec.get("accelerators") or []:
            if source_id not in sources:
                errors.append(f"{name} accelerator missing {source_id}")
            elif not sources[source_id].get("optional"):
                errors.append(f"{name} accelerator {source_id} is not optional")
    for source in sources.values():
        for key in _REQUIRED:
            if key not in source:
                errors.append(f"{source.get('id')} missing {key}")
        for banned in _BANNED_FACTS:
            if banned in source:
                errors.append(f"{source.get('id')} stores trip fact {banned}")
        fallback = source.get("fallback")
        if fallback not in sources and fallback != "terminal_unknown":
            errors.append(f"{source.get('id')} broken fallback {fallback}")
        if source.get("write_capable") and source.get("external_actions_default") != "none":
            errors.append(f"{source.get('id')} allows an external write by default")
        for ref in source.get("research_refs") or []:
            if ref not in research_ids:
                errors.append(f"{source.get('id')} unknown research ref {ref}")
    for observation in data.get("capability_observations") or []:
        for banned in _BANNED_FACTS:
            if banned in observation:
                errors.append(f"observation {observation.get('id')} stores trip fact {banned}")
    for candidate in data.get("candidates_not_enabled") or []:
        if candidate.get("enabled"):
            errors.append(f"{candidate.get('id')} candidate is enabled")
        for ref in candidate.get("research_refs") or []:
            if ref not in research_ids:
                errors.append(f"{candidate.get('id')} unknown research ref {ref}")
    return errors


def admits(source, claim):
    if claim in (source.get("never_proves") or []):
        return False
    if claim == "official_rule":
        return "official" in (source.get("roles") or [])
    if claim == "current_inventory":
        return source.get("offer_kind") != "cached" and "offer" in (source.get("roles") or [])
    if claim == "external_write":
        return source.get("external_actions_default") != "none"
    return True
