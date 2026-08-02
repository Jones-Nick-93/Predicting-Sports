from __future__ import annotations

from html import escape
from pathlib import Path

from .report import ClvRow


def _fmt_odds(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def render_dashboard(rows: list[ClvRow], health: dict[str, object], output: str | Path) -> Path:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    average_clv = sum(row.implied_probability_clv_pp for row in rows) / len(rows) if rows else 0.0
    positive = sum(row.implied_probability_clv_pp > 0 for row in rows)
    alerts = len(health["missing_books"]) + len(health["stale_books"]) + len(health["markets_missing_close"])

    table_rows = []
    for row in rows:
        line = row.line or "-"
        table_rows.append(
            "<tr>"
            f"<td>{escape(row.event_id)}</td>"
            f"<td>{escape(row.sportsbook)}</td>"
            f"<td>{escape(row.market_type)}</td>"
            f"<td>{escape(row.selection)}</td>"
            f"<td>{escape(line)}</td>"
            f"<td>{_fmt_odds(row.entry_odds)}</td>"
            f"<td>{_fmt_odds(row.close_odds)}</td>"
            f"<td class='number'>{row.implied_probability_clv_pp:+.2f} pp</td>"
            f"<td class='number'>{row.decimal_price_improvement_pct:+.2f}%</td>"
            "</tr>"
        )

    missing_close = health["markets_missing_close"]
    alert_items = [f"Missing expected book: {book}" for book in health["missing_books"]]
    alert_items += [f"Stale book: {book}" for book in health["stale_books"]]
    alert_items += [f"Entry has no close: {key}" for key in missing_close]
    alert_html = "".join(f"<li>{escape(item)}</li>" for item in alert_items) or "<li>No feed-health alerts.</li>"

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Synthetic CLV Dashboard</title>
<style>
:root{{--ink:#10243e;--blue:#2463a7;--pale:#eaf1f8;--line:#d6dee8;--good:#1d6b4f;--warn:#8a5a00}}
body{{font-family:Arial,sans-serif;margin:0;background:#f6f8fb;color:var(--ink)}}
main{{max-width:1120px;margin:0 auto;padding:32px 20px 48px}}
h1{{margin:0 0 6px;font-size:30px}} .sub{{color:#526173;margin:0 0 24px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}}
.card{{background:white;border:1px solid var(--line);border-radius:12px;padding:18px}}
.label{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#607086}}
.value{{font-size:28px;font-weight:700;margin-top:5px}}
.panel{{background:white;border:1px solid var(--line);border-radius:12px;padding:18px;margin-top:16px;overflow:auto}}
table{{border-collapse:collapse;width:100%;font-size:14px}} th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}}
th{{background:var(--pale);font-size:12px;text-transform:uppercase}} .number{{font-variant-numeric:tabular-nums}}
.note{{font-size:13px;color:#526173;line-height:1.45}} ul{{line-height:1.55}}
@media(max-width:720px){{.cards{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Synthetic Odds + CLV Dashboard</h1>
<p class="sub">Portfolio demo only. Fabricated events and prices; no recommendations.</p>
<section class="cards">
<div class="card"><div class="label">Paired markets</div><div class="value">{len(rows)}</div></div>
<div class="card"><div class="label">Average implied-probability CLV</div><div class="value">{average_clv:+.2f} pp</div></div>
<div class="card"><div class="label">Positive / feed alerts</div><div class="value">{positive} / {alerts}</div></div>
</section>
<section class="panel"><h2>Entry vs. close</h2><table><thead><tr><th>Event</th><th>Book</th><th>Market</th><th>Selection</th><th>Line</th><th>Entry</th><th>Close</th><th>Prob. CLV</th><th>Price improvement</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table>
<p class="note">Probability CLV is closing raw implied probability minus entry raw implied probability. Price improvement is entry decimal price divided by closing decimal price minus one. Neither measure removes vig.</p></section>
<section class="panel"><h2>Feed health</h2><ul>{alert_html}</ul><p class="note">As of {escape(str(health['as_of_utc']))}; {health['snapshot_count']} stored snapshots.</p></section>
</main></body></html>"""
    output_path.write_text(html, encoding="utf-8")
    return output_path
