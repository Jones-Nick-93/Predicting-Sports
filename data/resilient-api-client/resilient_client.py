"""A provider-neutral HTTP client for unattended API jobs.

The client implements generic bearer-token refresh, bounded retries, explicit
conflict handling, and guarded deletes. Resource paths and authentication are
supplied by the caller; no vendor endpoints, payload fields, or credentials are
embedded here.
"""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any
from urllib.parse import quote, urlsplit

import requests

logger = logging.getLogger(__name__)

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
CONFLICT_STATUS = 409
UNAUTHORIZED_STATUS = 401


class AuthError(RuntimeError):
    """Authentication failed without disclosing credential material."""


class ResilientApiClient:
    """Small resilient transport for bearer-authenticated JSON APIs."""

    def __init__(
        self,
        *,
        base_url: str,
        token_provider: Callable[[], str],
        timeout: float = 30.0,
        max_retries: int = 4,
        backoff_base: float = 1.5,
        dry_run: bool = True,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[float, float], float] = random.uniform,
    ) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute HTTP(S) URL")
        if parsed.username or parsed.password:
            raise ValueError("base_url must not contain credentials")
        if not callable(token_provider):
            raise TypeError("token_provider must be callable")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if backoff_base < 1:
            raise ValueError("backoff_base must be at least 1")

        self.base_url = base_url.rstrip("/")
        self._token_provider = token_provider
        self.timeout = float(timeout)
        self.max_retries = int(max_retries)
        self.backoff_base = float(backoff_base)
        self.dry_run = bool(dry_run)
        self.session = session or requests.Session()
        self._sleep_fn = sleep
        self._jitter_fn = jitter
        self._token: str | None = None

    def _refresh_token(self) -> None:
        try:
            token = self._token_provider()
        except Exception as exc:
            raise AuthError(f"token provider failed ({type(exc).__name__})") from None
        if not isinstance(token, str) or not token.strip():
            raise AuthError("token provider returned no usable token")
        self._token = token.strip()
        logger.info("Bearer token refreshed")

    def _authorization_headers(self) -> dict[str, str]:
        if self._token is None:
            self._refresh_token()
        return {"Authorization": f"Bearer {self._token}"}

    @staticmethod
    def _validate_path(path: str) -> None:
        if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
            raise ValueError("path must be a relative API path beginning with one slash")
        if urlsplit(path).scheme or urlsplit(path).netloc:
            raise ValueError("absolute request URLs are not allowed")

    def _wait(self, attempt: int, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                self._sleep_fn(min(float(retry_after), 60.0))
                return
            except (TypeError, ValueError):
                pass
        delay = (self.backoff_base**attempt) + self._jitter_fn(0.0, 0.5)
        self._sleep_fn(min(delay, 60.0))

    def request(
        self,
        method: str,
        path: str,
        *,
        allow_conflict: bool = False,
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> tuple[requests.Response, bool]:
        """Return ``(response, conflicted)`` after bounded retry handling."""
        self._validate_path(path)
        url = f"{self.base_url}{path}"
        reauthenticated = False

        for attempt in range(self.max_retries + 1):
            request_headers = dict(headers or {})
            request_headers.update(self._authorization_headers())
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=request_headers,
                    timeout=self.timeout,
                    **kwargs,
                )
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise
                logger.warning(
                    "%s %s failed (%s); retry %d of %d",
                    method,
                    path,
                    type(exc).__name__,
                    attempt + 1,
                    self.max_retries,
                )
                self._wait(attempt)
                continue

            if response.status_code == UNAUTHORIZED_STATUS and not reauthenticated:
                logger.info("Token rejected; refreshing once")
                self._token = None
                reauthenticated = True
                continue

            if response.status_code == CONFLICT_STATUS and allow_conflict:
                return response, True

            if response.status_code in RETRY_STATUSES and attempt < self.max_retries:
                logger.warning(
                    "%s %s returned %d; retry %d of %d",
                    method,
                    path,
                    response.status_code,
                    attempt + 1,
                    self.max_retries,
                )
                self._wait(attempt, response.headers.get("Retry-After"))
                continue

            response.raise_for_status()
            return response, False

        raise RuntimeError(f"{method} {path} exhausted the retry budget")

    def list_resources(self, path: str, *, result_field: str = "data", **params: Any) -> list[Any]:
        """Fetch a JSON collection from a caller-supplied relative path."""
        response, _ = self.request("GET", path, params=params)
        result = response.json().get(result_field, [])
        if not isinstance(result, list):
            raise ValueError(f"response field {result_field!r} must contain a list")
        return result

    def create_resource(
        self,
        path: str,
        payload: Mapping[str, Any],
        *,
        allow_conflict: bool = True,
    ) -> tuple[dict[str, Any] | None, bool]:
        """Create a resource, or report a conflict as a distinct outcome."""
        if self.dry_run:
            logger.info("[dry run] would POST one resource to %s", path)
            return None, False
        response, conflicted = self.request(
            "POST",
            path,
            json=dict(payload),
            allow_conflict=allow_conflict,
        )
        if conflicted:
            return None, True
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError("create response must contain a JSON object")
        return result, False

    def delete_resource(self, collection_path: str, resource_id: str) -> bool:
        """Delete one resource unless dry-run mode is active."""
        self._validate_path(collection_path)
        if self.dry_run:
            logger.info("[dry run] would DELETE one resource from %s", collection_path)
            return False
        encoded_id = quote(str(resource_id), safe="")
        self.request("DELETE", f"{collection_path.rstrip('/')}/{encoded_id}")
        return True

    def delete_many(
        self,
        collection_path: str,
        resource_ids: Iterable[str],
        *,
        confirm: bool = False,
    ) -> tuple[int, int]:
        """Delete many resources only when dry-run is off and confirmation is explicit."""
        ids = list(resource_ids)
        if self.dry_run or not confirm:
            logger.warning(
                "Refusing bulk delete of %d resources: dry_run=%s confirm=%s",
                len(ids),
                self.dry_run,
                confirm,
            )
            return 0, len(ids)

        deleted = 0
        failed = 0
        for resource_id in ids:
            try:
                self.delete_resource(collection_path, resource_id)
                deleted += 1
            except requests.RequestException as exc:
                logger.error("Resource deletion failed (%s)", type(exc).__name__)
                failed += 1
        return deleted, failed
