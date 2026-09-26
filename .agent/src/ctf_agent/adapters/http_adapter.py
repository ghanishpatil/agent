from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from http.client import HTTPResponse
from urllib.parse import urlsplit

from ..models import Action, ExecutionResult


@dataclass(frozen=True)
class HttpPolicy:
    """Explicit allow-list for the ``HttpAdapter``."""

    allowed_host_prefixes: tuple[str, ...]
    timeout_seconds: float = 5.0
    max_body_bytes: int = 65536


class HttpAdapter:
    """Performs one HTTP request per action against an explicitly allow-listed target.

    Requests to any host not matching ``policy.allowed_host_prefixes`` are refused before any
    network I/O happens; this keeps execution inside a configured, authorized environment rather
    than an unrestricted general-purpose fetcher.
    """

    def __init__(self, name: str, policy: HttpPolicy) -> None:
        self.name = name
        self._policy = policy

    def execute(self, action: Action) -> ExecutionResult:
        if action.tool != self.name:
            raise ValueError(f"HttpAdapter '{self.name}' cannot execute tool '{action.tool}'")

        target = action.target
        if not self._is_allowed(target):
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                network_state="unreachable",
                metadata={"reason": "target not in allowed_host_prefixes"},
            )

        method = str(action.relevant_parameters.get("method", "GET")).upper()
        body = self._encoded_body(action.input_data)
        headers = dict(action.relevant_parameters.get("headers", {}))
        request = urllib.request.Request(target, data=body, method=method, headers=headers)

        try:
            with urllib.request.urlopen(request, timeout=self._policy.timeout_seconds) as response:
                return self._from_response(action, response)
        except urllib.error.HTTPError as error:
            raw = error.read(self._policy.max_body_bytes)
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                http_status=error.code,
                response_headers=dict(error.headers or {}),
                response_body=self._decode(raw),
            )
        except TimeoutError:
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                timed_out=True,
            )
        except urllib.error.URLError:
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                network_state="unreachable",
            )

    def _is_allowed(self, target: str) -> bool:
        return any(target.startswith(prefix) for prefix in self._policy.allowed_host_prefixes)

    def _from_response(self, action: Action, response: HTTPResponse) -> ExecutionResult:
        raw = response.read(self._policy.max_body_bytes)
        return ExecutionResult(
            action_id=action.action_id,
            tool=action.tool,
            http_status=response.status,
            response_headers=dict(response.headers.items()),
            response_body=self._decode(raw),
        )

    @staticmethod
    def _decode(raw: bytes) -> str:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1", errors="replace")

    @staticmethod
    def _encoded_body(input_data: object) -> bytes | None:
        if input_data is None:
            return None
        if isinstance(input_data, bytes):
            return input_data
        if isinstance(input_data, str):
            return input_data.encode("utf-8")
        if isinstance(input_data, dict):
            import json as _json

            return _json.dumps(input_data).encode("utf-8")
        raise ValueError("HttpAdapter input_data must be None, bytes, str, or a JSON-able dict")


def host_prefix_from_url(url: str) -> str:
    """Helper to derive an allow-list prefix (scheme+host) from a full URL."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"
