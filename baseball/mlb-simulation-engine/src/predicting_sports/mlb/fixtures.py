from __future__ import annotations

from .simulation import BatterProfile, GameConfig, PitcherProfile, Team


def synthetic_game() -> GameConfig:
    """Return a deterministic, fictional MLB-style matchup."""

    away_lineup = (
        _batter("away-b1", "Away Leadoff", 0.18, 0.10, 0.24, 0.07, 0.01, 0.04),
        _batter("away-b2", "Away Power", 0.26, 0.11, 0.19, 0.08, 0.00, 0.08),
        _batter("away-b3", "Away Contact", 0.12, 0.08, 0.29, 0.06, 0.01, 0.03),
        _batter("away-b4", "Away Cleanup", 0.23, 0.09, 0.21, 0.09, 0.00, 0.07),
        _batter("away-b5", "Away Five", 0.20, 0.07, 0.23, 0.06, 0.01, 0.05),
        _batter("away-b6", "Away Six", 0.24, 0.06, 0.20, 0.06, 0.01, 0.04),
        _batter("away-b7", "Away Seven", 0.28, 0.07, 0.18, 0.05, 0.01, 0.04),
        _batter("away-b8", "Away Eight", 0.21, 0.06, 0.22, 0.05, 0.01, 0.03),
        _batter("away-b9", "Away Nine", 0.25, 0.05, 0.18, 0.04, 0.01, 0.03),
    )
    home_lineup = (
        _batter("home-b1", "Home Leadoff", 0.17, 0.11, 0.25, 0.07, 0.01, 0.04),
        _batter("home-b2", "Home Power", 0.25, 0.12, 0.20, 0.08, 0.00, 0.09),
        _batter("home-b3", "Home Star", 0.19, 0.10, 0.24, 0.08, 0.01, 0.07),
        _batter("home-b4", "Home Cleanup", 0.24, 0.09, 0.20, 0.09, 0.00, 0.08),
        _batter("home-b5", "Home Five", 0.22, 0.08, 0.22, 0.07, 0.01, 0.05),
        _batter("home-b6", "Home Six", 0.23, 0.07, 0.21, 0.06, 0.01, 0.04),
        _batter("home-b7", "Home Seven", 0.27, 0.07, 0.18, 0.05, 0.01, 0.04),
        _batter("home-b8", "Home Eight", 0.20, 0.06, 0.23, 0.05, 0.01, 0.03),
        _batter("home-b9", "Home Nine", 0.24, 0.05, 0.19, 0.04, 0.01, 0.03),
    )
    return GameConfig(
        away=Team(
            code="AWY",
            lineup=away_lineup,
            starter=PitcherProfile("away-sp", "Away Starter", 1.06, 0.95, 0.98, 24),
            bullpen=PitcherProfile("away-bp", "Away Bullpen", 0.96, 1.04, 1.02, 99),
        ),
        home=Team(
            code="HOM",
            lineup=home_lineup,
            starter=PitcherProfile("home-sp", "Home Starter", 0.98, 1.02, 1.03, 24),
            bullpen=PitcherProfile("home-bp", "Home Bullpen", 1.02, 1.00, 1.00, 99),
        ),
    )


def _batter(
    player_id: str,
    name: str,
    strikeout_rate: float,
    walk_rate: float,
    single_rate: float,
    double_rate: float,
    triple_rate: float,
    home_run_rate: float,
) -> BatterProfile:
    return BatterProfile(
        player_id=player_id,
        name=name,
        strikeout_rate=strikeout_rate,
        walk_rate=walk_rate,
        single_rate_on_contact=single_rate,
        double_rate_on_contact=double_rate,
        triple_rate_on_contact=triple_rate,
        home_run_rate_on_contact=home_run_rate,
    )
