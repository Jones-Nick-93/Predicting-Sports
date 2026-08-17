# Task brief

## Outcome
Build a deterministic bitemporal NLP lab that quantifies future-document leakage.
## In scope
Synthetic revisions, safe/leaky builders, TF-IDF, calibration, metrics, adversarial tests, dashboard.
## Out of scope
Real news, scraping, player forecasts, betting, deployment, and production claims.
## Acceptance criteria
Only available revisions enter the safe model; preprocessing is train-only; labels settle before later prediction blocks; the adversarial append test passes.
## Highest-risk validity gap
Synthetic language is intentionally separable and cannot establish real-world NLP performance.
