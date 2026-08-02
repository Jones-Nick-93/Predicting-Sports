"""Public-safe, synthetic sports-data pipeline primitives."""

from .api import PipelineApi
from .retry import PermanentSourceError, RetryPolicy, TransientSourceError
from .service import PipelineService, RunResult
from .store import PipelineStore

__all__ = [
    "PermanentSourceError",
    "PipelineApi",
    "PipelineService",
    "PipelineStore",
    "RetryPolicy",
    "RunResult",
    "TransientSourceError",
]
