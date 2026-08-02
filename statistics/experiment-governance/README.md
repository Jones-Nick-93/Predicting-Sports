# Statistical Experiment Governance

A public-safe, domain-agnostic toolkit for registering experiment families, logging
every tested hypothesis, correcting for multiple comparisons, and running transparent
paired inference on synthetic or user-supplied evaluation losses.

This project contains evaluation infrastructure only. It does not include forecasting
models, features, live data, position sizing, bankroll rules, execution criteria,
production performance, or private system architecture.

## What it demonstrates

- A fixed hypothesis family declared before results are recorded
- Rejection of undeclared and duplicate trials
- Bonferroni and Holm family-wise error control based on the full registered family
- A paired sign-flip test with exact enumeration for small samples and deterministic
  Monte Carlo estimation for larger samples
- Kish effective sample size as a weight-concentration diagnostic
- Explicit assumptions and failure modes instead of automatic “significant” claims

## Run

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python examples/run_governance_demo.py
```

The example uses fabricated fold-level losses and has no connection to a private model
or real decision history.

## Important limitations

- A low p-value does not establish practical value, causal validity, or future
  performance.
- The paired sign-flip test assumes exchangeable signs under the null. Correlated
  row-level observations should first be aggregated into defensible independent units,
  such as held-out time blocks.
- Effective sample size describes weight concentration; it is not, by itself, a valid
  significance test or a correction for dependence.
- Multiple-testing corrections work only when the full family is registered and every
  result is retained.

See `docs/inference-contract.md` and `docs/publication-scope.md`.
