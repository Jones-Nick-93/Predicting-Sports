from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clv_tracker.dashboard import render_dashboard
from clv_tracker.report import build_clv_rows
from clv_tracker.store import SnapshotStore


def main() -> None:
    artifacts = ROOT / "artifacts"
    store = SnapshotStore(artifacts / "clv_demo.sqlite3")
    ingestion = store.ingest_csv(ROOT / "data" / "sample" / "odds_snapshots.csv")
    health = store.feed_health(
        "2026-07-10T18:50:00Z",
        expected_books={"Book Alpha", "Book Beta", "Book Gamma"},
        stale_after_minutes=30,
    )
    rows = build_clv_rows(store.all_snapshots())
    dashboard = render_dashboard(rows, health, artifacts / "clv_dashboard.html")

    print(f"ingestion={ingestion}")
    print(f"paired_markets={len(rows)}")
    print(f"feed_health={health}")
    print(f"dashboard={dashboard}")


if __name__ == "__main__":
    main()
