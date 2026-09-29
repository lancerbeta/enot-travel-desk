"""One accepted revision, three views. External text is escaped."""

import html
from decimal import Decimal
from pathlib import Path


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
    if isinstance(url, str) and (url.startswith("https://") or url.startswith("http://")):
        return url
    return None


def render_bundle(content):
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


def write_bundle(directory, content):
    rendered = render_bundle(content)
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    (target / "Путеводитель.html").write_text(rendered["html"], encoding="utf-8")
    (target / "Поездка.md").write_text(rendered["markdown"], encoding="utf-8")
    (target / "Продолжение.md").write_text(rendered["continuation"], encoding="utf-8")
    rendered["zip_created"] = False
    return rendered
