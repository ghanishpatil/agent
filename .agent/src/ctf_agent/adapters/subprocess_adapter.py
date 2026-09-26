from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from ..models import Action, ExecutionResult


@dataclass(frozen=True)
class SubprocessCommand:
    """One explicitly allow-listed local command this adapter is permitted to run."""

    executable: str
    fixed_args: tuple[str, ...] = ()


class SubprocessAdapter:
    """Runs one explicitly allow-listed local executable per action.

    ``Action.input_data`` supplies only *arguments*, never the executable path. The executable
    itself is fixed at construction time, so an action can never redirect execution to an arbitrary
    binary. This is intentionally narrow: one adapter instance == one trusted local tool.
    """

    def __init__(self, name: str, command: SubprocessCommand, *, timeout_seconds: float = 10.0) -> None:
        self.name = name
        self._command = command
        self._timeout_seconds = timeout_seconds

    def execute(self, action: Action) -> ExecutionResult:
        if action.tool != self.name:
            raise ValueError(f"SubprocessAdapter '{self.name}' cannot execute tool '{action.tool}'")

        resolved = shutil.which(self._command.executable)
        if resolved is None:
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                tool_available=False,
            )

        extra_args = self._extra_args(action.input_data)
        argv = [resolved, *self._command.fixed_args, *extra_args]
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                tool_available=True,
                timed_out=True,
            )
        except OSError:
            return ExecutionResult(
                action_id=action.action_id,
                tool=action.tool,
                tool_available=False,
            )

        return ExecutionResult(
            action_id=action.action_id,
            tool=action.tool,
            tool_available=True,
            exit_code=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
        )

    @staticmethod
    def _extra_args(input_data: object) -> tuple[str, ...]:
        if input_data is None:
            return ()
        if isinstance(input_data, str):
            return (input_data,)
        if isinstance(input_data, (list, tuple)):
            return tuple(str(item) for item in input_data)
        if isinstance(input_data, dict):
            args_value = input_data.get("args", ())
            return tuple(str(item) for item in args_value)
        raise ValueError(
            "SubprocessAdapter input_data must be None, str, list/tuple of str, "
            "or a dict with an 'args' list"
        )
