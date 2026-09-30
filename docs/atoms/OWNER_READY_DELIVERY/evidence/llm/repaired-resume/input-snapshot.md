# Продолжение

Прочитайте сохранённый план ниже. Адресный вопрос не запускает новый подбор или общую анкету. Пропущенное `user_skipped` не спрашивать снова. При изменении дат сохраняйте выбранный вариант и прежние пожелания; зависимые цены, наличие, рейсы, правила и бюджет требуют повторной проверки. Старые `observed_at` не менять без нового чтения источника.

При записи следующего снимка сохраняйте машинные имена полей и типы. `stage`: brief, discovery, verification, decision_review, selection, planning, operational_review, publish. `status`: draft, running, needs_input, ready, partial, failed, cancelled. Перепроверка выбранной поездки: planning/running и конкретный `next_action`; delivery.checked=false, requires_revalidation=true. Завершённая согласованная доставка: publish/ready, next_action=null; это не бронь.

`invalidation` — список строк, подробные пояснения можно дать рядом в Markdown. `freshness` у Evidence: current_for_scope, stale, unknown. Ссылка на свидетельство — существующий evidence_id; поле типа — evidence_kind. `brief.unresolved` — список объектов с field, clarification_status (needs_input, offered_once, user_skipped) и impact. Пропущенное поле присутствует в brief со значением null. Не заменять эти машинные значения русскими или новыми enum; пояснения пишите отдельно. Не сочинять IDs, веса, результаты критиков или историю. Все три файла и ZIP прежней ревизии становятся историческими после изменения дат; их готовность не переносится автоматически.

```yaml
run_id: 2026-09-30_owner-ready-synthetic_01
revision: r03
method_version: 0.2.4
stage: publish
status: ready
brief:
  origins: Учебный город / аэропорт AAA
  return_to: Учебный город / AAA
  dates: 2026-11-10/2026-11-14; местное время Europe/Rome
  duration: 4 ночи
  party: 2 взрослых
  accommodation: 'Учебный отель «Сад»: Double, одна двуспальная кровать, BB'
  budget:
    scope: whole_party
    currency: RUB
    target_amount: '70000'
    hard_cap: '90000'
    included_categories:
    - all
    reserve_policy: '5000'
  veto:
  - no-car
  - no-self-transfer
  hard_constraints:
  - id: no-car
    requirement: Без аренды автомобиля
    origin: user
    applicability: whole trip
    must_pass: true
  soft_preferences: Тихий городской отдых в Тоскане, зелёный двор, одна прогулка и
    один музей; море не требуется
  effort_tolerance: немного самостоятельности
  assumptions: []
  unresolved:
  - field: baggage
    clarification_status: user_skipped
    impact: тариф/стоимость багажа
  intake_round: closed
  intake_outcome: skipped
  baggage: null
preset: relax
weights:
  fit: 35
  value: 20
  logistics: 20
  comfort: 20
  novelty: 0
  flexibility: 5
selection_cycle: 1
presented_candidate_ids:
- c-01
- c-02
- c-03
withdrawn_candidate_ids: []
selected_id: c-02
selection_user_basis: беру c-02
candidates:
- candidate_id: c-01
  concept: 'SYNTHETIC: загородный дом; больше переездов'
  gate: UNKNOWN
  evidence_ids:
  - e-01
  - e-02
  - e-03
- candidate_id: c-02
  concept: 'SYNTHETIC: городской сад и музей; выбранная сборка'
  gate: UNKNOWN
  evidence_ids:
  - e-01
  - e-02
  - e-03
- candidate_id: c-03
  concept: 'SYNTHETIC: озеро; длинный трансфер'
  gate: UNKNOWN
  evidence_ids:
  - e-01
  - e-02
  - e-03
evidence:
- evidence_id: e-01
  title: Frozen synthetic itinerary
  claim: Маршрут/ограничения
  value: Без машины и самостоятельной пересадки; четыре ночи
  source_url: https://example.com/enot-synthetic/e-01
  authority: frozen SYNTHETIC oracle, not live supplier
  observed_at: '2026-09-30'
  applies_to: 2026-11-10/2026-11-14; местное время Europe/Rome
  evidence_kind: estimate
  freshness: unknown
  limitation: Учебные объекты/условия; не реальная котировка, правило или контакт.
- evidence_id: e-02
  title: Учебный отель «Сад»
  claim: Тариф/часы
  value: Double BB24000 RUB; налог800/BB3200 включены. Заезд15:00, стойкадо22:00,
    выезддо11:00. ДепозитUNKNOWN.
  source_url: https://example.com/enot-synthetic/e-02
  authority: frozen SYNTHETIC oracle, not live supplier
  observed_at: '2026-09-30'
  applies_to: 2 взрослых, 4 ночи, выбранная категория
  evidence_kind: estimate
  freshness: unknown
  limitation: Учебные объекты/условия; не реальная котировка, правило или контакт.
- evidence_id: e-03
  title: Учебный транспорт
  claim: Времена/багаж
  value: 10.11 AAA19:30→BBB22:10; 14.11 BBB08:00→AAA11:30; единый билет; ручная кладь7кг;
    чемодан не включён
  source_url: https://example.com/enot-synthetic/e-03
  authority: frozen SYNTHETIC oracle, not live supplier
  observed_at: '2026-09-30'
  applies_to: all times local, 2 adults
  evidence_kind: estimate
  freshness: unknown
  limitation: Учебные объекты/условия; не реальная котировка, правило или контакт.
- evidence_id: e-04
  title: Учебный быт
  claim: Ориентиры
  value: Кафе «У сада», площадь Примеров2, лимит900 RUB/чел; «Арка», переулок Примеров4,
    лимит600 RUB/чел; еда8000 на двоих кроме BB
  source_url: https://example.com/enot-synthetic/e-04
  authority: frozen SYNTHETIC oracle, not live supplier
  observed_at: '2026-09-30'
  applies_to: synthetic city, estimate not menu quote
  evidence_kind: estimate
  freshness: unknown
  limitation: Учебные объекты/условия; не реальная котировка, правило или контакт.
- evidence_id: e-05
  title: Учебные сбои/помощь
  claim: Независимые fallback
  value: Поздний заезд согласовать до оплаты; дождь→indoor; нет связи→offline адрес/обслуживаемая
    стойка
  source_url: https://example.com/enot-synthetic/e-05
  authority: frozen SYNTHETIC oracle, not live supplier
  observed_at: '2026-09-30'
  applies_to: synthetic scenarios only
  evidence_kind: estimate
  freshness: unknown
  limitation: Учебные объекты/условия; не реальная котировка, правило или контакт.
critic_results:
- which: 1
  status: PARTIAL
  summary: 'Synthetic: три разные концепции; no-car/self-transfer сохранены; depositUNKNOWN
    — условный вариант'
  findings:
  - severity: MATERIAL
    problem: ДепозитUNKNOWN
    evidence_ids:
    - e-02
    consequence: cash_needed неизвестно
    repair: условие в первом слое
    recheck: остаётсяUNKNOWN, наблюдение не обновлено
  evidence_ids:
  - e-01
- which: 2
  status: PARTIAL
  summary: 'Synthetic: поздний доступ, дождь, отсутствие связи, ранний выезд проверены
    как сценарии; будущие согласования — owner tasks'
  findings:
  - severity: MATERIAL
    problem: Прилёт после закрытия стойки
    evidence_ids:
    - e-02
    - e-03
    consequence: доступ к номеру не установлен
    repair: не платить невозвратно без письменного late access
    recheck: UNKNOWN
  - severity: MATERIAL
    problem: Home leg not priced
    evidence_ids:
    - e-01
    consequence: full budget cannot pass cap
    repair: explicit mandatory UNKNOWN cost line; financial gate UNKNOWN
    recheck: frozen facts unchanged; no new observed_at
  evidence_ids:
  - e-01
  - e-02
  - e-03
  - e-05
invalidation: []
requires_revalidation: false
artifacts:
- Путеводитель.html
- Поездка.md
- Продолжение.md
next_action: null
budget:
  travel_spend: null
  known_spend: '56000'
  deposit: null
  cash_needed: null
  currency: RUB
  gate: UNKNOWN
  unknown_not_zero: true
  calculation_check: tool_verified
  savings_percent: null
  fx_as_of: null
  lines:
  - category: Билеты, ручная кладь
    amount: '14000'
    currency: RUB
    quantity: '1'
    unit: поездка на двоих
    known: true
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-03
  - category: Double BB, 4 ночи
    amount: '24000'
    currency: RUB
    quantity: '1'
    unit: поездка на двоих
    known: true
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-02
  - category: Еда кроме BB
    amount: '8000'
    currency: RUB
    quantity: '1'
    unit: поездка на двоих
    known: true
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-04
  - category: Музей
    amount: '2000'
    currency: RUB
    quantity: '1'
    unit: поездка на двоих
    known: true
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-04
  - category: Последняя миля и транспорт
    amount: '3000'
    currency: RUB
    quantity: '1'
    unit: поездка на двоих
    known: true
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-03
  - category: Резерв
    amount: '5000'
    currency: RUB
    quantity: '1'
    unit: поездка на двоих
    known: true
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-05
  - category: Городской налог
    amount: '800'
    currency: RUB
    quantity: '1'
    unit: весь срок
    known: true
    mandatory: true
    included_in: Double BB, 4 ночи
    kind: estimate
    evidence_ids:
    - e-02
  - category: Завтраки BB
    amount: '3200'
    currency: RUB
    quantity: '1'
    unit: весь срок
    known: true
    mandatory: true
    included_in: Double BB, 4 ночи
    kind: estimate
    evidence_ids:
    - e-02
  - category: Дорога дом—AAA—дом
    amount: null
    currency: RUB
    quantity: '2'
    unit: участок
    known: false
    mandatory: true
    kind: estimate
    evidence_ids:
    - e-01
  reserve: '5000'
scoring:
  c-01:
    score_inputs:
      fit:
        score: '4.5'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      value:
        score: '4'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      logistics:
        score: '3.5'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      comfort:
        score: '4'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      novelty:
        score: null
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      flexibility:
        score: null
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
    result:
      point: null
      low: '77.5'
      high: '82.5'
      exact: false
      gate_override: null
      rank_may_override_fail: false
  c-02:
    score_inputs:
      fit:
        score: '4.5'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      value:
        score: '4'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      logistics:
        score: '3.5'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      comfort:
        score: '4'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      novelty:
        score: null
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      flexibility:
        score: null
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
    result:
      point: null
      low: '77.5'
      high: '82.5'
      exact: false
      gate_override: null
      rank_may_override_fail: false
  c-03:
    score_inputs:
      fit:
        score: '4.5'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      value:
        score: '4'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      logistics:
        score: '3.5'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      comfort:
        score: '4'
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      novelty:
        score: null
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
      flexibility:
        score: null
        rationale: SYNTHETIC fixed editorial input
        evidence_ids:
        - e-01
    result:
      point: null
      low: '77.5'
      high: '82.5'
      exact: false
      gate_override: null
      rank_may_override_fail: false
guide:
  title: Тоскана · четыре дня без спешки
  synthetic: true
  date_range: 2026-11-10/2026-11-14; местное время Europe/Rome
  compromise: Городской отдых без руля; late access требует письменного согласования
    до оплаты. Ключи не подтверждены.
  risks:
  - 'SYNTHETIC: условия/цены учебные; реальные визы/страховка не проверялись, packet
    не пригоден для покупки.'
  - 'Дорога дом—AAA—дом не оценена: достаточность потолка 90 000 RUB неизвестна.'
  critical_unknowns:
  - condition: Поздний доступ UNKNOWN
    consequence: Отказ отеля делает размещение непригодным; сначала письменный доступ
      либо refundable альтернатива.
  - condition: Депозит UNKNOWN
    consequence: Известная часть расхода 56 000 RUB; полный расход и cash_needed UNKNOWN.
      Дом—AAA—дом не оценён; депозит не считать нулём.
  hard_gate_results:
    no-car: PASS
    no-self-transfer: PASS
    late-access: UNKNOWN
  practical_cards:
  - id: purchase
    topic: До покупки
    summary: Порядок действий; ничего не куплено. Цены учебные, RUB на двоих.
    facts:
    - label: Тариф
      value: Double BB, одна кровать, 4 ночи:24000. Налог800 и BB3200 уже включены.
      status: estimate
      evidence_ids:
      - e-02
    - label: Отмена/оплата
      value: 'Учебные условия: без штрафа до03.11 18:00 Europe/Rome; далее первая
        ночь. ВалютаRUB; способ оплаты уточнить без реквизитов.'
      status: estimate
      evidence_ids:
      - e-02
    - label: Депозит
      value: Размер/hold UNKNOWN; ликвидность неизвестна, спросить до невозвратного
        действия.
      status: UNKNOWN
      evidence_ids:
      - e-02
      critical: true
    actions:
    - Сначала поздний доступ/депозит; затем тариф/багаж; потом самостоятельная покупка
      жилья/транспорта.
    callouts:
    - kind: important
      text: Не делать невозвратную оплату до письменного late access и достаточной
        ликвидности.
      status: owner_action
      evidence_ids:
      - e-02
  - id: road
    topic: Дорога и первые часы
    summary: 10.11 AAA19:30→BBB22:10. Все часы местные; терминалUNKNOWN.
    facts:
    - label: Билет/багаж
      value: Единый билет без самостоятельной пересадки; ручная кладь7кг; чемодан
        не задан, не включён.
      status: estimate
      evidence_ids:
      - e-03
    - label: Последняя миля
      value: 'Официальная обслуживаемая стойка: BBB→площадь Примеров1. Учебный envelope3000
        на обе поездки/местный транспорт; машина не забронирована.'
      status: estimate
      evidence_ids:
      - e-03
    - label: Время и сбой
      value: Учебная оценка45–75мин, не проверенный маршрут. При закрытом доступе
        — заранее согласованные ключи либо refundable fallback night, не обещание
        входа.
      status: estimate
      evidence_ids:
      - e-05
    actions:
    - Сохранить адрес офлайн; сверить терминал/подачу в день выезда.
    callouts:
    - kind: fallback
      text: Нет машины/связи — обслуживаемая стойка, текстовый адрес. Не звонить по
        вымышленным номерам.
      status: owner_action
      evidence_ids:
      - e-05
  - id: hotel
    topic: Отель и нестандартные часы
    summary: Отель «Сад» вымышлен. Double/одна кровать/BB; фото — городской контекст,
      не отель.
    facts:
    - label: Адрес/карта
      value: Площадь Примеров1, учебный центр. https://example.com/enot-synthetic/map
        — учебная ссылка, не реальный POI.
      status: known
      evidence_ids:
      - e-02
    - label: Контакт
      value: https://example.com/enot-synthetic/e-02 — fixture channel, настоящего
        продавца/телефона нет.
      status: known
      evidence_ids:
      - e-02
    - label: Поздний доступ
      value: Заезд15:00; стойкадо22:00, прилёт22:10 плюс дорога. Письменное согласование
        ключей отсутствует; при отказе размещение непригодно.
      status: UNKNOWN
      evidence_ids:
      - e-02
      - e-03
      critical: true
    - label: Еда/багаж
      value: 'Учебный BB07:30–10:00 включён. Первый ужин после прилёта не обещан:
        взять еду до вылета. Storage/early breakfast box не подтверждены.'
      status: UNKNOWN
      evidence_ids:
      - e-02
    actions:
    - Согласовать late access при покупке; не писать «заезд подтверждён».
    callouts:
    - kind: important
      text: 'Выезд05:00: рассчитаться вечером, согласовать возврат ключей и breakfast
        box. Это owner task, не подтверждённая услуга.'
      status: owner_action
      evidence_ids:
      - e-02
  - id: local
    topic: На месте без машины
    summary: Две учебные точки еды и денежная база; география вымышлена.
    facts:
    - label: Где есть
      value: «У сада», площадь Примеров2:900 RUB/чел; «Арка», переулок Примеров4:600
        RUB/чел. 8000 на двоих за весь срок кроме BB — лимит/оценка, не будущая цена
        меню.
      status: estimate
      evidence_ids:
      - e-04
    - label: Как ходить
      value: Центральный квартал без авто. Проходимость/точное время UNKNOWN; не обещать15мин.
        При дожде local transport из envelope3000.
      status: UNKNOWN
      evidence_ids:
      - e-04
    - label: Связь/деньги
      value: Учебный Wi-Fi lobby; SIM/активация/оплата конкретной картой UNKNOWN.
        Проверить совместимость до выезда; сохранить офлайн адрес.
      status: UNKNOWN
      evidence_ids:
      - e-05
    actions:
    - Вода/перекус для позднего прилёта — до вылета. Прачечная для четырёх ночей N/A.
    callouts:
    - kind: tip
      text: BB уже в тарифе; не добавлять завтрак второй раз.
      status: owner_action
      evidence_ids:
      - e-02
  - id: anchors
    topic: Дни и два впечатления
    summary: 11.11 свободный день,12.11 музей,13.11 аллея и отдых. Дополнительная
      турпрограмма не нужна.
    facts:
    - label: Музей
      value: 'Учебный «Город», площадь Примеров3: час/2 билета в envelope2000. Часы
        на дату recheck; подвоз из общего local budget.'
      status: estimate
      evidence_ids:
      - e-04
    - label: Прогулка
      value: Аллея как учебный якорь, удобная обувь/слой от дождя; ступени/доступность
        точного входа UNKNOWN.
      status: UNKNOWN
      evidence_ids:
      - e-04
    - label: Сезон
      value: Прогноза на ноябрь нет; не подменять климатом. Пляж/купание не планируются
        — N/A.
      status: UNKNOWN
      evidence_ids:
      - e-05
    actions:
    - Усталость→кофе/свободный день. Дождь→indoor музей после проверки часов, без
      той же погодной причины отказа.
    callouts:
    - kind: fallback
      text: Музей закрыт — спокойный день в indoor пространстве размещения после подтверждения
        доступа; новые платные anchors не добавлять.
      status: owner_action
      evidence_ids:
      - e-05
  - id: help
    topic: Помощь и что взять
    summary: Гражданства/страховой в packet нет; официальные правила/контакты не выдумываются.
    facts:
    - label: Правила/помощь
      value: В реальной поездке применимые официальные источники обязательны. Виза/страховая/покрытие
        UNKNOWN; перед оплатой проверить, assistance сохранить офлайн.
      status: UNKNOWN
      evidence_ids:
      - e-05
    - label: Сборы
      value: Удобная обувь, слой от дождя, совместимая зарядка. Личные обычные лекарства
        без назначения лечения.
      status: known
      evidence_ids:
      - e-05
    actions:
    - В synthetic run не покупать страховку и не звонить на вымышленные номера.
    callouts: []
  - id: home
    topic: Домой без утренней спешки
    summary: 14.11 выезд05:00; BBB08:00→AAA11:30. Машина не заказана.
    facts:
    - label: Вечер13.11
      value: Рассчитаться/согласовать ключи и breakfast box до закрытия стойки22:00.
      status: owner_action
      evidence_ids:
      - e-02
    - label: Подача/запас
      value: Попросить машину05:00 через fixture channel, подтвердить утром. Резерв
        — staffed transport desk. Учебные45–75мин + 2ч до08:00 не гарантия; аэропортBBB,
        терминалUNKNOWN.
      status: future_recheck
      evidence_ids:
      - e-03
      - e-05
    - label: Багаж/до дома
      value: 'Ручная кладь7кг; чемодан не задан. AAA→дом: адрес не дан, last mileUNKNOWN;
        использовать резерв, не выдумывать цену.'
      status: UNKNOWN
      evidence_ids:
      - e-03
    actions:
    - 13.11 сверить дорогу/подачу; если время больше, выехать раньше.
    callouts:
    - kind: important
      text: '«Машина подтверждена» недопустимо: заказ/recheck выполнит владелец. Ответ
        продавца не нужен для закрытия этого чата.'
      status: owner_action
      evidence_ids:
      - e-05
  booking_tasks:
  - action: Уточнить поздний доступ и депозит
    deadline: до невозвратной оплаты
    consequence: отказ/недостаточная ликвидность обнуляют размещение
  - action: Сверить тариф, багаж и отмену
    deadline: при самостоятельной покупке
    consequence: новый состав требует пересчёта all-in
  - action: Согласовать расчёт, ключи и машину
    deadline: вечером13.11 до22:00; recheck перед выездом
    consequence: при сбое staffed transport fallback/раньше выйти
  media:
  - id: dscn0010
    section_ref: hero
    subject: Зелёные дворы
    scope: региональный редакционный контекст; не объект/номер/вид отеля
    caption: Городской пейзаж; контекст отдыха, не наш отель.
    alt: Зелёные дворы — контекст, не фото учебного отеля
    source_url: https://github.com/ianare/exif-samples/blob/master/jpg/gps/DSCN0010.jpg
    rights_basis: CC BY-SA 4.0 — repository README declaration; resized/re-encoded,
      EXIF removed
    credit: exif-samples contributors / Gaia GIS source collection; individual photographer
      not named
    asset: DSCN0010.jpg
  - id: dscn0012
    section_ref: anchors
    subject: Парковая аллея
    scope: региональный редакционный контекст; не объект/номер/вид отеля
    caption: Реальная аллея; не доказательство доступности учебного маршрута.
    alt: Парковая аллея — контекст, не фото учебного отеля
    source_url: https://github.com/ianare/exif-samples/blob/master/jpg/gps/DSCN0012.jpg
    rights_basis: CC BY-SA 4.0 — repository README declaration; resized/re-encoded,
      EXIF removed
    credit: exif-samples contributors / Gaia GIS source collection; individual photographer
      not named
    asset: DSCN0012.jpg
  - id: dscn0025
    section_ref: local
    subject: Городская улица
    scope: региональный редакционный контекст; не объект/номер/вид отеля
    caption: Реальная улица; кафе и цены ниже вымышлены.
    alt: Городская улица — контекст, не фото учебного отеля
    source_url: https://github.com/ianare/exif-samples/blob/master/jpg/gps/DSCN0025.jpg
    rights_basis: CC BY-SA 4.0 — repository README declaration; resized/re-encoded,
      EXIF removed
    credit: exif-samples contributors / Gaia GIS source collection; individual photographer
      not named
    asset: DSCN0025.jpg
  - id: dscn0042
    section_ref: hotel
    subject: Улица и башня
    scope: региональный редакционный контекст; не объект/номер/вид отеля
    caption: Архитектурный контекст; учебный отель «Сад» здесь не изображён.
    alt: Улица и башня — контекст, не фото учебного отеля
    source_url: https://github.com/ianare/exif-samples/blob/master/jpg/gps/DSCN0042.jpg
    rights_basis: CC BY-SA 4.0 — repository README declaration; resized/re-encoded,
      EXIF removed
    credit: exif-samples contributors / Gaia GIS source collection; individual photographer
      not named
    asset: DSCN0042.jpg
  media_fallback: 'Фото гостиницы нет: объект вымышлен; четыре реальные фотографии
    городского контекста.'
  seller_drafts:
  - Прошу подтвердить письменный доступ к ключам после23:00, сумму/способ депозита,
    возврат ключей05:00. Шаблон не отправлен.
delivery:
  mode: files
  checked: true
```
