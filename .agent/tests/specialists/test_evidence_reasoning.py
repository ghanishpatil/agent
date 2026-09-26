from __future__ import annotations

from ctf_agent.context import FactState
from ctf_agent.models import HypothesisImpact
from ctf_agent.specialists import CryptoSpecialist, WebSpecialist
from ctf_agent.specialists.base import extract_flag_candidates

from .conftest import make_specialist_context


def test_observed_flag_token_produces_a_submit_proposal() -> None:
    # A flag token observed in evidence from a probe the web specialist would itself construct.
    probe_url = "http://127.0.0.1:9/search?id=1%27%20OR%20%271%27%3D%271"
    context = make_specialist_context(
        category="web",
        description="search endpoint with an id parameter building a sql query",
        urls=("http://127.0.0.1:9/search",),
        evidence=(
            {
                "hypotheses": ("web-sqli",),
                "tool": "http_probe",
                "source": probe_url,
                "kind": "target_response",
                "response_body": "row: id=1, secret=CTF{sqli_found}",
                "impact": HypothesisImpact.NO_IMPACT,
            },
        ),
        available_tools=("http_probe",),
    )
    # The specialist's own probe for sqli builds exactly probe_url, so build_submit_actions matches.
    analysis = WebSpecialist().analyze(context)
    submit_actions = [a for a in analysis.candidate_actions if a.candidate_flag]
    assert submit_actions, "specialist should propose submitting the observed flag token"
    assert submit_actions[0].candidate_flag == "CTF{sqli_found}"


def test_extract_flag_candidates_reads_only_observed_evidence() -> None:
    # No flag in evidence -> no candidate extracted (never invented).
    context = make_specialist_context(
        category="crypto",
        description="xor encoded cipher",
        files=("h.bin",),
        evidence=(
            {
                "hypotheses": ("crypto-xor",),
                "tool": "decode_tool",
                "source": "h.bin",
                "kind": "success",
                "stdout": "DECODE_NOT_A_FLAG",
                "impact": HypothesisImpact.NO_IMPACT,
            },
        ),
    )
    assert extract_flag_candidates(context) == ()


def test_tool_failure_is_annotated_blocked_not_disproven() -> None:
    context = make_specialist_context(
        category="crypto",
        description="xor encoded cipher artifact",
        files=("h.bin",),
        evidence=(
            {
                "hypotheses": ("crypto-xor",),
                "tool": "decode_tool",
                "source": "h.bin",
                "kind": "tool_failure",
                "impact": HypothesisImpact.UNRESOLVES,
            },
        ),
    )
    analysis = CryptoSpecialist().analyze(context)
    # The xor mechanism must NOT be reported disproven from a tool failure.
    xor_mechs = [m for m in analysis.candidate_mechanisms if "XOR" in m.name]
    assert xor_mechs
    assert all(m.fact_state != FactState.DISPROVEN.value for m in xor_mechs)
    # And it should say the test was blocked, not that the mechanism failed.
    assert any("blocked" in obs.lower() for obs in analysis.observations)


def test_environment_failure_is_not_disproof() -> None:
    context = make_specialist_context(
        category="web",
        description="search endpoint with id parameter and sql query",
        urls=("http://127.0.0.1:9/search",),
        evidence=(
            {
                "hypotheses": ("web-sqli",),
                "tool": "http_probe",
                "source": "http://127.0.0.1:9/search?id=1",
                "kind": "environment_failure",
                "impact": HypothesisImpact.UNRESOLVES,
            },
        ),
        available_tools=("http_probe",),
    )
    analysis = WebSpecialist().analyze(context)
    sqli = [m for m in analysis.candidate_mechanisms if "SQL" in m.name]
    assert sqli
    assert all(m.fact_state != FactState.DISPROVEN.value for m in sqli)


def test_rate_limit_is_not_disproof() -> None:
    context = make_specialist_context(
        category="web",
        description="search endpoint with id parameter and sql query",
        urls=("http://127.0.0.1:9/search",),
        evidence=(
            {
                "hypotheses": ("web-sqli",),
                "tool": "http_probe",
                "source": "http://127.0.0.1:9/search?id=1",
                "kind": "rate_limit",
                "impact": HypothesisImpact.UNRESOLVES,
            },
        ),
        available_tools=("http_probe",),
    )
    analysis = WebSpecialist().analyze(context)
    from ctf_agent.specialists.base import mechanism_blocked_by_failure

    blockers = mechanism_blocked_by_failure(context, "web-sqli")
    assert blockers  # a RATE_LIMIT is recorded as a blocker
    sqli = [m for m in analysis.candidate_mechanisms if "SQL" in m.name]
    assert all(m.fact_state != FactState.DISPROVEN.value for m in sqli)


def test_historical_memory_does_not_override_absence_of_current_evidence() -> None:
    from pathlib import Path

    from ctf_agent.memory_retrieval import AdvisoryMemory

    audit_root = Path(__file__).parents[3] / ".agent_audit"
    memory = AdvisoryMemory(audit_root)
    context = make_specialist_context(
        category="web",
        description="sql injection in a search query",
        urls=("http://127.0.0.1:9/search",),
        memory=memory,
        available_tools=("http_probe",),
    )
    analysis = WebSpecialist().analyze(context)
    # Memory contributes advisory refs, but every proposed mechanism is still only PLAUSIBLE
    # (no current evidence) -- memory never promotes a mechanism to SUPPORTED/VERIFIED.
    assert analysis.relevant_memory_refs  # memory did contribute priors
    assert all(
        m.fact_state == FactState.PLAUSIBLE.value for m in analysis.candidate_mechanisms
    )


def test_ambiguous_observation_leaves_mechanism_plausible() -> None:
    context = make_specialist_context(
        category="crypto",
        description="xor encoded cipher",
        files=("h.bin",),
        evidence=(
            {
                "hypotheses": ("crypto-xor",),
                "tool": "decode_tool",
                "source": "h.bin",
                "kind": "ambiguous",
                "impact": HypothesisImpact.UNRESOLVES,
            },
        ),
    )
    analysis = CryptoSpecialist().analyze(context)
    xor = [m for m in analysis.candidate_mechanisms if "XOR" in m.name]
    assert xor
    assert all(m.fact_state != FactState.DISPROVEN.value for m in xor)
