"""Frozen Phase 5 benchmark: adapters, environments, and the labeled case set.

The 6 labeled cases (KNOWN / NOVEL / ADVERSARIAL / HELD_OUT) are constructed
deterministically under a caller-provided directory. No action or hypothesis sequence
is ever supplied to the solver; scenario tools/oracles only produce or verify
observations. This module must remain behaviourally frozen so the baseline and any
later augmented-knowledge run measure the identical challenges.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import parse_qs, quote, urlsplit

from ctf_agent import (
    CandidateVerifierRoute,
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    EvidenceRule,
    PermittedTool,
    ResourceKind,
    SolveConstraints,
)
from ctf_agent.adapters import SubprocessAdapter
from ctf_agent.adapters.subprocess_adapter import SubprocessCommand
from ctf_agent.autonomy.evaluation import EvaluationCase, EvaluationKind
from ctf_agent.autonomy.contracts import SolveStatus
from ctf_agent.models import Action, ExecutionResult


# --------------------------------------------------------------------------------------
# Local grading oracles and behaviour adapters (verify/produce observations only).
# --------------------------------------------------------------------------------------


class LocalVerifier:
    name = "flag_verifier"

    def __init__(self, expected: str) -> None:
        self.expected = expected
        self.calls = 0
        self.submitted = []

    def execute(self, action: Action) -> ExecutionResult:
        self.calls += 1
        candidate = (
            str(action.input_data.get("flag", ""))
            if isinstance(action.input_data, dict)
            else str(action.input_data or "")
        )
        self.submitted.append(candidate)
        accepted = candidate == self.expected
        return ExecutionResult(
            action.action_id,
            action.tool,
            exit_code=0,
            metadata={
                "submitted_candidate": candidate,
                "verifier_accepted": accepted,
                "rejection_reason": "wrong flag" if not accepted else "",
            },
        )


class SubprocessVerifierAdapter:
    """Grading oracle used by the crypto package; verifies outcomes, never picks actions."""

    def __init__(self, name: str, expected: str) -> None:
        self.name = name
        self.expected = expected
        self.calls = 0

    def execute(self, action: Action) -> ExecutionResult:
        self.calls += 1
        candidate = (
            str(action.input_data.get("flag", ""))
            if isinstance(action.input_data, dict)
            else str(action.input_data or "")
        )
        accepted = candidate == self.expected
        return ExecutionResult(
            action_id=action.action_id,
            tool=action.tool,
            exit_code=0,
            stdout="accepted" if accepted else "rejected",
            metadata={
                "submitted_candidate": candidate,
                "verifier_accepted": accepted,
                "rejection_reason": "wrong flag" if not accepted else "",
            },
        )


class WebBehaviorAdapter:
    name = "http_probe"

    def __init__(
        self,
        *,
        real_flag: str,
        decoy_flag: str = "",
        sql_environment_failure: bool = False,
    ) -> None:
        self.real_flag = real_flag
        self.decoy_flag = decoy_flag
        self.sql_environment_failure = sql_environment_failure
        self.calls = 0

    def execute(self, action: Action) -> ExecutionResult:
        self.calls += 1
        query = parse_qs(urlsplit(action.target).query)
        if "id" in query:
            if self.sql_environment_failure:
                return ExecutionResult(
                    action.action_id,
                    action.tool,
                    environment_available=False,
                    stdout=f"stale crash buffer {self.decoy_flag}" if self.decoy_flag else "",
                )
            body = "SQL_NOT_VULNERABLE"
            if self.decoy_flag:
                body += f" diagnostic-example={self.decoy_flag}"
            return ExecutionResult(
                action.action_id, action.tool, http_status=200, response_body=body
            )
        if "name" in query:
            return ExecutionResult(
                action.action_id,
                action.tool,
                http_status=200,
                response_body=f"EVAL=49 template-result {self.real_flag}",
            )
        return ExecutionResult(action.action_id, action.tool, http_status=200, response_body="normal")


class ClassicalTool:
    name = "decode_tool"

    def __init__(self, fail_base64: bool = True) -> None:
        self.fail_base64 = fail_base64

    def execute(self, action: Action) -> ExecutionResult:
        mode = action.input_data[0] if isinstance(action.input_data, (list, tuple)) else ""
        path = Path(action.input_data[1]) if isinstance(action.input_data, (list, tuple)) else None
        if mode == "base64" and self.fail_base64:
            return ExecutionResult(action.action_id, action.tool, exit_code=3, stderr="decoder crash")
        if mode == "classical" and path is not None:
            encoded = path.read_text(encoding="utf-8")
            for shift in range(26):
                decoded = "".join(_caesar_character(char, -shift) for char in encoded)
                if "CTF{" in decoded:
                    return ExecutionResult(
                        action.action_id,
                        action.tool,
                        exit_code=0,
                        stdout=f"DECODE_OK:{decoded}",
                    )
        return ExecutionResult(
            action.action_id, action.tool, exit_code=0, stdout="DECODE_NOT_A_FLAG"
        )


def _caesar_character(character: str, shift: int) -> str:
    if "a" <= character <= "z":
        return chr((ord(character) - ord("a") + shift) % 26 + ord("a"))
    if "A" <= character <= "Z":
        return chr((ord(character) - ord("A") + shift) % 26 + ord("A"))
    return character


class UnavailableTool:
    name = "decode_tool"

    def execute(self, action: Action) -> ExecutionResult:
        return ExecutionResult(action.action_id, action.tool, tool_available=False)


# --------------------------------------------------------------------------------------
# Environment builders.
# --------------------------------------------------------------------------------------


def web_case_environment(
    root: Path,
    *,
    flag: str,
    decoy: str = "",
    environment_failure: bool = False,
):
    probe = WebBehaviorAdapter(
        real_flag=flag,
        decoy_flag=decoy,
        sql_environment_failure=environment_failure,
    )
    verifier = LocalVerifier(flag)
    base = "http://local.invalid/render"
    sql_payload = quote("1' OR '1'='1")
    ssti_payload = quote("{{7*7}}")
    sql_url = f"{base}?id={sql_payload}"
    ssti_url = f"{base}?name={ssti_payload}"
    environment = EnvironmentConfig(
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
                contradicting_body_contains=("LITERAL_TEMPLATE",),
                authoritative_sources=(ssti_url,),
            ),
        ),
        verifier_route=CandidateVerifierRoute("flag_verifier", "local-grader"),
        workspace_root=root,
        journal_path=root / "journal.jsonl",
        run_id=root.name,
    )
    return environment, probe, verifier


def classical_environment(root: Path, resource: Path, flag: str):
    tool = ClassicalTool()
    verifier = LocalVerifier(flag)
    source = str(resource.resolve())
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
                contradicting_body_contains=("DECODE_NOT_A_FLAG",),
                authoritative_sources=(source,),
            ),
        ),
        verifier_route=CandidateVerifierRoute("flag_verifier", "local-grader"),
        workspace_root=root,
        journal_path=root / "journal.jsonl",
        run_id=root.name,
    )
    return environment, tool, verifier


def standard_constraints() -> SolveConstraints:
    return SolveConstraints(
        max_actions=10,
        max_iterations=10,
        max_tool_executions=10,
        max_network_actions=8,
        max_remote_attempts=8,
        max_submissions=3,
        max_specialist_calls=12,
        max_total_cost=20,
        timeout_seconds=10.0,
    )


# --------------------------------------------------------------------------------------
# Crypto challenge package (KNOWN case source; also used by unit-test fixtures).
# --------------------------------------------------------------------------------------


def build_crypto_package(root: Path):
    """Reconstruct the deterministic crypto challenge package under ``root``."""
    root.mkdir(parents=True, exist_ok=True)
    flag = "CTF{phase5_xor_novel}"
    handout = root / "novel-cipher.bin"
    handout.write_bytes(bytes(byte ^ 0x42 for byte in flag.encode("utf-8")))
    tool_script = root / "decode_tool.py"
    tool_script.write_text(
        """
import base64, sys
mode, path = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read()
if mode == 'base64':
    try:
        decoded = base64.b64decode(raw, validate=True).decode('ascii')
        print('DECODE_OK:' + decoded if decoded.startswith('CTF{') else 'DECODE_NOT_A_FLAG')
    except Exception:
        print('DECODE_FAILED')
elif mode == 'xor42':
    decoded = bytes(b ^ 0x42 for b in raw).decode('utf-8', 'replace')
    print('DECODE_OK:' + decoded if decoded.startswith('CTF{') else 'DECODE_NOT_A_FLAG')
else:
    print('DECODE_NOT_A_FLAG')
""".strip(),
        encoding="utf-8",
    )
    decode = SubprocessAdapter(
        "decode_tool", SubprocessCommand(sys.executable, (str(tool_script),))
    )
    verifier = SubprocessVerifierAdapter("flag_verifier", flag)
    challenge = ChallengeInput(
        name="unseen-cipher-package",
        description="An encoded cipher artifact may be base64 or single-byte XOR.",
        flag_format="CTF{...}",
        attempt_limit=2,
    )
    resources = (ChallengeResource("cipher", ResourceKind.BINARY, path=handout),)
    environment = EnvironmentConfig(
        permitted_tools=(
            PermittedTool(
                "decode_tool",
                decode,
                authoritative_sources=(str(handout.resolve()),),
                cost=1,
            ),
            PermittedTool("flag_verifier", verifier, verifier=True, cost=1),
        ),
        evidence_rules=(
            EvidenceRule(
                "crypto-base64",
                supporting_body_contains=("DECODE_OK:",),
                contradicting_body_contains=("DECODE_FAILED",),
                authoritative_sources=(str(handout.resolve()),),
            ),
            EvidenceRule(
                "crypto-xor",
                supporting_body_contains=("DECODE_OK:",),
                contradicting_body_contains=("DECODE_NOT_A_FLAG",),
                authoritative_sources=(str(handout.resolve()),),
            ),
        ),
        verifier_route=CandidateVerifierRoute(
            tool="flag_verifier", target="local-grader", method="POST", input_field="flag"
        ),
        workspace_root=root / "runtime",
        journal_path=root / "runtime" / "journal.jsonl",
        run_id="phase5-crypto",
    )
    constraints = SolveConstraints(max_actions=8, max_iterations=8, max_specialist_calls=8)
    return challenge, resources, environment, constraints, flag, verifier


# --------------------------------------------------------------------------------------
# Frozen labeled case set.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class BenchmarkCaseSpec:
    case_id: str
    kind: str
    expected_status: str
    expected_flag: Optional[str]
    expected_specialists: Tuple[str, ...]


PHASE5_MANIFEST: Tuple[BenchmarkCaseSpec, ...] = (
    BenchmarkCaseSpec("known-xor", "KNOWN", "SOLVED", "CTF{phase5_xor_novel}", ("crypto",)),
    BenchmarkCaseSpec("novel-ssti", "NOVEL", "SOLVED", "CTF{novel_template_49}", ("web",)),
    BenchmarkCaseSpec(
        "adversarial-decoy", "ADVERSARIAL", "SOLVED", "CTF{real_template_flag}", ("web",)
    ),
    BenchmarkCaseSpec(
        "heldout-classical", "HELD_OUT", "SOLVED", "CTF{heldout_caesar_structure}", ("crypto",)
    ),
    BenchmarkCaseSpec(
        "environment-recovery",
        "ADVERSARIAL",
        "SOLVED",
        "CTF{recovered_after_environment_failure}",
        ("web",),
    ),
    BenchmarkCaseSpec("unavailable-tool", "ADVERSARIAL", "BLOCKED", None, ("crypto",)),
)


def build_phase5_cases(root: Path, crypto_package=None):
    """Construct the 6 frozen labeled cases under ``root``.

    Returns ``(cases, adversarial_verifier)``. If ``crypto_package`` is not supplied it
    is built internally so the benchmark is reproducible outside pytest.
    """
    root.mkdir(parents=True, exist_ok=True)
    if crypto_package is None:
        crypto_package = build_crypto_package(root / "crypto-known")
    known_challenge, known_resources, known_env, known_limits, known_flag, _ = crypto_package
    known = EvaluationCase(
        case_id="known-xor",
        kind=EvaluationKind.KNOWN,
        challenge=known_challenge,
        resources=known_resources,
        environment_factory=lambda: known_env,
        constraints=known_limits,
        expected_status=SolveStatus.SOLVED,
        expected_flag=known_flag,
        expected_specialists=("crypto",),
        known_correct_hypotheses=("crypto-xor",),
        requires_dead_end_recovery=True,
    )

    novel_root = root / "novel-ssti"
    novel_root.mkdir()
    novel_flag = "CTF{novel_template_49}"
    novel_env, _, _ = web_case_environment(novel_root, flag=novel_flag)
    novel = EvaluationCase(
        case_id="novel-ssti",
        kind=EvaluationKind.NOVEL,
        challenge=ChallengeInput(
            name="profile-renderer",
            category="web",
            description="A profile greeting is rendered by a server-side template using name.",
            flag_format="CTF{...}",
            urls=("http://local.invalid/render",),
        ),
        resources=(),
        environment_factory=lambda: novel_env,
        constraints=standard_constraints(),
        expected_status=SolveStatus.SOLVED,
        expected_flag=novel_flag,
        expected_specialists=("web",),
        known_correct_hypotheses=("web-ssti",),
    )

    adversarial_root = root / "adversarial-decoy"
    adversarial_root.mkdir()
    adversarial_flag = "CTF{real_template_flag}"
    adversarial_env, _, adversarial_verifier = web_case_environment(
        adversarial_root,
        flag=adversarial_flag,
        decoy="CTF{misleading_diagnostic}",
    )
    adversarial = EvaluationCase(
        case_id="adversarial-decoy",
        kind=EvaluationKind.ADVERSARIAL,
        challenge=ChallengeInput(
            name="misleading-web",
            category="web",
            description="A SQL query hint and server-side template name renderer share a page.",
            hints=("SQL is probably the answer",),
            flag_format="CTF{...}",
            urls=("http://local.invalid/render",),
        ),
        resources=(),
        environment_factory=lambda: adversarial_env,
        constraints=standard_constraints(),
        expected_status=SolveStatus.SOLVED,
        expected_flag=adversarial_flag,
        expected_specialists=("web",),
        known_correct_hypotheses=("web-ssti",),
    )

    held_root = root / "heldout-classical"
    held_root.mkdir()
    held_flag = "CTF{heldout_caesar_structure}"
    held_file = held_root / "message.txt"
    held_file.write_text(
        "".join(
            chr((ord(char) - ord("A") + 7) % 26 + ord("A"))
            if "A" <= char <= "Z"
            else chr((ord(char) - ord("a") + 7) % 26 + ord("a"))
            if "a" <= char <= "z"
            else char
            for char in held_flag
        ),
        encoding="utf-8",
    )
    held_env, _, _ = classical_environment(held_root, held_file, held_flag)
    held = EvaluationCase(
        case_id="heldout-classical",
        kind=EvaluationKind.HELD_OUT,
        challenge=ChallengeInput(
            name="shifted-message",
            category="crypto",
            description="A classical Caesar shift message; distinguish encoding from cipher.",
            flag_format="CTF{...}",
        ),
        resources=(ChallengeResource("message", ResourceKind.FILE, path=held_file),),
        environment_factory=lambda: held_env,
        constraints=standard_constraints(),
        expected_status=SolveStatus.SOLVED,
        expected_flag=held_flag,
        expected_specialists=("crypto",),
        known_correct_hypotheses=("crypto-classical",),
        recovery_result_classes=("TOOL_FAILURE",),
    )

    recovery_root = root / "environment-recovery"
    recovery_root.mkdir()
    recovery_flag = "CTF{recovered_after_environment_failure}"
    recovery_env, _, _ = web_case_environment(
        recovery_root,
        flag=recovery_flag,
        decoy="CTF{stale_failed_buffer}",
        environment_failure=True,
    )
    recovery = EvaluationCase(
        case_id="environment-recovery",
        kind=EvaluationKind.ADVERSARIAL,
        challenge=ChallengeInput(
            name="blocked-sql-open-template",
            category="web",
            description="A SQL query and server-side template name renderer share a page.",
            flag_format="CTF{...}",
            urls=("http://local.invalid/render",),
        ),
        resources=(),
        environment_factory=lambda: recovery_env,
        constraints=standard_constraints(),
        expected_status=SolveStatus.SOLVED,
        expected_flag=recovery_flag,
        expected_specialists=("web",),
        known_correct_hypotheses=("web-ssti",),
        recovery_result_classes=("ENVIRONMENT_FAILURE",),
    )

    unavailable_root = root / "unavailable-tool"
    unavailable_root.mkdir()
    unavailable_file = unavailable_root / "cipher.bin"
    unavailable_file.write_bytes(b"opaque")
    unavailable_source = str(unavailable_file.resolve())
    unavailable_env = EnvironmentConfig(
        permitted_tools=(
            PermittedTool(
                "decode_tool", UnavailableTool(), authoritative_sources=(unavailable_source,)
            ),
        ),
        evidence_rules=(
            EvidenceRule(
                "crypto-base64",
                supporting_body_contains=("DECODE_OK:",),
                contradicting_body_contains=("DECODE_FAILED",),
                authoritative_sources=(unavailable_source,),
            ),
        ),
        workspace_root=unavailable_root,
        journal_path=unavailable_root / "journal.jsonl",
        run_id="unavailable-tool",
    )
    unavailable = EvaluationCase(
        case_id="unavailable-tool",
        kind=EvaluationKind.ADVERSARIAL,
        challenge=ChallengeInput(
            name="opaque-cipher",
            category="crypto",
            description="A base64 or XOR encoded cipher artifact.",
            flag_format="CTF{...}",
        ),
        resources=(ChallengeResource("opaque", ResourceKind.BINARY, path=unavailable_file),),
        environment_factory=lambda: unavailable_env,
        constraints=standard_constraints(),
        expected_status=SolveStatus.BLOCKED,
        expected_flag=None,
        expected_specialists=("crypto",),
    )
    return (known, novel, adversarial, held, recovery, unavailable), adversarial_verifier
