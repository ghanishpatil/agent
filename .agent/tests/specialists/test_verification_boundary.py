from __future__ import annotations

import inspect

from ctf_agent.specialists import (
    CryptoSpecialist,
    ForensicsSpecialist,
    PwnSpecialist,
    ReverseSpecialist,
    WebSpecialist,
)
from ctf_agent.specialists.base import analysis_to_suggestions

from .conftest import make_specialist_context


ALL = [WebSpecialist, CryptoSpecialist, ReverseSpecialist, ForensicsSpecialist, PwnSpecialist]


def test_specialist_modules_never_reference_kernel_or_evidence_types() -> None:
    """Architectural: no specialist module imports/uses TrustKernel, EvidenceManager, or the
    verification controller -- there is no code path from a specialist to trusted state."""
    import ctf_agent.specialists.web as web
    import ctf_agent.specialists.crypto as crypto
    import ctf_agent.specialists.reverse as reverse
    import ctf_agent.specialists.forensics as forensics
    import ctf_agent.specialists.pwn as pwn

    for module in (web, crypto, reverse, forensics, pwn):
        source = inspect.getsource(module)
        for forbidden in ("TrustKernel", "EvidenceManager", "VerificationController", "kernel.process"):
            assert forbidden not in source, f"{module.__name__} references {forbidden}"


def test_specialist_output_has_no_verification_or_evidence_mutation_method() -> None:
    context = make_specialist_context(category="crypto", description="xor cipher", files=("h.bin",))
    analysis = CryptoSpecialist().analyze(context)
    # The analysis and its parts are plain data: nothing that could verify or mutate.
    for obj in (analysis, *analysis.candidate_actions, *analysis.hypotheses):
        assert not hasattr(obj, "verify")
        assert not hasattr(obj, "commit")
        assert not hasattr(obj, "record_evidence")
        assert not hasattr(obj, "mark_verified")


def test_candidate_flag_is_only_a_proposed_value_not_a_verification() -> None:
    # Even when a flag is observed, the specialist only emits an ActionSuggestion carrying
    # candidate_flag; it does not and cannot set any verification status.
    probe_url = "http://127.0.0.1:9/search?id=1%27%20OR%20%271%27%3D%271"
    from ctf_agent.models import HypothesisImpact

    context = make_specialist_context(
        category="web",
        description="search endpoint id parameter sql query",
        urls=("http://127.0.0.1:9/search",),
        available_tools=("http_probe",),
        evidence=(
            {
                "hypotheses": ("web-sqli",),
                "tool": "http_probe",
                "source": probe_url,
                "kind": "target_response",
                "response_body": "secret=CTF{x}",
                "impact": HypothesisImpact.NO_IMPACT,
            },
        ),
    )
    analysis = WebSpecialist().analyze(context)
    _hyps, actions = analysis_to_suggestions(analysis)
    submits = [a for a in actions if a.candidate_flag]
    assert submits
    submit = submits[0]
    # It is an ordinary ActionSuggestion -- no verification fields exist on it at all.
    assert submit.candidate_flag == "CTF{x}"
    assert not hasattr(submit, "verified")
    assert not hasattr(submit, "verification_status")
