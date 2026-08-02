import pytest

from clv_tracker.domain import OddsSnapshot, american_to_decimal, american_to_probability


def base_row(**overrides):
    row = {
        "captured_at_utc": "2026-07-10T12:00:00Z",
        "event_id": "SYN-1",
        "starts_at_utc": "2026-07-10T19:00:00Z",
        "sportsbook": "Book Alpha",
        "market_type": "Moneyline",
        "selection": "Metro FC",
        "line": "",
        "american_odds": "+120",
        "snapshot_role": "entry",
    }
    row.update(overrides)
    return row


def test_snapshot_normalizes_tokens_and_timezones():
    snapshot = OddsSnapshot.from_mapping(base_row())
    assert snapshot.market_type == "moneyline"
    assert snapshot.captured_at_utc.endswith("+00:00")
    assert snapshot.american_odds == 120


def test_snapshot_canonicalizes_offset_timestamp_to_utc():
    snapshot = OddsSnapshot.from_mapping(
        base_row(captured_at_utc="2026-07-10T07:00:00-05:00")
    )
    assert snapshot.captured_at_utc == "2026-07-10T12:00:00+00:00"


def test_snapshot_rejects_non_string_required_token_cleanly():
    with pytest.raises(ValueError, match="event_id"):
        OddsSnapshot.from_mapping(base_row(event_id=None))


@pytest.mark.parametrize("odds", [-99, 0, 99])
def test_invalid_american_odds_are_rejected(odds):
    with pytest.raises(ValueError):
        OddsSnapshot.from_mapping(base_row(american_odds=str(odds)))


def test_odds_conversions_are_explicit():
    assert american_to_probability(100) == pytest.approx(0.5)
    assert american_to_probability(-120) == pytest.approx(120 / 220)
    assert american_to_decimal(120) == pytest.approx(2.2)
