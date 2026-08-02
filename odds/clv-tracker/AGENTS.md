# Codex Working Agreement

## Purpose

Build a public-safe odds and CLV tracking reference implementation. Favor clear
data contracts, reproducibility, and operational evidence over model complexity.

## Safety and scope

- Use fabricated data only in the repository.
- Never add sportsbook credentials, account identifiers, real bet history, private
  feed URLs, paid-feed payloads, bankroll rules, or production secrets.
- Do not describe raw implied-probability movement as no-vig CLV.
- Keep ingestion idempotent and timestamps timezone-aware.
- Treat external rows as untrusted; validate before database writes.
- Do not add forecasting, selection, or staking logic to this repository.

## Commands

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/demo.py
python -m compileall -q src scripts tests
```

## Definition of done

- Tests and the synthetic demo pass.
- Re-running ingestion adds zero duplicate rows.
- Metrics and limitations remain accurately labeled.
- No secret, private, licensed, or real wagering data is added.
- Handoff includes changed files, checks, assumptions, and known gaps.
