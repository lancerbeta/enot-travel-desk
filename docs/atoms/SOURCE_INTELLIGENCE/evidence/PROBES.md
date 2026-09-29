# Live probe receipts

Дата наблюдения: **2026-09-30**. Среда: локальный агент Cursor. Приложения хоста владельца не вызывались и не имитировались. Цены ниже, если они вообще названы, не записаны в `config/sources.yaml`.

## Transport

- Query: поезд Казань — Москва, есть ли расписание и места на конкретный состав.
- Route: `ground.operator_direct`, затем один fallback `ground.public_web`.
- Access: public web.
- Direct URL: https://www.rzd.ru/ — чтение оборвалось по timeout.
- Fallback URL: https://rasp.yandex.ru/train/kazan--moscow-kazanskaya — страница попросила подтвердить, что запрос не автоматический. Обход не делался.
- Supported claim: нет.
- Unsupported claim: наличие мест, цена и расписание на дату поездки. Сниппеты поиска не считаются прочитанным расписанием.
- Fallback outcome: `terminal_unknown`.
- Evidence: `evidence_kind=unknown`, `freshness=unknown`, `authority=not_read`, `retrieved_via=public_web`, `applies_to=Kazan-Moscow rail, date not confirmed`.

## Stay

- Query: что можно узнать об официальной гостинице Эрмитажа без брони.
- Route: `stays.property_direct`.
- Access: public web.
- URL: https://thehermitagehotel.ru/
- Supported claim: страница называет отель и адрес — Санкт-Петербург, ул. Правды, д. 10; указан телефон +7 812 777 98 10.
- Unsupported claim: цена, наличие номера на даты и состав. Фразы о пакетах без дат не являются offer.
- Fallback: не понадобился.
- Evidence: `evidence_kind=primary_fact` для адреса; `evidence_kind=unknown` для цены и квоты; `source_family=stays`; `retrieved_via=public_web`; `observed_at=2026-09-30`.

## Activity, затем проверка у оператора

- Query: можно ли понять часы Главного музейного комплекса Эрмитажа с его собственной страницы.
- Route: `activities.operator_direct` (сразу первичный оператор, не блог).
- Access: public web.
- URL: https://www.hermitagemuseum.org/wps/portal/hermitage/
- Supported claim: комплекс на Дворцовой площади, 2; вторник, пятница и суббота 11:00–20:00; среда, четверг и воскресенье 11:00–18:00; музей закрыт по понедельникам, 1 января и 9 мая. Кассы закрываются за час до конца работы.
- Unsupported claim: точная цена билета. Строка цены на странице прочиталась неоднозначно, поэтому тариф остаётся UNKNOWN.
- Evidence: `evidence_kind=primary_fact` для часов и выходного; `evidence_kind=unknown` для тарифа; `observed_at=2026-09-30`.

## Official / direct

- Query: даёт ли официальный метеоисточник прогноз на произвольную дату поездки только потому, что открылась главная страница.
- Route: `maps.official_local`.
- URL: https://meteoinfo.ru/
- Supported claim: Гидрометцентр на 2026-09-30 показывает текущие условия (на странице указаны 7 °C, влажность 98%, давление 762 мм рт. ст.). Это наблюдение этого дня, не прогноз на другую дату.
- Unsupported claim: погода на дату будущей поездки.
- Evidence: `evidence_kind=primary_fact` только для наблюдавшихся суток; `applies_to=2026-09-30 homepage`; климат или другой день не подтверждены.

Правило «закрыт по понедельникам» взято со страницы музея и относится к Эрмитажу, не к визовым правилам.
