"""Exercise retry and conflict behavior without making a network request."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resilient_client import ResilientApiClient


class DemoResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self.payload = payload or {}
        self.headers = {}

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"synthetic HTTP {self.status_code}")


class DemoSession:
    def __init__(self):
        self.responses = [
            DemoResponse(503),
            DemoResponse(200, {"items": [{"id": "sample-001"}]}),
            DemoResponse(409),
        ]
        self.call_count = 0

    def request(self, method, url, **kwargs):
        self.call_count += 1
        return self.responses.pop(0)


def main() -> None:
    session = DemoSession()
    client = ResilientApiClient(
        base_url="https://api.example.invalid",
        token_provider=lambda: "synthetic-token",
        dry_run=False,
        session=session,
        sleep=lambda _: None,
        jitter=lambda _low, _high: 0.0,
    )

    items = client.list_resources("/v1/items", result_field="items")
    created, conflicted = client.create_resource(
        "/v1/items",
        {"external_id": "sample-001"},
    )
    print(
        f"items={len(items)} retried=True created={created is not None} "
        f"conflicted={conflicted} calls={session.call_count}"
    )


if __name__ == "__main__":
    main()
