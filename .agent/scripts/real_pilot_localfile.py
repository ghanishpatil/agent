"""REAL-ADAPTER pilot: a local file challenge solved through the frozen pipeline using the REAL
FileAdapter (real disk I/O) + a REAL deterministic verifier — NOT the fake demo web probe.

Honesty notes:
* The REASONING is a scripted stand-in (no real LLM API key is configured in this environment;
  autonomous reasoning is therefore not exercised here). It only: (1) proposes reading the provided
  file, (2) after the flag appears in the REAL observed evidence, proposes that observed string.
* The flag is NOT injected by the caller into the submission — it is read from a real file by the
  real adapter, surfaced as real evidence, and independently re-derived by the verifier.
* Verification is a deterministic self-check (VerificationMethod handled by the frozen kernel).

Run:  python scripts/real_pilot_localfile.py   (from .agent/)
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ctf_agent.models import Action, ExecutionResult                      # noqa: E402
from ctf_agent.autonomy.contracts import EvidenceRule, SolveConstraints    # noqa: E402
from ctf_runtime.llm_client import ScriptedLLMClient                       # noqa: E402
from ctf_runtime.real_environment import OperatorPolicy, build_operator_gateway  # noqa: E402

# Deterministically derived flag (a real self-check challenge, not a hardcoded literal handed to
# the agent for submission — the verifier recomputes it independently).
FLAG = "CTF{" + hashlib.sha256(b"local-file-pilot-secret").hexdigest()[:16] + "}"


class DeterministicVerifier:
    """Operator/challenge authoritative self-check: recompute the expected flag and compare."""
    name = "flag_verifier"

    def execute(self, action: Action) -> ExecutionResult:
        candidate = (action.input_data or {}).get("flag", "") if isinstance(action.input_data, dict) else str(action.input_data or "")
        expected = "CTF{" + hashlib.sha256(b"local-file-pilot-secret").hexdigest()[:16] + "}"
        accepted = candidate == expected
        return ExecutionResult(
            action_id=action.action_id, tool=action.tool, exit_code=0,
            metadata={"submitted_candidate": candidate, "verifier_accepted": accepted,
                      "rejection_reason": "" if accepted else "wrong flag"},
        )


def _script(request):
    """Scripted reasoning stand-in (see honesty notes)."""
    prompt = request.prompt
    hyps = [{"id": "flag-in-file", "statement": "the provided file contains the flag",
             "mechanism": "file-read", "technique": "artifact inspection"}]
    # resources materialize under <workspace>/resources/<resource_id>/<filename>; the real
    # FileAdapter is rooted at the workspace, so read via that relative path.
    rel = "resources/notes/notes.txt"
    actions = [{"hypothesis_id": "flag-in-file", "objective": "read the provided challenge file",
                "tool": "read_file", "target": rel, "input_data": rel}]
    import re
    seen = re.search(r"CTF\{[0-9a-f]+\}", prompt)
    if seen:  # only after the REAL file read surfaced the flag in evidence
        actions.append({"hypothesis_id": "flag-in-file", "objective": "submit observed flag",
                        "tool": "flag_verifier", "target": "operator-grader",
                        "candidate_flag": seen.group(0)})
    return json.dumps({"hypotheses": hyps, "actions": actions})


def main() -> int:
    policy = OperatorPolicy(
        enable_file_read=True,
        allowed_host_prefixes=(),          # no network for this pilot
        allowed_executables=(),            # no process execution needed
        verifier_tool_name="flag_verifier",
        verifier_target="operator-grader",
        verifier_adapter=DeterministicVerifier(),
        evidence_rules=(EvidenceRule("flag-in-file", supporting_body_contains=(FLAG,),
                                     authoritative_sources=("resources/notes/notes.txt",)),),
        authoritative_sources_by_tool={"read_file": ("resources/notes/notes.txt",)},
        constraints=SolveConstraints(max_actions=6, max_iterations=6, timeout_seconds=600.0),
    )
    gw = build_operator_gateway(policy, ScriptedLLMClient(_script),
                                workspace_base=Path(tempfile.mkdtemp(prefix="ctf_pilot_")))

    # The challenge file is supplied as a controlled resource (materialized into the sandbox, then
    # read by the REAL FileAdapter). Its bytes contain the flag.
    resource_b64 = base64.b64encode(f"onboarding notes...\nflag: {FLAG}\n".encode()).decode()
    started = gw.ctf_start({
        "name": "local-file-pilot", "category": "forensics",
        "description": "Recover the flag from the provided file.", "flag_format": "CTF{...}",
        "resources": [{"resource_id": "notes", "kind": "FILE", "filename": "notes.txt",
                       "content_b64": resource_b64}],
    })
    sid = started["session_id"]
    print("ctf_start:", started["status"])

    run = gw.ctf_run(sid)
    print("ctf_run:", run["status"], "flag:", run["verified_flag"], "lifecycle:", run["lifecycle"])

    result = gw.ctf_result(sid)
    print("ctf_result:", result["result_type"], "verified:", result["verified"])

    journal = gw.session_journal(sid)
    adapters = sorted({r["execution_adapter"] for r in journal})
    print("journal steps:", len(journal), "real adapters used:", adapters)
    print("verified_states:", [r["verification_state"] for r in journal])

    ok = (run["status"] == "SOLVED" and result["verified"] and result["verified_flag"] == FLAG
          and "read_file" in adapters and "flag_verifier" in adapters)
    print("REAL-ADAPTER PILOT:", "PASS" if ok else "INCOMPLETE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
