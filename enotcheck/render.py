"""One accepted revision, three views. External text is escaped."""

import html
import base64
import copy
import io
import json
import re
import tempfile
import zipfile
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

from enotcheck.snapshot import read_snapshot, serialize_snapshot, validate_snapshot


def _money(value, sep=" "):
    if value is None:
        return "неизвестно"
    amount = Decimal(str(value)).quantize(Decimal("1"))
    sign = "-" if amount < 0 else ""
    digits = str(abs(int(amount)))
    groups = []
    while digits:
        groups.append(digits[-3:])
        digits = digits[:-3]
    return sign + sep.join(reversed(groups))


def _plain(value):
    if value is None:
        return "не задано"
    if isinstance(value, list):
        if not value:
            return "нет"
        if value and isinstance(value[0], dict):
            return None
        return ", ".join(str(item) for item in value)
    return str(value)


def _brief_block(brief):
    brief = brief or {}
    keys = (
        "origins",
        "return_to",
        "dates",
        "duration",
        "party",
        "accommodation",
        "budget",
        "veto",
        "soft_preferences",
        "effort_tolerance",
        "assumptions",
    )
    lines = []
    for key in keys:
        if key not in brief:
            lines.append(f"{key}: не передано")
            continue
        lines.append(f"{key}: {_plain(brief.get(key))}")
    unresolved = brief.get("unresolved", "не передано")
    skipped = []
    if isinstance(unresolved, list):
        lines.append("unresolved:" if unresolved else "unresolved: нет")
        for item in unresolved:
            if not isinstance(item, dict):
                lines.append(f"- {item}")
                continue
            lines.append(
                f"- {item.get('field')} | {item.get('clarification_status')} | {item.get('impact')}"
            )
            if item.get("clarification_status") == "user_skipped":
                skipped.append(str(item.get("field")))
    else:
        lines.append(f"unresolved: {unresolved}")
    lines.append("do_not_reask: " + (", ".join(skipped) if skipped else "нет"))
    lines.append("repeat_general_intake: false")
    return "\n".join(lines)


def _href(url):
    if not isinstance(url, str) or any(ord(c) < 32 for c in url):
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme in ("https", "http") and parsed.hostname and not parsed.username and not parsed.password:
            return url
    except ValueError:
        pass
    return None


def render_bundle(content, *, asset_directory=None):
    if content.get("method_version") == "0.2.4":
        return _render_editorial(content, asset_directory=asset_directory)
    budget = content["budget"]
    currency = budget.get("currency", "RUB")
    spend = _money(budget.get("travel_spend"))
    deposit = _money(budget.get("deposit"))
    cash = _money(budget.get("cash_needed"))
    spend_html = _money(budget.get("travel_spend"), "\u00a0")
    deposit_html = _money(budget.get("deposit"), "\u00a0")
    cash_html = _money(budget.get("cash_needed"), "\u00a0")
    risks = content.get("risks") or []
    actions = content.get("actions") or []
    practical = content.get("practical") or {}
    sources = content.get("sources") or []
    snapshot = content.get("snapshot") or {}
    hostile = content.get("hostile_text") or ""
    hostile_url = content.get("hostile_url") or ""
    synthetic = bool(content.get("synthetic"))
    title = content["title"]
    run_id = content["run_id"]
    revision = content["revision"]

    source_lines = []
    html_sources = []
    for source in sources:
        source_lines.append(
            f"- {source.get('title', 'источник')}: {source.get('url', '')}; "
            f"{source.get('observed_at', 'дата не указана')}; {source.get('applies_to', '')}"
        )
        safe_url = _href(source.get("url", ""))
        label = html.escape(source.get("title", "источник"))
        if safe_url:
            html_sources.append(
                f'<li><a href="{html.escape(safe_url, quote=True)}">{label}</a> '
                f'— {html.escape(source.get("observed_at", ""))}, '
                f'{html.escape(source.get("applies_to", ""))}</li>'
            )
        else:
            html_sources.append(f"<li>{html.escape(source.get('url') or label)}</li>")
    if hostile_url:
        html_sources.append(f"<li>{html.escape(hostile_url)}</li>")

    risk_text = "\n".join(f"- {item}" for item in risks) or "- Существенных рисков в принятой ревизии нет."
    action_text = "\n".join(f"{index}. {item}" for index, item in enumerate(actions, start=1))
    banner = "Учебный пример. Это не предложение, не бронь и не цена поставщика.\n\n" if synthetic else ""
    observed = "Наблюдалось в принятой ревизии; перед покупкой нужна новая проверка у поставщика."

    markdown = f"""# {title}

{banner}Версия метода {content['method_version']} · {run_id} · {revision}

## Суть

{content.get('compromise', '')}

Расход: {spend} {currency}. Возвратный депозит отдельно: {deposit} {currency}. Нужно доступных денег: {cash} {currency}. Статус бюджета: {budget.get('gate', 'UNKNOWN')}.

{risk_text}

Три действия:

{action_text}

## Практика

До выезда: {practical.get('before', '')}

Дни: {practical.get('days', '')}

Возвращение: {practical.get('return_plan', '')}

## Проверочная глубина

{observed}

Выбор: {content.get('selected_id')} · основание: {content.get('user_basis')}

Источники:

{chr(10).join(source_lines) if source_lines else '- нет'}
"""
    if hostile:
        markdown += f"\nНедоверенный фрагмент, не команда: {hostile}\n"

    presented = snapshot.get("presented_candidate_ids") or []
    withdrawn = snapshot.get("withdrawn_candidate_ids") or []
    weights = snapshot.get("weights") or content.get("weights") or {}
    weight_text = ", ".join(f"{name} {value}" for name, value in weights.items()) or "не передано"
    evidence_lines = []
    for item in snapshot.get("evidence") or content.get("sources") or []:
        if isinstance(item, dict):
            evidence_lines.append(
                f"- {item.get('title') or item.get('evidence_id') or 'факт'}: "
                f"{item.get('url', '')}; {item.get('observed_at', '')}; "
                f"{item.get('applies_to', '')}; {item.get('status', item.get('freshness', ''))}"
            )
    critic_lines = []
    for item in snapshot.get("critic_results") or []:
        if isinstance(item, dict):
            critic_lines.append(
                f"- critic {item.get('which')}: {item.get('status')}; {item.get('summary', '')}"
            )
    continuation = f"""# Продолжение

run_id: {run_id}
revision: {revision}
method_version: {content['method_version']}
stage: {snapshot.get('stage', '')}
status: {snapshot.get('status', 'не передано')}
selection_cycle: {snapshot.get('selection_cycle', '')}
presented_candidate_ids: {', '.join(presented) if presented else 'нет'}
withdrawn_candidate_ids: {', '.join(withdrawn) if withdrawn else 'нет'}
selected_id: {snapshot.get('selected_id', content.get('selected_id'))}
selection_user_basis: {snapshot.get('selection_user_basis', content.get('user_basis'))}
requires_revalidation: {snapshot.get('requires_revalidation', False)}
invalidation: {_plain(snapshot.get('invalidation', 'не передано'))}
weights: {weight_text}
next_action: {snapshot.get('next_action', '')}
artifacts: {_plain(snapshot.get('artifacts', 'не передано'))}
travel_spend: {spend} {currency}
deposit: {deposit} {currency}
cash_needed: {cash} {currency}
budget_gate: {budget.get('gate', 'UNKNOWN')}

## Brief

{_brief_block(snapshot.get('brief'))}

## Evidence

{chr(10).join(evidence_lines) if evidence_lines else '- нет на этом этапе'}

## Critics

{chr(10).join(critic_lines) if critic_lines else '- нет на этом этапе'}

{observed}
"""

    risk_html = "".join(f"<p class=\"warn\">{html.escape(item)}</p>" for item in risks)
    action_html = "".join(f"<li>{html.escape(item)}</li>" for item in actions)
    banner_html = (
        "<p class=\"warn\">Учебный пример. Это не предложение, не бронь и не цена поставщика.</p>"
        if synthetic
        else ""
    )
    page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  body {{ margin: 0; background: #F7F3EA; color: #183229; font: 17px/1.5 "Segoe UI", system-ui, sans-serif; }}
  main {{ padding: 20px; max-width: 42rem; margin: 0 auto; overflow-wrap: anywhere; }}
  h1, h2 {{ font-family: Georgia, "Times New Roman", serif; line-height: 1.2; }}
  a:focus, a:focus-visible, summary:focus, summary:focus-visible {{ outline: 2px solid #183229 !important; outline-offset: 2px; box-shadow: inset 0 -2px 0 #183229; }}
  .muted {{ color: #536257; }}
  .warn {{ color: #99492F; }}
  .sun {{ background: #EBCB63; display: inline-block; padding: 0 0.4rem; }}
  hr {{ border: 0; border-top: 1px solid #DCDDD2; }}
</style>
</head>
<body>
<main>
{banner_html}
<p class="muted">{html.escape(run_id)} · {html.escape(revision)} · метод {html.escape(content['method_version'])}</p>
<h1 id="essence">{html.escape(title)}</h1>
<p>{html.escape(content.get('compromise', ''))}</p>
<p>Расход <strong>{spend_html}</strong> {html.escape(currency)}. Депозит отдельно <strong>{deposit_html}</strong> {html.escape(currency)}. Нужно иметь <strong>{cash_html}</strong> {html.escape(currency)}. Статус бюджета: {html.escape(str(budget.get('gate', 'UNKNOWN')))}.</p>
{risk_html}
<h2>Три действия</h2>
<ol>{action_html}</ol>
<h2 id="practice">Практика</h2>
<p>До выезда: {html.escape(practical.get('before', ''))}</p>
<p>Дни: {html.escape(practical.get('days', ''))}</p>
<p>Возвращение: {html.escape(practical.get('return_plan', ''))}</p>
<details id="depth">
<summary>Проверочная глубина</summary>
<div>
<p>{html.escape(observed)}</p>
<p>Выбор {html.escape(str(content.get('selected_id')))}; основание: {html.escape(str(content.get('user_basis')))}.</p>
<ul>{''.join(html_sources)}</ul>
<p>{html.escape(hostile)}</p>
</div>
</details>
</main>
</body>
</html>
"""
    return {
        "html": page,
        "markdown": markdown,
        "continuation": continuation,
        "zip_created": False,
    }


def write_bundle(directory, content, *, asset_directory=None):
    if content.get("method_version") == "0.2.4":
        return _write_editorial(directory, content, asset_directory=asset_directory)
    rendered = render_bundle(content)
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    (target / "Путеводитель.html").write_text(rendered["html"], encoding="utf-8")
    (target / "Поездка.md").write_text(rendered["markdown"], encoding="utf-8")
    (target / "Продолжение.md").write_text(rendered["continuation"], encoding="utf-8")
    rendered["zip_created"] = False
    return rendered


_FILE_NAMES = ('Путеводитель.html', 'Поездка.md', 'Продолжение.md')


def content_from_snapshot(snapshot):
    """Use the accepted Guide in RunState, never reconstruct it from HTML."""
    return {**copy.deepcopy(snapshot['guide']), 'snapshot': copy.deepcopy(snapshot),
            **{key: snapshot[key] for key in ('run_id', 'revision', 'method_version', 'selected_id')},
            'budget': copy.deepcopy(snapshot['budget']),
            'user_basis': snapshot['selection_user_basis']}


def _escape(value):
    return html.escape(str(value), quote=True)


def _text(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value) if value is not None else 'UNKNOWN'


def _link(url, label):
    safe = _href(url)
    return f'<a href="{_escape(safe)}" rel="noopener noreferrer">{_escape(label)}</a>' if safe else _escape(label)


def _raster(media, asset_directory):
    """Only caller-approved asset directory; verify/re-encode raster and strip metadata."""
    from PIL import Image
    if asset_directory is None:
        raise ValueError('media requires an explicitly approved asset directory')
    root = Path(asset_directory).resolve()
    filename = media.get('asset')
    if not isinstance(filename, str) or Path(filename).name != filename or filename in ('.', '..'):
        raise ValueError('unsafe media asset path')
    path = (root / filename).resolve()
    if path.parent != root or not path.is_file() or path.stat().st_size > 10_000_000:
        raise ValueError('media outside approved directory or too large')
    data = path.read_bytes()
    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.format not in ('JPEG', 'PNG', 'WEBP') or img.width * img.height > 12_000_000:
                raise ValueError('unsupported raster')
            img.verify()
        with Image.open(io.BytesIO(data)) as img:
            img.load()
            if img.width < 1 or img.height < 1:
                raise ValueError('empty raster')
            img.thumbnail((1440, 1100))
            if img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
                rgba = img.convert('RGBA')
                clean = Image.new('RGB', rgba.size, 'white')
                clean.paste(rgba, mask=rgba.getchannel('A'))
            else:
                clean = img.convert('RGB')
            out = io.BytesIO()
            clean.save(out, format='JPEG', quality=82, optimize=True)
            return base64.b64encode(out.getvalue()).decode('ascii'), clean.width, clean.height
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError('invalid raster bytes') from exc


def _validate_guide(content):
    snapshot = content['snapshot']
    report = validate_snapshot(snapshot)
    if not report['compatible']:
        raise ValueError('snapshot: ' + ', '.join(report['gaps']))
    if not isinstance(snapshot.get('guide'), dict):
        raise ValueError('accepted practical Guide missing')
    if not isinstance(content.get('practical_cards'), list) or not content['practical_cards']:
        raise ValueError('accepted practical cards missing')
    for key in ('run_id', 'revision', 'method_version', 'selected_id'):
        if content.get(key) != snapshot.get(key):
            raise ValueError('guide/snapshot mismatch: ' + key)
    if content.get('user_basis') != snapshot.get('selection_user_basis'):
        raise ValueError('guide/snapshot mismatch: choice basis')
    if content.get('date_range') != snapshot['brief']['dates']:
        raise ValueError('guide/snapshot mismatch: dates')
    if content.get('budget') != snapshot.get('budget'):
        raise ValueError('guide/snapshot mismatch: budget')
    if content.get('practical_cards') != snapshot.get('guide', {}).get('practical_cards'):
        raise ValueError('guide/snapshot mismatch: practical cards')
    if content.get('booking_tasks') != snapshot.get('guide', {}).get('booking_tasks'):
        raise ValueError('guide/snapshot mismatch: owner tasks')
    if content.get('hard_gate_results', {}) != snapshot.get('guide', {}).get('hard_gate_results', {}):
        raise ValueError('guide/snapshot mismatch: gates')
    for key in ('title', 'date_range', 'compromise', 'risks', 'critical_unknowns',
                'media', 'media_fallback', 'seller_drafts', 'synthetic'):
        if content.get(key) != snapshot.get('guide', {}).get(key):
            raise ValueError('guide/snapshot mismatch: ' + key)
    if 'FAIL' in content.get('hard_gate_results', {}).values() or content['budget'].get('gate') == 'FAIL':
        raise ValueError('known hard FAIL cannot be published as a usable guide')
    from enotcheck.budget import evaluate_budget
    budget = content['budget']
    calculated = evaluate_budget(budget.get('lines', []), deposit=budget.get('deposit'),
                                 hard_cap=snapshot['brief']['budget']['hard_cap'],
                                 base_currency=budget['currency'])
    for key in ('travel_spend', 'known_spend', 'deposit', 'cash_needed', 'gate', 'unknown_not_zero'):
        if str(budget.get(key)) != str(calculated[key]):
            raise ValueError('accepted budget arithmetic mismatch: ' + key)
    eids = {e['evidence_id'] for e in snapshot['evidence']}
    critical = list(content.get('critical_unknowns') or [])
    ids = []
    for card in content.get('practical_cards') or []:
        if not isinstance(card, dict) or not all(isinstance(card.get(key), str) and card[key].strip()
                                                for key in ('topic', 'summary')):
            raise ValueError('practical card needs a topic and summary')
        cid = card.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', cid) or cid in ids:
            raise ValueError('invalid/duplicate practical card id')
        ids.append(cid)
        for fact in [*card.get('facts', []), *card.get('callouts', [])]:
            if not set(fact.get('evidence_ids', [])) <= eids:
                raise ValueError('unknown practical evidence ref')
            if fact.get('status') not in ('known', 'estimate', 'UNKNOWN', 'owner_action', 'future_recheck'):
                raise ValueError('invalid practical fact status')
            if fact.get('critical') and fact['status'] == 'UNKNOWN':
                critical.append({'condition': fact.get('label', card['topic']),
                                 'consequence': fact.get('value', fact.get('text'))})
        for callout in card.get('callouts', []):
            if callout.get('kind') not in ('important', 'tip', 'fallback'):
                raise ValueError('invalid callout kind')
    selected = next(c for c in snapshot['candidates'] if c['candidate_id'] == content['selected_id'])
    if selected['gate'] == 'UNKNOWN' and not critical:
        raise ValueError('critical UNKNOWN must be visible in summary')
    return critical


def _render_editorial(content, *, asset_directory=None):
    critical = _validate_guide(content)
    snapshot = copy.deepcopy(content['snapshot'])
    currency = content['budget']['currency']
    b = content['budget']
    sources = snapshot['evidence']
    cards = content.get('practical_cards') or []
    status_labels = {'known': 'Факт учебного пакета' if content.get('synthetic') else 'Подтверждено для указанной области',
                     'estimate': 'Оценка', 'UNKNOWN': 'Неизвестно',
                     'owner_action': 'Задача владельца', 'future_recheck': 'Перепроверить перед действием'}
    media = content.get('media') or []
    if len(media) > 5 or len({m['id'] for m in media}) != len(media):
        raise ValueError('media must have at most five unique identities')
    card_ids = {c['id'] for c in cards}
    figures = {}
    seen_rasters = set()
    credits_md = []
    for m in media:
        for field in ('id', 'section_ref', 'subject', 'scope', 'caption', 'alt', 'source_url', 'rights_basis', 'credit', 'asset'):
            if not isinstance(m.get(field), str) or not m[field].strip():
                raise ValueError('media missing ' + field)
        if m['section_ref'] not in card_ids | {'hero'} or not _href(m['source_url']):
            raise ValueError('unsafe media source/section')
        data, width, height = _raster(m, asset_directory)
        if data in seen_rasters:
            raise ValueError('duplicate photograph does not fill a media slot')
        seen_rasters.add(data)
        figure = (f'<figure><img src="data:image/jpeg;base64,{data}" width="{width}" height="{height}" '
                  f'alt="{_escape(m["alt"])}" loading="{"eager" if m["section_ref"] == "hero" else "lazy"}">'
                  f'<figcaption>{_escape(m["caption"])} · {_escape(m["scope"])}<br>'
                  f'{_link(m["source_url"], m["credit"])} · {_escape(m["rights_basis"])}</figcaption></figure>')
        figures.setdefault(m['section_ref'], []).append(figure)
        credits_md.append(f'- {m["subject"]}: {m["caption"]}; scope: {m["scope"]}; {m["credit"]}; {m["rights_basis"]}; {m["source_url"]}')
    refs = {e['evidence_id']: e for e in sources}
    def reference_html(ids):
        return ' · '.join(_link(refs[e]['source_url'], e) for e in ids)
    def reference_md(ids):
        return ', '.join(f'{e}: {refs[e]["source_url"]}' for e in ids)
    card_html, card_md = [], []
    for c in cards:
        facts_html, facts_md = [], []
        for f in c.get('facts', []):
            facts_html.append(f'<div class="pair"><dt>{_escape(f["label"])}</dt><dd>{_escape(f["value"])} '
                              f'<span class="status">{_escape(status_labels[f["status"]])}</span><small>{reference_html(f.get("evidence_ids", []))}</small></dd></div>')
            facts_md.append(f'- {f["label"]}: {f["value"]} [{status_labels[f["status"]]}]; {reference_md(f.get("evidence_ids", []))}')
        callouts_html, callouts_md = [], []
        for co in c.get('callouts', []):
            label = {'important': 'До оплаты', 'tip': 'На месте пригодится', 'fallback': 'Если планы меняются'}[co['kind']]
            callouts_html.append(f'<aside class="callout {co["kind"]}"><strong>{label}</strong><p>{_escape(co["text"])} '
                                 f'<span class="status">{_escape(status_labels[co["status"]])}</span></p><small>{reference_html(co.get("evidence_ids", []))}</small></aside>')
            callouts_md.append(f'> {label}: {co["text"]} [{status_labels[co["status"]]}]; {reference_md(co.get("evidence_ids", []))}')
        actions_html = ''.join(f'<li>{_escape(a)}</li>' for a in c.get('actions', []))
        card_html.append(f'<section class="card" id="{c["id"]}"><h2>{_escape(c["topic"])}</h2><p>{_escape(c["summary"])}</p>'
                         f'{"".join(figures.get(c["id"], []))}<dl>{"".join(facts_html)}</dl><ul>{actions_html}</ul>{"".join(callouts_html)}</section>')
        card_md.append(f'## {c["topic"]}\n\n{c["summary"]}\n\n' + '\n'.join(facts_md) + '\n\n' + '\n'.join('- ' + a for a in c.get('actions', [])) + '\n\n' + '\n\n'.join(callouts_md))
    tasks_html = ''.join(f'<li><strong>{_escape(t["action"])}</strong><br>{_escape(t["deadline"])} · {_escape(t["consequence"])}</li>' for t in content['booking_tasks'])
    tasks_md = '\n'.join(f'{i}. {t["action"]} — {t["deadline"]}; {t["consequence"]}' for i,t in enumerate(content['booking_tasks'],1))
    risks = list(content.get('risks') or []) + [f'{c["condition"]}: {c["consequence"]}' for c in critical]
    risk_html = ''.join(f'<p class="risk"><strong>Условие:</strong> {_escape(r)}</p>' for r in risks)
    risk_md = '\n'.join('- ' + r for r in risks)
    cash_label = _money(b.get('cash_needed')) + ' ' + currency
    spend_text = (f'Рабочий расход: {_money(b.get("travel_spend"))} {currency}. '
                  if b.get("travel_spend") is not None else
                  f'Известная часть расхода: {_money(b.get("known_spend"))} {currency}. Полный расход UNKNOWN. ')
    money_text = (spend_text +
                  f'Резерв в расходе: {_money(b.get("reserve"))} {currency}. '
                  f'Возвратный депозит отдельно: {_money(b.get("deposit"))} {currency}. '
                  f'Нужно доступных денег: {cash_label}. Статус бюджета: {b.get("gate")}.')
    if b.get('deposit') is None:
        money_text += ' Депозит UNKNOWN: итоговая ликвидность неизвестна, уточнить до невозвратной оплаты.'
    cost_html, cost_md = [], []
    for line in b.get('lines', []):
        included = 'Включено в ' + line['included_in'] if line.get('included_in') else 'Отдельная трата'
        line_text = f'{_money(line.get("amount"))} {line.get("currency", currency)}; {line.get("quantity", "?")} {line.get("unit", "?")}; {included}; {line.get("kind", "estimate")}'
        cost_html.append(f'<div class="pair"><dt>{_escape(line["category"])}</dt><dd>{_escape(line_text)}<small>{reference_html(line.get("evidence_ids", []))}</small></dd></div>')
        cost_md.append(f'- {line["category"]}: {line_text}; {reference_md(line.get("evidence_ids", []))}')
    source_html = ''.join(f'<li>{_link(e["source_url"], e["title"])} <strong>{_escape(e["evidence_id"])}</strong><br>'
                          f'{_escape(e["claim"])}; {_escape(_text(e["value"]))}<br>'
                          f'{_escape(e["observed_at"])} · {_escape(_text(e["applies_to"]))}<br>'
                          f'{_escape(e["authority"])} / {_escape(e["evidence_kind"])} / {_escape(e["freshness"])}. {_escape(e["limitation"])}</li>' for e in sources)
    source_md = '\n'.join(f'- {e["evidence_id"]}: {e["title"]}; {e["source_url"]}; {e["claim"]}; {_text(e["value"])}; observed_at={e["observed_at"]}; scope={_text(e["applies_to"])}; {e["authority"]}/{e["evidence_kind"]}/{e["freshness"]}; {e["limitation"]}' for e in sources)
    score_text = f'Preset: {snapshot["preset"]}. Веса: {_text(snapshot["weights"])}. Формула: Σ(вес × балл / 5).\n' + _text(snapshot.get('scoring', {'missing': 'Исторические баллы не переданы; не пересчитаны по памяти.'}))
    critics_text = _text(snapshot['critic_results'])
    drafts = content.get('seller_drafts') or []
    nav = ''.join(f'<a href="#{c["id"]}">{_escape(c["topic"])}</a>' for c in cards)
    fallback = content.get('media_fallback') or ('Фото не предоставлены: разрешённые релевантные assets недоступны.' if not media else '')
    final = snapshot['stage'] == 'publish' and snapshot['status'] == 'ready'
    delivery_text = ('Комплект подготовлен. Бронирований нет. Готово для сохранения.'
                     if final else 'План для проверки. Бронирований нет. Доставка ещё не завершена.')
    css = Path(__file__).with_name('guide.css').read_text(encoding='utf-8')
    banner = '<p class="synthetic">SYNTHETIC · учебные объекты и цены, не действующие предложения</p>' if content.get('synthetic') else ''
    page = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>{_escape(content['title'])}</title><style>{css}</style></head><body><main>
<header id="essence">{banner}<p class="eyebrow">ЕНОТ · личный travel desk</p><h1>{_escape(content['title'])}</h1>
<p class="lead">{_escape(content['date_range'])} · {_escape(snapshot['brief']['party'])}</p>
{''.join(figures.get('hero', []))}<p>{_escape(content.get('compromise', ''))}</p><p class="money">{_escape(money_text)}</p>
<p><strong>{_escape(delivery_text)}</strong></p>{risk_html}
<p class="muted">{_escape(fallback)}</p><h2>Ближайшие действия владельца</h2><ol>{tasks_html}</ol>
<p class="muted">{_escape(content['run_id'])} · {_escape(content['revision'])} · метод {_escape(content['method_version'])}</p></header>
<nav aria-label="Разделы поездки"><details><summary>Быстро найти</summary><div class="nav-links">{nav}<a href="#depth-budget">Бюджет и основания</a></div></details></nav>
<div class="card-grid">{''.join(card_html)}</div><section class="depth"><h2>Проверочная глубина</h2>
<details id="depth-budget"><summary>Бюджет по строкам</summary><p>{_escape(money_text)}</p><dl>{''.join(cost_html)}</dl></details>
<details id="depth-scoring"><summary>Выбор, веса и баллы</summary><p>Выбор {_escape(content['selected_id'])}: {_escape(content['user_basis'])}</p><pre>{_escape(score_text)}</pre><pre>{_escape(_text(snapshot['candidates']))}</pre></details>
<details id="depth-sources"><summary>Источники, дата и область</summary><p>Архивные наблюдения не обновляются автоматически. Внешние карты и продавцы требуют сеть.</p><ul>{source_html}</ul></details>
<details id="depth-critics"><summary>Critic 1 и Critic 2</summary><pre>{_escape(critics_text)}</pre></details>
<details id="depth-drafts"><summary>Короткие запросы продавцам</summary>{''.join('<p>' + _escape(d) + '</p>' for d in drafts)}<p>Отправляет владелец по своему решению. Возвращаться в чат с ответом необязательно.</p></details>
</section><footer>ЕНОТ · {_escape(content['run_id'])} / {_escape(content['revision'])}. Текст, стили и встроенные фото доступны без сети.</footer>
</main></body></html>'''
    markdown = (f'# {content["title"]}\n\n' + ('SYNTHETIC — учебный план, не предложение.\n\n' if content.get('synthetic') else '') +
                f'{content["run_id"]} · {content["revision"]} · метод {content["method_version"]}\n\n'
                f'## Суть\n\n{content["date_range"]}; {snapshot["brief"]["party"]}\n\n{content.get("compromise", "")}\n\n{money_text}\n\n'
                f'{delivery_text}\n\n{risk_md}\n\n{fallback}\n\n'
                f'### Действия владельца\n\n{tasks_md}\n\n' + '\n\n'.join(card_md) +
                f'\n\n## Проверочная глубина\n\nВыбор: {content["selected_id"]} · {content["user_basis"]}\n\n'
                f'### Запрос и ограничения\n\n{_text(snapshot["brief"])}\n\n### Бюджет\n\n' + '\n'.join(cost_md) +
                f'\n\n### Скоринг\n\n{score_text}\n\n### Источники\n\n{source_md}\n\n'
                f'### Проверки\n\n{critics_text}\n\n### Сообщения продавцам\n\n' + '\n\n'.join(drafts) +
                '\n\nОтправляет владелец; обязательного возврата в чат нет.\n\n### Изображения\n\n' + '\n'.join(credits_md) + '\n')
    continuation = serialize_snapshot(snapshot)
    return {'html': page, 'markdown': markdown, 'continuation': continuation, 'zip_created': False,
            'media_count': len(media), 'media_lane': 'complete' if 4 <= len(media) <= 5 else 'fallback'}


def _write_editorial(directory, content, *, asset_directory=None):
    """Stage, archive, read back, then install; caller state changes only on success."""
    accepted = copy.deepcopy(content)
    state = accepted['snapshot']
    # This receipt describes this writer's intended delivery; no ready result is
    # returned until serialized files and ZIP readback succeed.
    state.update(stage='publish', status='ready', next_action=None,
                 delivery={'mode': 'files', 'checked': True}, artifacts=list(_FILE_NAMES))
    accepted['snapshot'] = state
    rendered = _render_editorial(accepted, asset_directory=asset_directory)
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    archive_name = f'ENOT_{state["run_id"]}_{state["revision"]}.zip'
    with tempfile.TemporaryDirectory(dir=target, prefix='.enot-') as temporary:
        staging = Path(temporary)
        for name, key in zip(_FILE_NAMES, ('html', 'markdown', 'continuation')):
            (staging / name).write_text(rendered[key], encoding='utf-8')
        with zipfile.ZipFile(staging / archive_name, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name in _FILE_NAMES:
                archive.write(staging / name, name)
        with zipfile.ZipFile(staging / archive_name) as archive:
            if archive.namelist() != list(_FILE_NAMES) or archive.testzip() is not None:
                raise ValueError('bundle archive readback failed')
            for name, key in zip(_FILE_NAMES, ('html', 'markdown', 'continuation')):
                if archive.read(name).decode('utf-8') != rendered[key] or not archive.read(name):
                    raise ValueError('bundle views disagree')
            reread = read_snapshot(archive.read('Продолжение.md').decode('utf-8'))
            if not validate_snapshot(reread)['compatible'] or reread != state:
                raise ValueError('bundle snapshot readback failed')
        for name in (*_FILE_NAMES, archive_name):
            (staging / name).replace(target / name)
    content['snapshot'] = state
    rendered.update(zip_created=True, archive_path=str(target / archive_name),
                    snapshot_path=str(target / 'Продолжение.md'))
    return rendered
