"""Cumulative shortlist slots. Withdrawal does not return a used slot."""


def new_state():
    return {
        "cycle": 1,
        "presented": [],
        "concepts": {},
        "withdrawn": [],
        "cycle_reason": None,
    }


def present(state, candidate_id, concept):
    previous = state["concepts"].get(candidate_id)
    if previous is not None and previous != concept:
        return "rejected_id_reuse"
    if candidate_id in state["presented"]:
        return "already_shown"
    if len(state["presented"]) >= 5:
        return "rejected_quota"
    state["presented"].append(candidate_id)
    state["concepts"][candidate_id] = concept
    return "published"


def withdraw(state, candidate_id):
    if candidate_id not in state["presented"]:
        return "unknown_id"
    if candidate_id not in state["withdrawn"]:
        state["withdrawn"].append(candidate_id)
    return "withdrawn_slot_kept"


def open_cycle(state, reason):
    if reason is None or not str(reason).strip():
        return "rejected_no_cycle_reason"
    state["cycle"] += 1
    state["presented"] = []
    state["withdrawn"] = []
    state["cycle_reason"] = str(reason).strip()
    return "opened"
