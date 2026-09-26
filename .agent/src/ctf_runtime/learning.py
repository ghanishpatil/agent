"""Post-terminal observer — the single, failure-safe learning seam.

After a session reaches a terminal state, this observer derives learning artifacts from the
authoritative ``SolveResult`` (+ runtime journal + observations) and persists them under a single
agent-owned directory. It is invoked identically for both drivers (internal ``ctf_run`` and
Kiro-driven ``ctf_observe``/``ctf_propose``), so learning behaviour is driver-independent.

Non-negotiable safety properties:
* **Post-terminal only.** It runs after the frozen pipeline has finished and verification is owned;
  it reads a read-only ``SolveResult`` projection and never drives, mutates, or re-verifies anything.
* **Failure-safe.** Every code path is wrapped in a top-level ``try/except``. A learning error is
  logged softly to ``learning_errors.jsonl`` and swallowed — it can never change the solve result,
  the verified flag, verification state, or raise into the gateway/tool response.
* **Corpora-safe.** It writes ONLY under its own ``root`` (``agent_experience_v1`` by convention);
  it never touches the frozen solver or the external knowledge corpora.
* **Grounding-gated writeups.** A writeup is persisted only for a SOLVED result AND only if the
  grounding validator passes; the flag is copied verbatim from ``SolveResult.verified_flag``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from ctf_agent.autonomy.contracts import SolveResult, SolveStatus

from .experience import extract_failure_experience, extract_success_experience
from .experience_store import SOURCE_FAILURE, SOURCE_SUCCESS, ExperienceStore
from .writeup import generate_writeup

WRITEUPS_DIR = "writeups_generated"
ERRORS_FILE = "learning_errors.jsonl"


class PostTerminalObserver:
    """Derives + persists writeup/experience artifacts once, after a session is terminal.

    ``root`` is the agent-owned base directory (by convention ``knowledge/agent_experience_v1``).
    Everything the observer writes lives strictly under ``root``:
    ``root/success/``, ``root/failure/``, ``root/writeups_generated/``, ``root/learning_errors.jsonl``.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def observe(
        self,
        result: SolveResult,
        *,
        session_id: str,
        driver: str,
        session_journal: Sequence[Dict[str, Any]] = (),
        observations: Sequence[Dict[str, Any]] = (),
    ) -> Dict[str, Any]:
        """Persist learning artifacts for a terminal result. NEVER raises."""
        try:
            if result.status is SolveStatus.SOLVED:
                return self._learn_success(result, session_id, driver, session_journal, observations)
            return self._learn_failure(result, session_id, driver, session_journal, observations)
        except Exception as exc:  # noqa: BLE001 — learning must never break the solve path
            return self._soft_error(result, session_id, driver, exc)

    # -- success ---------------------------------------------------------------------------
    def _learn_success(
        self, result: SolveResult, session_id: str, driver: str,
        session_journal: Sequence[Dict[str, Any]], observations: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        writeup = generate_writeup(result, session_journal, observations)
        writeup_ref = ""
        if writeup.grounded and writeup.markdown:
            wdir = self.root / WRITEUPS_DIR
            wdir.mkdir(parents=True, exist_ok=True)
            wpath = wdir / f"{result.run_id}.md"
            wpath.write_text(writeup.markdown, encoding="utf-8")
            writeup_ref = str(wpath)

        record = extract_success_experience(
            result, session_id=session_id, driver=driver,
            session_journal=session_journal, observations=observations,
            writeup_ref=writeup_ref, writeup_grounded=writeup.grounded,
        )
        store = ExperienceStore.for_kind(self.root, SOURCE_SUCCESS)
        manifest = store.append(record)
        return {
            "learned": True,
            "source_kind": SOURCE_SUCCESS,
            "record_id": record.record_id,
            "writeup_ref": writeup_ref,
            "writeup_grounded": writeup.grounded,
            "writeup_markdown": writeup.markdown if writeup.grounded else "",
            "writeup_errors": list(writeup.errors),
            "record": record.to_dict(),
            "manifest": manifest,
            "error": None,
        }

    # -- failure ---------------------------------------------------------------------------
    def _learn_failure(
        self, result: SolveResult, session_id: str, driver: str,
        session_journal: Sequence[Dict[str, Any]], observations: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        record = extract_failure_experience(
            result, session_id=session_id, driver=driver,
            session_journal=session_journal, observations=observations,
        )
        store = ExperienceStore.for_kind(self.root, SOURCE_FAILURE)
        manifest = store.append(record)
        return {
            "learned": True,
            "source_kind": SOURCE_FAILURE,
            "record_id": record.record_id,
            "writeup_ref": "",
            "writeup_grounded": None,
            "writeup_markdown": "",
            "writeup_errors": [],
            "record": record.to_dict(),
            "manifest": manifest,
            "error": None,
        }

    # -- soft error (never raises) ---------------------------------------------------------
    def _soft_error(self, result: object, session_id: str, driver: str, exc: Exception) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "driver": driver,
            "run_id": getattr(result, "run_id", ""),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            with (self.root / ERRORS_FILE).open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")
        except Exception:  # noqa: BLE001 — even error logging must not raise
            pass
        return {
            "learned": False,
            "source_kind": None,
            "record_id": None,
            "writeup_ref": "",
            "writeup_grounded": None,
            "writeup_markdown": "",
            "writeup_errors": [],
            "record": None,
            "manifest": None,
            "error": f"{type(exc).__name__}: {exc}",
        }

    # -- read-only accessors (for MCP artifact tools) --------------------------------------
    def read_errors(self) -> List[Dict[str, Any]]:
        path = self.root / ERRORS_FILE
        if not path.exists():
            return []
        return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
