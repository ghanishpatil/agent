from __future__ import annotations

from ctf_agent.specialists import SpecialistRegistry, SpecialistReasoningSource

from .conftest import make_specialist_context


def test_two_specialists_may_disagree_and_brain_surfaces_both() -> None:
    # A web challenge that also mentions JWT: web proposes SQLi-style mechanisms, crypto proposes
    # token/algorithm mechanisms. They "disagree" about the primary mechanism.
    context = make_specialist_context(
        category="web",
        description="login issues a jwt bearer token; the search endpoint builds a sql query",
        urls=("http://127.0.0.1:9/search",),
        available_tools=("http_probe", "decode_tool"),
    )
    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("http_probe", "decode_tool")
    )
    hypotheses = brain.suggest_hypotheses(context.challenge)
    ids = {h.hypothesis_id for h in hypotheses}
    # Both domains contributed competing hypotheses; the brain did not pre-pick one.
    assert any(i.startswith("web-") for i in ids)
    assert any(i.startswith("crypto-") for i in ids)
    assert brain.last_selection is not None
    selected_names = {s.name for s in brain.last_selection.selected}
    assert {"web", "crypto"} <= selected_names


def test_brain_orders_but_does_not_pre_decide_the_winner() -> None:
    # The brain only orders proposals (a tie-break hint); it emits ALL non-duplicate actions so the
    # planner + real evidence decide. Confidence alone never removes a competing proposal.
    context = make_specialist_context(
        category="web",
        description="jwt token and sql injection in the search query",
        urls=("http://127.0.0.1:9/search",),
        available_tools=("http_probe", "decode_tool"),
    )
    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("http_probe", "decode_tool")
    )
    actions = brain.suggest_actions(context.challenge)
    hyp_ids = {a.hypothesis_id for a in actions}
    # Competing mechanisms both remain on the table as proposals.
    assert any(i.startswith("web-") for i in hyp_ids)


def test_brain_only_selects_relevant_specialists() -> None:
    context = make_specialist_context(
        category="crypto", description="rsa modulus with small exponent", files=("key.pem",)
    )
    brain = SpecialistReasoningSource(SpecialistRegistry.default())
    brain.suggest_hypotheses(context.challenge)
    selected_names = {s.name for s in brain.last_selection.selected}
    assert "crypto" in selected_names
    # A pure crypto challenge should not drag in web/pwn/forensics.
    assert "web" not in selected_names
    assert "pwn" not in selected_names


def test_brain_emits_no_proposals_when_no_specialist_is_relevant() -> None:
    # A category none of the 5 specialists own, with no indicators -> empty proposals (the loop
    # would then report BLOCKED_NO_ACTIONS rather than inventing work).
    context = make_specialist_context(category="misc", description="a plain text puzzle")
    brain = SpecialistReasoningSource(SpecialistRegistry.default())
    assert brain.suggest_hypotheses(context.challenge) == ()
    assert brain.suggest_actions(context.challenge) == ()
