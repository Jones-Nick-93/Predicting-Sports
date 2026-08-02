"""
Push-aware Asian handicap (soccer spread) cover-probability logic.

This is pure market-mechanics math, independent of any projection method. Given
any score-probability grid, it handles push cases using standard settlement rules.

Convention: `sh` (spread, home perspective) is negative when the home team is
giving goals (favorite) and positive when the home team is getting goals
(underdog). sh=0 is pick'em, equivalent to draw-no-bet.
"""

import numpy as np


def cover_prob(grid: np.ndarray, sh: float, max_goals: int | None = None) -> float:
    """
    Probability the HOME team covers a given Asian handicap line.

    grid: 2D array where grid[h, a] = P(home scores h, away scores a)
    sh:   home-team spread, e.g. -0.75, -0.5, 0 (PK), +0.5, +1.25

    Rules:
      - Quarter lines (..., -0.75, -0.25, +0.25, +0.75, ...): split 50/50
        into the two adjacent half-integer lines (this is how the market
        itself defines a quarter-line wager — half the stake at each
        neighboring line).
      - Half lines (..., -1.5, -0.5, +0.5, +1.5, ...): no push is possible.
      - Whole-number lines (..., -1, 0, +1, ...): the exact margin equal to
        the line is a PUSH (half the grid's probability mass returns as a
        push rather than counting as a win or loss). sh=0 (PK) pushes on a
        draw, which is the draw-no-bet behavior.
    """
    if max_goals is None:
        max_goals = grid.shape[0] - 1

    # Quarter line: recursively split into the two adjacent half lines.
    if abs(sh % 0.5) == 0.25:
        return 0.5 * cover_prob(grid, sh - 0.25, max_goals) + \
               0.5 * cover_prob(grid, sh + 0.25, max_goals)

    total = 0.0
    is_whole_line = (sh == int(sh))

    for h in range(min(max_goals + 1, grid.shape[0])):
        for a in range(min(max_goals + 1, grid.shape[1])):
            p = grid[h, a]
            margin = h - a
            if is_whole_line:
                if margin > -sh:
                    total += p                 # full win
                elif margin == -sh:
                    total += 0.5 * p           # push: half stake returned
                # else: full loss, add nothing
            else:
                if margin > -sh:
                    total += p                 # half lines: no push possible
    return total


def spread_labels(sh: float) -> tuple[str, str]:
    """Human-readable labels for the home and away side of a given line."""
    home_label = "PK" if sh == 0 else (f"+{sh}" if sh > 0 else str(sh))
    away_sh = -sh
    away_label = "PK" if away_sh == 0 else (f"+{away_sh}" if away_sh > 0 else str(away_sh))
    return home_label, away_label


if __name__ == "__main__":
    # Tiny illustrative sanity check with a fabricated probability grid.
    rng = np.random.default_rng(0)
    toy_grid = rng.dirichlet(np.ones(36)).reshape(6, 6)  # fabricated, sums to 1

    for line in [-1.25, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5]:
        p_home = cover_prob(toy_grid, line)
        h_label, a_label = spread_labels(line)
        print(f"home {h_label:>6} / away {a_label:>6}: "
              f"P(home covers) = {p_home:.3f}, P(away covers) = {1 - p_home:.3f}")
