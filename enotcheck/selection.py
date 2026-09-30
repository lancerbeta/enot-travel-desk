"""Explicit selection gate. Continue, stale ids, and hard FAIL do not open PLAN."""

import re


_CONTINUE = re.compile(r"^\s*продолжай(\s+\S+)?\s*$", re.IGNORECASE)
_ID = re.compile(r"\b[cC]-\d+\b")
_DIRECT_CHOICE = re.compile(
    r"^(?:беру|выбираю|выбрал[аи]?|проработай|планируй|choose|select)\s+"
    r"(?:(?:вариант|option)\s+)?(?:№\s*)?(c-\d+)\b", re.IGNORECASE)
_CONDITIONAL = re.compile(r"\b(?:если|if|unless|при\s+условии|только\s+когда)\b", re.IGNORECASE)
_WITHDRAWN = re.compile(
    r"\b(?:передумал[аи]?|отменяю\s+(?:выбор|план)|не\s+(?:планируй|прорабатывай|беру|выбираю)|"
    r"not\s+(?:choose|select|plan)|changed\s+my\s+mind|cancel\s+(?:my\s+)?(?:choice|plan))\b"
    r"|(?:^|[.!;\n])\s*нет\b", re.IGNORECASE)


def _blocked(action, brief_revision, selected_id=None):
    return {
        "action": action,
        "plan_allowed": False,
        "selected_id": selected_id,
        "user_basis": None,
        "brief_revision": brief_revision,
    }


def resolve_selection(utterance, presented_ids, *, brief_revision, gates=None):
    """Recognize bounded direct choices; ambiguous language needs clarification.

    This mechanical guard does not replace the primary LLM's semantic review.
    """
    text = utterance.strip()
    gates = gates or {}
    if _CONTINUE.match(text):
        return _blocked("continue_current_stage", brief_revision)
    folded = text.lower()
    mentioned = [cid for cid in presented_ids
                 if re.search(r"(?<![\w-])" + re.escape(cid) + r"(?![\w-])", text, re.IGNORECASE)]
    known = {cid.lower() for cid in presented_ids}
    unknown = [token for token in _ID.findall(text) if token.lower() not in known]
    if (" или " in folded and len(mentioned) >= 2) or len(mentioned) > 1:
        return _blocked("clarify_selection", brief_revision)
    if unknown:
        return _blocked("clarify_selection", brief_revision)
    # Bare current ID is an explicit answer to the shortlist CTA. A reference,
    # recommendation, question or negation is not a choice.
    direct = _DIRECT_CHOICE.match(text)
    explicit = bool(direct) or text.lower() in known
    choice_clause = re.split(r"[.!;\n]", folded, maxsplit=1)[0]
    first_id = _ID.search(choice_clause)
    choice_prefix = choice_clause[:first_id.start()] if first_id else choice_clause
    # A separate 'do not buy/contact' instruction does not negate the choice.
    negative = bool(re.search(r"\b(?:не|not|нет)\b", choice_prefix) or
                    '?' in choice_clause or
                    re.search(r"\b(?:не\s+(?:беру|выбираю)|not\s+(?:choose|select)|нет\s*$)", choice_clause))
    uncertain = bool(_CONDITIONAL.search(text) or _WITHDRAWN.search(text))
    if len(mentioned) == 1 and explicit and not negative and not uncertain:
        chosen = mentioned[0]
        if gates.get(chosen) == "FAIL":
            return _blocked("return_to_selection", brief_revision, chosen)
        return {
            "action": "selected",
            "plan_allowed": True,
            "selected_id": chosen,
            "user_basis": text,
            "brief_revision": brief_revision,
        }
    return _blocked("clarify_selection", brief_revision)
