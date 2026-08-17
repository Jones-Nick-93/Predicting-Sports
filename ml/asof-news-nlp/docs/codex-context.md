# Betting project context

## Decision and market
Classify a synthetic status label for methodology testing; make no market decision.
## Time semantics
Publication <= ingestion <= feature availability <= prediction < event < settlement. Revisions are distinct bitemporal records.
## Leakage controls
Complete chronological event blocks; vocabulary fit on train only; calibration on the middle block; as-of document filtering before feature extraction.
## Evaluation
Accuracy, ROC AUC, log loss, Brier score, and expected calibration error.
## Public/private boundary
Generated documents only. Exclude real entities, feeds, forecasts, prices, wagers, accounts, credentials, and private infrastructure.
