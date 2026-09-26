"""End-to-end scenario A (WEB) driven by the WebSpecialist through the real loop + a local HTTP
server (HttpAdapter).

Ambiguity: the app is a host-lookup tool with a search box, so both command-injection and SQL-
injection are plausible. The specialist probes the (alphabetically first) command-injection
mechanism -- the WRONG path -- which the server contradicts (DISPROVEN), then the SQL-injection
probe reveals a secret (SUPPORTED), and the observed flag is submitted + verified.

The server is local (127.0.0.1, ephemeral port), started only for the test.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from ctf_agent.adapters import AdapterRegistry, HttpAdapter
from ctf_agent.adapters.http_adapter import HttpPolicy
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.models import (
    EnvironmentState,
    HypothesisStatus,
    RelevantState,
    TestSpecification,
    VerificationPolicy,
)
from ctf_agent.planner import ActionPlanner
from ctf_agent.specialists import SpecialistRegistry, SpecialistReasoningSource


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)
REAL_FLAG = "CTF{web_specialist}"


def _install_routes(routes: dict, base_url: str) -> tuple[str, str]:
    cmdi_path = "/search?host=" + quote("127.0.0.1; id")
    sqli_path = "/search?id=" + quote("1' OR '1'='1")

    def cmdi(handler) -> None:
        handler.send_response(200)
        handler.end_headers()
        handler.wfile.write(b"lookup complete: no command output")  # contradicts cmdi

    def sqli(handler) -> None:
        handler.send_response(200)
        handler.end_headers()
        handler.wfile.write(f"row: id=1, name=admin, secret={REAL_FLAG}".encode("utf-8"))

    routes[cmdi_path] = cmdi
    routes[sqli_path] = sqli
    return base_url + cmdi_path, base_url + sqli_path


def build_web_specialist_loop(tmp_path: Path, local_http_server):
    base_url, routes = local_http_server
    cmdi_url, sqli_url = _install_routes(routes, base_url)

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("http_probe",)),
        trusted_sources={"http_probe": (cmdi_url, sqli_url)},
    )
    registry = AdapterRegistry()
    registry.register(HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=(base_url,))))
    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("http_probe",)
    )
    trusted_sources_for_disproof = {
        "web-cmdi": TestSpecification(
            hypothesis_id="web-cmdi",
            supporting_body_contains=("uid=",),
            contradicting_body_contains=("no command output",),
            authoritative_sources=(cmdi_url,),
        ),
        "web-sqli": TestSpecification(
            hypothesis_id="web-sqli",
            supporting_body_contains=("secret=",),
            contradicting_body_contains=("name=guest",),
            authoritative_sources=(sqli_url,),
        ),
    }
    loop = ReasoningLoop(
        metadata=ChallengeMetadata(
            name="host-lookup",
            category="web",
            description=(
                "a host lookup / ping tool with a search box that builds a SQL query from the id= "
                "parameter"
            ),
            urls=(base_url + "/search",),
            flag_format="CTF{...}",
        ),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=brain,
        journal=RuntimeJournal(tmp_path / "runtime" / "web.jsonl"),
        run_id="spec-web-1",
        clock=lambda: FIXED_CLOCK,
        board=HypothesisBoard(),
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, loop.board, brain


def test_web_specialist_discriminates_and_verifies(tmp_path: Path, local_http_server) -> None:
    loop, board, brain = build_web_specialist_loop(tmp_path, local_http_server)
    state = RelevantState(
        EnvironmentState("env-1", ("http_probe",)), "guest", "s1", "web-1"
    )
    result = loop.run(state, max_actions=8)

    assert result.outcome is LoopOutcome.VERIFIED
    assert board.get("web-cmdi").status is HypothesisStatus.DISPROVEN  # wrong path, evidence-based
    assert board.get("web-sqli").status is HypothesisStatus.SUPPORTED
    assert "web" in {s.name for s in brain.last_selection.selected}
