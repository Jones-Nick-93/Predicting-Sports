from __future__ import annotations

from html import escape
from pathlib import Path


def render_dashboard(report: dict[str, object], output: str | Path) -> Path:
    path = Path(output); path.parent.mkdir(parents=True, exist_ok=True)
    safe = report["pipelines"]["asof_safe"]; leaky = report["pipelines"]["leaky_event_join"]
    rows = "".join(
        f"<tr><td>{escape(label)}</td><td>{values['metrics']['accuracy']:.1%}</td><td>{values['metrics']['roc_auc']:.3f}</td><td>{values['metrics']['log_loss']:.3f}</td><td>{values['metrics']['brier_score']:.3f}</td><td>{values['metrics']['expected_calibration_error']:.3f}</td></tr>"
        for label, values in (("As-of safe", safe), ("Leaky event join", leaky))
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>As-of News NLP Lab</title><style>
:root{{--bg:#f3efe7;--ink:#17231f;--green:#176b52;--red:#b23a48;--panel:#fffdf8;--line:#d9d2c4}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px Georgia,serif}}main{{max-width:1050px;margin:auto;padding:50px 22px}}h1{{font-size:43px;margin:8px 0;letter-spacing:-.035em}}.eyebrow{{font:700 12px Arial;color:var(--green);text-transform:uppercase;letter-spacing:.16em}}.sub{{max-width:720px;line-height:1.6;color:#55615c}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:28px 0}}.card,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px;box-shadow:0 12px 35px #483b2520}}.label{{font:11px Arial;text-transform:uppercase;letter-spacing:.1em;color:#69736f}}.value{{font:700 30px Arial;margin-top:7px}}.safe{{color:var(--green)}}.leak{{color:var(--red)}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left}}th{{font:700 11px Arial;text-transform:uppercase;color:#69736f}}code{{background:#efe9dd;padding:2px 5px;border-radius:4px}}.note{{font-size:13px;line-height:1.55;color:#5d6863}}@media(max-width:700px){{.cards{{grid-template-columns:1fr}}.panel{{overflow:auto}}}}</style></head><body><main>
<div class="eyebrow">NLP / bitemporal data / leakage audit</div><h1>The model that knew tomorrow's news</h1><p class="sub">Two identical TF-IDF classifiers. One respects feature availability. One joins every revision by event ID and quietly reads definitive and post-event reports.</p>
<section class="cards"><div class="card"><div class="label">Safe ROC AUC</div><div class="value safe">{safe['metrics']['roc_auc']:.3f}</div></div><div class="card"><div class="label">Leaky ROC AUC</div><div class="value leak">{leaky['metrics']['roc_auc']:.3f}</div></div><div class="card"><div class="label">Future items blocked</div><div class="value">{safe['documents']['future_items_excluded']}</div></div></section>
<section class="panel"><h2>Same model, different information set</h2><table><thead><tr><th>Pipeline</th><th>Accuracy</th><th>ROC AUC</th><th>Log loss</th><th>Brier</th><th>ECE</th></tr></thead><tbody>{rows}</tbody></table><p class="note">Lower log loss, Brier score, and ECE are better. The leaky result is invalid even when its metrics look spectacular.</p></section>
<section class="panel"><h2>Confirmed finding</h2><p>{escape(report['audit']['confirmed_leakage'])}</p><p class="note"><strong>Prevention test:</strong> {escape(report['audit']['prevention_test'])}</p></section><p class="note">Generated documents only. No real players, teams, events, forecasts, prices, or wagers.</p></main></body></html>"""
    path.write_text(html, encoding="utf-8"); return path
