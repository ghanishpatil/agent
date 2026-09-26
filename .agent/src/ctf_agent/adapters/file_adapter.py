from __future__ import annotations

from pathlib import Path

from ..models import Action, ExecutionResult


class FileAdapter:
    """Reads one file per action from within an explicitly allow-listed root directory.

    This is read-only local inspection (e.g. an extracted CTF handout). It never writes, never
    executes, and refuses any path that resolves outside ``allowed_root``.
    """

    def __init__(self, name: str, allowed_root: Path, *, max_bytes: int = 1_048_576) -> None:
        self.name = name
        self._allowed_root = allowed_root.resolve()
        self._max_bytes = max_bytes

    def execute(self, action: Action) -> ExecutionResult:
        if action.tool != self.name:
            raise ValueError(f"FileAdapter '{self.name}' cannot execute tool '{action.tool}'")

        if not self._allowed_root.is_dir():
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                environment_available=False,
                metadata={"reason": "allowed_root does not exist"},
            )

        relative = self._relative_path(action.input_data)
        if relative is None:
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                input_rejected=True,
                metadata={"reason": "input_data must be a relative path string"},
            )

        candidate = (self._allowed_root / relative).resolve()
        if not self._is_within_root(candidate):
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                tool_available=False,
                metadata={"reason": "path escapes allowed_root"},
            )
        if not candidate.exists() or not candidate.is_file():
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                tool_available=True,
                exit_code=1,
                stderr="file not found",
            )

        raw = candidate.read_bytes()[: self._max_bytes]
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1", errors="replace")
        return ExecutionResult(
            action_id=action.action_id,
            tool=action.tool,
            tool_available=True,
            exit_code=0,
            stdout=content,
        )

    def _is_within_root(self, candidate: Path) -> bool:
        try:
            candidate.relative_to(self._allowed_root)
        except ValueError:
            return False
        return True

    @staticmethod
    def _relative_path(input_data: object) -> str | None:
        if isinstance(input_data, str) and input_data.strip():
            return input_data
        if isinstance(input_data, dict):
            path_value = input_data.get("path")
            if isinstance(path_value, str) and path_value.strip():
                return path_value
        return None
