# Codex Working Agreement

- Use generated documents only; exclude real players, injuries, prices, wagers, accounts, feeds, credentials, and private parameters.
- Define prediction time and feature-availability time for every document revision.
- Fit vocabulary, classifier, and calibration only on their registered chronological blocks.
- Keep the intentionally leaky join visibly named and never reuse it as a production path.
- Report discrimination and calibration; perfect results require a leakage investigation.
- No output grants forecasting, wagering, or production authority.

Run `python -m pytest` and `python examples/run_demo.py`.
