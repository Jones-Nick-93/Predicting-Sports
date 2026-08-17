# As-of News NLP Lab

A public-safe NLP project demonstrating how a plausible event-ID join can let a
classifier read tomorrow's definitive update and post-event recap.

## Reproducible finding

| Pipeline | ROC AUC | Log loss | Brier score |
| --- | ---: | ---: | ---: |
| As-of safe | 0.675 | 0.614 | 0.212 |
| Leaky event join | 1.000 | 0.006 | 0.00004 |

The safe test builder blocks 180 future revisions across 90 events. The perfect
leaky result is invalid, not impressive.

## Run

```text
python -m pip install -r requirements-dev.txt
python -m pytest
python examples/run_demo.py
```

The demo writes `artifacts/asof_nlp_dashboard.html`.

## Skills demonstrated

TF-IDF n-grams, logistic text classification, held-out Platt calibration,
bitemporal revision modeling, chronological evaluation, Brier/log-loss/ECE,
adversarial leakage tests, and static frontend generation.

All documents and labels are generated. There are no real injuries, forecasts,
prices, selections, or wagers. See the contracts under [`docs`](docs).
