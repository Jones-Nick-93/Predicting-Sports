from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from asof_news_nlp.dashboard import render_dashboard
from asof_news_nlp.experiment import run_experiment
if __name__ == "__main__":
    report = run_experiment(); print(json.dumps(report, indent=2, sort_keys=True)); print(f"dashboard={render_dashboard(report, ROOT / 'artifacts' / 'asof_nlp_dashboard.html')}")
