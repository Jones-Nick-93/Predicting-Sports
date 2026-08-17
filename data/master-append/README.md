# Master Append

An append and reconciliation engine for scheduled reports that accumulate into a
single Excel workbook.

## The problem

Scheduled workbook jobs must remain correct when a run is repeated, missed and later
backfilled, or supplied with records that already exist. A blind `DataFrame.to_excel()`
call does not define how those states should be reconciled.

Different datasets have different duplicate semantics:

- A daily state snapshot should retain the same record on different dates.
- An event feed should reject a repeated natural key.
- A full-state extract should replace prior state rather than accumulate it.

The caller therefore chooses the reconciliation mode explicitly. The library does not
guess the dataset grain.

```python
from master_append import append_to_master

append_to_master(
    df=report_df,
    master_path="./output/report_master.xlsx",
    sheet_name="Records",
    dedup_keys=["Record_ID", "Line_ID"],
    rerun_mode="dedup",
)
```

## Modes

| Mode | Behavior | Appropriate use |
| --- | --- | --- |
| `replace_snapshot` | Replaces rows carrying the supplied snapshot value | Repeated state snapshots |
| `dedup` | Rejects keys already stored and collapses duplicates in the incoming batch | Event data with a natural key |
| `replace_all` | Replaces the target sheet with the current extract | Complete-state extracts |
| `append` | Performs an explicitly unprotected append | Reconciliation already completed upstream |

## Engineering behavior

- Columns align by name when schemas evolve.
- Snapshot values that parse as dates are stored as real Excel dates.
- Existing sheets outside the target sheet are preserved.
- Writes use a temporary file in the destination directory followed by `os.replace`.
- Optional timestamped backups have bounded retention.
- Missing snapshot columns produce a warning rather than silent degradation.

## Run

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q master_append.py test_master_append.py
python examples/run_demo.py
```

The suite contains fourteen deterministic tests covering reconciliation modes,
same-day idempotency, cross-day accumulation, schema validation, snapshot retention,
legacy text dates, and preservation of unrelated sheets.

## Limitations

- Workbooks are read fully into memory.
- `openpyxl` may not preserve charts, images, or pivot tables.
- Concurrent writers are not coordinated; schedule writes sequentially or use a
  database-backed design.
- `append` intentionally provides no duplicate protection.

## Publication boundary

All identifiers, paths, dates, and examples are fabricated. The project contains no
source queries, real report schemas, workbook contents, company identifiers, network
locations, credentials, or production schedules.

Released under the MIT License. See `LICENSE`.
