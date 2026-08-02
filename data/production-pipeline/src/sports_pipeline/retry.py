from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable


class TransientSourceError(RuntimeError):
    """A source failure that may succeed within a bounded retry budget."""


class PermanentSourceError(RuntimeError):
    """A source failure that requires configuration or operator action."""


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25
    jitter_seconds: float = 0.05

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if self.base_delay_seconds < 0 or self.jitter_seconds < 0:
            raise ValueError("retry delays cannot be negative")


def fetch_with_retry(
    fetcher: Callable[[], bytes],
    policy: RetryPolicy,
    *,
    sleep: Callable[[float], None] = time.sleep,
    random_fraction: Callable[[], float] = random.random,
) -> tuple[bytes, int]:
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fetcher(), attempt
        except PermanentSourceError:
            raise
        except TransientSourceError:
            if attempt == policy.max_attempts:
                raise
            delay = policy.base_delay_seconds * (2 ** (attempt - 1))
            delay += policy.jitter_seconds * random_fraction()
            sleep(delay)
    raise AssertionError("retry loop exhausted unexpectedly")
