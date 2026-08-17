from __future__ import annotations

from hypothesis import strategies as st


@st.composite
def probability_simplexes(
    draw: st.DrawFn, *, min_size: int = 2, max_size: int = 12
) -> tuple[float, ...]:
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    weights = draw(
        st.lists(
            st.floats(
                min_value=0.01,
                max_value=100.0,
                allow_nan=False,
                allow_infinity=False,
            ),
            min_size=size,
            max_size=size,
        )
    )
    total = sum(weights)
    return tuple(value / total for value in weights)


@st.composite
def overround_markets(draw: st.DrawFn) -> tuple[tuple[float, ...], float, tuple[float, ...]]:
    truth = draw(probability_simplexes())
    maximum_margin = min(0.20, (0.999999 / max(truth)) - 1.0)
    margin = draw(
        st.floats(
            min_value=0.0,
            max_value=max(0.0, maximum_margin),
            allow_nan=False,
            allow_infinity=False,
        )
    )
    implied = tuple(value * (1.0 + margin) for value in truth)
    return truth, margin, implied

