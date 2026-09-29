"""Mechanical oracles for ENOT A0+A1. Fixtures are not live offers."""

import json
import unittest
from decimal import Decimal
from pathlib import Path

from enotcheck.budget import evaluate_budget
from enotcheck.evidence import (
    admission,
    group_quote,
    retain_observed_at,
)
from enotcheck.score import evaluate_score, sensitivity
from enotcheck.selection import resolve_selection
from enotcheck.slots import new_state, open_cycle, present, withdraw
from enotcheck.snapshot import apply_delta, validate_snapshot

ROOT = Path(__file__).resolve().parents[1]
DEMO = json.loads((ROOT / "examples" / "score-demo.json").read_text(encoding="utf-8"))


def money(value):
    return Decimal(str(value))


class BudgetOracle(unittest.TestCase):
    def test_t07_preview_lines_and_deposit(self):
        lines_map = DEMO["budget"]["cost_lines"]
        lines = [
            {
                "category": name,
                "quantity": "1",
                "unit": "trip",
                "amount": str(amount),
                "currency": "RUB",
                "mandatory": True,
                "known": True,
            }
            for name, amount in lines_map.items()
        ]
        result = evaluate_budget(
            lines,
            deposit="8000",
            hard_cap="90000",
            base_currency="RUB",
        )
        self.assertEqual(result["travel_spend"], money(48000))
        self.assertEqual(result["deposit"], money(8000))
        self.assertEqual(result["cash_needed"], money(56000))
        self.assertEqual(result["gate"], "PASS")
        self.assertEqual(result["calculation_check"], "tool_verified")
        self.assertEqual(DEMO["budget"]["expected_spend"], 48000)
        self.assertEqual(DEMO["budget"]["expected_cash_needed"], 56000)

    def test_included_food_is_not_counted_twice(self):
        result = evaluate_budget(
            [
                {
                    "category": "lodging",
                    "quantity": "1",
                    "unit": "stay",
                    "amount": "24000",
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                },
                {
                    "category": "breakfast",
                    "quantity": "4",
                    "unit": "meal",
                    "amount": "3000",
                    "currency": "RUB",
                    "included_in": "lodging",
                    "mandatory": True,
                    "known": True,
                },
            ],
            deposit="0",
            hard_cap=None,
            base_currency="RUB",
        )
        self.assertEqual(result["travel_spend"], money(24000))

    def test_unknown_mandatory_is_not_zero(self):
        result = evaluate_budget(
            [
                {
                    "category": "train",
                    "quantity": "2",
                    "unit": "ticket",
                    "amount": "4000",
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                },
                {
                    "category": "local_transfer",
                    "quantity": "2",
                    "unit": "ride",
                    "amount": None,
                    "currency": "RUB",
                    "mandatory": True,
                    "known": False,
                },
            ],
            deposit="1000",
            hard_cap="20000",
            base_currency="RUB",
        )
        self.assertEqual(result["known_spend"], money(4000))
        self.assertIsNone(result["travel_spend"])
        self.assertIsNone(result["cash_needed"])
        self.assertEqual(result["gate"], "UNKNOWN")
        self.assertTrue(result["unknown_not_zero"])

    def test_lower_bound_above_cap_fails(self):
        result = evaluate_budget(
            [
                {
                    "category": "lodging",
                    "quantity": "1",
                    "unit": "stay",
                    "amount": None,
                    "lower": "100000",
                    "upper": "120000",
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                }
            ],
            deposit="0",
            hard_cap="90000",
            base_currency="RUB",
        )
        self.assertEqual(result["gate"], "FAIL")

    def test_range_crossing_cap_is_not_pass(self):
        result = evaluate_budget(
            [
                {
                    "category": "lodging",
                    "quantity": "1",
                    "unit": "stay",
                    "amount": None,
                    "lower": "40000",
                    "upper": "100000",
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                }
            ],
            deposit="0",
            hard_cap="90000",
            base_currency="RUB",
        )
        self.assertEqual(result["gate"], "UNKNOWN")
        self.assertNotEqual(result["gate"], "PASS")

    def test_currencies_are_not_summed_without_fx(self):
        with self.assertRaises(ValueError):
            evaluate_budget(
                [
                    {
                        "category": "train",
                        "quantity": "1",
                        "unit": "ticket",
                        "amount": "1000",
                        "currency": "RUB",
                        "mandatory": True,
                        "known": True,
                    },
                    {
                        "category": "fee",
                        "quantity": "1",
                        "unit": "fee",
                        "amount": "10",
                        "currency": "EUR",
                        "mandatory": True,
                        "known": True,
                    },
                ],
                deposit="0",
                hard_cap=None,
                base_currency="RUB",
            )

    def test_fx_uses_stated_rate_date_and_fee(self):
        result = evaluate_budget(
            [
                {
                    "category": "fee",
                    "quantity": "1",
                    "unit": "fee",
                    "amount": "10",
                    "currency": "EUR",
                    "mandatory": True,
                    "known": True,
                }
            ],
            deposit="0",
            hard_cap=None,
            base_currency="RUB",
            fx={
                ("EUR", "RUB"): {
                    "rate": "100",
                    "as_of": "2026-09-30",
                    "direction": "EUR_to_RUB",
                    "fee_rate": "0.02",
                }
            },
        )
        self.assertEqual(result["travel_spend"], money("1020"))
        self.assertEqual(result["fx_as_of"], "2026-09-30")

    def test_savings_percent_requires_comparable_baseline(self):
        comparable = evaluate_budget(
            [
                {
                    "category": "all",
                    "quantity": "1",
                    "unit": "trip",
                    "amount": "48000",
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                }
            ],
            deposit="8000",
            hard_cap=None,
            base_currency="RUB",
            baseline_total="60000",
            baseline_comparable=True,
        )
        self.assertEqual(comparable["savings_percent"], money(20))
        incomparable = evaluate_budget(
            [
                {
                    "category": "all",
                    "quantity": "1",
                    "unit": "trip",
                    "amount": "48000",
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                }
            ],
            deposit="0",
            hard_cap=None,
            base_currency="RUB",
            baseline_total="60000",
            baseline_comparable=False,
        )
        self.assertIsNone(incomparable["savings_percent"])


class ScoreOracle(unittest.TestCase):
    def test_t08_known_scores_are_83(self):
        weights = DEMO["weighted_score"]["weights"]
        scores = DEMO["weighted_score"]["scores"]
        result = evaluate_score(weights, scores)
        self.assertEqual(result["point"], money(83))
        self.assertTrue(result["exact"])
        self.assertEqual(result["low"], money(83))
        self.assertEqual(result["high"], money(83))

    def test_unknown_novelty_is_interval_not_two_and_half(self):
        weights = DEMO["weighted_score"]["weights"]
        scores = dict(DEMO["weighted_score"]["scores"])
        scores["novelty"] = None
        result = evaluate_score(weights, scores)
        self.assertEqual(result["low"], money(76))
        self.assertEqual(result["high"], money(86))
        self.assertFalse(result["exact"])
        self.assertIsNone(result["point"])
        self.assertNotEqual(result["low"], money("78.5"))

    def test_zero_weight_allows_missing_score_but_not_a_failed_gate(self):
        weights = {
            "fit": 35,
            "value": 20,
            "logistics": 20,
            "comfort": 20,
            "novelty": 0,
            "flexibility": 5,
        }
        scores = {
            "fit": "4",
            "value": "4",
            "logistics": "4",
            "comfort": "4",
            "novelty": None,
            "flexibility": "3",
        }
        result = evaluate_score(weights, scores, hard_gates={"party_fit": "FAIL"})
        self.assertTrue(result["exact"])
        self.assertEqual(result["gate_override"], "FAIL")
        self.assertFalse(result["rank_may_override_fail"])

    def test_sensitivity_not_claimed_for_single_nonzero_weight(self):
        weights = {
            "fit": 100,
            "value": 0,
            "logistics": 0,
            "comfort": 0,
            "novelty": 0,
            "flexibility": 0,
        }
        scores = {"fit": "5"}
        result = sensitivity(weights, scores)
        self.assertFalse(result["claimed"])
        self.assertEqual(result["reason"], "single_nonzero_weight")


class SlotsAndSelection(unittest.TestCase):
    def test_three_then_two_then_bonus_rejected(self):
        state = new_state()
        for index in range(1, 4):
            status = present(state, f"c-0{index}", f"concept-{index}")
            self.assertEqual(status, "published")
        for index in range(4, 6):
            status = present(state, f"c-0{index}", f"concept-{index}")
            self.assertEqual(status, "published")
        self.assertEqual(present(state, "c-06", "bonus"), "rejected_quota")
        self.assertEqual(len(state["presented"]), 5)

    def test_withdrawal_does_not_free_slot_and_id_is_not_recycled(self):
        state = new_state()
        present(state, "c-01", "water")
        self.assertEqual(withdraw(state, "c-01"), "withdrawn_slot_kept")
        self.assertEqual(present(state, "c-01", "mountains"), "rejected_id_reuse")
        self.assertIn("c-01", state["presented"])
        self.assertEqual(len(state["presented"]), 1)

    def test_new_cycle_needs_user_reason(self):
        state = new_state()
        for index in range(1, 6):
            present(state, f"c-0{index}", f"concept-{index}")
        self.assertEqual(open_cycle(state, ""), "rejected_no_cycle_reason")
        self.assertEqual(state["cycle"], 1)
        self.assertEqual(open_cycle(state, "хочу другие направления"), "opened")
        self.assertEqual(state["cycle"], 2)
        self.assertEqual(state["presented"], [])
        self.assertEqual(present(state, "c-01", "other"), "rejected_id_reuse")
        self.assertEqual(present(state, "c-07", "new-water"), "published")

    def test_continue_and_stale_id_do_not_start_plan(self):
        presented = ["c-01", "c-02", "c-03"]
        cont = resolve_selection("Продолжай", presented, brief_revision="r01")
        self.assertFalse(cont["plan_allowed"])
        self.assertIsNone(cont["selected_id"])
        stale = resolve_selection("беру c-09", presented, brief_revision="r01")
        self.assertEqual(stale["action"], "clarify_selection")
        self.assertFalse(stale["plan_allowed"])
        ambiguous = resolve_selection(
            "беру c-01 или c-02", presented, brief_revision="r01"
        )
        self.assertEqual(ambiguous["action"], "clarify_selection")
        self.assertFalse(ambiguous["plan_allowed"])
        chosen = resolve_selection("беру c-02", presented, brief_revision="r01")
        self.assertTrue(chosen["plan_allowed"])
        self.assertEqual(chosen["selected_id"], "c-02")
        self.assertEqual(chosen["brief_revision"], "r01")
        failed = resolve_selection(
            "беру c-02",
            presented,
            brief_revision="r01",
            gates={"c-02": "FAIL"},
        )
        self.assertFalse(failed["plan_allowed"])
        self.assertEqual(failed["action"], "return_to_selection")


class EvidencePolicy(unittest.TestCase):
    def test_cache_blog_and_split_group_are_not_upgraded(self):
        cached = admission("cached_price", "current_inventory")
        self.assertFalse(cached["allowed"])
        blog = admission("anecdote", "official_rule")
        self.assertFalse(blog["allowed"])
        snippet = admission("snippet", "read_terms")
        self.assertFalse(snippet["allowed"])
        quote = group_quote(
            unit_amount="5000",
            seats_priced=1,
            party_size=8,
            single_offer_covers_party=False,
        )
        self.assertFalse(quote["proves_quota"])
        self.assertEqual(quote["evidence_kind"], "estimate")

    def test_old_observation_does_not_receive_a_new_date(self):
        kept = retain_observed_at("2026-09-01", "2026-09-30", rechecked=False)
        self.assertEqual(kept["observed_at"], "2026-09-01")
        self.assertTrue(kept["rejected_new_date"])


class SnapshotDelta(unittest.TestCase):
    def _doc(self):
        return {
            "run_id": "2026-09-30_kazan-voda_01",
            "revision": "r01",
            "method_version": "0.2.1",
            "stage": "selection",
            "brief": {
                "dates": "2026-10-16/2026-10-18",
                "party": "2 adults",
                "budget": "70000/90000 RUB",
                "veto": ["no-car", "no-self-transfer", "no-departure-before-08:00"],
            },
            "weights": {"fit": 30, "value": 25, "logistics": 15, "comfort": 15, "novelty": 10, "flexibility": 5},
            "selection_cycle": 1,
            "presented_candidate_ids": ["c-01", "c-02"],
            "selected_id": "c-02",
            "selection_user_basis": "беру c-02",
            "next_action": "recheck selected",
        }

    def test_compatible_snapshot_keeps_slots_and_veto(self):
        report = validate_snapshot(self._doc())
        self.assertTrue(report["compatible"])
        self.assertEqual(report["slot_count"], 2)
        self.assertEqual(len(report["veto"]), 3)

    def test_missing_veto_or_future_method_is_incompatible(self):
        missing = self._doc()
        del missing["brief"]["veto"]
        self.assertFalse(validate_snapshot(missing)["compatible"])
        future = self._doc()
        future["method_version"] = "0.3.0"
        report = validate_snapshot(future)
        self.assertFalse(report["compatible"])
        self.assertIn("method_version", report["gaps"])

    def test_date_change_keeps_choice_and_marks_recheck(self):
        state = {
            "selected_id": "c-02",
            "evidence": {"e1": {"observed_at": "2026-09-01", "freshness": "current_for_scope"}},
        }
        updated = apply_delta(state, "dates")
        self.assertEqual(updated["selected_id"], "c-02")
        self.assertTrue(updated["requires_revalidation"])
        self.assertIn("budget", updated["invalidation"])
        self.assertEqual(updated["evidence"]["e1"]["observed_at"], "2026-09-01")
        self.assertEqual(updated["evidence"]["e1"]["freshness"], "stale")
        self.assertTrue(updated["recheck_pending"])


if __name__ == "__main__":
    unittest.main()
