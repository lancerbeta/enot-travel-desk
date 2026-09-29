"""Evidence admission. Kind and freshness are not upgraded by silence."""


_FORBIDDEN = {
    ("cached_price", "current_inventory"),
    ("anecdote", "official_rule"),
    ("snippet", "read_terms"),
    ("estimate", "party_quota"),
    ("observed_offer", "booking"),
}


def admission(kind, claimed_proves):
    allowed = (kind, claimed_proves) not in _FORBIDDEN
    return {
        "allowed": allowed,
        "reason": "claim matches evidence kind" if allowed else "evidence kind cannot prove this claim",
    }


def group_quote(*, unit_amount, seats_priced, party_size, single_offer_covers_party):
    del unit_amount
    covers = bool(single_offer_covers_party) and int(seats_priced) >= int(party_size)
    if covers:
        return {"proves_quota": True, "evidence_kind": "observed_offer"}
    return {
        "proves_quota": False,
        "evidence_kind": "estimate",
        "note": "a unit price times the party is not simultaneous availability",
    }


def retain_observed_at(previous, proposed, *, rechecked):
    if not rechecked and proposed != previous:
        return {"observed_at": previous, "rejected_new_date": True}
    return {
        "observed_at": proposed if rechecked else previous,
        "rejected_new_date": False,
    }
