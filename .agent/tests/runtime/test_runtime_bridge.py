"""Runtime bridge proof tests (Step 8).

Positive: a scripted LLM drives the FULL frozen pipeline to a kernel-verified STOP:
  LLM -> typed proposal -> planner -> trusted adapter -> observation -> classifier -> evidence
      -> impact -> verification -> STOP.

Negative: an LLM attempt to execute a shell command is rejected because the model has no execution
authority — the unregistered tool never reaches an adapter and nothing runs.

Plus: model-routing policy and the anti-guessing/verification invariants.
"""

from __future__ import annotations

import json
import re

from ctf_agent.autonomy.contracts import ChallengeInput, SolveStatus

# Reuse the proven, deterministic SSTI web environment from the frozen experiment layer.
from ctf_experiment.knowledge_dependent_benchmark_v2 import (
    BASE_URL,
    _SSTI_URL,
    _constraints,
    web_environment,
)

from ctf_runtime import AgentSession, ModelRouter, ModelTier, ScriptedLLMClient
from ctf_runtime.routing import RoutingSignals

FLAG = "CTF{rt_ssti_real}"


def _solver_script(request):
    """A faithful LLM stand-in: propose the SSTI probe; once EVAL=49 + a flag are visible in the
    OBSERVED evidence embedded in the prompt, propose submitting that observed flag."""
    prompt = request.prompt
    hyps = [{
        "id": "web-ssti",
        "statement": "the name parameter is evaluated by a server-side template",
        "mechanism": "ssti",
        "technique": "Server-Side Template Injection",
    }]
    actions = [{
        "hypothesis_id": "web-ssti",
        "objective": "probe template evaluation with {{7*7}}",
        "tool": "http_probe",
        "target": _SSTI_URL,
        "expected_observation": "EVAL=49",
    }]
    # Extract the REAL flag from observed evidence (exclude the "CTF{...}" flag_format placeholder).
    seen_flag = re.search(r"CTF\{[A-Za-z0-9_]+\}", prompt)
    if "EVAL=49" in prompt and seen_flag:
        actions.append({
            "hypothesis_id": "web-ssti",
            "objective": "submit the flag observed in evidence",
            "tool": "http_probe",
            "target": _SSTI_URL,
            "candidate_flag": seen_flag.group(0),
        })
    return json.dumps({"hypotheses": hyps, "actions": actions})


def _shell_script(request):
    """A malicious LLM that tries to run a shell command directly."""
    return json.dumps({
        "hypotheses": [{"id": "h-shell", "statement": "just run a wordlist crack"}],
        "actions": [{
            "hypothesis_id": "h-shell",
            "objective": "pull a wordlist and run a proper crack",
            "tool": "execute_pwsh",           # NOT a registered trusted adapter
            "target": "cmd.exe",
            "input_data": "whoami",
        }],
    })


# --- POSITIVE: full pipeline to verified STOP, driven by the LLM ------------------------------

def test_llm_drives_full_pipeline_to_verified_stop(tmp_path):
    env = web_environment(tmp_path / "env", flag=FLAG)
    challenge = ChallengeInput(name="rt-web", category="web", description="A web application.",
                               flag_format="CTF{...}", urls=(BASE_URL,))
    session = AgentSession(
        challenge,
        llm_client=ScriptedLLMClient(_solver_script),
        environment=env,
        constraints=_constraints(),
        session_journal_path=tmp_path / "session.jsonl",
        use_specialist_base=False,   # pure LLM -> pipeline (no specialist fallback)
    ).start()

    result = session.run()

    assert result.status is SolveStatus.SOLVED
    assert result.verified_flag == FLAG
    assert result.verification_evidence_ids            # verified through bound evidence
    assert result.final_verification_method
    assert session.is_verified() and session.get_flag() == FLAG

    # The runtime journal proves each stage of the pipeline was traversed.
    recs = session.session_journal_records()
    assert recs, "runtime journal must contain executed steps"
    for r in recs:                                     # every required field present
        for key in ("timestamp", "challenge_id", "model", "reasoning_source", "hypothesis_id",
                    "hypothesis_state", "proposal_id", "action_fingerprint", "planner_decision",
                    "execution_adapter", "observation_class", "impact", "verification_state",
                    "escalation_reason"):
            assert key in r
    assert any(r["execution_adapter"] == "http_probe" for r in recs)     # trusted adapter executed
    assert any(r["verification_state"] == "VERIFIED" for r in recs)      # kernel verified
    assert all(r["model"] == "sonnet-5" for r in recs)                   # FAST default tier
    assert all(r["action_fingerprint"] for r in recs)                    # dedup fingerprint recorded


# --- NEGATIVE: the LLM cannot execute a shell command -----------------------------------------

def test_llm_shell_command_is_rejected_no_execution(tmp_path):
    env = web_environment(tmp_path / "env2", flag=FLAG)
    challenge = ChallengeInput(name="rt-web-evil", category="web", description="A web application.",
                               flag_format="CTF{...}", urls=(BASE_URL,))
    session = AgentSession(
        challenge,
        llm_client=ScriptedLLMClient(_shell_script),
        environment=env,
        constraints=_constraints(),
        session_journal_path=tmp_path / "session2.jsonl",
        use_specialist_base=False,
    ).start()

    report = session.step()

    # The shell tool is unregistered -> validate_action_suggestion rejects it before the planner.
    assert report.action_tool != "execute_pwsh"
    assert not report.executed                          # nothing executed this step
    assert not session.is_verified()
    assert session.get_flag() is None
    rejections = session.proposal_rejections()
    assert any("execute_pwsh" in msg or "not registered" in msg for msg in rejections)
    # No runtime-journal record for a shell adapter (nothing ran through a shell).
    assert all(r["execution_adapter"] != "execute_pwsh" for r in session.session_journal_records())


def _guess_script(request):
    """A model that asserts a flag with no supporting evidence (pure guess)."""
    return json.dumps({
        "hypotheses": [{"id": "web-ssti", "statement": "guessy", "mechanism": "ssti",
                        "technique": "Server-Side Template Injection"}],
        "actions": [{"hypothesis_id": "web-ssti", "objective": "just submit a guess",
                     "tool": "http_probe", "target": _SSTI_URL,
                     "candidate_flag": "CTF{totally_made_up_guess}"}],
    })


def test_llm_cannot_submit_flag_without_evidence(tmp_path):
    env = web_environment(tmp_path / "envg", flag=FLAG)
    challenge = ChallengeInput(name="rt-web-guess", category="web", description="A web application.",
                               flag_format="CTF{...}", urls=(BASE_URL,))
    session = AgentSession(
        challenge, llm_client=ScriptedLLMClient(_guess_script), environment=env,
        constraints=_constraints(), use_specialist_base=False,
    ).start()
    session.run(max_steps=3)
    # The guessed candidate is never bound to evidence -> it is dropped before execution and the
    # kernel never verifies it. No fabricated flag can pass.
    assert not session.is_verified()
    assert session.get_flag() is None


def test_llm_client_receives_only_text(tmp_path):
    """The model capability is text-in/text-out; it is handed no tool/adapter/kernel handle."""
    env = web_environment(tmp_path / "env3", flag=FLAG)
    client = ScriptedLLMClient(_solver_script)
    session = AgentSession(
        ChallengeInput(name="rt-web", category="web", description="A web app.", urls=(BASE_URL,)),
        llm_client=client, environment=env, constraints=_constraints(), use_specialist_base=False,
    ).start()
    session.step()
    assert client.calls, "client should have been called"
    for req in client.calls:
        assert isinstance(req.prompt, str) and isinstance(req.model, str)
        # the request object carries no executable handles — only text fields
        assert set(vars(req)) <= {"model", "prompt", "response_format", "schema_hint", "metadata"}


# --- model routing policy ---------------------------------------------------------------------

def test_router_starts_fast_and_escalates_on_evidence():
    router = ModelRouter()
    fast = router.select(RoutingSignals(category="web", uncertainty=0, stall_steps=0))
    assert fast.tier is ModelTier.FAST and fast.model == "sonnet-5"

    deep = router.select(RoutingSignals(category="web", uncertainty=4))
    assert deep.tier is ModelTier.DEEP and deep.model == "opus-5"

    deep_stall = router.select(RoutingSignals(stall_steps=2))
    assert deep_stall.tier is ModelTier.DEEP

    high = router.select(RoutingSignals(stall_steps=5))
    assert high.tier is ModelTier.HIGH_END and high.model == "gpt-5.6-sol-high"

    fb = router.fallback(RoutingSignals(), "ConnectionError: boom")
    assert fb.tier is ModelTier.FALLBACK and fb.model == "gpt-5.6-luna-think"


def test_router_does_not_hardcode_category_to_model():
    router = ModelRouter()
    # Same category, different evidence -> different tiers (category alone does not decide).
    a = router.select(RoutingSignals(category="pwn", uncertainty=0, stall_steps=0))
    b = router.select(RoutingSignals(category="pwn", uncertainty=5))
    assert a.tier is ModelTier.FAST and b.tier is ModelTier.DEEP
