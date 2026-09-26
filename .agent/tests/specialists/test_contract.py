from __future__ import annotations

import pytest

from ctf_agent.specialists import (
    CryptoSpecialist,
    ForensicsSpecialist,
    PwnSpecialist,
    ReverseSpecialist,
    SpecialistAnalysis,
    SpecialistError,
    WebSpecialist,
    validate_specialist_analysis,
)
from ctf_agent.specialists.base import (
    CandidateAction,
    SpecialistHypothesis,
    analysis_to_suggestions,
)

from .conftest import make_specialist_context


ALL_SPECIALISTS = [
    (WebSpecialist(), "web"),
    (CryptoSpecialist(), "crypto"),
    (ReverseSpecialist(), "reverse"),
    (ForensicsSpecialist(), "forensics"),
    (PwnSpecialist(), "pwn"),
]


@pytest.mark.parametrize("specialist,category", ALL_SPECIALISTS)
def test_specialist_produces_valid_structured_analysis(specialist, category) -> None:
    context = make_specialist_context(
        category=category if category != "reverse" else "rev",
        description="sql injection xor rsa strings overflow exif trailer template",
        files=("artifact.bin",),
        urls=("http://127.0.0.1:9/search",),
    )
    analysis = specialist.analyze(context)
    assert isinstance(analysis, SpecialistAnalysis)
    assert analysis.specialist == specialist.name
    # Structured, not free-form: any actionable info is typed.
    assert validate_specialist_analysis(analysis) is analysis
    for action in analysis.candidate_actions:
        assert isinstance(action, CandidateAction)
        assert action.tool and action.objective and action.target
    for hypothesis in analysis.hypotheses:
        assert isinstance(hypothesis, SpecialistHypothesis)


def test_analysis_converts_to_phase3_suggestions() -> None:
    context = make_specialist_context(
        category="crypto", description="the file is an xor-encoded cipher", files=("h.bin",)
    )
    analysis = CryptoSpecialist().analyze(context)
    hypotheses, actions = analysis_to_suggestions(analysis)
    assert hypotheses  # crypto proposes at least one hypothesis
    assert all(h.hypothesis_id for h in hypotheses)
    assert all(a.tool and a.objective for a in actions)


def test_validate_rejects_forbidden_state_assertion() -> None:
    bad = SpecialistAnalysis(
        specialist="web",
        category="web",
        relevance=0.5,
        reasoning_summary="we should mark disproven the sqli idea",
    )
    with pytest.raises(SpecialistError, match="state transition"):
        validate_specialist_analysis(bad)


def test_validate_rejects_terminal_state_hypothesis() -> None:
    bad = SpecialistAnalysis(
        specialist="web",
        category="web",
        relevance=0.5,
        hypotheses=(
            SpecialistHypothesis(
                hypothesis_id="web-sqli",
                statement="sqli exists",
                mechanism="sqli",
                technique="sqli",
                fact_state="VERIFIED",
            ),
        ),
    )
    with pytest.raises(SpecialistError, match="terminal state"):
        validate_specialist_analysis(bad)


def test_validate_rejects_missing_required_fields() -> None:
    bad = SpecialistAnalysis(
        specialist="web",
        category="web",
        relevance=0.5,
        candidate_actions=(
            CandidateAction(hypothesis_id="web-sqli", objective="", tool="http_probe", target="x"),
        ),
    )
    with pytest.raises(SpecialistError, match="objective"):
        validate_specialist_analysis(bad)


def test_validate_rejects_out_of_range_relevance() -> None:
    bad = SpecialistAnalysis(specialist="web", category="web", relevance=1.5)
    with pytest.raises(SpecialistError, match="relevance"):
        validate_specialist_analysis(bad)


def test_validate_rejects_invalid_fact_state() -> None:
    bad = SpecialistAnalysis(
        specialist="web",
        category="web",
        relevance=0.5,
        hypotheses=(
            SpecialistHypothesis(
                hypothesis_id="web-sqli",
                statement="sqli",
                mechanism="sqli",
                technique="sqli",
                fact_state="MAYBE",
            ),
        ),
    )
    with pytest.raises(SpecialistError, match="fact_state"):
        validate_specialist_analysis(bad)
