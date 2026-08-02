from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .simulation import GameResult


@dataclass(frozen=True)
class MarketPrice:
    market: str
    selection: str
    line: float | None
    probability: float
    push_probability: float
    conditional_win_probability: float | None
    fair_american: int | None


def fair_american(probability: float) -> int | None:
    """Convert a strictly interior probability to fair American odds."""

    if probability <= 0 or probability >= 1:
        return None
    if probability >= 0.5:
        return round(-100 * probability / (1 - probability))
    return round(100 * (1 - probability) / probability)


def price_markets(
    results: list[GameResult],
    *,
    total_line: float = 8.5,
    home_run_line: float = -1.5,
    home_team_total_line: float = 4.5,
    away_team_total_line: float = 4.5,
    hitter_total_bases_line: float = 1.5,
    pitcher_strikeouts_line: float = 4.5,
) -> list[MarketPrice]:
    """Price multiple market families from one coherent result collection.

    Raw win and push probabilities are reported separately. Fair odds use the
    conditional win probability after pushes are removed from the denominator.
    """

    _validate_results(results)
    first = results[0]
    home_team = first.home_team
    away_team = first.away_team
    prices = [
        _price(
            results,
            "moneyline",
            home_team,
            None,
            lambda result: result.home_runs > result.away_runs,
        ),
        _price(
            results,
            "moneyline",
            away_team,
            None,
            lambda result: result.away_runs > result.home_runs,
        ),
        _price(
            results,
            "total",
            f"over {total_line:g}",
            total_line,
            lambda result: result.total_runs > total_line,
            lambda result: result.total_runs == total_line,
        ),
        _price(
            results,
            "total",
            f"under {total_line:g}",
            total_line,
            lambda result: result.total_runs < total_line,
            lambda result: result.total_runs == total_line,
        ),
        _price(
            results,
            "run_line",
            f"{home_team} {home_run_line:+g}",
            home_run_line,
            lambda result: result.home_margin + home_run_line > 0,
            lambda result: result.home_margin + home_run_line == 0,
        ),
        _price(
            results,
            "run_line",
            f"{away_team} {-home_run_line:+g}",
            -home_run_line,
            lambda result: result.home_margin + home_run_line < 0,
            lambda result: result.home_margin + home_run_line == 0,
        ),
    ]

    prices.extend(
        _team_total_prices(
            results,
            home_team,
            home_team_total_line,
            lambda result: result.home_runs,
        )
    )
    prices.extend(
        _team_total_prices(
            results,
            away_team,
            away_team_total_line,
            lambda result: result.away_runs,
        )
    )

    for player_id in sorted(first.batter_lines):
        player_name = first.player_names[player_id]
        prices.append(
            _price(
                results,
                "hitter_total_bases",
                f"{player_name} over {hitter_total_bases_line:g}",
                hitter_total_bases_line,
                lambda result, key=player_id: (
                    result.batter_lines[key].total_bases > hitter_total_bases_line
                ),
                lambda result, key=player_id: (
                    result.batter_lines[key].total_bases == hitter_total_bases_line
                ),
            )
        )
        prices.append(
            _price(
                results,
                "hitter_home_run",
                f"{player_name} yes",
                0.5,
                lambda result, key=player_id: result.batter_lines[key].home_runs >= 1,
            )
        )

    for player_id in sorted(first.starting_pitcher_ids):
        player_name = first.player_names[player_id]
        prices.append(
            _price(
                results,
                "pitcher_strikeouts",
                f"{player_name} over {pitcher_strikeouts_line:g}",
                pitcher_strikeouts_line,
                lambda result, key=player_id: (
                    result.pitcher_lines[key].strikeouts > pitcher_strikeouts_line
                ),
                lambda result, key=player_id: (
                    result.pitcher_lines[key].strikeouts == pitcher_strikeouts_line
                ),
            )
        )
    return prices


def _team_total_prices(
    results: list[GameResult],
    team: str,
    line: float,
    value: Callable[[GameResult], int],
) -> list[MarketPrice]:
    return [
        _price(
            results,
            "team_total",
            f"{team} over {line:g}",
            line,
            lambda result: value(result) > line,
            lambda result: value(result) == line,
        ),
        _price(
            results,
            "team_total",
            f"{team} under {line:g}",
            line,
            lambda result: value(result) < line,
            lambda result: value(result) == line,
        ),
    ]


def _price(
    results: list[GameResult],
    market: str,
    selection: str,
    line: float | None,
    wins: Callable[[GameResult], bool],
    pushes: Callable[[GameResult], bool] | None = None,
) -> MarketPrice:
    win_count = sum(1 for result in results if wins(result))
    push_count = (
        sum(1 for result in results if pushes(result)) if pushes is not None else 0
    )
    resolved_count = len(results) - push_count
    probability = win_count / len(results)
    push_probability = push_count / len(results)
    conditional = win_count / resolved_count if resolved_count else None
    return MarketPrice(
        market=market,
        selection=selection,
        line=line,
        probability=probability,
        push_probability=push_probability,
        conditional_win_probability=conditional,
        fair_american=(fair_american(conditional) if conditional is not None else None),
    )


def _validate_results(results: list[GameResult]) -> None:
    if not results:
        raise ValueError("results cannot be empty")
    first = results[0]
    if first.away_runs == first.home_runs:
        raise ValueError("moneyline results cannot contain ties")
    expected_batters = set(first.batter_lines)
    expected_pitchers = set(first.pitcher_lines)
    expected_starters = set(first.starting_pitcher_ids)
    for result in results[1:]:
        if (result.away_team, result.home_team) != (
            first.away_team,
            first.home_team,
        ):
            raise ValueError("all results must describe the same matchup")
        if result.away_runs == result.home_runs:
            raise ValueError("moneyline results cannot contain ties")
        if set(result.batter_lines) != expected_batters:
            raise ValueError("batter IDs must be consistent across results")
        if set(result.pitcher_lines) != expected_pitchers:
            raise ValueError("pitcher IDs must be consistent across results")
        if set(result.starting_pitcher_ids) != expected_starters:
            raise ValueError("starting pitcher IDs must be consistent across results")
