# Текущее состояние проекта

Дата: **2026-09-30**. Проект **0.3.1**. Протокол чата **0.2.4**.

Основной потребитель — **владелец**. Сильный облачный чат остаётся runtime. Переносимость для друга сохранена как будущая возможность и не является release gate.

Атом `ENOT_A0_A1_CLOUD_FIRST_VERTICAL_PROOF_V1` закрыт как `STOP_OWNER_SCOPE_CHANGE`. Это не PASS и не technical FAIL. История — в [docs/atoms/A0_A1/ACCEPTANCE.md](docs/atoms/A0_A1/ACCEPTANCE.md).

Атом `ENOT_OWNER_FIRST_SOURCE_INTELLIGENCE_V1` принят как **PASS** на ревизии `d7daf25d0811eefc391886ec3fb910deb42d7be9`. Запись — в [docs/atoms/SOURCE_INTELLIGENCE/ACCEPTANCE.md](docs/atoms/SOURCE_INTELLIGENCE/ACCEPTANCE.md).

`ENOT_OWNER_READY_DELIVERY_V1` (D1 → D2) принят родителем как **independent PASS** на `4b0ebf82ff8081eba710b3fb490c17fea771a29d`. Независимо пройдены 49 canonical tests, 4 focused tests и 31 negative probes; нерешённых P0/P1 нет. Corrected native final: full_integrity, publish/ready/null, сохранённые записи, exact ZIP и production regeneration проверены. Это приёмка ограниченного upgrade на synthetic evidence, не live-travel acceptance. A2 не назначен.

| Область | Состояние |
|---|---|
| Визуальное направление | Пользователь одобрил; стиль сохранён |
| Основной потребитель | Владелец продукта |
| Runtime | Сильный облачный чат; веб, репозиторий и доступные инструменты — необязательные ускорители |
| Друг / родственник | Метод не удалён; не текущий release gate |
| Этапность | До пяти вариантов → явный выбор → план |
| Реестр источников | PASS: routing prior, не whitelist и не база цен |
| Приложение / сервер | Не реализуются |
| A2 | Условный, не начат |

## Активная работа

Evidence collection `OWNER_REAL_TRIP_PILOT_V1` завершён. Наблюдались DISCOVER → выбор → PLAN/Critic 2 → HTML/snapshot → содержательное resume. Это owner-runtime smoke, не состоявшийся отпуск. Поставка требует REPAIR: утрата IDs/cycle/weights/method в snapshot и мобильный/трёхслойный HTML; полный исходный ZIP/Поездка.md независимо не проверен. Исторический source PASS сохраняется.

D1: один optional intake, точный перенос состояния и завершение на согласованном комплекте. D2: практический guide, фотографии, карточки, offline mobile и три файла/ZIP из одной ревизии. [PR #1](https://github.com/lancerbeta/enot-travel-desk/pull/1) уже слит в main обычным merge с сохранением истории D1/D2 (`2a86bdea5874d1e9709eeae8cd34a6684f9f5f75`); deployment и booking не входят. [Acceptance](docs/atoms/OWNER_READY_DELIVERY/ACCEPTANCE.md), [focused export evidence](docs/atoms/OWNER_READY_DELIVERY/evidence/focused-final-export/README.md).

Видимый run_id отсутствует в native HTML: reviewer классифицировал это как P2, same-run identity доказана snapshot/MD/ZIP/provenance без противоречий. Browser proof canonical HTML применим; полный browser/accessibility/print audit отдельного actor HTML, provenance native host, sufficient-brief native branch, авторство отдельных фото и live travel не доказаны. Исторические failure receipts сохранены без изменения.
