# Codex Working Agreement

## Repository purpose

This is a deliberately limited, public-safe portfolio sample of generic soccer
market arithmetic. It is not the private forecasting system and must not grow
into a reproduction of that system.

## Public/private boundary

- Keep the exclusions in `docs/publication-scope.md` authoritative.
- Never add real fixtures, prices, projections, results, account information,
  bankroll values, production staking rules, data-source details, production parameters,
  credentials, endpoints, serialized models, or private-system architecture.
- Use only small, fabricated inputs in examples and tests.
- Do not infer or reconstruct withheld private logic from surrounding files.

## Working rules

- Inspect the relevant files before editing.
- Prefer the smallest coherent change; do not expand scope without explaining why.
- Preserve pure, deterministic market-math functions.
- Generic Kelly arithmetic may accept an explicit caller-supplied multiplier, but
  must not encode a production multiplier, bankroll, cap, limit, or bet-selection rule.
- Treat probability grids as untrusted inputs when adding public APIs: validate
  shape, finiteness, non-negativity, and normalization explicitly.
- Keep settlement quantities clearly named. Do not label a push-adjusted score as
  a literal win probability or convert it directly to odds without documenting
  the pricing convention.
- Add or update synthetic tests for every behavior change.
- Do not weaken `.gitignore` or the publication boundary.

## Commands

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python examples/run_market_math.py
python -m compileall -q src examples
```

## Definition of done

- Tests pass.
- The example runs.
- No private or licensed data is introduced.
- New behavior is documented in plain language.
- The handoff lists changed files, verification performed, assumptions, and risks.
