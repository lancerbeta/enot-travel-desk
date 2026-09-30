"""Producer-to-consumer seams. Synthetic fixture only."""

import unittest
from decimal import Decimal
from pathlib import Path

from enotcheck.budget import evaluate_budget
from enotcheck.intake import apply_skip, resume_intake
from enotcheck.render import render_bundle
from enotcheck.selection import resolve_selection
from enotcheck.slots import new_state, present
from enotcheck.snapshot import apply_delta, validate_snapshot


class Seams(unittest.TestCase):
    def test_evidence_budget_selection_plan_and_exports_agree(self):
        state = new_state()
        self.assertEqual(present(state, "c-01", "package"), "published")
        self.assertEqual(present(state, "c-02", "train-and-house"), "published")
        choice = resolve_selection("беру c-02", state["presented"], brief_revision="r01")
        self.assertTrue(choice["plan_allowed"])

        budget = evaluate_budget(
            [
                {
                    "category": name,
                    "quantity": "1",
                    "unit": "trip",
                    "amount": str(amount),
                    "currency": "RUB",
                    "mandatory": True,
                    "known": True,
                    "evidence_ids": ["e-fixture"],
                }
                for name, amount in {
                    "lodging": 24000,
                    "door_to_door": 4000,
                    "food": 9000,
                    "activities": 4000,
                    "misc": 2000,
                    "reserve": 5000,
                }.items()
            ],
            deposit="8000",
            hard_cap="90000",
            base_currency="RUB",
        )
        self.assertEqual(budget["gate"], "PASS")

        changed = apply_delta(
            {
                "selected_id": choice["selected_id"],
                "evidence": {"e-fixture": {"observed_at": "2026-09-29", "freshness": "current_for_scope"}},
            },
            "dates",
        )
        self.assertTrue(changed["recheck_pending"])
        self.assertEqual(changed["selected_id"], "c-02")

        snapshot = {
            "run_id": "2026-09-30_synthetic-oracle_01",
            "revision": "r02",
            "method_version": "0.2.1",
            "stage": "planning",
            "brief": {
                "dates": "2026-10-23/2026-10-25",
                "party": "2 adults",
                "budget": "70000/90000 RUB",
                "veto": ["no-car"],
            },
            "weights": {"fit": 30},
            "selection_cycle": state["cycle"],
            "presented_candidate_ids": list(state["presented"]),
            "selected_id": changed["selected_id"],
            "selection_user_basis": choice["user_basis"],
            "requires_revalidation": True,
            "next_action": "recheck transport and lodging before new claims",
        }
        report = validate_snapshot(snapshot)
        self.assertTrue(report["compatible"])
        self.assertEqual(report["slot_count"], 2)
        self.assertEqual(report["selected_id"], "c-02")

        bundle = render_bundle(
            {
                "run_id": snapshot["run_id"],
                "revision": snapshot["revision"],
                "method_version": snapshot["method_version"],
                "title": "Учебная корзина, не предложение",
                "synthetic": True,
                "selected_id": snapshot["selected_id"],
                "user_basis": snapshot["selection_user_basis"],
                "compromise": "Учебные числа из score-demo, живой квоты нет.",
                "risks": ["Депозит 8 000 ₽ нужно иметь отдельно от расхода 48 000 ₽."],
                "actions": [
                    "Сверить учебную сумму ещё раз по строкам.",
                    "Не считать пример бронью.",
                    "Для живой поездки открыть чистый чат с пилотным brief.",
                ],
                "practical": {
                    "before": "Ничего не бронировать по этому файлу.",
                    "days": "Дни не заданы: это проверка оформления.",
                    "return_plan": "Возврат в этом примере не существует.",
                },
                "budget": budget,
                "sources": [
                    {
                        "title": "examples/score-demo.json",
                        "url": "https://example.com/enot-synthetic-fixture",
                        "observed_at": "2026-09-29",
                        "applies_to": "arithmetic fixture only",
                    }
                ],
                "snapshot": snapshot,
                "hostile_text": '<script>alert("x")</script>',
                "hostile_url": "javascript:alert(1)",
            }
        )
        self.assertIn("48\u00a0000", bundle["html"])
        self.assertIn("56\u00a0000", bundle["html"])
        self.assertIn("48 000", bundle["markdown"])
        self.assertIn("56 000", bundle["markdown"])
        self.assertIn(snapshot["run_id"], bundle["continuation"])
        self.assertIn("c-02", bundle["continuation"])
        self.assertIn("no-car", bundle["continuation"])
        self.assertNotIn("<script>", bundle["html"])
        self.assertIn("&lt;script&gt;", bundle["html"])
        self.assertNotIn('href="javascript:', bundle["html"])
        self.assertLess(bundle["html"].find("Депозит 8 000"), bundle["html"].find("<details"))
        for key in ("html", "markdown", "continuation"):
            self.assertIn("2026-09-30_synthetic-oracle_01", bundle[key])
            self.assertIn("r02", bundle[key])


class RenderFiles(unittest.TestCase):
    def test_written_files_open_and_match(self):
        from enotcheck.render import write_bundle

        target = Path(__file__).resolve().parents[1] / "docs" / "atoms" / "A0_A1" / "evidence" / "synthetic-render"
        bundle = write_bundle(
            target,
            {
                "run_id": "2026-09-30_synthetic-oracle_01",
                "revision": "r01",
                "method_version": "0.2.1",
                "title": "Учебная корзина, не предложение",
                "synthetic": True,
                "selected_id": "c-demo",
                "user_basis": "fixture",
                "compromise": "Синтетические суммы.",
                "risks": ["Это не живое размещение и не билет."],
                "actions": ["Открыть файл.", "Прочитать риск.", "Не бронировать."],
                "practical": {
                    "before": "Подготовка не требуется.",
                    "days": "Дневного плана нет.",
                    "return_plan": "Возврата нет.",
                },
                "budget": {
                    "travel_spend": Decimal("48000"),
                    "deposit": Decimal("8000"),
                    "cash_needed": Decimal("56000"),
                    "currency": "RUB",
                    "gate": "PASS",
                    "lines": [],
                },
                "sources": [],
                "snapshot": {
                    "run_id": "2026-09-30_synthetic-oracle_01",
                    "revision": "r01",
                    "method_version": "0.2.1",
                    "stage": "publish",
                    "presented_candidate_ids": ["c-demo"],
                    "selected_id": "c-demo",
                    "next_action": "none — synthetic",
                    "brief": {"veto": ["synthetic-only"]},
                },
                "hostile_text": "",
                "hostile_url": "",
            },
        )
        html = (target / "Путеводитель.html").read_text(encoding="utf-8")
        trip = (target / "Поездка.md").read_text(encoding="utf-8")
        resume = (target / "Продолжение.md").read_text(encoding="utf-8")
        self.assertIn("48\u00a0000", html)
        self.assertIn("48 000", trip)
        self.assertIn("c-demo", resume)
        self.assertFalse(bundle["zip_created"])
        self.assertIn("overflow-wrap", html)
        self.assertIn(":focus", html)
        self.assertIn("<details", html)


class IntakeSnapshotRoundTrip(unittest.TestCase):
    def _brief(self):
        brief = {
            "origins": "Казань",
            "return_to": "Казань",
            "dates": "2026-10-16/2026-10-18",
            "duration": "2 nights",
            "party": "2 adults",
            "accommodation": "one double room",
            "budget": "на двоих, RUB, желательно 70 000, потолок 90 000",
            "veto": ["no-car", "no-self-transfer", "no-departure-before-08:00"],
            "soft_preferences": "quiet water",
            "effort_tolerance": None,
            "assumptions": [],
            "unresolved": [],
        }
        return apply_skip(
            brief,
            "effort_tolerance",
            "ширина поиска по хлопотам; точная нагрузка не задана",
        )

    def _snapshot(self, brief):
        return {
            "run_id": "2026-09-30_kazan-voda_01",
            "revision": "r01",
            "method_version": "0.2.2",
            "stage": "discovery",
            "status": "running",
            "brief": brief,
            "weights": {
                "fit": 30,
                "value": 25,
                "logistics": 15,
                "comfort": 15,
                "novelty": 10,
                "flexibility": 5,
            },
            "selection_cycle": 1,
            "presented_candidate_ids": ["c-01", "c-02"],
            "withdrawn_candidate_ids": [],
            "selected_id": None,
            "next_action": "continue discover without another intake question",
            "evidence": [
                {
                    "title": "fixture",
                    "url": "https://example.com/enot-synthetic-fixture",
                    "observed_at": "2026-09-30",
                    "applies_to": "intake seam only",
                    "status": "not_a_live_offer",
                }
            ],
            "critic_results": [],
            "invalidation": [],
            "artifacts": [],
        }

    def test_skip_survives_continuation_and_blocks_repeat_intake(self):
        brief = self._brief()
        self.assertIsNone(brief["effort_tolerance"])
        snapshot = self._snapshot(brief)
        report = validate_snapshot(snapshot)
        self.assertTrue(report["compatible"], report["gaps"])
        self.assertEqual(report["do_not_reask"], ["effort_tolerance"])
        bundle = render_bundle(
            {
                "run_id": snapshot["run_id"],
                "revision": snapshot["revision"],
                "method_version": snapshot["method_version"],
                "title": "Учебный перенос, не поездка",
                "synthetic": True,
                "selected_id": None,
                "user_basis": None,
                "compromise": "Снимок для проверки пропуска.",
                "risks": ["Хлопоты не заданы, поиск шире."],
                "actions": ["Не спрашивать хлопоты снова."],
                "practical": {"before": "", "days": "", "return_plan": ""},
                "budget": {
                    "travel_spend": None,
                    "deposit": Decimal("0"),
                    "cash_needed": None,
                    "currency": "RUB",
                    "gate": "UNKNOWN",
                },
                "sources": [],
                "snapshot": snapshot,
                "hostile_text": "",
                "hostile_url": "",
            }
        )
        text = bundle["continuation"]
        self.assertIn("user_skipped", text)
        self.assertIn("effort_tolerance", text)
        self.assertIn("Казань", text)
        self.assertIn("70 000", text.replace("\u00a0", " "))
        self.assertIn("do_not_reask: effort_tolerance", text)
        self.assertIn("repeat_general_intake: false", text)
        self.assertIn("fit 30", text)
        resumed = resume_intake(snapshot["brief"])
        self.assertFalse(resumed["repeat_general_intake"])
        self.assertEqual(resumed["do_not_reask"], ["effort_tolerance"])

    def test_silent_default_and_old_method_compatibility(self):
        brief = self._brief()
        brief["effort_tolerance"] = "немного самостоятельности"
        report = validate_snapshot(self._snapshot(brief))
        self.assertFalse(report["compatible"])
        self.assertIn("silent_default", report["gaps"])
        older = self._snapshot(self._brief())
        older["method_version"] = "0.2.1"
        del older["brief"]["unresolved"]
        del older["status"]
        self.assertTrue(validate_snapshot(older)["compatible"])
        future = self._snapshot(self._brief())
        future["method_version"] = "0.3.0"
        self.assertFalse(validate_snapshot(future)["compatible"])


class MobilePreviewLayout(unittest.TestCase):
    def test_preview_is_generated_by_the_actual_mobile_template(self):
        import json
        import tempfile
        from enotcheck.render import content_from_snapshot, write_bundle
        root = Path(__file__).resolve().parents[1]
        fixture = root / "docs/atoms/OWNER_READY_DELIVERY/evidence"
        state = json.loads((fixture / "accepted-state.json").read_text())
        with tempfile.TemporaryDirectory() as target:
            bundle = write_bundle(target, content_from_snapshot(state), asset_directory=fixture / "assets")
        text = root.joinpath("design-preview.html").read_text(encoding="utf-8")
        self.assertEqual(text, bundle["html"])
        phone = text.split("@media(max-width:650px)", 1)[1].split("@media", 1)[0]
        self.assertIn(".card-grid{grid-template-columns:1fr}", phone)
        self.assertIn(".pair{grid-template-columns:1fr;", phone)
        self.assertNotIn("overflow:hidden", text)


if __name__ == "__main__":
    unittest.main()
