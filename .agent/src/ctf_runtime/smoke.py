"""Controlled real-challenge smoke-test interface (Step 9).

This prepares — but never auto-runs — a real ``AgentSession`` for a manually chosen challenge. The
first real target must be selected by a human; this module refuses to launch anything on its own.

The trusted ``EnvironmentConfig`` (permitted tools/adapters, evidence rules, verifier route) is the
operator's responsibility: real network/subprocess capability must be supplied as trusted adapters,
not fabricated here. This module only assembles the challenge intent and hands back a prepared,
NOT-yet-run session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Tuple

from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    SolveConstraints,
)

from .llm_client import LLMClient
from .routing import ModelRouter
from .session import AgentSession


@dataclass(frozen=True)
class RealChallengeSpec:
    name: str
    description: str = ""
    category: str = ""
    hints: Tuple[str, ...] = ()
    target: str = ""                      # a URL/host; only reachable via a trusted network adapter
    flag_format: str = ""
    resources: Tuple[ChallengeResource, ...] = ()
    credentials: Mapping[str, str] = field(default_factory=dict)
    attempt_limit: Optional[int] = None


def prepare_real_session(
    spec: RealChallengeSpec,
    *,
    environment: EnvironmentConfig,
    llm_client: LLMClient,
    constraints: Optional[SolveConstraints] = None,
    router: Optional[ModelRouter] = None,
    session_journal_path: Optional[Path] = None,
) -> AgentSession:
    """Assemble and START (compose) a real session WITHOUT running it.

    The caller must explicitly call ``.run()`` / ``.step()`` to execute anything. Nothing is
    auto-run here — the first real challenge is launched manually.
    """
    if not environment.permitted_tools:
        raise ValueError(
            "refusing to prepare a real session with no trusted tools: real capability must be "
            "supplied as trusted adapters in EnvironmentConfig.permitted_tools"
        )
    urls = (spec.target,) if spec.target else ()
    challenge = ChallengeInput(
        name=spec.name, category=spec.category or None, description=spec.description or None,
        hints=tuple(spec.hints), flag_format=spec.flag_format or None, urls=urls,
        credentials=dict(spec.credentials), attempt_limit=spec.attempt_limit,
    )
    session = AgentSession(
        challenge,
        llm_client=llm_client,
        environment=environment,
        constraints=constraints or SolveConstraints(),
        resources=tuple(spec.resources),
        router=router,
        session_journal_path=session_journal_path,
    )
    session.start()  # composes the frozen pipeline; executes NOTHING until .step()/.run()
    return session


# An explicit, greppable marker that this module must never auto-run a live target.
AUTORUN_DISABLED = True
