from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .contracts import ChallengeResource


def materialize_resources(
    resources: Tuple[ChallengeResource, ...], workspace_root: Path
) -> Tuple[str, ...]:
    """Return absolute resource paths, materializing caller-supplied content under workspace_root.

    Existing paths are never modified. Content resources are confined to a generated resources
    directory using a basename-only filename, preventing traversal outside the permitted workspace.
    """
    resource_root = workspace_root / "resources"
    paths = []
    normalized_targets: set[Path] = set()
    for resource in resources:
        if resource.path is not None:
            path = resource.path.resolve()
            paths.append(str(path))
            continue
        resource_root.mkdir(parents=True, exist_ok=True)
        raw_name = resource.filename or resource.resource_id
        filename = Path(raw_name).name or resource.resource_id
        # Scope materialized content by resource id so equal basenames cannot overwrite each other.
        safe_id = Path(resource.resource_id).name
        if not safe_id:
            raise ValueError("resource_id must produce a safe path component")
        target = (resource_root / safe_id / filename).resolve()
        if resource_root.resolve() not in target.parents:
            raise ValueError(f"resource path escapes workspace: {resource.resource_id}")
        if target in normalized_targets:
            raise ValueError(f"resource target collision: {resource.resource_id}")
        normalized_targets.add(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(resource.content, bytes):
            target.write_bytes(resource.content)
        else:
            target.write_text(str(resource.content or ""), encoding="utf-8")
        paths.append(str(target))
    return tuple(paths)
