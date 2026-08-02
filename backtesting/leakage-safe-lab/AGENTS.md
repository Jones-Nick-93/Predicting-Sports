# Codex Working Agreement

- Use synthetic data only.
- Never random-split time-series evaluation data.
- Every feature and prediction must have an explicit as-of timestamp.
- Fit transformations, calibration, and thresholds on training data only.
- Keep an embargo between training and test when information can arrive late.
- Include limits, latency, market availability, and event lock in execution tests.
- Do not report ROI without sample size, uncertainty, drawdown, and assumptions.
- Add a regression test for every leakage or execution bug.

Run `python -m pytest -q` and `python scripts/demo.py` before handoff.
