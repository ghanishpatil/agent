from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from .evaluation import EvaluationReport


def write_baseline(
    path: Path,
    *,
    report: EvaluationReport,
    test_count: int,
    historical_regressions: str,
    available_tools: Sequence[str],
    model_configuration: str,
    memory_root: Path,
    protected_integrity: Mapping[str, str],
) -> Path:
    """Write the reproducible Phase 5 clean-baseline manifest as stable JSON."""
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": _git_state(path.parent),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "test_count": test_count,
        "historical_regressions": historical_regressions,
        "challenge_set": [
            {
                "case_id": item.case_id,
                "kind": item.kind.value,
                "status": item.result.status.value,
                "failures": item.failures,
            }
            for item in report.cases
        ],
        "configuration": {
            "available_tools": sorted(available_tools),
            "model": model_configuration,
            "external_writeups_ingested": False,
            "fine_tuned": False,
        },
        "memory": {
            "root": str(memory_root),
            "files": _file_hashes(memory_root),
        },
        "metrics": _jsonable(report.metrics),
        "knowledge_attribution": _jsonable(report.knowledge_attribution),
        "protected_integrity": dict(protected_integrity),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _file_hashes(root: Path) -> Mapping[str, str]:
    if not root.is_dir():
        return {}
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _git_state(cwd: Path) -> Mapping[str, Any]:
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=top,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=top,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
        return {"revision": revision, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"revision": "unavailable", "dirty": None}


def _jsonable(value):
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value
