from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from ..context import FactState
from ..models import ResultClass
from .base import (
    CandidateAction,
    CandidateMechanism,
    RecommendedTest,
    SpecialistAnalysis,
    SpecialistContext,
    SpecialistHypothesis,
    build_submit_actions,
    current_hypothesis_state,
    mechanism_blocked_by_failure,
    preferred_tools,
    score_relevance,
)


@dataclass(frozen=True)
class _CryptoMechanism:
    suffix: str
    name: str
    technique: str
    indicators: Tuple[str, ...]
    mode: str  # the analysis-tool mode arg this mechanism's probe would run
    expected_supporting: str
    expected_contradicting: str
    cost: int


# Mechanism-first: distinguishing encoding-vs-encryption-vs-cipher IS the discriminating work.
# Base64 (an ENCODING, the common wrong first guess) is listed first so it is tested and
# potentially disproven before the more specific XOR/RSA mechanisms.
_MECHANISMS: Tuple[_CryptoMechanism, ...] = (
    _CryptoMechanism(
        "base64", "base64 encoding", "encoding-base64",
        ("base64", "b64", "encoded", "encoding", "cipher", "encrypt", "decode"),
        "base64",
        "decodes to a valid flag-format string",
        "decode fails or yields non-flag bytes (encoding hypothesis weakened, NOT the challenge)",
        1,
    ),
    _CryptoMechanism(
        "xor", "single-byte XOR", "xor-single-byte",
        ("xor", "cipher", "encrypt", "key", "encoded", "stream"),
        "xor42",
        "XOR with the recovered key yields a valid flag-format string",
        "no single-byte key yields readable text",
        2,
    ),
    _CryptoMechanism(
        "rsa", "RSA weakness (small e / shared factor / etc.)", "rsa-key-recovery",
        ("rsa", "modulus", "public key", "n =", "e =", "factor", "totient"),
        "rsa",
        "the modulus factors / small-e root gives plaintext",
        "modulus resists the attempted structural weakness",
        3,
    ),
    _CryptoMechanism(
        "classical", "classical substitution/transposition", "classical-cipher",
        ("caesar", "rot", "vigenere", "substitution", "transposition", "shift"),
        "classical",
        "frequency analysis / shift search yields readable plaintext",
        "no shift/key yields readable plaintext",
        2,
    ),
    _CryptoMechanism(
        "jwt", "JWT signature / algorithm-confusion weakness", "jwt-signature",
        ("jwt", "token", "bearer", "algorithm confusion", "hs256", "rs256", "alg", "signature"),
        "jwt",
        "a forged token with alg=none or key-confusion is accepted",
        "the server enforces the expected signature algorithm and rejects forgeries",
        2,
    ),
)


class CryptoSpecialist:
    name = "crypto"
    category = "crypto"

    def relevance(self, context: SpecialistContext) -> float:
        indicators = tuple(kw for mech in _MECHANISMS for kw in mech.indicators) + (
            "crypto",
            "jwt",
            "token",
            "hash",
            "nonce",
            "iv",
            "padding",
            "signature",
        )
        base = score_relevance(context, self.category, indicators)
        # JWT / token signing is a strong cross-domain crypto signal even on a web challenge:
        # bump so the brain consults crypto alongside web when a token appears.
        corpus = context.indicator_corpus()
        if any(k in corpus for k in ("jwt", "json web token", "algorithm confusion", "hs256", "rs256")):
            base = round(min(1.0, base + 0.35), 4)
        return base

    def analyze(self, context: SpecialistContext) -> SpecialistAnalysis:
        corpus = context.indicator_corpus()
        tool = _decode_tool(context)
        target = context.challenge.metadata.files[0] if context.challenge.metadata.files else ""

        mechanisms: list[CandidateMechanism] = []
        hypotheses: list[SpecialistHypothesis] = []
        actions: list[CandidateAction] = []
        recommended: list[RecommendedTest] = []
        observations: list[str] = []

        for mech in _MECHANISMS:
            if not any(ind in corpus for ind in mech.indicators):
                continue
            hyp_id = f"crypto-{mech.suffix}"
            state = current_hypothesis_state(context, hyp_id)
            if state == FactState.DISPROVEN.value:
                # The kernel already disproved this mechanism from evidence; stop re-proposing it
                # (anti-spray). Reflecting the board's terminal state is not the specialist
                # asserting disproof -- it simply closes this branch and moves on.
                observations.append(f"{mech.name}: DISPROVEN by prior evidence; branch closed")
                continue
            blockers = mechanism_blocked_by_failure(context, hyp_id)
            if blockers:
                state = FactState.BLOCKED.value if state == FactState.UNRESOLVED.value else state
                observations.append(
                    f"{mech.name}: prior attempt blocked by {', '.join(b.value for b in blockers)};"
                    " tool/environment failure is not cryptographic disproof"
                )

            mechanisms.append(
                CandidateMechanism(
                    name=mech.name,
                    description=f"structural hypothesis: artifact is {mech.name}",
                    fact_state=state,
                    rationale=f"indicators for {mech.name} present in challenge/evidence",
                )
            )
            hypotheses.append(
                SpecialistHypothesis(
                    hypothesis_id=hyp_id,
                    statement=f"The ciphertext/artifact is {mech.name}",
                    mechanism=mech.name,
                    technique=mech.technique,
                    fact_state=state,
                )
            )
            recommended.append(
                RecommendedTest(
                    objective=f"attempt {mech.name} decode",
                    description=(
                        f"run the decode tool in '{mech.mode}' mode and check whether the output "
                        "is a valid flag-format string (structure -> weakness -> derive -> test)"
                    ),
                    expected_supporting_observation=mech.expected_supporting,
                    expected_contradicting_observation=mech.expected_contradicting,
                    blocked_by_failures=(ResultClass.TOOL_FAILURE, ResultClass.ENVIRONMENT_FAILURE),
                )
            )
            if target and tool:
                actions.append(
                    CandidateAction(
                        hypothesis_id=hyp_id,
                        objective=f"attempt {mech.name} decode of the artifact",
                        tool=tool,
                        target=target,
                        input_data=[mech.mode, target],
                        expected_observation=mech.expected_supporting,
                        estimated_cost=mech.cost,
                        reasoning=(
                            f"mechanism-first: test {mech.name} with a single deterministic decode; "
                            "a decode failure weakens THIS mechanism, it does not disprove others"
                        ),
                    )
                )

        actions.extend(build_submit_actions(tuple(actions), context))

        relevance = self.relevance(context)
        return SpecialistAnalysis(
            specialist=self.name,
            category=self.category,
            relevance=relevance,
            observations=tuple(observations),
            candidate_mechanisms=tuple(mechanisms),
            hypotheses=tuple(hypotheses),
            recommended_tests=tuple(recommended),
            candidate_actions=tuple(actions),
            required_tools=(tool,) if tool else (),
            expected_observations=tuple(m.expected_supporting for m in _MECHANISMS),
            confidence=min(1.0, relevance),
            reasoning_summary=(
                "Reasoned from artifact structure to candidate cryptographic mechanisms, testing "
                "the cheaper encoding hypothesis before more specific cipher weaknesses. No "
                "parameter is brute-forced without a structural reason, and a failed decode weakens "
                "only the mechanism it tested."
            ),
            uncertainty=(
                "The exact cipher is not yet determined; competing mechanisms are resolved by "
                "which decode actually yields flag-format plaintext."
            ),
            applicable_techniques=tuple(m.technique for m in _MECHANISMS),
            relevant_memory_refs=context.memory_refs(
                self.category, ("xor", "rsa", "base64", "cipher", "nonce")
            ),
        )


def _decode_tool(context: SpecialistContext) -> str:
    tools = preferred_tools(context, ("decode_tool",))
    for preferred in ("decode_tool", "crypto_tool"):
        if preferred in tools:
            return preferred
    return tools[0] if tools else "decode_tool"
