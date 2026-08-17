# Synthetic Data Contract

## Grain and identity

One row represents one synthetic event forecast. Row order is the stable event
identity for this laboratory; no external team, league, market, or account
identifier exists.

## Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `X[:, 0]` | float | Synthetic strength feature |
| `X[:, 1]` | float | Synthetic pace feature |
| `X[:, 2]` | float | Nonnegative volatility feature |
| `X[:, 3]` | float | Synthetic seasonal feature |
| `y` | float | Synthetic continuous outcome |
| `regime` | string | `stable` or deliberately `shifted` |

All features and targets must be finite. The generator is deterministic for a
fixed seed.

## Time semantics

Every row carries timezone-aware UTC timestamps satisfying:

```text
publication_time <= ingestion_time <= feature_available_time
                 <= prediction_time < event_time
```

`event_time` is strictly increasing. No feature is treated as usable before its
`feature_available_time`.

## Evaluation split

Rows are divided without shuffling:

- First 60%: model training.
- Next 20%: conformalization and uncertainty-gate reference predictions.
- Final 20%: one test block containing stable and shifted regimes.

Test targets never determine interval widths, feature envelopes, or gate
thresholds.

## Missingness, corrections, and provenance

The synthetic generator emits no missing, late, duplicated, or corrected rows.
A real-data adapter would need to represent those states explicitly and preserve
source, publication, ingestion, revision, and availability timestamps. This
project deliberately does not claim that adapter exists.
