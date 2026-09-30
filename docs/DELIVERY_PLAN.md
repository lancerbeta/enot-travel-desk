# План поставки / 0.3.1 — owner-ready

Активный move — `ENOT_OWNER_READY_DELIVERY_V1`, постановка в [PRD_SSD](atoms/OWNER_READY_DELIVERY/PRD_SSD.md). Одновременно активен один податом.

| Податом | Outcome | Gate / состояние |
|---|---|---|
| D1 DIALOG_AND_HANDOFF | Один optional intake, явный выбор, snapshot 0.2.4, delivery completion | LOCAL GREEN: 38 tests, serialized round-trip; not independent PASS |
| D2 PRACTICAL_EDITORIAL_BUNDLE | Практический трёхслойный guide, 4–5 фото, offline mobile и реальный комплект | Independent REPAIR на 7ed6e5a: три P1; bounded repair, 48 local tests, actual bundle/snapshot readback; retest pending |

D1 → D2 разрешён этой постановкой без нового OK. Провал gate, material authority conflict или нарушение прав останавливают продвижение. Один независимый verdict всего move после handback; локальный green не independent PASS. [Acceptance](atoms/OWNER_READY_DELIVERY/ACCEPTANCE.md).

Pilot `OWNER_REAL_TRIP_PILOT_V1`: evidence collection завершён; observed end-to-end + resume, REPAIR по delivery. Покупка не нужна для приёмки и не выполняется. Source intelligence сохраняет PASS на `d7daf25d0811eefc391886ec3fb910deb42d7be9`; [история](atoms/SOURCE_INTELLIGENCE/ACCEPTANCE.md). A0+A1 остаётся `STOP_OWNER_SCOPE_CHANGE`; [история](atoms/A0_A1/ACCEPTANCE.md).

Не включены COMPOSITION_FIRST_V1, budget evidence-kind experiment, A2, новый travel research, booking, backend, deployment и новые платные подключения. Сильный облачный чат — основной runtime, local tools optional. Отдельные commits D1/D2 позволяют обычный revert последнего шага.

Текущая публикационная граница: feature branch, [draft PR #1](https://github.com/lancerbeta/enot-travel-desk/pull/1). Родитель разрешил push ограниченного repair и ожидание CI на exact head; merge удержан до независимого retest. Старый executor command про direct-main superseded. [Repair receipt](atoms/OWNER_READY_DELIVERY/evidence/REPAIR.md).
