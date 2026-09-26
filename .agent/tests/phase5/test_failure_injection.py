from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

import pytest

from ctf_agent import (
    CandidateVerifierRoute,
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    EvidenceRule,
    PermittedTool,
    ResourceKind,
    SolveConstraints,
    SolveStatus,
    solve,
)
from ctf_agent.models import Action, ExecutionResult

from .support import LocalVerifier, standard_constraints


class InjectedWebAdapter:
    name = "http_probe"

    def __init__(self, failure: str, flag: str) -> None:
        self.failure = failure
        self.flag = flag

    def execute(self, action: Action) -> ExecutionResult:
        query = parse_qs(urlsplit(action.target).query)
        if "name" in query:
            return ExecutionResult(
                action.action_id,
                action.tool,
                http_status=200,
                response_body=f"EVAL=49 {self.flag}",
            )
        return self._failure(action)

    def _failure(self, action: Action) -> ExecutionResult:
        if self.failure == "timeout":
            return ExecutionResult(action.action_id, action.tool, timed_out=True)
        if self.failure == "command":
            return ExecutionResult(action.action_id, action.tool, exit_code=3, stderr="failed")
        if self.failure == "network":
            return ExecutionResult(action.action_id, action.tool, network_state="unreachable")
        if self.failure == "429":
            return ExecutionResult(action.action_id, action.tool, http_status=429)
        if self.failure == "401":
            return ExecutionResult(action.action_id, action.tool, http_status=401)
        if self.failure == "403":
            return ExecutionResult(action.action_id, action.tool, http_status=403)
        if self.failure == "malformed":
            return ExecutionResult(action.action_id, action.tool, exit_code=0, stdout="\x00???")
        if self.failure == "unavailable":
            return ExecutionResult(action.action_id, action.tool, tool_available=False)
        if self.failure == "environment":
            return ExecutionResult(action.action_id, action.tool, environment_available=False)
        if self.failure == "contradiction":
            return ExecutionResult(
                action.action_id,
                action.tool,
                http_status=200,
                response_body="SQL_NOT_VULNERABLE",
            )
        raise AssertionError(self.failure)


def _recovering_environment(tmp_path: Path, failure: str, flag: str):
    base = "http://local.invalid/render"
    sql_payload = quote("1' OR '1'='1")
    ssti_payload = quote("{{7*7}}")
    sql_url = f"{base}?id={sql_payload}"
    ssti_url = f"{base}?name={ssti_payload}"
    probe = InjectedWebAdapter(failure, flag)
    verifier = LocalVerifier(flag)
    return EnvironmentConfig(
        permitted_tools=(
            PermittedTool(
                "http_probe",
                probe,
                authoritative_sources=(ssti_url,),
                network=True,
                remote=True,
            ),
            PermittedTool("flag_verifier", verifier, verifier=True, remote=True),
        ),
        evidence_rules=(
            EvidenceRule(
                "web-sqli",
                supporting_body_contains=("SQL_ROWS_EXPANDED",),
                contradicting_body_contains=("SQL_NOT_VULNERABLE",),
                authoritative_sources=(sql_url,),
            ),
            EvidenceRule(
                "web-ssti",
                supporting_body_contains=("EVAL=49",),
                authoritative_sources=(ssti_url,),
            ),
        ),
        verifier_route=CandidateVerifierRoute("flag_verifier", "local-grader"),
        workspace_root=tmp_path,
        journal_path=tmp_path / "journal.jsonl",
        run_id=f"inject-{failure}",
    )


@pytest.mark.parametrize(
    "failure,expected_class",
    [
        ("timeout", "TIMEOUT"),
        ("command", "TOOL_FAILURE"),
        ("network", "NETWORK_FAILURE"),
        ("429", "RATE_LIMIT"),
        ("401", "AUTH_FAILURE"),
        ("403", "AUTHZ_FAILURE"),
        ("malformed", "SUCCESS"),
        ("unavailable", "TOOL_FAILURE"),
        ("environment", "ENVIRONMENT_FAILURE"),
        ("contradiction", "TARGET_RESPONSE"),
    ],
)
def test_failure_is_diagnosed_then_alternative_mechanism_solves(
    tmp_path: Path, failure: str, expected_class: str
) -> None:
    flag = f"CTF{{recovered_{failure}}}"
    environment = _recovering_environment(tmp_path, failure, flag)
    result = solve(
        ChallengeInput(
            name=f"recovery-{failure}",
            category="web",
            description="A SQL query and server-side template name renderer share a page.",
            flag_format="CTF{...}",
            urls=("http://local.invalid/render",),
        ),
        environment=environment,
        constraints=standard_constraints(),
    )
    assert result.status is SolveStatus.SOLVED
    assert result.verified_flag == flag
    assert result.actions[0].result_class == expected_class
    assert result.actions[-1].decision == "STOP"


class CorruptedArtifactTool:
    name = "decode_tool"

    def __init__(self, flag: str) -> None:
        self.flag = flag

    def execute(self, action: Action) -> ExecutionResult:
        mode = action.input_data[0]
        if mode == "base64":
            return ExecutionResult(action.action_id, action.tool, input_rejected=True)
        if mode == "classical":
            return ExecutionResult(
                action.action_id, action.tool, exit_code=0, stdout=f"DECODE_OK:{self.flag}"
            )
        return ExecutionResult(
            action.action_id, action.tool, exit_code=0, stdout="DECODE_NOT_A_FLAG"
        )


def test_corrupted_artifact_rejects_one_path_then_recovers(tmp_path: Path) -> None:
    artifact = tmp_path / "corrupted.txt"
    artifact.write_bytes(b"\x00\xffcorrupt-shift")
    flag = "CTF{corrupt_but_classical}"
    tool = CorruptedArtifactTool(flag)
    verifier = LocalVerifier(flag)
    source = str(artifact.resolve())
    environment = EnvironmentConfig(
        permitted_tools=(
            PermittedTool("decode_tool", tool, authoritative_sources=(source,)),
            PermittedTool("flag_verifier", verifier, verifier=True),
        ),
        evidence_rules=(
            EvidenceRule(
                "crypto-base64",
                supporting_body_contains=("DECODE_OK:",),
                contradicting_body_contains=("DECODE_NOT_A_FLAG",),
                authoritative_sources=(source,),
            ),
            EvidenceRule(
                "crypto-classical",
                supporting_body_contains=("DECODE_OK:",),
                authoritative_sources=(source,),
            ),
        ),
        verifier_route=CandidateVerifierRoute("flag_verifier", "local-grader"),
        workspace_root=tmp_path / "runtime",
        journal_path=tmp_path / "runtime" / "journal.jsonl",
        run_id="corrupted",
    )
    result = solve(
        ChallengeInput(
            name="corrupted-classical",
            category="crypto",
            description="A corrupted base64-looking classical Caesar shift message.",
            flag_format="CTF{...}",
        ),
        resources=(ChallengeResource("corrupt", ResourceKind.FILE, path=artifact),),
        environment=environment,
        constraints=standard_constraints(),
    )
    assert result.status is SolveStatus.SOLVED
    assert any(action.result_class == "INPUT_REJECTION" for action in result.actions)
