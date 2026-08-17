# Evaluation contract

- Default nominal coverage: 90%.
- Model fit block: earliest 60% of rows.
- Conformalization block: next 20%.
- Test block: final 20%.
- Regime shift begins at 90% of the full sequence, dividing the test block into
  stable and shifted halves.
- Gate width thresholds come from conformalization predictions only.
- Feature-envelope thresholds come from training features only.
- No test outcome may change a model, interval, threshold, or gate.
- Report all registered model families, including degraded results.

