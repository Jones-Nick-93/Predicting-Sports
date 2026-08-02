# Repository Working Agreements

## Purpose
This repository is a sanitized sports prediction portfolio project. Keep it portable, reproducible, and honest about uncertainty.

## Public Boundary
- Do not commit secrets, raw wagers, account information, private hostnames, local machine paths, licensed data, vendor payloads, or generated betting slips.
- Use deterministic synthetic fixtures for demos and tests.
- Keep live data connectors behind interfaces and environment variables.

## Modeling Rules
- One simulation core should produce the event ledger used by all market extractors.
- Do not create separate market-specific models that can contradict the shared simulation.
- Distinguish event time, source publication time, ingestion time, feature availability time, prediction time, close time, and settlement time.
- Document as-of assumptions before using a feature in a prediction.
- Prefer walk-forward evaluation, calibration checks, and uncertainty intervals over single headline accuracy claims.

## Betting Boundaries
- Separate analytical evidence from wagering decisions.
- Never describe model output as guaranteed profit.
- Include market availability, limits, latency, slippage, and closing-line comparison assumptions when evaluating strategy.

## Verification
- From this project directory, run `python -m unittest discover` and
  `python scripts/run_demo.py` before publishing changes.
- Review diffs for secrets, private data, misleading claims, and accidental generated outputs.
