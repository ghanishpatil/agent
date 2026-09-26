"""Kiro integration layer.

Kiro (the IDE LLM assistant) interacts with the agent ONLY through this facade. The facade exposes
solving as: start a challenge, provide description/files/urls/resources, inspect state/evidence/
hypotheses, invoke the next reasoning step, and read the final verified flag. It deliberately
exposes NO execution primitive — there is no ``run_shell`` / ``http`` / ``tool`` method here. Once a
session is active, Kiro must drive it through ``next_step()`` / ``run()`` and must not solve the
challenge with its own IDE tools.

Trust separation: the *challenge intent* (name, description, files, urls, credentials) comes from
Kiro; the *trusted environment* (permitted tools/adapters, evidence rules, verifier route) is
supplied by the operator via ``EnvironmentConfig`` at construction. Kiro cannot inject an execution
tool, because it never provides the adapter registry — it only provides text/resource intent.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Mapping, Optional, Tuple

from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    ResourceKind,
    SolveConstraints,
)

from .llm_client import LLMClient
from .routing import ModelRouter
from .session import AgentSession, StepReport


class KiroBridge:
    """Facade Kiro uses instead of solving directly. No execution primitive is exposed."""

    def __init__(
        self,
        *,
        environment: EnvironmentConfig,
        llm_client: LLMClient,
        constraints: Optional[SolveConstraints] = None,
        router: Optional[ModelRouter] = None,
        session_journal_path: Optional[Path] = None,
    ) -> None:
        self._environment = environment
        self._client = llm_client
        self._constraints = constraints or SolveConstraints()
        self._router = router or ModelRouter()
        self._session_journal_path = session_journal_path
        self._session: Optional[AgentSession] = None
        self._pending_resources: List[ChallengeResource] = []

    # -- challenge intake (Kiro-provided) ---------------------------------------------------
    def provide_resource(
        self, resource_id: str, kind: ResourceKind, *, path: Optional[Path] = None,
        content: bytes | str | None = None, filename: str = "",
    ) -> None:
        if self._session is not None:
            raise RuntimeError("resources must be provided before start_challenge()")
        self._pending_resources.append(
            ChallengeResource(resource_id=resource_id, kind=kind, path=path,
                              content=content, filename=filename)
        )

    def start_challenge(
        self,
        *,
        name: str,
        category: str = "",
        description: str = "",
        hints: Tuple[str, ...] = (),
        urls: Tuple[str, ...] = (),
        flag_format: str = "",
        credentials: Optional[Mapping[str, str]] = None,
        attempt_limit: Optional[int] = None,
    ) -> dict:
        if self._session is not None:
            raise RuntimeError("a challenge session is already active")
        challenge = ChallengeInput(
            name=name, category=category or None, description=description or None,
            hints=tuple(hints), flag_format=flag_format or None, urls=tuple(urls),
            credentials=dict(credentials or {}), attempt_limit=attempt_limit,
        )
        self._session = AgentSession(
            challenge,
            llm_client=self._client,
            environment=self._environment,
            constraints=self._constraints,
            resources=tuple(self._pending_resources),
            router=self._router,
            session_journal_path=self._session_journal_path,
        ).start()
        return self._session.get_state()

    # -- driving the agent (Kiro observes / advances; it never executes) --------------------
    def next_step(self) -> StepReport:
        self._require_session()
        return self._session.step()

    def run(self, max_steps: Optional[int] = None) -> dict:
        self._require_session()
        result = self._session.run(max_steps)
        return {
            "status": result.status.value,
            "verified_flag": result.verified_flag,
            "terminal_reason": result.terminal_reason,
            "actions": len(result.actions),
            "journal_path": result.journal_path,
        }

    # -- observation ------------------------------------------------------------------------
    def get_state(self) -> dict:
        self._require_session()
        return self._session.get_state()

    def get_hypotheses(self) -> List[dict]:
        self._require_session()
        return self._session.get_hypotheses()

    def get_evidence(self) -> List[dict]:
        self._require_session()
        return self._session.get_evidence()

    def get_pending_actions(self) -> List[dict]:
        self._require_session()
        return self._session.get_pending_actions()

    def is_verified(self) -> bool:
        self._require_session()
        return self._session.is_verified()

    def get_flag(self) -> Optional[str]:
        self._require_session()
        return self._session.get_flag()

    def progress(self) -> dict:
        self._require_session()
        state = self._session.get_state()
        return {
            "run_id": state["run_id"],
            "steps": state["steps"],
            "actions_executed": state["actions_executed"],
            "verified": state["verified"],
            "hypotheses": len(state["hypotheses"]),
            "evidence": len(state["evidence"]),
            "last_model": state["last_model"],
        }

    def session_journal(self) -> List[dict]:
        self._require_session()
        return self._session.session_journal_records()

    def get_result(self):
        """Read-only authoritative SolveResult projection (for post-terminal learning)."""
        self._require_session()
        return self._session.get_result()

    def recent_observations(self, limit: int = 50) -> List[dict]:
        self._require_session()
        return self._session.recent_observations(limit)

    def _require_session(self) -> None:
        if self._session is None:
            raise RuntimeError("no active challenge session; call start_challenge() first")
