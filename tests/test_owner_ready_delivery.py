"""Frozen synthetic, production-seam regressions; no model behavior claims."""

import copy
import unittest

from enotcheck.intake import offer_intake, close_intake, resume_intake
from enotcheck.selection import resolve_selection
from enotcheck.snapshot import apply_delta, read_snapshot, serialize_snapshot, validate_snapshot


def state_fixture():
    return {
        "run_id": "2026-09-30_owner-ready-synthetic_01", "revision": "r01",
        "method_version": "0.2.4", "stage": "selection", "status": "needs_input",
        "brief": {
            "origins": "Учебный город", "return_to": "Учебный город",
            "dates": "2026-11-10/2026-11-14", "duration": "4 nights", "party": "2 adults",
            "accommodation": "double / BB",
            "budget": {"scope": "whole_party", "currency": "RUB", "target_amount": "70000",
                       "hard_cap": "90000", "included_categories": ["all"], "reserve_policy": "5000"},
            "veto": ["no-car", "no-self-transfer"],
            "hard_constraints": [
                {"id": "no-car", "requirement": "Без аренды автомобиля", "origin": "user",
                 "applicability": "whole trip", "must_pass": True}],
            "soft_preferences": "Море и один короткий музей", "effort_tolerance": "немного самостоятельности",
            "assumptions": [], "unresolved": [], "intake_round": "closed", "intake_outcome": "sufficient",
        },
        "preset": "relax",
        "weights": {"fit": 35, "value": 20, "logistics": 20, "comfort": 20, "novelty": 0, "flexibility": 5},
        "selection_cycle": 1, "presented_candidate_ids": ["c-01", "c-02", "c-03"],
        "withdrawn_candidate_ids": [], "selected_id": None, "selection_user_basis": None,
        "candidates": [
            {"candidate_id": cid, "concept": concept, "gate": "UNKNOWN", "evidence_ids": ["e-01"]}
            for cid, concept in (("c-01", "Побережье"), ("c-02", "Город и море"), ("c-03", "Дом у озера"))],
        "evidence": [{"evidence_id": "e-01", "title": "Frozen synthetic packet",
                      "claim": "Учебные условия; не реальное предложение", "value": "fixture",
                      "source_url": "https://example.com/enot-synthetic", "authority": "synthetic",
                      "observed_at": "2026-09-30", "applies_to": "synthetic trip only",
                      "evidence_kind": "estimate", "freshness": "unknown", "limitation": "Not live"}],
        "critic_results": [{"which": 1, "status": "PARTIAL", "summary": "Synthetic review only",
                            "findings": [], "evidence_ids": ["e-01"]}],
        "invalidation": [], "requires_revalidation": False, "artifacts": [],
        "next_action": "Choose one current concept",
    }


class DialogAndHandoff(unittest.TestCase):
    def test_useful_fit_gaps_once_skip_partial_and_sufficient(self):
        brief = state_fixture()["brief"]
        del brief["intake_round"]
        gaps = [
            {"field": "effort_tolerance", "impact": "effort", "question": "Хлопоты?"},
            {"field": "beach_access", "impact": "fit", "question": "Пляж рядом?"},
            {"field": "baggage", "impact": "logistics", "question": "Чемодан?"}]
        offered, questions = offer_intake(brief, gaps)
        self.assertEqual([q["field"] for q in questions], ["beach_access", "baggage"])
        self.assertEqual(offered["intake_round"], "offered")
        closed = close_intake(offered, {"beach_access": "walkable"}, continue_as_is=True)
        self.assertIsNone(closed["baggage"])
        self.assertEqual(closed["intake_round"], "closed")
        self.assertEqual(resume_intake(closed)["do_not_reask"], ["baggage"])
        self.assertFalse(offer_intake(closed, gaps)[1])
        sufficient, questions = offer_intake(brief, gaps[:1])
        self.assertFalse(questions)
        self.assertEqual(sufficient["intake_outcome"], "sufficient")
        skipped, questions = offer_intake(brief, gaps, no_questions=True)
        self.assertFalse(questions)
        self.assertIsNone(skipped["baggage"])
        self.assertEqual(skipped["intake_outcome"], "skipped")

    def test_selection_is_not_reference_comparison_or_negation(self):
        ids = state_fixture()["presented_candidate_ids"]
        for utterance in ("Продолжай", "Мне не подходит c-02", "сравни c-01 и c-02",
                          "c-020", "беру c-02 или c-09", "рекомендую c-02", "А c-02?",
                          "выбираю не c-02"):
            with self.subTest(utterance=utterance):
                self.assertFalse(resolve_selection(utterance, ids, brief_revision="r01")["plan_allowed"])
        for utterance in ("беру c-02", "c-02", "проработай c-02"):
            self.assertTrue(resolve_selection(utterance, ids, brief_revision="r01")["plan_allowed"])

    def test_serialized_roundtrip_preserves_closed_intake_history_and_refs(self):
        doc = state_fixture()
        doc["brief"].pop("intake_round")
        brief, _ = offer_intake(doc["brief"], [{"field": "baggage", "impact": "cost", "question": "Чемодан?"}])
        doc["brief"] = close_intake(brief, {}, continue_as_is=True)
        text = serialize_snapshot(doc)
        reread = read_snapshot(text)
        self.assertEqual(reread, doc)
        self.assertTrue(validate_snapshot(reread)["full_integrity"])
        self.assertEqual(validate_snapshot(reread)["do_not_reask"], ["baggage"])
        changed = apply_delta(reread, "dates")
        self.assertEqual(changed["evidence"][0]["observed_at"], "2026-09-30")
        self.assertEqual(changed["evidence"][0]["freshness"], "stale")
        self.assertEqual(reread["evidence"][0]["freshness"], "unknown")

    def test_new_snapshot_rejects_semantic_corruption(self):
        mutations = [
            lambda s: s.update(stage="PLAN"),
            lambda s: s.update(status="delivered"),
            lambda s: s.update(selection_cycle=True),
            lambda s: s.update(weights={"fit": 100}),
            lambda s: s["weights"].update(fit=-1, value=56),
            lambda s: s.update(presented_candidate_ids=["c-01"] * 6),
            lambda s: s.update(selected_id="c-99", selection_user_basis="беру c-99"),
            lambda s: s.update(selected_id="c-02", selection_user_basis="не беру c-02"),
            lambda s: s.update(stage="planning"),
            lambda s: s["candidates"][0].update(evidence_ids=["missing"]),
            lambda s: s["evidence"][0].update(freshness="verified"),
            lambda s: s.update(next_action=None),
        ]
        for mutate in mutations:
            doc = state_fixture()
            mutate(doc)
            with self.subTest(doc=doc):
                self.assertFalse(validate_snapshot(doc)["compatible"])
                with self.assertRaises(ValueError):
                    serialize_snapshot(doc)

    def test_final_delivery_and_targeted_delta_keep_choice(self):
        doc = state_fixture()
        choice = resolve_selection("беру c-02", doc["presented_candidate_ids"], brief_revision="r01")
        doc.update(selected_id=choice["selected_id"], selection_user_basis=choice["user_basis"],
                   stage="publish", status="ready", next_action=None,
                   delivery={"mode": "files", "checked": True})
        doc["critic_results"].append({"which": 2, "status": "PARTIAL", "summary": "Owner checklist",
                                     "findings": [], "evidence_ids": ["e-01"]})
        self.assertTrue(validate_snapshot(read_snapshot(serialize_snapshot(doc)))["compatible"])
        changed = apply_delta(doc, "dates")
        self.assertEqual(changed["selected_id"], "c-02")
        self.assertTrue(changed["requires_revalidation"])
        self.assertEqual(changed["stage"], "planning")
        self.assertEqual(changed["evidence"][0]["observed_at"], doc["evidence"][0]["observed_at"])
        self.assertTrue(validate_snapshot(changed)["compatible"])
        doc["candidates"][1]["gate"] = "FAIL"
        self.assertFalse(validate_snapshot(doc)["compatible"])

    def test_legacy_readable_without_fabricated_integrity(self):
        old = {"method_version": "0.2.3", "stage": "custom", "brief": {"veto": ["no-car"]},
               "selected_id": "old-known-choice"}
        report = validate_snapshot(old)
        self.assertTrue(report["readable"])
        self.assertFalse(report["compatible"])
        self.assertFalse(report["full_integrity"])
        self.assertEqual(report["selected_id"], "old-known-choice")
        self.assertNotIn("presented_candidate_ids", old)


if __name__ == "__main__":
    unittest.main()
