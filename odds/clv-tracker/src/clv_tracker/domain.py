from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping


REQUIRED_FIELDS = {
    "captured_at_utc",
    "event_id",
    "starts_at_utc",
    "sportsbook",
    "market_type",
    "selection",
    "line",
    "american_odds",
    "snapshot_role",
}


def parse_utc(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 timestamp")
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def normalize_token(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        raise ValueError(f"{field} is required")
    return cleaned


def validate_american_odds(odds: int) -> int:
    if -99 <= odds <= 99:
        raise ValueError("american_odds must be <= -100 or >= +100")
    return odds


def american_to_probability(odds: int) -> float:
    validate_american_odds(odds)
    if odds < 0:
        return abs(odds) / (abs(odds) + 100.0)
    return 100.0 / (odds + 100.0)


def american_to_decimal(odds: int) -> float:
    validate_american_odds(odds)
    if odds < 0:
        return 1.0 + 100.0 / abs(odds)
    return 1.0 + odds / 100.0


@dataclass(frozen=True)
class OddsSnapshot:
    captured_at_utc: str
    event_id: str
    starts_at_utc: str
    sportsbook: str
    market_type: str
    selection: str
    line: str
    american_odds: int
    snapshot_role: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, str]) -> "OddsSnapshot":
        missing = REQUIRED_FIELDS.difference(row.keys())
        if missing:
            raise ValueError(f"missing fields: {', '.join(sorted(missing))}")

        captured = parse_utc(row["captured_at_utc"], "captured_at_utc")
        starts = parse_utc(row["starts_at_utc"], "starts_at_utc")
        if captured > starts:
            raise ValueError("captured_at_utc cannot be after starts_at_utc")

        try:
            odds = validate_american_odds(int(row["american_odds"]))
        except (TypeError, ValueError) as exc:
            raise ValueError("american_odds must be a valid integer price") from exc

        role = row["snapshot_role"].strip().lower()
        if role not in {"entry", "close"}:
            raise ValueError("snapshot_role must be entry or close")

        return cls(
            captured_at_utc=captured.isoformat(),
            event_id=normalize_token(row["event_id"], "event_id"),
            starts_at_utc=starts.isoformat(),
            sportsbook=normalize_token(row["sportsbook"], "sportsbook"),
            market_type=normalize_token(row["market_type"], "market_type").lower().replace(" ", "_"),
            selection=normalize_token(row["selection"], "selection"),
            line="" if row["line"] is None else str(row["line"]).strip(),
            american_odds=odds,
            snapshot_role=role,
        )

    @property
    def market_key(self) -> tuple[str, str, str, str, str]:
        return (self.event_id, self.sportsbook, self.market_type, self.selection, self.line)
