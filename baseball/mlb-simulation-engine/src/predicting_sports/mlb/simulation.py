from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BatterProfile:
    player_id: str
    name: str
    strikeout_rate: float
    walk_rate: float
    single_rate_on_contact: float
    double_rate_on_contact: float
    triple_rate_on_contact: float
    home_run_rate_on_contact: float

    def __post_init__(self) -> None:
        if not self.player_id or not self.name:
            raise ValueError("batter player_id and name must be nonempty")
        rates = (
            self.strikeout_rate,
            self.walk_rate,
            self.single_rate_on_contact,
            self.double_rate_on_contact,
            self.triple_rate_on_contact,
            self.home_run_rate_on_contact,
        )
        if any(rate < 0 or rate > 1 for rate in rates):
            raise ValueError("batter rates must be between zero and one")
        contact_total = sum(rates[2:])
        if contact_total > 1:
            raise ValueError("contact outcome rates cannot sum above one")


@dataclass(frozen=True)
class PitcherProfile:
    player_id: str
    name: str
    strikeout_multiplier: float = 1.0
    walk_multiplier: float = 1.0
    contact_quality_multiplier: float = 1.0
    expected_batters_faced: int = 24

    def __post_init__(self) -> None:
        if not self.player_id or not self.name:
            raise ValueError("pitcher player_id and name must be nonempty")
        multipliers = (
            self.strikeout_multiplier,
            self.walk_multiplier,
            self.contact_quality_multiplier,
        )
        if any(value <= 0 for value in multipliers):
            raise ValueError("pitcher multipliers must be positive")
        if self.expected_batters_faced <= 0:
            raise ValueError("expected_batters_faced must be positive")


@dataclass(frozen=True)
class Team:
    code: str
    lineup: tuple[BatterProfile, ...]
    starter: PitcherProfile
    bullpen: PitcherProfile

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("team code must be nonempty")
        if len(self.lineup) != 9:
            raise ValueError("an MLB-style lineup must contain exactly nine batters")
        batter_ids = [batter.player_id for batter in self.lineup]
        if len(set(batter_ids)) != len(batter_ids):
            raise ValueError("batter player IDs must be unique within a lineup")
        if self.starter.player_id == self.bullpen.player_id:
            raise ValueError("starter and bullpen IDs must be distinct")


@dataclass(frozen=True)
class GameConfig:
    away: Team
    home: Team
    innings: int = 9
    max_extra_innings: int = 30

    def __post_init__(self) -> None:
        if self.away.code == self.home.code:
            raise ValueError("away and home team codes must be distinct")
        if self.innings <= 0:
            raise ValueError("innings must be positive")
        if self.max_extra_innings <= 0:
            raise ValueError("max_extra_innings must be positive")
        player_ids = [
            *(batter.player_id for batter in self.away.lineup),
            *(batter.player_id for batter in self.home.lineup),
            self.away.starter.player_id,
            self.away.bullpen.player_id,
            self.home.starter.player_id,
            self.home.bullpen.player_id,
        ]
        if len(set(player_ids)) != len(player_ids):
            raise ValueError("player IDs must be unique across the game")


@dataclass
class BatterLine:
    plate_appearances: int = 0
    total_bases: int = 0
    home_runs: int = 0
    hits: int = 0


@dataclass
class PitcherLine:
    strikeouts: int = 0
    batters_faced: int = 0


@dataclass
class GameResult:
    away_team: str
    home_team: str
    away_runs: int
    home_runs: int
    innings_played: int
    batter_lines: dict[str, BatterLine] = field(default_factory=dict)
    pitcher_lines: dict[str, PitcherLine] = field(default_factory=dict)
    player_names: dict[str, str] = field(default_factory=dict)
    starting_pitcher_ids: tuple[str, str] = ()
    event_ledger: list[dict[str, object]] = field(default_factory=list)

    @property
    def total_runs(self) -> int:
        return self.away_runs + self.home_runs

    @property
    def home_margin(self) -> int:
        return self.home_runs - self.away_runs


@dataclass
class _OffenseState:
    runs: int
    batter_index: int
    batter_lines: dict[str, BatterLine]
    pitcher_lines: dict[str, PitcherLine]


def simulate_many(config: GameConfig, n: int, seed: int = 7) -> list[GameResult]:
    if n <= 0:
        raise ValueError("n must be positive")
    rng = random.Random(seed)
    return [simulate_game(config, rng) for _ in range(n)]


def simulate_game(config: GameConfig, rng: random.Random) -> GameResult:
    away_state = _new_offense_state(config.away, config.home)
    home_state = _new_offense_state(config.home, config.away)
    event_ledger: list[dict[str, object]] = []

    for inning in range(1, config.innings + 1):
        _simulate_half_inning(
            config.away,
            config.home,
            inning,
            "top",
            away_state,
            event_ledger,
            rng,
        )
        if inning < config.innings or home_state.runs <= away_state.runs:
            _simulate_half_inning(
                config.home,
                config.away,
                inning,
                "bottom",
                home_state,
                event_ledger,
                rng,
                walkoff_target=away_state.runs if inning == config.innings else None,
            )

    innings_played = config.innings
    while away_state.runs == home_state.runs:
        innings_played += 1
        if innings_played > config.innings + config.max_extra_innings:
            raise RuntimeError("game remained tied beyond max_extra_innings")
        _simulate_half_inning(
            config.away,
            config.home,
            innings_played,
            "top",
            away_state,
            event_ledger,
            rng,
        )
        _simulate_half_inning(
            config.home,
            config.away,
            innings_played,
            "bottom",
            home_state,
            event_ledger,
            rng,
            walkoff_target=away_state.runs,
        )

    player_names = {
        player.player_id: player.name
        for team in (config.away, config.home)
        for player in (*team.lineup, team.starter, team.bullpen)
    }
    return GameResult(
        away_team=config.away.code,
        home_team=config.home.code,
        away_runs=away_state.runs,
        home_runs=home_state.runs,
        innings_played=innings_played,
        batter_lines={**away_state.batter_lines, **home_state.batter_lines},
        pitcher_lines={**away_state.pitcher_lines, **home_state.pitcher_lines},
        player_names=player_names,
        starting_pitcher_ids=(
            config.away.starter.player_id,
            config.home.starter.player_id,
        ),
        event_ledger=event_ledger,
    )


def _new_offense_state(batting_team: Team, pitching_team: Team) -> _OffenseState:
    return _OffenseState(
        runs=0,
        batter_index=0,
        batter_lines={batter.player_id: BatterLine() for batter in batting_team.lineup},
        pitcher_lines={
            pitching_team.starter.player_id: PitcherLine(),
            pitching_team.bullpen.player_id: PitcherLine(),
        },
    )


def _simulate_half_inning(
    batting_team: Team,
    pitching_team: Team,
    inning: int,
    half: str,
    state: _OffenseState,
    event_ledger: list[dict[str, object]],
    rng: random.Random,
    walkoff_target: int | None = None,
) -> None:
    outs = 0
    bases = [False, False, False]
    starter_line = state.pitcher_lines[pitching_team.starter.player_id]

    while outs < 3:
        pitcher = (
            pitching_team.starter
            if starter_line.batters_faced < pitching_team.starter.expected_batters_faced
            else pitching_team.bullpen
        )
        pitcher_line = state.pitcher_lines[pitcher.player_id]
        batter = batting_team.lineup[state.batter_index % len(batting_team.lineup)]
        state.batter_index += 1
        outcome, bases_taken = _sample_plate_appearance(batter, pitcher, rng)

        batter_line = state.batter_lines[batter.player_id]
        batter_line.plate_appearances += 1
        pitcher_line.batters_faced += 1
        outs_before = outs
        bases_before = tuple(bases)
        runs_before = state.runs

        if outcome == "strikeout":
            outs += 1
            pitcher_line.strikeouts += 1
        elif outcome == "walk":
            scored, bases = _advance_walk(bases)
            state.runs += scored
        elif outcome == "out":
            outs += 1
        else:
            batter_line.hits += 1
            batter_line.total_bases += bases_taken
            batter_line.home_runs += int(outcome == "home_run")
            scored, bases = _advance_hit(bases, bases_taken)
            state.runs += scored

        event_ledger.append(
            {
                "sequence": len(event_ledger) + 1,
                "team": batting_team.code,
                "inning": inning,
                "half": half,
                "batter_id": batter.player_id,
                "pitcher_id": pitcher.player_id,
                "outcome": outcome,
                "outs_before": outs_before,
                "outs_after": outs,
                "bases_before": bases_before,
                "bases_after": tuple(bases),
                "runs_scored": state.runs - runs_before,
                "team_runs_after_play": state.runs,
            }
        )
        if walkoff_target is not None and state.runs > walkoff_target:
            break


def _sample_plate_appearance(
    batter: BatterProfile,
    pitcher: PitcherProfile,
    rng: random.Random,
) -> tuple[str, int]:
    strikeout_prob = _clip(
        batter.strikeout_rate * pitcher.strikeout_multiplier, 0.05, 0.45
    )
    walk_prob = _clip(batter.walk_rate * pitcher.walk_multiplier, 0.03, 0.20)
    roll = rng.random()
    if roll < strikeout_prob:
        return "strikeout", 0
    if roll < strikeout_prob + walk_prob:
        return "walk", 0

    hit_rates = [
        batter.single_rate_on_contact * pitcher.contact_quality_multiplier,
        batter.double_rate_on_contact * pitcher.contact_quality_multiplier,
        batter.triple_rate_on_contact * pitcher.contact_quality_multiplier,
        batter.home_run_rate_on_contact * pitcher.contact_quality_multiplier,
    ]
    total_hit_rate = sum(hit_rates)
    if total_hit_rate > 0.95:
        scale = 0.95 / total_hit_rate
        hit_rates = [rate * scale for rate in hit_rates]

    contact_roll = rng.random()
    cumulative = 0.0
    for outcome, bases_taken, rate in zip(
        ("single", "double", "triple", "home_run"),
        (1, 2, 3, 4),
        hit_rates,
        strict=True,
    ):
        cumulative += rate
        if contact_roll < cumulative:
            return outcome, bases_taken
    return "out", 0


def _advance_walk(bases: list[bool]) -> tuple[int, list[bool]]:
    scored = int(all(bases))
    if bases[0] and bases[1]:
        bases[2] = True
    if bases[0]:
        bases[1] = True
    bases[0] = True
    return scored, bases


def _advance_hit(bases: list[bool], total_bases: int) -> tuple[int, list[bool]]:
    if total_bases == 4:
        return sum(bases) + 1, [False, False, False]

    scored = 0
    new_bases = [False, False, False]
    for base_index, occupied in enumerate(bases):
        if not occupied:
            continue
        destination = base_index + total_bases
        if destination >= 3:
            scored += 1
        else:
            new_bases[destination] = True
    new_bases[total_bases - 1] = True
    return scored, new_bases


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
