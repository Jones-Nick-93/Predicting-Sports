from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from uncertainty_gates.experiment import run_experiment


def main() -> None:
    report = run_experiment(n_samples=800, seed=71, ngboost_estimators=80)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
