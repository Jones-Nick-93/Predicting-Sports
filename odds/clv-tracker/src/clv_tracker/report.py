from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from .domain import OddsSnapshot, american_to_decimal, american_to_probability


@dataclass(frozen=True)
class ClvRow:
    event_id: str
    sportsbook: str
    market_type: str
    selection: str
    line: str
    entry_odds: int
    close_odds: int
    entry_captured_at_utc: str
    close_captured_at_utc: str
    implied_probability_clv_pp: float
    decimal_price_improvement_pct: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_clv_rows(snapshots: list[OddsSnapshot]) -> list[ClvRow]:
    grouped: dict[tuple[str, str, str, str, str], list[OddsSnapshot]] = defaultdict(list)
    for snapshot in snapshots:
        grouped[snapshot.market_key].append(snapshot)

    result: list[ClvRow] = []
    for key, values in sorted(grouped.items()):
        entries = [item for item in values if item.snapshot_role == "entry"]
        closes = [item for item in values if item.snapshot_role == "close"]
        if not entries or not closes:
            continue
        close = max(closes, key=lambda item: item.captured_at_utc)
        valid_entries = [item for item in entries if item.captured_at_utc <= close.captured_at_utc]
        if not valid_entries:
            continue
        entry = max(valid_entries, key=lambda item: item.captured_at_utc)

        entry_probability = american_to_probability(entry.american_odds)
        close_probability = american_to_probability(close.american_odds)
        entry_decimal = american_to_decimal(entry.american_odds)
        close_decimal = american_to_decimal(close.american_odds)

        result.append(
            ClvRow(
                event_id=key[0],
                sportsbook=key[1],
                market_type=key[2],
                selection=key[3],
                line=key[4],
                entry_odds=entry.american_odds,
                close_odds=close.american_odds,
                entry_captured_at_utc=entry.captured_at_utc,
                close_captured_at_utc=close.captured_at_utc,
                implied_probability_clv_pp=round((close_probability - entry_probability) * 100.0, 3),
                decimal_price_improvement_pct=round((entry_decimal / close_decimal - 1.0) * 100.0, 3),
            )
        )
    return result
