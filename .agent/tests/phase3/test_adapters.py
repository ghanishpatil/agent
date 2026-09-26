from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ctf_agent.adapters import AdapterRegistry, FileAdapter, SubprocessAdapter, UnknownToolError
from ctf_agent.adapters.subprocess_adapter import SubprocessCommand
from ctf_agent.models import Action, EnvironmentState, RelevantState


STATE = RelevantState(EnvironmentState("env-1", ()), "guest", "s1", "c1")


def action(tool: str, target: str = "target", input_data: object = None) -> Action:
    return Action(
        action_id="a1",
        objective="probe",
        tool=tool,
        target=target,
        input_data=input_data,
        relevant_parameters={},
        prerequisites=(),
        state_before=STATE,
    )


# --- SubprocessAdapter -----------------------------------------------------


def test_subprocess_adapter_successful_execution_captures_stdout() -> None:
    adapter = SubprocessAdapter("py", SubprocessCommand(sys.executable, ("-c",)))
    result = adapter.execute(action("py", input_data="print('hello')"))
    assert result.tool_available is True
    assert result.exit_code == 0
    assert "hello" in result.stdout


def test_subprocess_adapter_nonzero_exit_is_captured() -> None:
    adapter = SubprocessAdapter("py", SubprocessCommand(sys.executable, ("-c",)))
    result = adapter.execute(action("py", input_data="import sys; sys.exit(3)"))
    assert result.exit_code == 3
    assert result.tool_available is True


def test_subprocess_adapter_timeout_is_captured() -> None:
    adapter = SubprocessAdapter(
        "py", SubprocessCommand(sys.executable, ("-c",)), timeout_seconds=0.2
    )
    result = adapter.execute(action("py", input_data="import time; time.sleep(5)"))
    assert result.timed_out is True


def test_subprocess_adapter_missing_tool_is_captured() -> None:
    adapter = SubprocessAdapter(
        "ghost", SubprocessCommand("definitely-not-a-real-executable-xyz")
    )
    result = adapter.execute(action("ghost"))
    assert result.tool_available is False


def test_subprocess_adapter_rejects_mismatched_tool_name() -> None:
    adapter = SubprocessAdapter("py", SubprocessCommand(sys.executable, ("-c",)))
    with pytest.raises(ValueError, match="cannot execute tool"):
        adapter.execute(action("other-tool"))


def test_subprocess_adapter_malformed_input_raises() -> None:
    adapter = SubprocessAdapter("py", SubprocessCommand(sys.executable, ("-c",)))
    with pytest.raises(ValueError, match="input_data"):
        adapter.execute(action("py", input_data=12345))


# --- FileAdapter ------------------------------------------------------------


def test_file_adapter_reads_allowed_file(tmp_path: Path) -> None:
    (tmp_path / "flag.txt").write_text("CTF{local}", encoding="utf-8")
    adapter = FileAdapter("file_read", tmp_path)
    result = adapter.execute(action("file_read", input_data="flag.txt"))
    assert result.exit_code == 0
    assert result.stdout == "CTF{local}"


def test_file_adapter_missing_file_is_captured(tmp_path: Path) -> None:
    adapter = FileAdapter("file_read", tmp_path)
    result = adapter.execute(action("file_read", input_data="missing.txt"))
    assert result.exit_code == 1
    assert result.tool_available is True


def test_file_adapter_refuses_path_escaping_allowed_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside_secret.txt"
    outside.write_text("secret", encoding="utf-8")
    adapter = FileAdapter("file_read", tmp_path)
    result = adapter.execute(action("file_read", input_data="../outside_secret.txt"))
    assert result.tool_available is False


def test_file_adapter_environment_unavailable_when_root_missing(tmp_path: Path) -> None:
    missing_root = tmp_path / "does-not-exist"
    adapter = FileAdapter("file_read", missing_root)
    result = adapter.execute(action("file_read", input_data="x.txt"))
    assert result.environment_available is False


# --- AdapterRegistry --------------------------------------------------------


def test_registry_executes_registered_tool(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("ok", encoding="utf-8")
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    result = registry.execute(action("file_read", input_data="a.txt"))
    assert result.stdout == "ok"


def test_registry_rejects_unregistered_tool() -> None:
    registry = AdapterRegistry()
    with pytest.raises(UnknownToolError):
        registry.execute(action("mystery_tool"))


# --- HttpAdapter -------------------------------------------------------------

from ctf_agent.adapters import HttpAdapter
from ctf_agent.adapters.http_adapter import HttpPolicy


def _http_action(base_url: str, path: str, method: str = "GET") -> Action:
    return Action(
        action_id="a1",
        objective="probe endpoint",
        tool="http_probe",
        target=f"{base_url}{path}",
        input_data=None,
        relevant_parameters={"method": method},
        prerequisites=(),
        state_before=STATE,
    )


def test_http_adapter_success_captures_status_and_body(local_http_server) -> None:
    base_url, routes = local_http_server

    def ok(handler) -> None:
        handler.send_response(200)
        handler.end_headers()
        handler.wfile.write(b"hello world")

    routes["/ok"] = ok
    adapter = HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=(base_url,)))
    result = adapter.execute(_http_action(base_url, "/ok"))
    assert result.http_status == 200
    assert result.response_body == "hello world"


def test_http_adapter_captures_429(local_http_server) -> None:
    base_url, routes = local_http_server

    def rate_limited(handler) -> None:
        handler.send_response(429)
        handler.end_headers()

    routes["/limited"] = rate_limited
    adapter = HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=(base_url,)))
    result = adapter.execute(_http_action(base_url, "/limited"))
    assert result.http_status == 429


def test_http_adapter_captures_401(local_http_server) -> None:
    base_url, routes = local_http_server

    def unauthorized(handler) -> None:
        handler.send_response(401)
        handler.end_headers()

    routes["/auth"] = unauthorized
    adapter = HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=(base_url,)))
    result = adapter.execute(_http_action(base_url, "/auth"))
    assert result.http_status == 401


def test_http_adapter_captures_403(local_http_server) -> None:
    base_url, routes = local_http_server

    def forbidden(handler) -> None:
        handler.send_response(403)
        handler.end_headers()

    routes["/forbidden"] = forbidden
    adapter = HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=(base_url,)))
    result = adapter.execute(_http_action(base_url, "/forbidden"))
    assert result.http_status == 403


def test_http_adapter_refuses_target_outside_allow_list(local_http_server) -> None:
    base_url, _routes = local_http_server
    adapter = HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=("http://only-this-host",)))
    result = adapter.execute(_http_action(base_url, "/ok"))
    assert result.network_state == "unreachable"


def test_http_adapter_network_failure_when_server_unreachable() -> None:
    adapter = HttpAdapter(
        "http_probe",
        HttpPolicy(allowed_host_prefixes=("http://127.0.0.1:1",), timeout_seconds=1.0),
    )
    result = adapter.execute(_http_action("http://127.0.0.1:1", "/ok"))
    assert result.network_state == "unreachable"
