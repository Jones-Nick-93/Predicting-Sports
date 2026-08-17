"""
Tests for master_append.

Each test targets a reconciliation guarantee the engine claims to make.
Run with: pytest test_master_append.py
"""

import os
import tempfile
import warnings
from datetime import date

import pandas as pd
import pytest

from master_append import append_to_master


@pytest.fixture
def master(tmp_path):
    return str(tmp_path / "master.xlsx")


def read(path, sheet="Data"):
    return pd.read_excel(path, sheet_name=sheet)


def test_replace_snapshot_is_idempotent(master):
    """Running the same day twice must not double the rows."""
    df = pd.DataFrame({"Order": ["A", "B"], "Qty": [1, 2]})
    append_to_master(df, master, "Data", rerun_mode="replace_snapshot",
                     snapshot_value=date(2026, 1, 15), verbose=False)
    append_to_master(df, master, "Data", rerun_mode="replace_snapshot",
                     snapshot_value=date(2026, 1, 15), verbose=False)
    assert len(read(master)) == 2


def test_replace_snapshot_accumulates_across_days(master):
    """Distinct snapshot days must both survive."""
    df = pd.DataFrame({"Order": ["A", "B"], "Qty": [1, 2]})
    append_to_master(df, master, "Data", rerun_mode="replace_snapshot",
                     snapshot_value=date(2026, 1, 15), verbose=False)
    append_to_master(df, master, "Data", rerun_mode="replace_snapshot",
                     snapshot_value=date(2026, 1, 16), verbose=False)
    assert len(read(master)) == 4


def test_dedup_blocks_keys_already_in_master(master):
    df1 = pd.DataFrame({"Order": ["A", "B"], "Item": ["1", "2"], "Qty": [1, 2]})
    df2 = pd.DataFrame({"Order": ["B", "C"], "Item": ["2", "3"], "Qty": [2, 3]})
    append_to_master(df1, master, "Data", dedup_keys=["Order", "Item"],
                     rerun_mode="dedup", verbose=False)
    append_to_master(df2, master, "Data", dedup_keys=["Order", "Item"],
                     rerun_mode="dedup", verbose=False)
    out = read(master)
    assert len(out) == 3
    assert set(out["Order"]) == {"A", "B", "C"}


def test_dedup_collapses_duplicates_inside_one_batch(master):
    """
    Regression: a single pull containing the same key twice previously
    wrote both rows, because incoming rows were only compared against the
    master and never against each other.
    """
    df = pd.DataFrame({
        "Order": ["A", "A", "B"],
        "Item": ["1", "1", "2"],
        "Qty": [5, 5, 7],
    })
    append_to_master(df, master, "Data", dedup_keys=["Order", "Item"],
                     rerun_mode="dedup", verbose=False)
    assert len(read(master)) == 2


def test_replace_all_discards_prior_state(master):
    df1 = pd.DataFrame({"Order": ["A", "B", "C"], "Qty": [1, 2, 3]})
    df2 = pd.DataFrame({"Order": ["D"], "Qty": [4]})
    append_to_master(df1, master, "Data", rerun_mode="replace_all", verbose=False)
    append_to_master(df2, master, "Data", rerun_mode="replace_all", verbose=False)
    out = read(master)
    assert len(out) == 1
    assert out["Order"].iloc[0] == "D"


def test_append_does_not_protect(master):
    """append is documented as unprotected. Prove it stays that way."""
    df = pd.DataFrame({"Order": ["A"], "Qty": [1]})
    append_to_master(df, master, "Data", rerun_mode="append", verbose=False)
    append_to_master(df, master, "Data", rerun_mode="append", verbose=False)
    assert len(read(master)) == 2


def test_missing_snapshot_column_warns_instead_of_silently_appending(master):
    """
    Regression: when the existing master lacks the snapshot column,
    replace_snapshot has nothing to match on and degrades to a blind
    append. That must be surfaced, not silent.
    """
    pd.DataFrame({"Order": ["A"], "Qty": [1]}).to_excel(
        master, sheet_name="Data", index=False
    )
    df = pd.DataFrame({"Order": ["B"], "Qty": [2]})
    with pytest.warns(UserWarning, match="absent from the existing master"):
        append_to_master(df, master, "Data", rerun_mode="replace_snapshot",
                         verbose=False)


def test_snapshot_stored_as_real_date(master):
    df = pd.DataFrame({"Order": ["A"], "Qty": [1]})
    append_to_master(df, master, "Data", snapshot_value=date(2026, 1, 15),
                     verbose=False)
    out = read(master)
    assert pd.api.types.is_datetime64_any_dtype(out["Snapshot_Date"])


def test_text_snapshot_from_older_master_still_matches(master):
    """
    Backward compatibility: masters written before dates were stored as
    real dates hold text. The compare key normalizes both so replacement
    still finds them.
    """
    pd.DataFrame({
        "Snapshot_Date": ["2026-01-15"],
        "Order": ["A"],
        "Qty": [1],
    }).to_excel(master, sheet_name="Data", index=False)
    df = pd.DataFrame({"Order": ["B"], "Qty": [2]})
    append_to_master(df, master, "Data", rerun_mode="replace_snapshot",
                     snapshot_value=date(2026, 1, 15), verbose=False)
    assert len(read(master)) == 1


def test_empty_frame_leaves_master_untouched(master):
    df = pd.DataFrame({"Order": ["A"], "Qty": [1]})
    append_to_master(df, master, "Data", verbose=False)
    before = os.path.getmtime(master)
    result = append_to_master(pd.DataFrame(), master, "Data", verbose=False)
    assert result is None
    assert os.path.getmtime(master) == before


def test_dedup_without_keys_raises(master):
    with pytest.raises(ValueError):
        append_to_master(pd.DataFrame({"A": [1]}), master, "Data",
                         rerun_mode="dedup", verbose=False)


def test_unknown_mode_raises(master):
    with pytest.raises(ValueError):
        append_to_master(pd.DataFrame({"A": [1]}), master, "Data",
                         rerun_mode="upsert", verbose=False)


def test_keep_snapshots_trims_to_most_recent(master):
    df = pd.DataFrame({"Order": ["A"], "Qty": [1]})
    for d in (date(2026, 1, 13), date(2026, 1, 14), date(2026, 1, 15)):
        append_to_master(df, master, "Data", snapshot_value=d,
                         keep_snapshots=2, verbose=False)
    out = read(master)
    assert len(out) == 2
    assert out["Snapshot_Date"].min() == pd.Timestamp("2026-01-14")


def test_other_sheets_are_preserved(master):
    with pd.ExcelWriter(master) as w:
        pd.DataFrame({"X": [1]}).to_excel(w, sheet_name="Other", index=False)
    append_to_master(pd.DataFrame({"Order": ["A"]}), master, "Data",
                     verbose=False)
    assert set(pd.ExcelFile(master).sheet_names) >= {"Other", "Data"}
