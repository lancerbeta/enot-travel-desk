# Источники и границы проверки

Срез исследования: **29 сентября 2026**. Это реестр источников проектного ресерча, а не база проверенных предложений для поездки. Ни один туристический API/MCP не проходил здесь live-интеграционный тест. Звёзды GitHub округлены на дату просмотра и не измеряют надёжность. Лицензии следует перепроверить на точном commit перед копированием кода; это не юридическое заключение.

Публичные технические выводы основаны на первичных документах/README. Для научных работ прочитаны доступные abstracts, не проведена репликация экспериментов. Внешние условия требуют новой проверки перед реализацией. Новые факты о конкретной поездке нельзя подменять этой библиографией.

## Публичные источники

### S01 — Aviasales Data API

[Официальная документация](https://support.travelpayouts.com/hc/en-us/articles/203956163-Aviasales-Data-API).

Кэш поисков; использовать для discovery, не доказательства текущей покупки.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S02 — Booking.com Demand API: prerequisites

[Официальная документация](https://developers.booking.com/demand/docs/getting-started/prerequisites).

Партнёрский доступ, договор и идентификаторы; не публичный API без условий.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S03 — Яндекс Путешествия: партнёрский API

[Официальная документация](https://yandex.ru/support/travel-distr/ru/instruments/partner-api).

Запрос партнёрского доступа; кандидаты для цен/размещения в РФ.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S04 — Duffel: Offers

[Официальная документация](https://duffel.com/docs/api/offers).

Параметры offer и expires_at; предложение не бессрочно.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S05 — Ostrovok API: integration guide

[Официальная документация](https://docs-api.ostrovok.ru/docs/integration-guide/).

Партнёрская интеграция; не обязательная зависимость первого среза.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S06 — Amadeus for Developers

[Официальная организация GitHub](https://github.com/amadeus4dev).

Архивирована 17.07.2026, SDK deprecated. Страница официального пресс-релиза не открылась этим инструментом; live endpoints не тестировались.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S07 — TREK

[README проекта](https://github.com/liketrek/TREK).

Около 14.4k stars; AGPL-3.0; полноценный self-hosted planner, MCP/совместные планы/экспорт. Не установлен.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S08 — AdventureLog

[README проекта](https://github.com/seanmorley15/AdventureLog).

Около 3.8k stars; GPL-3.0; планировщик/дневник/карты. Не установлен.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S09 — Wanderlog

[Официальный сайт продукта](https://wanderlog.com/).

Пример карты+маршрута+бюджета+совместной работы; тарифы и entitlement отдельно.

Уровень: `product_page_checked`. Проверено/попытка чтения: 2026-09-29.

### S10 — Mindtrip

[Официальный сайт продукта](https://mindtrip.ai/).

Пример персонализации, визуальной карты и creator discovery.

Уровень: `product_page_checked`. Проверено/попытка чтения: 2026-09-29.

### S11 — Black Tomato

[Официальный сайт сервиса](https://www.blacktomato.com/).

Bespoke travel и человеческая поддержка; UX-принцип заботы не даёт агенту их возможностей.

Уровень: `product_page_checked`. Проверено/попытка чтения: 2026-09-29.

### S12 — WorldTravel: benchmark

[Первичное исследование; abstract](https://arxiv.org/abs/2602.08367).

Связанные ограничения и работа с реальными веб-представлениями; численные результаты не переносим на ЕНОТ.

Уровень: `abstract_checked`. Проверено/попытка чтения: 2026-09-29.

### S13 — TripTailor: personalized travel planning

[Первичное исследование; abstract](https://arxiv.org/abs/2508.01432).

Качество поездки шире формальной выполнимости.

Уровень: `abstract_checked`. Проверено/попытка чтения: 2026-09-29.

### S14 — Flex-TravelPlanner

[Первичное исследование; abstract](https://arxiv.org/abs/2506.04649).

Риск нарушения прежних ограничений при новых репликах пользователя.

Уровень: `abstract_checked`. Проверено/попытка чтения: 2026-09-29.

### S15 — Atlas Obscura

[Каталог/редакционный ресурс](https://www.atlasobscura.com/).

Необычные места и подборки; есть sponsored content, требуется проверка на месте/у оператора.

Уровень: `landing_checked`. Проверено/попытка чтения: 2026-09-29.

### S16 — Spotted by Locals

[Редакционный ресурс](https://www.spottedbylocals.com/).

Локальные городские находки; доступ/актуальность конкретной статьи проверяются при использовании.

Уровень: `landing_checked`. Проверено/попытка чтения: 2026-09-29.

### S17 — The Man in Seat 61

[Авторский транспортный ресурс](https://www.seat61.com/).

Идеи поездов/паромов и тактика; автор раскрывает рекламу/affiliate, не источник live stock.

Уровень: `landing_checked`. Проверено/попытка чтения: 2026-09-29.

### S18 — Форум Винского

[Публичные пользовательские отчёты](https://forum.awd.ru/).

Датированные полевые наблюдения и контрсвидетельства; не юридическое основание въезда.

Уровень: `landing_checked`. Проверено/попытка чтения: 2026-09-29.

### S19 — Tripster

[Каталог операторов/экскурсий](https://experience.tripster.ru/).

Локальные активности; дата, язык, состав и реальная доступность уточняются отдельно.

Уровень: `landing_checked`. Проверено/попытка чтения: 2026-09-29.

### S20 — Awesome Digital Nomads

[Кураторский список](https://github.com/cbovis/awesome-digital-nomads).

Около 1.1k stars; начальные категории/ресурсы, не эталон их свежести.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S21 — YouTube captions.download

[Официальная документация](https://developers.google.com/youtube/v3/docs/captions/download).

Скачивание зависит от авторизации и полномочий; нельзя обещать любые субтитры.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S22 — Anthropic: Building effective agents

[Официальная инженерная статья](https://www.anthropic.com/engineering/building-effective-agents).

Простые составные workflows; применение как архитектурного принципа.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S23 — Google Maps URLs

[Официальная документация](https://developers.google.com/maps/documentation/urls/get-started).

Без API key; api=1; ограничения URL/waypoints, отдельные ссылки и сегменты.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S24 — Pentagram: Impala

[Официальное портфолио бюро](https://www.pentagram.com/work/impala).

Вдохновение принципами туристических документов/навигации, без копирования бренда.

Уровень: `product_page_checked`. Проверено/попытка чтения: 2026-09-29.

### S25 — FastAPI: Templates

[Официальная документация](https://fastapi.tiangolo.com/ru/advanced/templates/).

Тонкий web слой с Jinja; предлагаемый стек, не установленный пакет.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S26 — Jinja

[README проекта](https://github.com/pallets/jinja).

Около 11.8k stars, BSD-3-Clause; шаблонизация HTML из данных.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S27 — Pydantic

[README проекта](https://github.com/pydantic/pydantic).

Около 29k stars, MIT; модели и валидация данных.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S28 — Codex: Non-interactive mode

[Официальная документация OpenAI](https://developers.openai.com/codex/noninteractive/).

exec, JSONL, structured output и resume; проверить инструменты/авторизацию выбранной среды отдельно.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S29 — MCP: tool annotations

[Официальная статья протокола](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/).

Аннотации read-only — hints, а не enforcement.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S30 — Trafilatura

[README проекта](https://github.com/adbar/trafilatura).

Около 6.9k stars, Apache-2.0; извлечение основного текста. Не детектор истины/SEO.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S31 — Microsoft Playwright MCP

[README проекта](https://github.com/microsoft/playwright-mcp).

Около 37.7k stars, Apache-2.0; браузерный инструмент. CLI+skills может быть экономнее для coding agents.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S32 — Crawl4AI

[README проекта](https://github.com/unclecode/crawl4AI).

Около 84k stars; Apache-2.0 с условиями attribution в материалах проекта. Проверить LICENSE/NOTICE в выбранном pin. Резерв.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S33 — dzhng/deep-research

[README проекта](https://github.com/dzhng/deep-research).

Около 19.7k stars, MIT; паттерн ограниченного итеративного исследования, не готовый travel backend.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S34 — Skiplagged MCP

[Официальная страница интеграции](https://skiplagged.github.io/mcp/).

Кандидат для поискового read-only маршрута; покрытие/фильтрация hidden-city/доступ не тестировались.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S35 — AWeirdDev/flights

[README проекта](https://github.com/AWeirdDev/flights).

Около 2.1k stars, MIT; неофициальный Google Flights scraper, только экспериментальный кандидат.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S36 — trvl license

[LICENSE проекта](https://github.com/MikkoParkkola/trvl/blob/main/LICENSE).

PolyForm Noncommercial 1.0.0; не свободная основа без ограничений коммерческого использования.

Уровень: `license_checked`. Проверено/попытка чтения: 2026-09-29.

### S37 — ppiova/TravelMCP

[README проекта](https://github.com/ppiova/TravelMCP).

Демонстрационные статические JSON-данные не доказывают live-поиск.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S38 — Spoofkapoof/travel-mcp-server

[README проекта](https://github.com/Spoofkapoof/travel-mcp-server).

Зависимость от Amadeus; пример необходимости проверки backend, а не только обёртки.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

### S39 — Akber Ahmed: Roam case study

[Первичный авторский кейс, доступный через поисковую выдачу](https://akberahmed.com/roam).

Самоотчёт автора: валидные places могут быть в неверном городе; UI доверяли несмотря на ошибки; API cost требует внимания. Не независимая оценка сервиса.

Уровень: `indexed_content_checked_direct_open_failed`. Проверено/попытка чтения: 2026-09-29.

### S40 — Aviasales API FAQ

[Официальная документация](https://support.travelpayouts.com/hc/en-us/articles/204529267-FAQ-about-Aviasales-API).

Data API и live search имеют разные условия доступа/использования.

Уровень: `document_checked`. Проверено/попытка чтения: 2026-09-29.

### S41 — RUSSPASS

[Кандидат каталога РФ](https://russpass.ru/).

Прямое чтение в этом исследовании не удалось; семя для отдельной проверки, не подтверждённый источник.

Уровень: `retrieval_failed`. Проверено/попытка чтения: 2026-09-29.

### S42 — Культура.РФ

[Кандидат афиш/культуры РФ](https://www.culture.ru/).

Прямое чтение в этом исследовании не удалось; не считать сведения подтверждёнными.

Уровень: `retrieval_failed`. Проверено/попытка чтения: 2026-09-29.

### S43 — Суточно.ру

[Каталог размещения](https://sutochno.ru/).

Семя для самостоятельного размещения; публичный открытый API не подтверждён.

Уровень: `landing_search_checked`. Проверено/попытка чтения: 2026-09-29.

### S44 — Level.Travel

[Кандидат пакетного baseline](https://level.travel/).

Получена ошибка страницы; реальные цены/доступность не читались.

Уровень: `retrieval_failed`. Проверено/попытка чтения: 2026-09-29.

### S45 — shadcn/ui

[README проекта](https://github.com/shadcn-ui/ui).

Около 125k stars; UI-компоненты при выборе React, не причина вводить его в этот срез.

Уровень: `readme_checked`. Проверено/попытка чтения: 2026-09-29.

## Репозитории владельца: ограниченное чтение

### R01 — Solana Alpha Lab

[README](https://github.com/lancerbeta/solana-alpha-lab/blob/main/README.md), прочитан через авторизованный GitHub-коннектор. Взяты разделение навигации и текущего состояния, явные маршруты. Не переносится сложный Catalog/Delivery Harness. README blob: `d6488e9bca16ae1ee1ae830d1a2114e9bc13c35c`.

### R02 — RF Market Research

[README](https://github.com/lancerbeta/rf-market-research/blob/main/README.md), прочитан через авторизованный GitHub-коннектор. Взяты понятные стартеры, scoped resume, разделение источника и доказанного факта. Не переносится портфельная методология.

### R03 — Aletheia Crypto Research

[README](https://github.com/lancerbeta/aletheia-crypto-research/blob/main/README.md), прочитан через авторизованный GitHub-коннектор. Взяты явные режимы, сохранение результатов и визуал как производное от данных. Не переносится прогнозная/ledger-машина.

Полный код, тесты, история всех commits и актуальное выполнение репозиториев не аудировались. Изменений, PR и commits не делалось.

## Каталог приложений ChatGPT

Через Plugin_Management на эту дату обнаружены Expedia (подключён), Skyscanner, Booking.com и Tripadvisor (найдены в каталоге, не установлены в ходе задачи). Проверка Expedia ограничена доступностью инструмента; реальные отели/рейсы не искались. Наличие ChatGPT-приложения не предоставляет автоматически API-доступ для самостоятельного приложения. Новые приложения/платные аккаунты не подключались.


## Дополнение 0.2.0 — облачный режим; 29 сентября 2026

Прочитана официальная документация ниже. Это `documentation_checked`, **не live-пилот ЕНОТа**, не проверка конкретных аккаунтов и не сравнение качества моделей. Ранее собранные S01–S45 не перепроверялись в этом атоме. Квоты/тарифы/перечни моделей не переносим в долговечный контракт.

### S46 — OpenAI: Projects in ChatGPT

[Официальная справка](https://help.openai.com/en/articles/10169521-projects-in-chatgpt).

Проекты объединяют чаты, файлы и инструкции; доступны инструменты чата, включая поиск. Функции зависят от плана и настроек workspace. Применение: Project удобен, но не prerequisite; конкретную видимость контекста и инструменты нельзя угадывать.

### S47 — OpenAI: Searching the web with ChatGPT

[Официальная справка](https://help.openai.com/en/articles/9237897-searching-the-web-with-chatgpt).

Описаны веб-поиск, цитаты и ограничения использования. Применение: обычный чат может быть research-host без собственного travel API; цитата сама по себе не проверенная доступность поездки.

### S48 — OpenAI: Working with files in ChatGPT

[Официальный материал OpenAI Academy](https://openai.com/academy/working-with-files/).

Описана работа с загруженными файлами, редактирование и генерируемые результаты. Применение: входной Markdown и файловая поставка возможны в подходящей среде; формат архива/скачивание проверяются фактическим readback, не этой статьёй.

### S49 — Anthropic: Enable and use web search

[Официальная справка Claude](https://support.claude.com/en/articles/10684626-enable-and-use-web-search).

Описаны веб-поиск, источники и зависимость от доступности/настроек. Применение: тот же семантический маршрут возможен без локального repo; актуальная модель/интерфейс не hard-coded.

### S50 — Anthropic: Create and edit files with Claude

[Официальная справка Claude](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude).

Описаны создание/редактирование файлов прямо в разговоре, вычислительная среда и использование лимитов. Применение: облако не означает отсутствие вычислений или экспорта. Реальную возможность HTML/ZIP в конкретном сеансе следует установить действием, не предположением.
