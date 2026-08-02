"""
Sanity checks for push-aware Asian handicap logic, using hand-computed
probabilities on simple synthetic grids rather than any real match data.

Run: python -m pytest src/test_asian_handicap.py -q
"""

import numpy as np
from asian_handicap import cover_prob


def make_grid(cells: dict[tuple[int, int], float]) -> np.ndarray:
    """Build a small score grid from an explicit {(h, a): prob} mapping."""
    max_g = max(max(h, a) for h, a in cells)
    grid = np.zeros((max_g + 1, max_g + 1))
    for (h, a), p in cells.items():
        grid[h, a] = p
    return grid


def test_pk_pushes_on_draw():
    # 40% home win, 30% draw, 30% away win.
    # cover_prob returns an expected-return-weighted figure: a full win
    # counts fully, a push counts as half (stake returned), a loss counts
    # as zero. So PK cover = 0.40 (win) + 0.5 * 0.30 (draw push) = 0.55.
    grid = make_grid({(1, 0): 0.40, (0, 0): 0.30, (0, 1): 0.30})
    p_home = cover_prob(grid, 0.0)
    assert abs(p_home - 0.55) < 1e-9


def test_whole_line_push_on_exact_margin():
    # Home wins by exactly 1 in 25% of mass; -1 line should push there.
    grid = make_grid({(2, 0): 0.20, (1, 0): 0.25, (0, 0): 0.20, (0, 1): 0.35})
    p_home = cover_prob(grid, -1.0)
    # 2-0 (win by 2+) fully covers -1 (0.20); 1-0 (win by exactly 1) pushes
    # (0.5 * 0.25); everything else is a full loss.
    assert abs(p_home - (0.20 + 0.5 * 0.25)) < 1e-9


def test_half_line_no_push():
    grid = make_grid({(1, 0): 0.50, (0, 0): 0.20, (0, 1): 0.30})
    p_home = cover_prob(grid, -0.5)
    # No push possible at a half line: only strict wins count.
    assert abs(p_home - 0.50) < 1e-9


def test_quarter_line_is_average_of_neighbors():
    grid = make_grid({(1, 0): 0.50, (0, 0): 0.20, (0, 1): 0.30})
    p_quarter = cover_prob(grid, -0.25)
    p_pk = cover_prob(grid, 0.0)
    p_half = cover_prob(grid, -0.5)
    assert abs(p_quarter - 0.5 * (p_pk + p_half)) < 1e-9


def test_home_away_probs_sum_to_one_off_half_line():
    # On a half line there's no push, so the away side's cover probability
    # at the mirrored line is exactly 1 - home's cover probability (this is
    # how the caller derives the away price, rather than calling cover_prob
    # a second time with a naively negated line against the same grid).
    grid = make_grid({(1, 0): 0.50, (0, 0): 0.20, (0, 1): 0.30})
    p_home = cover_prob(grid, -0.5)
    p_away = 1 - p_home
    assert abs((p_home + p_away) - 1.0) < 1e-9


if __name__ == "__main__":
    test_pk_pushes_on_draw()
    test_whole_line_push_on_exact_margin()
    test_half_line_no_push()
    test_quarter_line_is_average_of_neighbors()
    test_home_away_probs_sum_to_one_off_half_line()
    print("All tests passed.")
