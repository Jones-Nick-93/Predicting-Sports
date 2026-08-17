"""Run a deterministic workbook reconciliation demo in a temporary directory."""

from datetime import date
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from master_append import append_to_master


def main() -> None:
    records = pd.DataFrame(
        {
            "Record_ID": ["sample-a", "sample-b"],
            "Metric_Value": [10, 20],
        }
    )

    with TemporaryDirectory() as temporary_directory:
        workbook = Path(temporary_directory) / "report_master.xlsx"
        for snapshot in (date(2026, 1, 15), date(2026, 1, 15), date(2026, 1, 16)):
            append_to_master(
                records,
                workbook,
                "Records",
                rerun_mode="replace_snapshot",
                snapshot_value=snapshot,
                keep_backup=False,
                verbose=False,
            )

        result = pd.read_excel(workbook, sheet_name="Records")
        snapshot_count = result["Snapshot_Date"].nunique()
        print(f"rows={len(result)} snapshots={snapshot_count} same_day_rerun=idempotent")


if __name__ == "__main__":
    main()
