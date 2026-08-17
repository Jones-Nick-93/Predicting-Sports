from asof_news_nlp.dashboard import render_dashboard
from asof_news_nlp.experiment import run_experiment


def test_dashboard_renders_leakage_finding(tmp_path) -> None:
    html = render_dashboard(run_experiment(n_events=300), tmp_path / "report.html").read_text(encoding="utf-8")
    assert "The model that knew tomorrow's news" in html
    assert "As-of safe" in html and "Leaky event join" in html
    assert "No real players, teams, events" in html
