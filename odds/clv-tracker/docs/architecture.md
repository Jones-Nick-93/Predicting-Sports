# Architecture

```text
synthetic/public CSV
        |
        v
validation + normalization
        |
        v
SQLite snapshots (unique replay key)
        |
        +--> feed-health checks
        |      - stale books
        |      - expected books missing
        |      - entry without close
        |
        +--> entry/close pairing
               - implied-probability CLV
               - decimal-price improvement
                       |
                       v
                static HTML dashboard
```

The starter keeps transport and vendor integrations outside the repository. That
lets reviewers evaluate the data contract, idempotency, calculations, and operations
without exposing credentials or licensed payloads.
