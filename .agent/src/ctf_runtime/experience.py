"""Success/failure experience extraction — grounded in the authoritative SolveResult + journals.

Every field is derived from runtime traces; nothing is invented. Failure classification is read
straight from the runtime (ResultClass / hypothesis status), so environmental/tool/rate-limit
failures are NEVER recorded as technique disproof, and unresolved hypotheses stay unresolved.
Only an authoritative DISPROVEN hypothesis status produces a "disproven" conclusion.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from ctf_agent.autonomy.contracts import SolveResult, SolveStatus

from .experience_store import (
    SOURCE_FAILURE,
    SOURCE_SUCCESS,
    ExperienceProvenance,
    ExperienceRecord,
)

_FAILURE_CLASSES = {
    "RATE_LIMIT", "TIMEOUT", "NETWORK_FAILURE", "TOOL_FAILURE", "ENVIRONMENT_FAILURE",
    "AUTH_FAILURE", "AUTHZ_FAILURE", "INPUT_REJECTION",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_id(source_kind: str, run_id: str, seed: str) -> str:
    h = hashlib.sha256((source_kind + run_id + seed).encode("utf-8")).hexdigest()[:12]
    tag = "success" if source_kind == SOURCE_SUCCESS else "failure"
    return f"exp-{tag}-{run_id}-{h}"


def _common(result: SolveResult, session_journal: Sequence[Dict[str, Any]],
            observations: Sequence[Dict[str, Any]]):
    hyps = [{"id": h.hypothesis_id, "statement": h.statement, "status": h.status}
            for h in result.key_hypotheses]
    transitions, seen = [], set()
    for j in session_journal:
        hid, state, impact = j.get("hypothesis_id"), j.get("hypothesis_state"), j.get("impact")
        if hid and state and (hid, state, impact) not in seen:
            seen.add((hid, state, impact))
            transitions.append({"hypothesis_id": hid, "to": state, "impact": impact})
    tests, successful, dead = [], [], []
    failure_classes = set()
    for a in result.actions:
        entry = {"tool": a.tool, "target": a.target, "objective": a.objective,
                 "result_class": a.result_class, "impact": a.impact}
        if a.result_class in _FAILURE_CLASSES:
            failure_classes.add(a.result_class)
            dead.append(entry)
        else:
            tests.append(entry)
            if a.result_class in ("SUCCESS", "TARGET_RESPONSE", "STATE_CHANGE"):
                successful.append(entry)
    for e in result.important_evidence:
        if e.result_class in _FAILURE_CLASSES:
            failure_classes.add(e.result_class)
    useful_obs = [{"source": o.get("source", ""), "result_class": o.get("result_class", ""),
                   "snippet": str(o.get("output", ""))[:200]} for o in observations][-5:]
    disproven = tuple(h.hypothesis_id for h in result.key_hypotheses if h.status == "DISPROVEN")
    unresolved = tuple(h.hypothesis_id for h in result.key_hypotheses if h.status == "UNRESOLVED")
    unresolved = unresolved + tuple(x for x in result.remaining_hypotheses if x not in unresolved)
    evidence_refs = tuple(dict.fromkeys(
        list(result.verification_evidence_ids) + [e.evidence_id for e in result.important_evidence]))
    supported = [h for h in result.key_hypotheses if h.status == "SUPPORTED"]
    mechanism = supported[0].statement if supported else ""
    techniques = tuple(sorted({a["tool"] for a in successful})) if successful else ()
    preconditions = tuple(result.understanding.constraints) if result.understanding else ()
    return dict(
        hypotheses=tuple(hyps), hypothesis_transitions=tuple(transitions),
        discriminating_tests=tuple(tests), successful_actions=tuple(successful),
        dead_end_actions=tuple(dead), failure_classes=tuple(sorted(failure_classes)),
        useful_observations=tuple(useful_obs), evidence_refs=evidence_refs,
        disproven=disproven, unresolved=unresolved,
        unresolved_blockers=tuple(result.unresolved_blockers),
        mechanism=mechanism, techniques=techniques, preconditions=preconditions,
    )


def extract_success_experience(
    result: SolveResult, *, session_id: str, driver: str,
    session_journal: Sequence[Dict[str, Any]] = (), observations: Sequence[Dict[str, Any]] = (),
    writeup_ref: str = "", writeup_grounded: Optional[bool] = None,
) -> ExperienceRecord:
    if result.status is not SolveStatus.SOLVED:
        raise ValueError("extract_success_experience requires a SOLVED result")
    c = _common(result, session_journal, observations)
    prov = ExperienceProvenance(
        run_id=result.run_id, session_id=session_id, driver=driver, source_kind=SOURCE_SUCCESS,
        journal_path=result.journal_path, verification_evidence_ids=tuple(result.verification_evidence_ids),
        generated_at=_now(),
    )
    return ExperienceRecord(
        record_id=_record_id(SOURCE_SUCCESS, result.run_id, result.verified_flag or ""),
        source_kind=SOURCE_SUCCESS, status=result.status.value, provenance=prov,
        challenge_name=result.challenge_name, category=(result.understanding.likely_categories[0]
                                                        if result.understanding and result.understanding.likely_categories else ""),
        verification_method=result.final_verification_method or "",
        solution_path=result.solution_path_summary or "",
        verified_flag=result.verified_flag, writeup_ref=writeup_ref, writeup_grounded=writeup_grounded,
        **c,
    )


def extract_failure_experience(
    result: SolveResult, *, session_id: str, driver: str,
    session_journal: Sequence[Dict[str, Any]] = (), observations: Sequence[Dict[str, Any]] = (),
) -> ExperienceRecord:
    if result.status is SolveStatus.SOLVED:
        raise ValueError("extract_failure_experience must not be used for a SOLVED result")
    c = _common(result, session_journal, observations)
    prov = ExperienceProvenance(
        run_id=result.run_id, session_id=session_id, driver=driver, source_kind=SOURCE_FAILURE,
        journal_path=result.journal_path, verification_evidence_ids=(), generated_at=_now(),
    )
    return ExperienceRecord(
        record_id=_record_id(SOURCE_FAILURE, result.run_id, result.terminal_reason or result.status.value),
        source_kind=SOURCE_FAILURE, status=result.status.value, provenance=prov,
        challenge_name=result.challenge_name,
        category=(result.understanding.likely_categories[0]
                  if result.understanding and result.understanding.likely_categories else ""),
        terminal_reason=result.terminal_reason or "",
        verification_method="", solution_path="", verified_flag=None,  # never a flag on failure
        **c,
    )
