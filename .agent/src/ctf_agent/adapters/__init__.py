"""Trusted tool adapters.

Every adapter turns a Phase 2 ``Action`` into a Phase 2 ``ExecutionResult`` honestly. No adapter
may construct ``Evidence``, mutate a ``Hypothesis``, or set ``FlagCandidate.verification_status``.
Only ``TrustKernel.process()`` may do that.
"""

from .base import AdapterRegistry, ToolAdapter, UnknownToolError
from .file_adapter import FileAdapter
from .http_adapter import HttpAdapter
from .subprocess_adapter import SubprocessAdapter

__all__ = [
    "AdapterRegistry",
    "ToolAdapter",
    "UnknownToolError",
    "FileAdapter",
    "HttpAdapter",
    "SubprocessAdapter",
]
