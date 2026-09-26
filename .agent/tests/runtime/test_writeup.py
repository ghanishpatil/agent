"""Auto-Writeup + grounding-validator tests (checklist items 1-11).

These are pure unit tests over synthetic ``SolveResult`` projections (no gateway, no network, no
model). They pin the hard writeup rules: SOLVED-only, verbatim flag, omitted-when-unsupported
sections, correctly-labelled dead ends, and a grounding validator that rejects any claim not backed
by the authoritative trajectory.
"""

from __future__ import annotations

from ctf_agent.autonomy.contracts import (
    ActionTrace,
    ChallengeUnderstanding,
    EvidenceTrace,
    HypothesisTrace,
    InputFact,
    InputFactState,
    SolveResult,
    SolveStatus,
)
from ctf_runtime.writeup import generate_writeup, validate_writeup

FLAG = "CTF{grounded_writeup}"
SSTI_URL = "http://127.0.0.1:9/render"


def _understanding(*, description="A server-side rendered page.", categories=("web",),
                   surfaces=("name parameter",), constraints=()):
    facts = ()
    if description:
        facts = (InputFact("description", description, InputFactState.KNOWN, "challenge"),)
    return ChallengeUnderstanding(
        facts=facts, likely_categories=tuple(categories), attack_surfaces=tuple(surfaces),
        unknowns=(), constraints=tuple(constraints),
    )


def _solved(**overrides):
    base = dict(
        status=SolveStatus.SOLVED, run_id="run-1", challenge_name="Render Me",
        understanding=_understanding(),
        terminal_reason="flag verified",
        verified_flag=FLAG,
        verification_evidence_ids=("ev-2",),
        final_verification_method="local-grader",
        solution_path_summary="SSTI on name -> read flag",
        actions=(
            ActionTrace("a1", "probe {{7*7}}", "http_probe", SSTI_URL, "TARGET_RESPONSE", "SUPPORTS", "CONTINUE", 1),
        ),
        key_hypotheses=(
            HypothesisTrace("web-ssti", "name is evaluated by a server-side template", "SUPPORTED",
                            ("ev-1",), (), (), 1),
        ),
        important_evidence=(
            EvidenceTrace("ev-1", SSTI_URL, "TARGET_RESPONSE", "SUPPORTS", ("web-ssti",), "http_probe"),
        ),
    )
    base.update(overrides)
    return SolveResult(**base)


def _observations(flag=FLAG):
    return [{"source": SSTI_URL, "result_class": "TARGET_RESPONSE",
             "output": f"EVAL=49 rendered output; flag={flag}"}]


# 1 — writeup is produced ONLY for a SOLVED result.
def test_writeup_only_for_solved():
    blocked = SolveResult(
        status=SolveStatus.BLOCKED, run_id="r", challenge_name="c",
        understanding=_understanding(), terminal_reason="stuck",
    )
    out = generate_writeup(blocked)
    assert out.markdown == "" and out.grounded is False and out.flag is None


# 2 — the flag is copied verbatim from SolveResult.verified_flag.
def test_flag_copied_verbatim():
    out = generate_writeup(_solved(), (), _observations())
    assert out.flag == FLAG


# 3 — the ## Flag section contains exactly the verified flag.
def test_flag_section_equals_verified_flag():
    out = generate_writeup(_solved(), (), _observations())
    assert f"## Flag\n`{FLAG}`" in out.markdown


# 4 — sections with no support are omitted.
def test_unsupported_sections_omitted():
    r = _solved(understanding=_understanding(description="", surfaces=(), categories=()),
                key_hypotheses=())
    out = generate_writeup(r, (), _observations())
    assert "## Description" not in out.markdown        # no description fact
    assert "## Hypothesis" not in out.markdown          # no supported hypotheses
    assert "## Initial Analysis" not in out.markdown    # no surfaces/categories
    assert out.grounded is True


# 5 — Enumeration lists executed non-failure actions with tool/target.
def test_enumeration_lists_executed_actions():
    out = generate_writeup(_solved(), (), _observations())
    assert "## Enumeration" in out.markdown
    assert "`http_probe` on `%s`" % SSTI_URL in out.markdown


# 6 — Hypothesis section lists supported hypotheses only.
def test_hypothesis_section_lists_supported():
    r = _solved(key_hypotheses=(
        HypothesisTrace("h1", "supported idea", "SUPPORTED", ("ev-1",), (), (), 1),
        HypothesisTrace("h2", "unresolved idea", "UNRESOLVED", (), (), ("ev-x",), 2),
    ))
    out = generate_writeup(r, (), _observations())
    assert "supported idea" in out.markdown
    # unresolved statement must NOT appear under Hypothesis (only under Dead Ends)
    hyp_section = out.markdown.split("## Hypothesis")[1].split("##")[0]
    assert "unresolved idea" not in hyp_section


# 7 — Exploitation references grounded tool/target + a grounded flag snippet.
def test_exploitation_grounded_snippet():
    out = generate_writeup(_solved(), (), _observations())
    assert "## Exploitation" in out.markdown
    assert "I ran `http_probe` against `%s`" % SSTI_URL in out.markdown
    assert "contained the flag" in out.markdown


# 8 — Dead Ends label failures as non-disproof, and preserve disproven/unresolved distinctions.
def test_dead_ends_labeling():
    r = _solved(
        actions=(
            ActionTrace("a1", "probe", "http_probe", SSTI_URL, "TARGET_RESPONSE", "SUPPORTS", "CONTINUE", 1),
            ActionTrace("a2", "brute login", "http_probe", "http://127.0.0.1:9/login", "RATE_LIMIT",
                        "UNRESOLVES", "CONTINUE", 1),
        ),
        key_hypotheses=(
            HypothesisTrace("web-ssti", "ssti", "SUPPORTED", ("ev-1",), (), (), 1),
            HypothesisTrace("h-sqli", "login is sql-injectable", "DISPROVEN", (), ("ev-3",), (), 2),
            HypothesisTrace("h-jwt", "jwt is forgeable", "UNRESOLVED", (), (), ("ev-4",), 3),
        ),
    )
    out = generate_writeup(r, (), _observations())
    dead = out.markdown.split("## Dead Ends")[1]
    assert "was rate-limited" in dead and "not a disproof" in dead
    assert "was disproven by authoritative evidence" in dead
    assert "remained unresolved" in dead
    assert out.grounded is True


# 9 — Verification section reflects method + evidence count.
def test_verification_section():
    out = generate_writeup(_solved(), (), _observations())
    assert "## Verification" in out.markdown
    assert "local-grader" in out.markdown
    assert "bound to 1 evidence record" in out.markdown


# 10 — the generated writeup validates as grounded (no errors).
def test_generated_writeup_is_grounded():
    r = _solved()
    out = generate_writeup(r, (), _observations())
    assert out.errors == () and out.grounded is True
    assert validate_writeup(out.markdown, r, (), _observations()) == []


# 11 — the validator catches tampering: ungrounded tool, wrong flag, ungrounded snippet.
def test_validator_catches_tampering():
    r = _solved()
    good = generate_writeup(r, (), _observations()).markdown

    # (a) inject an ungrounded tool/target claim
    tampered_tool = good + "\nI ran `nmap` against `10.0.0.1` to scan ports.\n"
    errs = validate_writeup(tampered_tool, r, (), _observations())
    assert any("ungrounded tool" in e for e in errs)

    # (b) swap the flag for a different value
    tampered_flag = good.replace(FLAG, "CTF{not_the_real_flag}")
    errs = validate_writeup(tampered_flag, r, (), _observations())
    assert any("does not equal SolveResult.verified_flag" in e for e in errs)

    # (c) claim an observation snippet that was never observed
    tampered_snip = good + "\nThe response included `SECRET_TOKEN=xyz` in the body.\n"
    errs = validate_writeup(tampered_snip, r, (), _observations())
    assert any("ungrounded observation snippet" in e for e in errs)

    # (d) validator refuses a non-SOLVED result outright
    blocked = SolveResult(status=SolveStatus.BLOCKED, run_id="r", challenge_name="c",
                          understanding=_understanding(), terminal_reason="stuck")
    assert validate_writeup(good, blocked, (), ()) == ["writeup produced for a non-SOLVED result"]
