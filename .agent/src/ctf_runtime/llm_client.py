"""LLM client contract for the runtime bridge.

HARD SECURITY BOUNDARY: an ``LLMClient`` receives ONLY text (a model id + a prompt) and returns
ONLY text. It is never handed a tool handle, an adapter, a subprocess, a network client, the kernel,
the registry, or any executable capability. The model can therefore only *emit words*; turning those
words into anything executable is the job of the validated proposal pipeline downstream.

This module intentionally has NO dependency on any model SDK. A production deployment supplies a
concrete client (e.g. wrapping an HTTP model API) by implementing ``LLMClient.complete`` or by
wrapping any ``callable(model, prompt) -> str`` in ``CallableLLMClient``. Tests use
``FakeLLMClient`` / ``ScriptedLLMClient`` for full determinism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Protocol, runtime_checkable


@dataclass(frozen=True)
class LLMRequest:
    """Everything the model is given. Text only — no handles, no callables, no state objects."""

    model: str
    prompt: str
    response_format: str = "json"          # advisory: we always parse JSON defensively
    schema_hint: str = ""                  # human-readable schema description embedded in the prompt
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str


@runtime_checkable
class LLMClient(Protocol):
    """The only capability the runtime grants a model: turn a text request into text."""

    def complete(self, request: LLMRequest) -> str: ...


class CallableLLMClient:
    """Adapt any ``callable(model, prompt) -> str`` into an ``LLMClient``.

    This is the intended production seam: a deployment passes a function that calls its model API and
    returns the raw text. The function still receives only strings.
    """

    def __init__(self, fn: Callable[[str, str], str]) -> None:
        self._fn = fn

    def complete(self, request: LLMRequest) -> str:
        return self._fn(request.model, request.prompt)


class ScriptedLLMClient:
    """Deterministic test client driven by a ``callable(LLMRequest) -> str`` script."""

    def __init__(self, script: Callable[[LLMRequest], str]) -> None:
        self._script = script
        self.calls: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> str:
        self.calls.append(request)
        return self._script(request)


# Backwards-friendly alias used in tests/docs.
FakeLLMClient = ScriptedLLMClient
