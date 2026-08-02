# Data Contracts and Time Semantics

## Required Times
Every real data source added later should define:

- `event_time`: when the game starts.
- `source_publication_time`: when the source says the information became public.
- `ingestion_time`: when our system received it.
- `feature_available_time`: when the feature could first be used by the model.
- `prediction_time`: when the model output was generated.
- `market_snapshot_time`: when odds or lines were observed.
- `settlement_time`: when the result became final.

## Market Contract
Each market record should include:

- event identifier
- sport and league
- market type
- selection
- line, if any
- American odds
- book or source
- snapshot time
- status
- provenance

The public `MarketPrice` output additionally separates:

- raw selection win probability;
- push probability;
- conditional win probability after pushes are removed; and
- fair American odds derived from that conditional probability.

## Simulation Ledger Contract

Every plate appearance records:

- a monotonic sequence number;
- team, inning, and top/bottom half;
- stable batter and pitcher identifiers;
- outcome;
- outs and base occupancy before and after the play;
- runs scored on the play; and
- the batting team's cumulative runs after the play.

Display names are presentation metadata and are never used as identifiers.

## Leakage Controls
- A feature is valid only if `feature_available_time <= prediction_time`.
- Closing prices cannot be used to choose entries.
- Corrected historical data must preserve revision timing.
- Missing, late, stale, corrected, and duplicated records are explicit states, not silent defaults.
