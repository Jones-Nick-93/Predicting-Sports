# Codex Context

## Decision and Market
Build one MLB-style simulator that generates all supported game and player
markets from a shared ledger. Market modules summarize results; they do not run
independent predictive models.

## Current Public Scope
- MLB-style synthetic demo.
- Deterministic simulation with seeded randomness.
- Regulation, walk-off, extra-inning, and starter-to-bullpen accounting.
- Market extractors for moneyline, totals, team totals, run line, pitcher strikeouts, hitter total bases, and hitter home runs.

## Time Semantics
The synthetic demo has no live timing. A real data adapter must record event,
publication, ingestion, feature-availability, prediction, market-snapshot,
close, and settlement timestamps before evaluation.

## Data Sources and Rights
Only deterministic fictional fixtures are public. Real sources require a
documented license or redistribution basis and must remain outside this project
unless their inclusion is explicitly safe.

## Evaluation and Calibration
Software invariants are tested now. Predictive claims require chronological,
slate-grouped evaluation; calibration by market family; uncertainty intervals;
and realistic line availability, limits, latency, slippage, and close timing.

## Private-to-Public Boundary
Do not copy the working lab repository directly. The lab may contain private paths, generated projections, database notes, live-data assumptions, caches, and other non-public material. Public examples should use synthetic fixtures and portable configuration.

## Definition of Done for Public Work
- `python -m unittest` passes.
- `python scripts/run_demo.py` completes from a clean setup.
- README claims are supported by tests or demo output.
- No raw data, secrets, local paths, private infrastructure details, or wager records are committed.
- Timing assumptions are documented when a model uses real data.
