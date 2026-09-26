from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import Action, ExecutionResult


@runtime_checkable
class ToolAdapter(Protocol):
    """Narrow trusted-execution boundary.

    An adapter's only job is: take an ``Action``, run exactly the one tool it wraps, and return an
    honest ``ExecutionResult``. It must never invent success, never decide a flag is verified, and
    never touch kernel/hypothesis/evidence state directly.
    """

    name: str

    def execute(self, action: Action) -> ExecutionResult: ...


class UnknownToolError(ValueError):
    """Raised when an action names a tool that has no registered trusted adapter."""


class AdapterRegistry:
    """Explicit allow-list of tools this run is permitted to execute.

    Nothing is executed by name-guessing or dynamic import. A tool must be registered before any
    action referencing it can run.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, ToolAdapter] = {}

    def register(self, adapter: ToolAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def is_registered(self, tool: str) -> bool:
        return tool in self._adapters

    def available_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))

    def execute(self, action: Action) -> ExecutionResult:
        adapter = self._adapters.get(action.tool)
        if adapter is None:
            raise UnknownToolError(
                f"tool '{action.tool}' has no registered trusted adapter; "
                f"available: {self.available_tools()}"
            )
        result = adapter.execute(action)
        if result.action_id != action.action_id or result.tool != action.tool:
            raise ValueError(
                "adapter returned an ExecutionResult that does not match the requested action"
            )
        return result
