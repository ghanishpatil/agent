"""Runtime session journal — proves a real solve actually went through the architecture.

This is ADDITIVE and separate from the frozen loop's own ``RuntimeJournal`` (which the loop still
writes). It composes, per executed pipeline step, the model/routing fields (which the frozen loop
does not know about) with the pipeline facts (hypothesis, fingerprint, decision, adapter,
classification, evidence, impact, verification) read back from the ``PipelineResult``.

Required fields (all present per record):
  timestamp, challenge_id, model, reasoning_source, hypothesis_id, hypothesis_state, proposal_id,
  action_fingerprint, planner_decision, execution_adapter, observation_class, evidence_id, impact,
  verification_state, escalation_reason
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ctf_agent.deduplication import fingerprint_action
from ctf_agent.kernel import PipelineResult


@dataclass
class RuntimeSessionJournal:
    path: Optional[Path]
    challenge_id: str
    reasoning_source: str = "LLMReasoningSource(base=SpecialistReasoningSource)"
    records: List[dict] = field(default_factory=list)

    def record_step(
        self,
        *,
        pipeline_result: PipelineResult,
        model: str,
        escalation_reason: str,
        timestamp: str,
    ) -> dict:
        pr = pipeline_result
        rec = {
            "timestamp": timestamp,
            "challenge_id": self.challenge_id,
            "model": model,
            "reasoning_source": self.reasoning_source,
            "hypothesis_id": pr.hypothesis.hypothesis_id if pr.hypothesis else None,
            "hypothesis_state": pr.hypothesis.status.value if pr.hypothesis else None,
            "proposal_id": pr.action.action_id,
            "action_fingerprint": fingerprint_action(pr.action),
            "planner_decision": pr.decision.value,
            "execution_adapter": pr.action.tool,
            "observation_class": pr.classification.result_class.value if pr.classification else None,
            "evidence_id": pr.evidence.evidence_id if pr.evidence else None,
            "impact": pr.impact.value,
            "verification_state": (
                pr.verification.candidate.verification_status.value
                if pr.verification is not None and pr.verification.candidate is not None
                else None
            ),
            "escalation_reason": escalation_reason,
        }
        self.records.append(rec)
        self._append(rec)
        return rec

    def _append(self, rec: dict) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(rec, sort_keys=True) + "\n")
