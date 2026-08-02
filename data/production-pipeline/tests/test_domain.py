import pytest

from sports_pipeline.domain import Snapshot


def valid_row(**overrides):
    row = {
        "captured_at_utc": "2026-07-10T13:45:00-05:00",
        "event_id": "SYN-1",
        "starts_at_utc": "2026-07-10T19:00:00Z",
        "sportsbook": "Book Alpha",
        "market_type": "Moneyline",
        "selection": "Metro FC",
        "line": "",
        "american_odds": 105,
        "snapshot_role": "close",
    }
    row.update(overrides)
    return row


def test_snapshot_normalizes_contract_to_utc():
    snapshot = Snapshot.from_mapping(valid_row())
    assert snapshot.captured_at_utc == "2026-07-10T18:45:00+00:00"
    assert snapshot.market_type == "moneyline"


@pytest.mark.parametrize("odds", [-99, 0, 99])
def test_snapshot_rejects_invalid_american_odds(odds):
    with pytest.raises(ValueError):
        Snapshot.from_mapping(valid_row(american_odds=odds))


def test_snapshot_rejects_null_required_token():
    with pytest.raises(ValueError, match="event_id"):
        Snapshot.from_mapping(valid_row(event_id=None))
