from __future__ import annotations

from ctf_agent.specialists import SpecialistRegistry

from .conftest import make_specialist_context


def _selected_names(context) -> set[str]:
    registry = SpecialistRegistry.default()
    return {s.name for s in registry.select(context).selected}


def test_web_challenge_selects_web_specialist() -> None:
    context = make_specialist_context(
        category="web",
        description="a search endpoint with an id parameter that builds a SQL query",
        urls=("http://127.0.0.1:9/search",),
    )
    selected = _selected_names(context)
    assert "web" in selected


def test_pure_web_challenge_does_not_invoke_every_specialist() -> None:
    context = make_specialist_context(
        category="web",
        description="a login form with a search box",
        urls=("http://127.0.0.1:9/search",),
    )
    selected = _selected_names(context)
    # Web is relevant; pwn/forensics/reverse are not for a plain web challenge.
    assert "web" in selected
    assert "pwn" not in selected
    assert "forensics" not in selected
    assert "reverse" not in selected


def test_jwt_web_challenge_selects_web_and_crypto() -> None:
    context = make_specialist_context(
        category="web",
        description="the app authenticates with a JWT bearer token in the Authorization header",
        urls=("http://127.0.0.1:9/api",),
    )
    selected = _selected_names(context)
    assert "web" in selected
    assert "crypto" in selected  # JWT is a cross-domain crypto indicator


def test_crypto_challenge_selects_crypto_specialist() -> None:
    context = make_specialist_context(
        category="crypto", description="an RSA modulus with a suspiciously small public exponent"
    )
    selected = _selected_names(context)
    assert "crypto" in selected
    assert "web" not in selected


def test_reverse_challenge_maps_rev_category() -> None:
    context = make_specialist_context(
        category="rev", description="an ELF crackme that validates a serial key", files=("crackme",)
    )
    selected = _selected_names(context)
    assert "reverse" in selected


def test_forensics_challenge_selects_forensics_specialist() -> None:
    context = make_specialist_context(
        category="forensics",
        description="a PNG with suspicious appended data after the trailer",
        files=("image.png",),
    )
    selected = _selected_names(context)
    assert "forensics" in selected


def test_pwn_challenge_selects_pwn_specialist() -> None:
    context = make_specialist_context(
        category="pwn", description="a binary using gets() into a fixed stack buffer", files=("vuln",)
    )
    selected = _selected_names(context)
    assert "pwn" in selected


def test_selection_is_ordered_by_relevance() -> None:
    context = make_specialist_context(
        category="web",
        description="jwt token and sql injection in the search query",
        urls=("http://127.0.0.1:9/search",),
    )
    registry = SpecialistRegistry.default()
    selection = registry.select(context)
    relevances = [rel for _name, rel in selection.scored]
    assert relevances == sorted(relevances, reverse=True)
    # The scored list covers every candidate specialist, selected or not.
    assert len(selection.scored) == len(registry.names())
