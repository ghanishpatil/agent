"""Synthetic end-to-end scenario A (WEB), per prompt_phase 3.md section 8.

A local, synthetic HTTP service simulates a search endpoint with a discoverable SQL-injection-style
vulnerability. The agent:
  1. forms a hypothesis ("the search endpoint is vulnerable to a filter-bypass injection"),
  2. runs a cheap benign probe first (id=1) -- this returns ordinary data, no evidence either way,
  3. runs the discriminating probe (id=1' OR '1'='1) -- the server, being a controlled synthetic
     fixture, returns a body containing the flag only for that exact payload shape, giving
     SUPPORTS-level evidence,
  4. submits the derived flag through the same trusted, authoritative "challenge_service" tool,
  5. the kernel's VerificationController independently confirms the candidate against that
     evidence and returns STOP.

Nothing here attacks a real third-party system: the server is started locally on 127.0.0.1 on an
ephemeral port for the duration of the test only.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from ctf_agent.adapters import AdapterRegistry, HttpAdapter
from ctf_agent.adapters.http_adapter import HttpPolicy
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.models import EnvironmentState, RelevantState, TestSpecification, VerificationPolicy
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)
FLAG = "CTF{web_injection_found}"


def _install_search_route(routes: dict, base_url: str) -> None:
    """The conftest fixture's route table is keyed by exact ``handler.path`` (including any query
    string), so every distinct query value needs its own explicit route entry."""

    def search(handler) -> None:
        from urllib.parse import urlsplit, parse_qs

        query = parse_qs(urlsplit(handler.path).query)
        raw_id = query.get("id", [""])[0]
        handler.send_response(200)
        handler.send_header("Content-Type", "text/plain")
        handler.end_headers()
        if raw_id == "1' OR '1'='1":
            handler.wfile.write(
                f"row: id=1, name=admin, secret={FLAG}".encode("utf-8")
            )
        else:
            handler.wfile.write(b"row: id=1, name=guest")

    def submit(handler) -> None:
        import json as _json

        length = int(handler.headers.get("Content-Length", "0"))
        raw = handler.rfile.read(length) if length else b"{}"
        payload = _json.loads(raw.decode("utf-8")) if raw else {}
        submitted = payload.get("flag", "")
        handler.send_response(200)
        handler.end_headers()
        if submitted == FLAG:
            handler.wfile.write(f"accepted {FLAG}".encode("utf-8"))
        else:
            handler.wfile.write(b"rejected")

    from urllib.parse import quote

    injection_payload = quote("1' OR '1'='1")
    routes["/search?id=1"] = search
    routes["/search?id=" + injection_payload] = search
    routes["/submit"] = submit


class ScriptedWebReasoning:
    """Deterministic stand-in for an LLM: scripted, but only ever emits *proposals*.

    Every ActionSuggestion below still has to pass through validate_action_suggestion(), the
    planner's dedup/prerequisite checks, and (for the submit step) the kernel's own
    VerificationController -- nothing here has a privileged path to kernel state.
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._step = 0

    def suggest_hypotheses(self, context):
        return ()

    def suggest_actions(self, context) -> Tuple[ActionSuggestion, ...]:
        self._step += 1
        if self._step == 1:
            return (
                ActionSuggestion(
                    hypothesis_id="h-injection",
                    objective="benign baseline probe of the search endpoint",
                    tool="http_probe",
                    target=f"{self._base_url}/search?id=1",
                    expected_observation="ordinary row data, nothing discriminating yet",
                ),
            )
        if self._step == 2:
            from urllib.parse import quote

            payload = quote("1' OR '1'='1")
            return (
                ActionSuggestion(
                    hypothesis_id="h-injection",
                    objective="filter-bypass discriminating probe",
                    tool="http_probe",
                    target=f"{self._base_url}/search?id={payload}",
                    expected_observation="a secret field appears in the response body",
                ),
            )
        return (
            ActionSuggestion(
                hypothesis_id="h-injection",
                objective="submit the flag observed in the discriminating probe",
                tool="challenge_service",
                target=f"{self._base_url}/submit",
                input_data={"flag": FLAG},
                relevant_parameters={"method": "POST"},
                candidate_flag=FLAG,
            ),
        )

    def interpret(self, context):
        return ()


def build_web_scenario_loop(tmp_path: Path, local_http_server) -> ReasoningLoop:
    """Reusable builder so other tests (e.g. a cross-scenario metrics aggregate) can run this
    exact scenario without duplicating its setup."""
    base_url, routes = local_http_server
    _install_search_route(routes, base_url)

    from urllib.parse import quote as _quote

    injection_query = "1' OR '1'='1"
    baseline_url = f"{base_url}/search?id=1"
    discriminating_url = f"{base_url}/search?id={_quote(injection_query)}"

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("challenge_service",)),
        # Only the discriminating probe's URL is trusted as authoritative evidence for
        # h-injection. A single ordinary-looking baseline response is real, useful evidence
        # (WEAKENS) but is deliberately NOT treated as strong enough to fully disprove a
        # filter-bypass hypothesis on its own -- that would be poor methodology even for a real
        # analyst. Only the actual injection payload's response is authoritative.
        trusted_sources={"http_probe": (discriminating_url,)},
    )
    board = HypothesisBoard()
    board.propose_hypothesis(
        "h-injection",
        "the /search endpoint is vulnerable to a filter-bypass injection",
        technique="sql-injection-style-filter-bypass",
    )

    registry = AdapterRegistry()
    registry.register(HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=(base_url,))))
    registry.register(
        HttpAdapter("challenge_service", HttpPolicy(allowed_host_prefixes=(base_url,)))
    )

    # A real discriminating test for h-injection: the response body must contain "secret=" to
    # count as supporting evidence of the injection, and the ordinary "name=guest" shape as
    # contradicting it -- this is what makes the discriminating probe's evidence actually move the
    # hypothesis's status, rather than only feeding the separate flag-verification path.
    trusted_sources_for_disproof = {
        "h-injection": TestSpecification(
            hypothesis_id="h-injection",
            supporting_body_contains=("secret=",),
            contradicting_body_contains=("name=guest",),
            authoritative_sources=(baseline_url, discriminating_url),
        ),
    }

    return ReasoningLoop(
        metadata=ChallengeMetadata(name="web-scenario", category="web"),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=ScriptedWebReasoning(base_url),
        journal=RuntimeJournal(tmp_path / "runtime" / "web_scenario.jsonl"),
        run_id="scenario-web-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )


def test_scenario_web_injection_discovered_and_flag_verified(
    tmp_path: Path, local_http_server
) -> None:
    loop = build_web_scenario_loop(tmp_path, local_http_server)
    state = RelevantState(EnvironmentState("env-1", ("http_probe", "challenge_service")), "guest", "s1", "web-1")
    result = loop.run(state, max_actions=5)

    assert result.outcome is LoopOutcome.VERIFIED
    assert result.actions_taken == 3

    # The benign baseline probe's ordinary body contradicts the hypothesis against the registered
    # TestSpecification, but its source is not trusted as authoritative -- so it only WEAKENS the
    # hypothesis (real evidence, real signal) rather than fully disproving it from one probe.
    from ctf_agent.models import HypothesisImpact

    baseline_result = result.pipeline_results[0]
    assert baseline_result.impact is HypothesisImpact.WEAKENS

    # The discriminating (injection) probe then supports the hypothesis with real evidence,
    # correcting the branch that the baseline alone would have closed.
    discriminating_result = result.pipeline_results[1]
    assert discriminating_result.impact is HypothesisImpact.SUPPORTS

    # The final action must be the one that actually flips verification to STOP, and it must be
    # traceable to real evidence, not an assumption.
    final_result = result.pipeline_results[-1]
    assert final_result.verification is not None
    assert final_result.verification.candidate.value == FLAG

    # The journal recorded every stage of the winning path.
    events = [e["kind"] for e in loop.journal.read_all()]
    assert "evidence_recorded" in events
    assert "control_decision" in events

    from ctf_agent.metrics import evaluate_single_run

    metrics = evaluate_single_run(result)
    assert metrics.verified is True
    assert metrics.actions_to_solution == 3
    assert metrics.duplicate_action_count == 0
    # The registered TestSpecification for h-injection applies to every action targeting that
    # hypothesis (register_test keys by action fingerprint, and the loop re-registers the same
    # spec per action via trusted_sources_for_disproof), including the final submit action -- whose
    # "accepted CTF{...}" body matches neither the supporting nor contradicting marker, so it comes
    # back UNRESOLVES rather than NO_IMPACT. Nothing here is "unnecessary" by the strict
    # impact-based metric: every action produced a real, distinct evidence-level signal.
    assert metrics.unnecessary_action_count == 0
    assert metrics.state_is_consistent
