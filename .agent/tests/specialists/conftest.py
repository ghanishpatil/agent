from __future__ import annotations

from datetime import datetime, timezone
from typing import Tuple

import pytest

from ctf_agent.classifier import classify_result
from ctf_agent.context import ChallengeMetadata, build_context
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.kernel import TrustKernel
from ctf_agent.models import (
    ExecutionResult,
    HypothesisImpact,
    Observation,
)
from ctf_agent.specialists.base import SpecialistContext


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)


def make_execution(tool: str, *, kind: str = "success", stdout: str = "", response_body: str = "") -> ExecutionResult:
    """Build an ExecutionResult that classify_result maps to a chosen result class."""
    if kind == "success":
        return ExecutionResult("a", tool, exit_code=0, stdout=stdout, response_body=response_body)
    if kind == "target_response":
        return ExecutionResult("a", tool, http_status=200, stdout=stdout, response_body=response_body)
    if kind == "rate_limit":
        return ExecutionResult("a", tool, http_status=429, stdout=stdout, response_body=response_body)
    if kind == "timeout":
        return ExecutionResult("a", tool, timed_out=True, stdout=stdout, response_body=response_body)
    if kind == "tool_failure":
        return ExecutionResult("a", tool, tool_available=True, exit_code=1, stdout=stdout, response_body=response_body)
    if kind == "environment_failure":
        return ExecutionResult("a", tool, environment_available=False, stdout=stdout, response_body=response_body)
    if kind == "ambiguous":
        return ExecutionResult("a", tool, stdout=stdout, response_body=response_body)
    raise ValueError(f"unknown execution kind {kind}")


def make_specialist_context(
    *,
    name: str = "sample",
    category: str = "web",
    description: str = "",
    hints: Tuple[str, ...] = (),
    files: Tuple[str, ...] = (),
    urls: Tuple[str, ...] = (),
    flag_format: str = "CTF{...}",
    available_tools: Tuple[str, ...] = (),
    memory: object = None,
    evidence: Tuple[dict, ...] = (),
) -> SpecialistContext:
    """Build a SpecialistContext, optionally pre-recording current evidence.

    Each ``evidence`` dict: {hypotheses:(ids,), tool, source, kind, stdout, response_body,
    impact(HypothesisImpact), seed_board(bool)}.
    """
    kernel = TrustKernel()
    board = HypothesisBoard()
    for i, spec in enumerate(evidence):
        tool = spec.get("tool", "http_probe")
        source = spec.get("source", "target")
        execution = make_execution(
            tool,
            kind=spec.get("kind", "target_response"),
            stdout=spec.get("stdout", ""),
            response_body=spec.get("response_body", ""),
        )
        observation = Observation(f"obs-{i}", f"a{i}", NOW, source, execution)
        classification = classify_result(execution)
        hyps = tuple(spec.get("hypotheses", ()))
        for hyp_id in hyps:
            if spec.get("seed_board", True) and hyp_id not in {h.hypothesis_id for h in board.all_hypotheses()}:
                board.propose_hypothesis(hyp_id, f"seeded {hyp_id}")
        kernel.evidence.record_current(
            observation=observation,
            classification=classification,
            impact=spec.get("impact", HypothesisImpact.NO_IMPACT),
            affected_hypotheses=hyps,
        )
    metadata = ChallengeMetadata(
        name=name,
        category=category,
        description=description,
        hints=hints,
        files=files,
        urls=urls,
        flag_format=flag_format,
    )
    challenge = build_context(metadata, kernel, board)
    return SpecialistContext(challenge=challenge, available_tools=available_tools, memory=memory)


@pytest.fixture
def audit_root():
    from pathlib import Path

    return Path(__file__).parents[3] / ".agent_audit"


@pytest.fixture
def local_http_server():
    """A real local HTTP server on 127.0.0.1 with a caller-populated exact-path route table.
    Used only to exercise the HttpAdapter boundary against a controlled synthetic target."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from typing import Callable, Iterator

    routes: dict = {}

    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # noqa: A002
            return None

        def do_GET(self):  # noqa: N802
            self._dispatch()

        def do_POST(self):  # noqa: N802
            self._dispatch()

        def _dispatch(self):
            handler = routes.get(self.path)
            if handler is None:
                self.send_response(404)
                self.end_headers()
                return
            handler(self)

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}", routes
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
