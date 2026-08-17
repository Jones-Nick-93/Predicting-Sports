# Task brief

## Outcome

Create a reproducible public demonstration that measures predictive uncertainty
and routes unreliable synthetic forecasts to review instead of forcing action.

## Known facts

- The monorepo already contains leakage-safe evaluation and experiment-governance projects.
- It does not yet contain a runnable uncertainty-quantification challenger.
- MAPIE and NGBoost are available as general-purpose Python packages.

## Assumptions

- A synthetic continuous target is sufficient for the first reusable vertical slice.
- Time-ordered regime shift is more informative than an IID random-split demonstration.

## In scope

- Time-aware synthetic data with explicit availability semantics.
- Point, split-conformal, and distributional predictions.
- Coverage, width, proper interval score, MAE, and RMSE.
- Out-of-domain and excessive-width review gates.
- Stable and shifted regime reporting.

## Out of scope

- Real sports data, prices, selections, staking, CLV, production deployment, or
  a claim that uncertainty alone creates an edge.

## Relevant artifacts

- `backtesting/leakage-safe-lab`
- `statistics/experiment-governance`
- `statistics/uncertainty-gates`

## Acceptance criteria

- Every split is chronological and nonoverlapping.
- Feature availability precedes prediction, which precedes event time.
- MAPIE and NGBoost intervals are finite and ordered.
- Metrics are reported overall and by known synthetic regime.
- Gate thresholds do not use test outcomes.
- Tests and deterministic demo pass.

## Verification

- Run pytest and the example.
- Re-run the example and compare deterministic non-timing output.
- Syntax-check all Python files without generating repository artifacts.
- Scan the new project for prohibited private content.

## Risks and approval gates

- Exchangeability violations can invalidate nominal conformal coverage.
- Distributional assumptions may produce narrower but miscalibrated intervals.
- Any real-data extension requires a separate publication and leakage review.

## Finish and handoff

- Report coverage, width, shifted-regime degradation, gate routing, dependency
  versions, and unresolved validity risks.

