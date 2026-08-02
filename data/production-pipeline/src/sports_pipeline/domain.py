from __future__ import annotations

from dataclasses import asdict, dataclass
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


def parse_utc(value: str, field: str) -> datetime:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _token(value: object, field: str) -> str:
    try:
        cleaned = " ".join(value.strip().split())
    except AttributeError as exc:
        raise ValueError(f"{field} must be a string") from exc
    if not cleaned:
        raise ValueError(f"{field} is required")
    return cleaned


@dataclass(frozen=True)
class Snapshot:
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
    def from_mapping(cls, row: Mapping[str, object]) -> "Snapshot":
        missing = REQUIRED_FIELDS.difference(row.keys())
        if missing:
            raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
        captured = parse_utc(str(row["captured_at_utc"]), "captured_at_utc")
        starts = parse_utc(str(row["starts_at_utc"]), "starts_at_utc")
        if captured > starts:
            raise ValueError("captured_at_utc cannot be after starts_at_utc")
        try:
            odds = int(row["american_odds"])
        except (TypeError, ValueError) as exc:
            raise ValueError("american_odds must be an integer") from exc
        if -99 <= odds <= 99:
            raise ValueError("american_odds must be <= -100 or >= +100")
        role = _token(str(row["snapshot_role"]), "snapshot_role").lower()
        if role not in {"entry", "close"}:
            raise ValueError("snapshot_role must be entry or close")
        line_value = row["line"]
        if line_value is None:
            line = ""
        elif isinstance(line_value, (str, int, float)):
            line = str(line_value).strip()
        else:
            raise ValueError("line must be a scalar value")
        return cls(
            captured_at_utc=captured.isoformat(),
            event_id=_token(row["event_id"], "event_id"),
            starts_at_utc=starts.isoformat(),
            sportsbook=_token(row["sportsbook"], "sportsbook"),
            market_type=_token(row["market_type"], "market_type").lower().replace(" ", "_"),
            selection=_token(row["selection"], "selection"),
            line=line,
            american_odds=odds,
            snapshot_role=role,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
