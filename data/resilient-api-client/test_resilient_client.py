"""Deterministic tests using a fake transport and fabricated resources."""

import pytest
import requests

from resilient_client import AuthError, ResilientApiClient


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, headers=None):
        self.status_code = status_code
        self._json = {} if json_data is None else json_data
        self.headers = headers or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if not self.responses:
            return FakeResponse(200, {})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class TokenProvider:
    def __init__(self):
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return f"synthetic-token-{self.calls}"


def build(session, provider=None, **kwargs):
    kwargs.setdefault("dry_run", False)
    kwargs.setdefault("backoff_base", 1.0)
    kwargs.setdefault("sleep", lambda _: None)
    kwargs.setdefault("jitter", lambda _low, _high: 0.0)
    return ResilientApiClient(
        base_url="https://api.example.invalid",
        token_provider=provider or TokenProvider(),
        session=session,
        **kwargs,
    )


def test_invalid_configuration_fails_fast():
    with pytest.raises(ValueError):
        ResilientApiClient(base_url="not-a-url", token_provider=TokenProvider())
    with pytest.raises(TypeError):
        ResilientApiClient(base_url="https://api.example.invalid", token_provider=None)


def test_expired_token_triggers_one_refresh_and_replay():
    provider = TokenProvider()
    session = FakeSession([
        FakeResponse(401),
        FakeResponse(200, {"items": [{"id": "item-1"}]}),
    ])
    client = build(session, provider=provider)
    result = client.list_resources("/v1/items", result_field="items")
    assert result == [{"id": "item-1"}]
    assert provider.calls == 2


def test_repeated_401_does_not_loop_forever():
    client = build(FakeSession([FakeResponse(401), FakeResponse(401)]))
    with pytest.raises(requests.HTTPError):
        client.list_resources("/v1/items")


def test_server_error_is_retried():
    session = FakeSession([FakeResponse(503), FakeResponse(200, {"data": []})])
    assert build(session).list_resources("/v1/items") == []
    assert len(session.calls) == 2


def test_client_error_is_not_retried():
    session = FakeSession([FakeResponse(400)])
    with pytest.raises(requests.HTTPError):
        build(session).list_resources("/v1/items")
    assert len(session.calls) == 1


def test_rate_limit_honors_retry_after():
    slept = []
    session = FakeSession([
        FakeResponse(429, headers={"Retry-After": "2"}),
        FakeResponse(200, {"data": []}),
    ])
    client = build(session, sleep=slept.append)
    client.list_resources("/v1/items")
    assert slept == [2.0]


def test_conflict_is_reported_as_a_distinct_outcome():
    client = build(FakeSession([FakeResponse(409)]))
    created, conflicted = client.create_resource(
        "/v1/items",
        {"external_id": "sample-001"},
    )
    assert created is None
    assert conflicted is True


def test_dry_run_makes_no_write_calls():
    session = FakeSession([])
    client = build(session, dry_run=True)
    client.create_resource("/v1/items", {"external_id": "sample-001"})
    client.delete_resource("/v1/items", "item-1")
    assert session.calls == []


def test_bulk_delete_requires_confirmation():
    session = FakeSession([])
    client = build(session)
    assert client.delete_many("/v1/items", ["item-1", "item-2"]) == (0, 2)
    assert session.calls == []


def test_bulk_delete_is_blocked_in_dry_run_even_when_confirmed():
    session = FakeSession([])
    client = build(session, dry_run=True)
    assert client.delete_many("/v1/items", ["item-1"], confirm=True) == (0, 1)
    assert session.calls == []


def test_bulk_delete_encodes_identifiers():
    session = FakeSession([FakeResponse(200)])
    client = build(session)
    assert client.delete_many("/v1/items", ["item/with/slashes"], confirm=True) == (1, 0)
    assert session.calls[0][1].endswith("/v1/items/item%2Fwith%2Fslashes")


def test_token_provider_failure_does_not_leak_exception_text():
    def bad_provider():
        raise RuntimeError("synthetic-sensitive-value")

    client = build(FakeSession([]), provider=bad_provider)
    with pytest.raises(AuthError) as exc:
        client.list_resources("/v1/items")
    assert "synthetic-sensitive-value" not in str(exc.value)


@pytest.mark.parametrize("path", ["https://other.example.invalid/items", "//other/items", "items"])
def test_absolute_or_malformed_paths_are_rejected(path):
    session = FakeSession([])
    client = build(session)
    with pytest.raises(ValueError):
        client.list_resources(path)
    assert session.calls == []
