from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sports_pipeline import PipelineApi, PipelineService, PipelineStore


def main() -> None:
    now = datetime(2026, 7, 10, 18, 50, tzinfo=timezone.utc)
    store = PipelineStore(ROOT / "artifacts" / "pipeline_demo.sqlite3")
    body = (ROOT / "data" / "sample" / "snapshots.json").read_bytes()
    service = PipelineService(store, clock=lambda: now)
    run_id = f"demo-run-{store.counts()['runs'] + 1}"
    result = service.run("synthetic-demo", lambda: body, run_id=run_id)
    api = PipelineApi(store, "synthetic-demo", clock=lambda: now)
    print(result.to_json())
    print(f"counts={store.counts()}")
    print(f"ready={api.handle('/ready')}")
    print(f"latest={api.handle('/latest-snapshot')}")


if __name__ == "__main__":
    main()
