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
        forced, questions = offer_intake(offered, gaps, no_questions=True)
        self.assertEqual(forced["intake_round"], "closed")
        self.assertFalse(questions)
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
        for utterance in ("беру c-02", "c-02", "проработай c-02",
                          "Беру c-02. Собери учебный комплект из данных packet. Ничего не покупай и не пиши продавцам.",
                          "Выбираю c-02, не бронируй", "Беру c-02. Сколько стоит депозит?"):
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
            lambda s: s["evidence"][0].update(observed_at="yesterday"),
            lambda s: s["critic_results"][0].update(findings=[{"problem": "missing source", "evidence_ids": ["missing"]}]),
            lambda s: s.update(preset="mystery"),
            lambda s: s.update(next_action=None),
        ]
        for mutate in mutations:
            doc = state_fixture()
            mutate(doc)
            with self.subTest(doc=doc):
                self.assertFalse(validate_snapshot(doc)["compatible"])
                with self.assertRaises(ValueError):
                    serialize_snapshot(doc)

    def test_malformed_field_types_return_gaps_instead_of_crashing(self):
        for section in (None, "brief"):
            original = state_fixture()
            keys = original if section is None else original[section]
            for key in keys:
                for value in (None, True, 1, "broken", [], {}):
                    doc = state_fixture()
                    (doc if section is None else doc[section])[key] = value
                    report = validate_snapshot(doc)
                    self.assertIsInstance(report["gaps"], list)

    def test_final_delivery_and_targeted_delta_keep_choice(self):
        import json
        from pathlib import Path
        # A final-state positive control needs the reached delivery content.
        doc = json.loads((Path(__file__).resolve().parents[1] /
                          'docs/atoms/OWNER_READY_DELIVERY/evidence/accepted-state.json').read_text())
        choice = resolve_selection("беру c-02", doc["presented_candidate_ids"], brief_revision="r01")
        doc.update(selected_id=choice["selected_id"], selection_user_basis=choice["user_basis"],
                   stage="publish", status="ready", next_action=None,
                   delivery={"mode": "files", "checked": True})
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


class EditorialBundle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        from pathlib import Path
        cls.root = Path(__file__).resolve().parents[1] / 'docs/atoms/OWNER_READY_DELIVERY/evidence'
        cls.state = json.loads((cls.root / 'accepted-state.json').read_text())

    def content(self):
        from enotcheck.render import content_from_snapshot
        return content_from_snapshot(copy.deepcopy(self.state))

    def test_final_content_loss_is_not_full_integrity_or_ready_delivery(self):
        import tempfile
        from pathlib import Path
        from enotcheck.render import content_from_snapshot, write_bundle
        final = read_snapshot((self.root / 'bundle/Продолжение.md').read_text())
        mutations = [lambda s, key=key: s.pop(key) for key in ('guide', 'budget', 'scoring')]
        mutations += [lambda s, key=key: s.update({key: {}}) for key in ('guide', 'budget', 'scoring')]
        mutations += [
            lambda s: s['scoring'].pop(s['selected_id']),
            lambda s: s['scoring'][s['selected_id']].pop('result'),
            lambda s: s['budget'].pop('known_spend'),
            lambda s: s['budget'].update(known_spend='0'),
            lambda s: s['guide'].update(booking_tasks=[]),
        ]
        def erase_practice(s):
            for card in s['guide']['practical_cards']:
                card.update(facts=[], actions=[], callouts=[])
            s['guide']['booking_tasks'] = []
        mutations.append(erase_practice)
        def erase_cards(s):
            for card in s['guide']['practical_cards']:
                card.update(facts=[], actions=[], callouts=[])
        mutations.append(erase_cards)
        for mutate in mutations:
            broken = copy.deepcopy(final)
            mutate(broken)
            with self.subTest(mutation=mutate):
                self.assertFalse(validate_snapshot(broken)['full_integrity'])
                with self.assertRaises(ValueError):
                    serialize_snapshot(broken)
                with tempfile.TemporaryDirectory() as target:
                    with self.assertRaises(ValueError):
                        write_bundle(target, content_from_snapshot(broken), asset_directory=self.root / 'assets')
                    self.assertFalse(list(Path(target).iterdir()))
                direct = self.content()
                direct['snapshot'] = broken
                before = copy.deepcopy(broken)
                with tempfile.TemporaryDirectory() as target:
                    with self.assertRaises(ValueError):
                        write_bundle(target, direct, asset_directory=self.root / 'assets')
                    self.assertFalse(list(Path(target).iterdir()))
                self.assertEqual(direct['snapshot'], before)
        # Earlier stages have not reached delivery content; no final quota applies.
        self.assertTrue(validate_snapshot(state_fixture())['full_integrity'])
        incomplete = state_fixture()
        incomplete.update(stage='planning', status='running', selected_id='c-02',
                          selection_user_basis='Беру c-02', next_action='Prepare the selected guide')
        self.assertTrue(validate_snapshot(incomplete)['full_integrity'])
        # A smaller useful guide and an explained inapplicable owner checklist
        # are legitimate; no fixed card/fact/task quota is imposed.
        small = copy.deepcopy(final)
        small['guide']['practical_cards'] = small['guide']['practical_cards'][:1]
        retained_sections = {'hero', small['guide']['practical_cards'][0]['id']}
        small['guide']['media'] = [m for m in small['guide']['media'] if m['section_ref'] in retained_sections]
        small['guide']['media_fallback'] = 'Reduced synthetic guide; only retained sections have photographs.'
        small['guide'].update(booking_tasks=[], booking_tasks_not_applicable=
                             'Synthetic reading-only comparison: no owner transaction is requested.')
        with tempfile.TemporaryDirectory() as target:
            bundle = write_bundle(target, content_from_snapshot(small), asset_directory=self.root / 'assets')
            self.assertIn(small['guide']['booking_tasks_not_applicable'], bundle['markdown'])
            self.assertTrue(validate_snapshot(read_snapshot(bundle['continuation']))['full_integrity'])

    def test_unresolved_critic_blocker_cannot_be_completed_or_archived(self):
        import tempfile
        from pathlib import Path
        from enotcheck.render import write_bundle
        for index in (0, 1):
            for verdict in ('REPAIR', 'PARTIAL', 'PASS'):
                content = self.content()
                critic = content['snapshot']['critic_results'][index]
                critic.update(status=verdict, findings=[{
                    'severity': 'BLOCKER', 'problem': 'Unresolved synthetic delivery defect',
                    'evidence_ids': ['e-01'], 'repair': 'Not yet performed', 'recheck': 'UNKNOWN'}])
                final = copy.deepcopy(content['snapshot'])
                final.update(stage='publish', status='ready', next_action=None,
                             delivery={'mode': 'files', 'checked': True})
                with self.subTest(index=index, verdict=verdict):
                    with self.assertRaises(ValueError):
                        serialize_snapshot(final)
                    before = copy.deepcopy(content['snapshot'])
                    with tempfile.TemporaryDirectory() as target:
                        with self.assertRaises(ValueError):
                            write_bundle(target, content, asset_directory=self.root / 'assets')
                        self.assertFalse(list(Path(target).iterdir()))
                    self.assertEqual(content['snapshot'], before)
        # Preserve a resolved historical finding and justified conditional PARTIAL.
        content = self.content()
        content['snapshot']['critic_results'][1]['findings'].append({
            'severity': 'BLOCKER', 'problem': 'Synthetic repair completed', 'evidence_ids': ['e-01'],
            'resolution': 'resolved',
            'recheck': {'status': 'PASS', 'summary': 'Affected synthetic seam checked', 'evidence_ids': ['e-01']}})
        with tempfile.TemporaryDirectory() as target:
            result = write_bundle(target, content, asset_directory=self.root / 'assets')
            self.assertTrue(result['zip_created'])
            restored = read_snapshot(result['continuation'])
        self.assertTrue(validate_snapshot(restored)['full_integrity'])
        self.assertIsNone(restored['budget']['deposit'])
        self.assertEqual(restored['critic_results'][1]['status'], 'PARTIAL')
        content = self.content()
        content['snapshot']['critic_results'][1].update(status='REPAIR', findings=[])
        # Pending repair is a valid checkpoint, but not a completed bundle.
        self.assertTrue(validate_snapshot(content['snapshot'])['full_integrity'])
        with tempfile.TemporaryDirectory() as target, self.assertRaises(ValueError):
            write_bundle(target, content, asset_directory=self.root / 'assets')

    def test_conditional_or_withdrawn_choice_cannot_authorize_final_delivery(self):
        import tempfile
        from enotcheck.render import write_bundle
        messages = (
            'Планируй только если я выберу c-02',
            'Выбираю c-02. Нет, передумал, пока не планируй.',
            'Беру c-02, если решусь',
            'Выбираю c-02. Отменяю выбор.',
        )
        for message in messages:
            content = self.content()
            content['user_basis'] = content['snapshot']['selection_user_basis'] = message
            with self.subTest(message=message):
                self.assertFalse(resolve_selection(message, ['c-01', 'c-02', 'c-03'], brief_revision='r04')['plan_allowed'])
                final = copy.deepcopy(content['snapshot'])
                final.update(stage='publish', status='ready', next_action=None, delivery={'mode': 'files', 'checked': True})
                with self.assertRaises(ValueError):
                    serialize_snapshot(final)
                with tempfile.TemporaryDirectory() as target, self.assertRaises(ValueError):
                    write_bundle(target, content, asset_directory=self.root / 'assets')
        content = self.content()
        content['user_basis'] = content['snapshot']['selection_user_basis'] = 'Выбираю c-02, не бронируй'
        with tempfile.TemporaryDirectory() as target:
            result = write_bundle(target, content, asset_directory=self.root / 'assets')
            self.assertTrue(result['zip_created'])

    def test_unknown_deposit_and_included_lines_keep_cash_unknown(self):
        from enotcheck.budget import evaluate_budget
        b = self.state['budget']
        result = evaluate_budget(b['lines'], deposit=None, hard_cap='90000', base_currency='RUB')
        self.assertEqual(str(result['known_spend']), '56000')
        self.assertIsNone(result['travel_spend'])
        self.assertIsNone(result['deposit'])
        self.assertIsNone(result['cash_needed'])
        self.assertEqual(result['gate'], 'UNKNOWN')

    def test_writer_archive_and_actual_snapshot_same_accepted_state(self):
        import tempfile,zipfile
        from pathlib import Path
        from enotcheck.render import write_bundle
        content = self.content()
        with tempfile.TemporaryDirectory() as target:
            bundle = write_bundle(target, content, asset_directory=self.root / 'assets')
            self.assertTrue(bundle['zip_created'])
            self.assertEqual(bundle['media_count'], 4)
            self.assertEqual(bundle['media_lane'], 'complete')
            with zipfile.ZipFile(bundle['archive_path']) as archive:
                self.assertEqual(archive.namelist(), ['Путеводитель.html', 'Поездка.md', 'Продолжение.md'])
                for name in archive.namelist():
                    self.assertEqual(archive.read(name), (Path(target) / name).read_bytes())
                restored = read_snapshot(archive.read('Продолжение.md').decode())
            self.assertTrue(validate_snapshot(restored)['full_integrity'])
            self.assertEqual(restored['brief'], self.state['brief'])
            self.assertEqual(restored['weights'], self.state['weights'])
            self.assertEqual(restored['evidence'], self.state['evidence'])
            self.assertEqual(restored['scoring'], self.state['scoring'])
            self.assertEqual(restored['guide'], self.state['guide'])
            self.assertEqual((restored['stage'], restored['status'], restored['next_action']), ('publish', 'ready', None))
            self.assertEqual(bundle['html'].count('<img '), 4)
            self.assertIn('56 000', bundle['markdown'])
            self.assertIn('неизвестно', bundle['html'])
            self.assertLess(bundle['html'].index('Поздний доступ UNKNOWN'), bundle['html'].index('<details'))
            self.assertIn('Площадь Примеров1', bundle['html'])
            self.assertIn('ранний выезд', restored['critic_results'][1]['summary'])
            self.assertLess(len(bundle['html'].encode()), 5_000_000)

    def test_guide_conflicts_and_known_failure_stop_before_ready(self):
        from enotcheck.render import render_bundle,write_bundle
        import tempfile
        for field,value in [('title','other title'),('date_range','other dates'),('selected_id','c-01'),('budget',{}),('critical_unknowns',[])]:
            content=self.content();content[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                render_bundle(content,asset_directory=self.root/'assets')
        content=self.content()
        content['hard_gate_results']['no-car']='FAIL'
        content['snapshot']['guide']['hard_gate_results']['no-car']='FAIL'
        with tempfile.TemporaryDirectory() as target,self.assertRaises(ValueError):
            write_bundle(target,content,asset_directory=self.root/'assets')
        self.assertEqual(content['snapshot']['stage'],'operational_review')
        content=self.content()
        content['budget']['travel_spend']='52000'
        content['snapshot']['budget']['travel_spend']='52000'
        with self.assertRaises(ValueError):
            render_bundle(content,asset_directory=self.root/'assets')
        content=self.content()
        content.pop('practical_cards')
        content['snapshot']['guide'].pop('practical_cards')
        with self.assertRaises(ValueError):
            render_bundle(content,asset_directory=self.root/'assets')
        content=self.content()
        content['budget']['known_spend']='53000'
        content['snapshot']['budget']['known_spend']='53000'
        with self.assertRaises(ValueError):
            render_bundle(content,asset_directory=self.root/'assets')

    def test_external_text_links_and_media_cannot_execute_or_read_paths(self):
        from enotcheck.render import render_bundle
        import tempfile
        from pathlib import Path
        content=self.content()
        hostile='<script>alert(1)</script>'
        for guide in (content,content['snapshot']['guide']):
            guide['practical_cards'][0]['summary']=hostile
        content['snapshot']['evidence'][0]['source_url']='javascript:alert(1)'
        rendered=render_bundle(content,asset_directory=self.root/'assets')
        self.assertNotIn('<script>',rendered['html'])
        self.assertIn('&lt;script&gt;',rendered['html'])
        self.assertNotIn('href="javascript:',rendered['html'])
        for filename in ('../secret.jpg','/tmp/photo.jpg'):
            content=self.content()
            for guide in (content,content['snapshot']['guide']):guide['media'][0]['asset']=filename
            with self.assertRaises(ValueError):render_bundle(content,asset_directory=self.root/'assets')
        with tempfile.TemporaryDirectory() as target:
            target=Path(target)
            (target/'unsafe.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"></svg>')
            (target/'link.jpg').symlink_to(self.root/'assets/DSCN0010.jpg')
            for filename in ('unsafe.svg','link.jpg'):
                content=self.content()
                for guide in (content,content['snapshot']['guide']):guide['media'][0]['asset']=filename
                with self.assertRaises(ValueError):render_bundle(content,asset_directory=target)

    def test_snapshot_only_consumer_keeps_practical_answer_and_delta(self):
        import tempfile
        from enotcheck.render import write_bundle
        with tempfile.TemporaryDirectory() as target:
            result=write_bundle(target,self.content(),asset_directory=self.root/'assets')
            restored=read_snapshot(result['continuation'])
        hotel=next(c for c in restored['guide']['practical_cards'] if c['id']=='hotel')
        self.assertIn('05:00',hotel['callouts'][0]['text'])
        changed=apply_delta(restored,'dates')
        self.assertEqual(changed['selected_id'],'c-02')
        self.assertEqual(changed['evidence'][0]['observed_at'],'2026-09-30')
        self.assertTrue(changed['requires_revalidation'])
        self.assertFalse(resume_intake(changed['brief'])['repeat_general_intake'])
        self.assertEqual(validate_snapshot(read_snapshot(serialize_snapshot(changed)))['selected_id'],'c-02')
        for kind in ('weights','presentation'):
            updated=apply_delta(restored,kind)
            self.assertEqual(updated['selected_id'],'c-02')
            self.assertEqual(updated['evidence'],restored['evidence'])
            self.assertFalse(updated['requires_revalidation'])
            self.assertTrue(validate_snapshot(updated)['compatible'])

    def test_legacy_actual_writer_text_is_readable_without_full_integrity(self):
        from enotcheck.render import render_bundle
        doc=state_fixture();doc['method_version']='0.2.3'
        content={'run_id':doc['run_id'],'revision':doc['revision'],'method_version':'0.2.3',
                 'title':'Legacy','budget':{'travel_spend':'56000','deposit':None,'cash_needed':None},
                 'snapshot':doc,'sources':[]}
        restored=read_snapshot(render_bundle(content)['continuation'])
        report=validate_snapshot(restored)
        self.assertTrue(report['readable'])
        self.assertFalse(report['full_integrity'])
        self.assertEqual(restored['presented_candidate_ids'],['c-01','c-02','c-03'])


if __name__ == "__main__":
    unittest.main()
