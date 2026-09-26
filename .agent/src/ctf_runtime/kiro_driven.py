"""Architecture A — Kiro-driven reasoning inversion.

Kiro's own model is the reasoner. It reads authoritative agent state via ``observe()`` and submits
TYPED proposals via ``propose()``. Those proposals are validated through the SAME frozen validators
and then flow through the frozen ``RoutedReasoningSource -> ReasoningLoop -> ActionPlanner ->
TrustKernel -> trusted adapters -> Evidence -> Verification`` pipeline. There is **no LLM inside the
runtime** on this path: the reasoning source is a queue that Kiro fills.

Trust properties preserved (nothing weakened):
* Kiro only *proposes* typed hypotheses/actions; it never executes anything.
* ``validate_action_suggestion`` rejects unregistered tools (shell/execute_pwsh/etc.) before the
  planner; the planner de-duplicates; the kernel classifies, binds evidence, and owns verification.
* A candidate flag is verified only by the frozen VerificationController (kernel STOP), never by
  Kiro asserting it.
* Budgets, failure classification, session isolation, and the audit journal are the frozen ones.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple

from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    SolveConstraints,
)
from ctf_agent.proposals import (
    ActionSuggestion,
    HypothesisSuggestion,
    ProposalRejected,
    validate_action_suggestion,
    validate_hypothesis_suggestion,
)

from .session import AgentSession

# The JSON proposal schema returned by observe(), so Kiro knows exactly what to submit.
PROPOSAL_SCHEMA = {
    "hypotheses": [{
        "hypothesis_id": "str (stable id you choose)",
        "statement": "str (what you believe about the target)",
        "mechanism": "str (optional)", "technique": "str (optional)", "rationale": "str (optional)",
    }],
    "actions": [{
        "hypothesis_id": "str (must match a hypothesis you proposed)",
        "objective": "str (what this action tests)",
        "tool": "str (MUST be one of available_tools)",
        "target": "str (non-empty; e.g. the URL/path/label the tool acts on)",
        "input_data": "optional (str | list | dict, tool-specific)",
        "relevant_parameters": "optional dict (e.g. {'method':'GET'})",
        "expected_observation": "str (optional)",
        "candidate_flag": "str (optional; only set if a flag is ALREADY visible in evidence)",
        "rationale": "str (optional)",
    }],
}


class QueuedReasoningSource:
    """A ReasoningSource whose proposals are whatever Kiro last loaded. Session-compatible."""

    def __init__(self, base: Optional[object] = None) -> None:
        self.base = base
        self._hyps: Tuple[HypothesisSuggestion, ...] = ()
        self._acts: Tuple[ActionSuggestion, ...] = ()
        self._notes: Tuple[Any, ...] = ()
        self._registry = None
        # attributes AgentSession/route reporting expect to exist
        self.last_route = None
        self.route_history: List[Any] = []
        self.rejections: List[str] = []

    def attach(self, registry) -> None:
        self._registry = registry

    def load(self, hyps: Tuple[HypothesisSuggestion, ...], acts: Tuple[ActionSuggestion, ...]) -> None:
        self._hyps, self._acts = tuple(hyps), tuple(acts)

    def clear(self) -> None:
        self._hyps, self._acts, self._notes = (), (), ()

    def suggest_hypotheses(self, context):
        base = tuple(self.base.suggest_hypotheses(context)) if self.base else ()
        ids = {h.hypothesis_id for h in base}
        return base + tuple(h for h in self._hyps if h.hypothesis_id not in ids)

    def suggest_actions(self, context):
        base = tuple(self.base.suggest_actions(context)) if self.base else ()
        return base + self._acts

    def interpret(self, context):
        return tuple(self.base.interpret(context)) if self.base else ()


class KiroDrivenController:
    """Owns one Kiro-driven session: observe() -> Kiro reasons -> propose() -> frozen pipeline."""

    def __init__(
        self,
        challenge: ChallengeInput,
        *,
        environment: EnvironmentConfig,
        constraints: Optional[SolveConstraints] = None,
        resources: Tuple[ChallengeResource, ...] = (),
        session_journal_path: Optional[Path] = None,
    ) -> None:
        self._queued = QueuedReasoningSource(base=None)  # Kiro is the sole reasoner (no auto-solve)
        self._session = AgentSession(
            challenge,
            inner_reasoning_source=self._queued,
            environment=environment,
            constraints=constraints,
            resources=resources,
            session_journal_path=session_journal_path,
        ).start()
        self._registry = self._session.adapter_registry

    # -- observation ------------------------------------------------------------------------
    def observe(self) -> dict:
        s = self._session.get_state()
        meta = self._session.metadata
        constraints = self._session._effective_constraints
        recent_ev = s["evidence"][-5:]
        recent_failures = [e for e in recent_ev if e["result_class"] in (
            "RATE_LIMIT", "TIMEOUT", "AUTH_FAILURE", "AUTHZ_FAILURE", "NETWORK_FAILURE",
            "TOOL_FAILURE", "ENVIRONMENT_FAILURE")]
        return {
            "session_id": None,  # filled by gateway
            "run_id": s["run_id"],
            "challenge": {
                "name": getattr(meta, "name", ""), "category": getattr(meta, "category", ""),
                "flag_format": getattr(meta, "flag_format", ""),
            },
            "hypotheses": s["hypotheses"],
            "evidence": s["evidence"],
            "recent_evidence": recent_ev,
            "recent_observations": self._session.recent_observations(),
            "recent_failures": recent_failures,
            "available_tools": list(self._registry.available_tools()) if self._registry else [],
            "verified": s["verified"],
            "verification_state": "VERIFIED" if s["verified"] else "IN_PROGRESS",
            "candidate_flag": self._session.get_flag() if s["verified"] else None,
            "actions_executed": s["actions_executed"],
            "steps": s["steps"],
            "budget": {
                "max_actions": constraints.max_actions,
                "actions_executed": s["actions_executed"],
                "actions_remaining": max(0, constraints.max_actions - s["actions_executed"]),
            },
            "terminal": s["verified"],
            "proposal_schema": PROPOSAL_SCHEMA,
            "guidance": (
                "Propose the single cheapest discriminating action using ONLY available_tools. "
                "Set candidate_flag ONLY if a flag is already visible in evidence. You cannot "
                "execute anything; the agent validates, executes via trusted adapters, and verifies."
            ),
        }

    # -- proposal ---------------------------------------------------------------------------
    def propose(self, hypotheses: Any, actions: Any) -> dict:
        accepted_hyps: List[HypothesisSuggestion] = []
        accepted_acts: List[ActionSuggestion] = []
        rejected: List[dict] = []

        for i, item in enumerate(_as_list(hypotheses)):
            try:
                if not isinstance(item, Mapping):
                    raise ProposalRejected("hypothesis must be an object")
                sug = HypothesisSuggestion(
                    hypothesis_id=str(item.get("hypothesis_id") or item.get("id") or ""),
                    statement=str(item.get("statement", "")),
                    mechanism=str(item.get("mechanism", "")),
                    technique=str(item.get("technique", "")),
                    rationale=str(item.get("rationale", "")),
                )
                validate_hypothesis_suggestion(sug)
                accepted_hyps.append(sug)
            except (ProposalRejected, TypeError, KeyError) as exc:
                rejected.append({"kind": "hypothesis", "index": i, "reason": str(exc)})

        for i, item in enumerate(_as_list(actions)):
            try:
                if not isinstance(item, Mapping):
                    raise ProposalRejected("action must be an object")
                sug = ActionSuggestion(
                    hypothesis_id=str(item.get("hypothesis_id", "")),
                    objective=str(item.get("objective", "")),
                    tool=str(item.get("tool", "")),
                    target=str(item.get("target", "")),
                    input_data=item.get("input_data"),
                    relevant_parameters=item.get("relevant_parameters") or {},
                    prerequisites=tuple(str(p) for p in _as_list(item.get("prerequisites"))),
                    expected_observation=str(item.get("expected_observation", "")),
                    rationale=str(item.get("rationale", "")),
                    candidate_flag=str(item.get("candidate_flag", "")),
                )
                # Hard tool-isolation gate: unregistered tools (execute_pwsh/shell/...) rejected here.
                validate_action_suggestion(sug, self._registry)
                accepted_acts.append(sug)
            except (ProposalRejected, TypeError, KeyError) as exc:
                rejected.append({"kind": "action", "index": i, "reason": str(exc)})

        # Load accepted proposals and drive the frozen loop to execute them (bounded by count/budget).
        self._queued.load(tuple(accepted_hyps), tuple(accepted_acts))
        executed: List[dict] = []
        steps = max(1, len(accepted_acts))
        for _ in range(steps):
            if self._session.is_verified():
                break
            report = self._session.step()
            if report.executed:
                executed.append({
                    "tool": report.action_tool, "objective": report.action_objective,
                    "planner_decision": report.planner_decision,
                    "observation_class": report.observation_class, "impact": report.impact,
                    "hypothesis_id": report.hypothesis_id, "hypothesis_state": report.hypothesis_state,
                })
            if report.verified:
                break
            if not report.executed:
                break  # duplicate/blocked -> no new action this cycle
        self._queued.clear()

        s = self._session.get_state()
        verified = s["verified"]
        return {
            "accepted": {"hypotheses": [h.hypothesis_id for h in accepted_hyps],
                          "actions": [a.tool for a in accepted_acts]},
            "rejected": rejected,
            "executed": executed,
            "hypotheses": s["hypotheses"],
            "new_evidence": s["evidence"][-len(executed):] if executed else [],
            "verified": verified,
            "result_type": "VERIFIED_FLAG" if verified and self._session.get_flag() else (
                "CANDIDATE_ONLY" if any(a.candidate_flag for a in accepted_acts) and not verified else "IN_PROGRESS"),
            "verified_flag": self._session.get_flag() if verified else None,
            "actions_executed": s["actions_executed"],
            "budget": {"max_actions": self._session._effective_constraints.max_actions,
                        "actions_remaining": max(0, self._session._effective_constraints.max_actions - s["actions_executed"])},
            "next": "call ctf_observe to see updated state, then propose the next action",
        }

    # -- passthrough reads (so the gateway can treat this like a bridge) --------------------
    def get_state(self) -> dict:
        return self._session.get_state()

    def get_hypotheses(self) -> List[dict]:
        return self._session.get_hypotheses()

    def get_evidence(self) -> List[dict]:
        return self._session.get_evidence()

    def get_pending_actions(self) -> List[dict]:
        return self._session.get_pending_actions()

    def is_verified(self) -> bool:
        return self._session.is_verified()

    def get_flag(self) -> Optional[str]:
        return self._session.get_flag()

    def progress(self) -> dict:
        s = self._session.get_state()
        return {"run_id": s["run_id"], "steps": s["steps"], "actions_executed": s["actions_executed"],
                "verified": s["verified"], "hypotheses": len(s["hypotheses"]),
                "evidence": len(s["evidence"]), "last_model": "kiro-driven"}

    def session_journal(self) -> List[dict]:
        return self._session.session_journal_records()

    def get_result(self):
        """Read-only authoritative SolveResult projection (for post-terminal learning)."""
        return self._session.get_result()

    def recent_observations(self, limit: int = 50) -> List[dict]:
        return self._session.recent_observations(limit)


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]
