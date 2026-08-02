# Snapshot Data Contract

Each CSV row is one quoted selection at one capture time.

| Field | Type | Rule |
|---|---|---|
| `captured_at_utc` | ISO-8601 timestamp | Required, timezone-aware |
| `event_id` | string | Required stable synthetic/public event key |
| `starts_at_utc` | ISO-8601 timestamp | Required, timezone-aware |
| `sportsbook` | string | Required normalized book name |
| `market_type` | string | Required, lowercase token such as `moneyline` |
| `selection` | string | Required normalized outcome label |
| `line` | string | Empty for line-free markets; otherwise explicit signed line |
| `american_odds` | integer | At most `-100` or at least `+100`; zero is invalid |
| `snapshot_role` | enum | `entry` or `close` |

## Normalized market identity

CLV rows are paired on:

`event_id + sportsbook + market_type + selection + line`

That conservative key prevents a price from being compared with another book,
selection, market type, or handicap line.

## Idempotency

The database uniqueness constraint covers the complete normalized snapshot. An
identical replay is skipped. A changed capture time or changed price is a new snapshot.

## Close policy

The starter trusts the explicit `snapshot_role`. A production feed must define and
test its own close policy, for example the last complete and non-stale snapshot before
an event-specific market lock.
