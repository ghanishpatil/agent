from __future__ import annotations

import hashlib
import re
from datetime import datetime

from .deduplication import fingerprint_state
from .evidence import EvidenceManager
from .models import (
    ControlDecision,
    EvidenceOrigin,
    FlagAttempt,
    FlagCandidate,
    Freshness,
    RelevantState,
    ResultClass,
    VerificationDecision,
    VerificationMethod,
    VerificationPolicy,
    VerificationStatus,
)


_ELIGIBLE_VERIFICATION_RESULTS = {
    ResultClass.SUCCESS,
    ResultClass.TARGET_RESPONSE,
    ResultClass.STATE_CHANGE,
}


_DETERMINISTIC_METHODS = {
    VerificationMethod.DETERMINISTIC_DERIVATION.value,
    VerificationMethod.CRYPTOGRAPHIC_PROOF.value,
    VerificationMethod.GRADING_LOGIC.value,
    VerificationMethod.CHALLENGE_SPECIFIC_SELF_CHECK.value,
}


def _output_contains_exact_candidate(output: str, candidate: str) -> bool:
    pattern = rf"(?<![\w{{]){re.escape(candidate)}(?![\w}}])"
    return re.search(pattern, output, flags=re.UNICODE) is not None


def _candidate_with(
    candidate: FlagCandidate,
    *,
    status: VerificationStatus,
    evidence_ids: tuple[str, ...],
    verified_at: datetime | None = None,
    rejection_reason: str | None = None,
) -> FlagCandidate:
    updated = FlagCandidate(candidate.value, candidate.source)
    object.__setattr__(updated, "supporting_evidence", evidence_ids)
    object.__setattr__(updated, "verification_status", status)
    object.__setattr__(updated, "attempts", candidate.attempts)
    object.__setattr__(updated, "verified_at", verified_at)
    object.__setattr__(updated, "rejection_reason", rejection_reason)
    return updated


class VerificationController:
    """Derive verification only from current evidence produced by trusted tool adapters."""

    def __init__(self, evidence: EvidenceManager, policy: VerificationPolicy) -> None:
        self._evidence = evidence
        self._policy = policy

    def evaluate(
        self,
        candidate: FlagCandidate,
        evidence_ids: tuple[str, ...],
    ) -> VerificationDecision:
        records = tuple(self._evidence.get(evidence_id) for evidence_id in evidence_ids)
        if any(
            record.provenance.origin is not EvidenceOrigin.CURRENT_OBSERVATION
            or record.freshness is not Freshness.CURRENT
            for record in records
        ):
            invalid = _candidate_with(
                candidate,
                status=VerificationStatus.INVALID,
                evidence_ids=evidence_ids,
            )
            return VerificationDecision(
                invalid, ControlDecision.CONTINUE, "Verification requires current evidence"
            )

        rejection = self._verifier_rejection(candidate, records)
        if rejection:
            rejected = _candidate_with(
                candidate,
                status=VerificationStatus.REJECTED,
                evidence_ids=evidence_ids,
                rejection_reason=rejection,
            )
            return VerificationDecision(
                rejected, ControlDecision.CONTINUE, "Trusted verifier rejected candidate"
            )

        verified_at = self._verified_at(candidate, records)
        if verified_at is not None:
            verified = _candidate_with(
                candidate,
                status=VerificationStatus.VERIFIED,
                evidence_ids=evidence_ids,
                verified_at=verified_at,
            )
            return VerificationDecision(
                verified, ControlDecision.STOP, "Minimum sufficient verification achieved"
            )

        status = VerificationStatus.SUPPORTED if records else VerificationStatus.CANDIDATE
        updated = _candidate_with(candidate, status=status, evidence_ids=evidence_ids)
        return VerificationDecision(
            updated, ControlDecision.CONTINUE, "Verification evidence insufficient"
        )

    def _verifier_rejection(self, candidate: FlagCandidate, records) -> str | None:
        for record in records:
            if record.result_class not in _ELIGIBLE_VERIFICATION_RESULTS:
                continue
            execution = record.observation.execution
            if execution.tool not in self._policy.verifier_tools:
                continue
            metadata = execution.metadata
            if metadata.get("submitted_candidate") != candidate.value:
                continue
            if metadata.get("verifier_accepted") is False:
                return str(metadata.get("rejection_reason") or "rejected")
        return None

    def _verified_at(self, candidate: FlagCandidate, records) -> datetime | None:
        for record in records:
            if record.result_class not in _ELIGIBLE_VERIFICATION_RESULTS:
                continue
            execution = record.observation.execution
            output = "\n".join((execution.stdout, execution.response_body))
            if (
                execution.tool in self._policy.authoritative_output_tools
                and _output_contains_exact_candidate(output, candidate.value)
            ):
                return record.timestamp

            metadata = execution.metadata
            if (
                execution.tool in self._policy.verifier_tools
                and metadata.get("submitted_candidate") == candidate.value
                and metadata.get("verifier_accepted") is True
            ):
                return record.timestamp

            if execution.tool not in self._policy.deterministic_tools:
                continue
            if metadata.get("verified_candidate") != candidate.value:
                continue
            if metadata.get("verification_passed") is not True:
                continue
            if metadata.get("verification_method") not in _DETERMINISTIC_METHODS:
                continue
            if not str(metadata.get("verification_basis") or "").strip():
                continue
            return record.timestamp
        return None


class FlagAttemptRegistry:
    def __init__(self, evidence: EvidenceManager) -> None:
        self._evidence = evidence
        self._seen: set[str] = set()
        self._attempts: list[FlagAttempt] = []

    @property
    def attempts(self) -> tuple[FlagAttempt, ...]:
        return tuple(self._attempts)

    @staticmethod
    def _fingerprint(
        candidate: FlagCandidate,
        verifier: str,
        evidence_ids: tuple[str, ...],
        state: RelevantState,
    ) -> str:
        identity = "\x1f".join(
            (candidate.value, verifier, fingerprint_state(state), *sorted(evidence_ids))
        )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    def check_and_record(
        self,
        candidate: FlagCandidate,
        verifier: str,
        evidence_ids: tuple[str, ...],
        state: RelevantState,
        attempted_at: datetime,
    ) -> ControlDecision:
        if not evidence_ids:
            raise ValueError("flag attempts require non-empty evidence")
        for evidence_id in evidence_ids:
            record = self._evidence.get(evidence_id)
            if (
                record.provenance.origin is not EvidenceOrigin.CURRENT_OBSERVATION
                or record.freshness is not Freshness.CURRENT
            ):
                raise ValueError("flag attempts require current evidence")
            execution = record.observation.execution
            output = "\n".join((execution.stdout, execution.response_body))
            candidate_fields = {
                execution.metadata.get("verified_candidate"),
                execution.metadata.get("submitted_candidate"),
            }
            if (
                not _output_contains_exact_candidate(output, candidate.value)
                and candidate.value not in candidate_fields
            ):
                raise ValueError("evidence is not bound to the candidate")
        fingerprint = self._fingerprint(candidate, verifier, evidence_ids, state)
        if fingerprint in self._seen:
            return ControlDecision.DUPLICATE
        self._seen.add(fingerprint)
        self._attempts.append(
            FlagAttempt(
                candidate.value,
                verifier,
                evidence_ids,
                fingerprint_state(state),
                attempted_at,
                candidate.source,
            )
        )
        return ControlDecision.ALLOWED
