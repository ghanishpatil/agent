from __future__ import annotations

from typing import Tuple

from .base import (
    SpecialistAnalysis,
    SpecialistContext,
    ToolMechanism,
    analyze_with_tool,
    score_relevance,
)


# binary -> protections -> vulnerability -> primitive -> controllability -> exploitability ->
# verification. Do NOT blindly generate payloads: each mechanism is a distinct hypothesis about the
# vulnerability class, tested through the controlled adapter (never direct execution).
_MECHANISMS: Tuple[ToolMechanism, ...] = (
    ToolMechanism(
        "overflow", "stack buffer overflow", "stack-overflow",
        ("overflow", "gets", "strcpy", "buffer", "stack", "read(", "scanf", "canary"),
        "overflow",
        "controlled input reaches a return address / a win path is triggered",
        "input length is bounded; no corruption primitive", 2,
    ),
    ToolMechanism(
        "format", "format string", "format-string",
        ("printf", "format", "%n", "%x", "%s", "fmt"),
        "format",
        "a format specifier leaks or writes memory",
        "the format argument is constant / not attacker-controlled", 2,
    ),
    ToolMechanism(
        "heap", "heap corruption (UAF / double-free)", "heap-corruption",
        ("malloc", "free", "heap", "use-after-free", "uaf", "double free", "tcache"),
        "heap",
        "a freed/overlapping chunk yields a controllable primitive",
        "allocation lifecycle is safe; no reuse primitive", 3,
    ),
)


class PwnSpecialist:
    name = "pwn"
    category = "pwn"

    def relevance(self, context: SpecialistContext) -> float:
        indicators = tuple(kw for m in _MECHANISMS for kw in m.indicators) + (
            "pwn",
            "exploit",
            "binary",
            "libc",
            "rop",
            "nx",
            "pie",
            "aslr",
            "relro",
            "got",
            "plt",
        )
        return score_relevance(context, self.category, indicators)

    def analyze(self, context: SpecialistContext) -> SpecialistAnalysis:
        return analyze_with_tool(
            context,
            specialist=self.name,
            category=self.category,
            id_prefix="pwn",
            mechanisms=_MECHANISMS,
            tool_default=("exploit_harness", "pwn_tool", "analyze_tool"),
            extra_relevance_indicators=("pwn", "exploit", "libc", "rop", "canary", "got", "plt"),
            memory_keywords=("overflow", "format", "heap", "rop", "ret2libc"),
            reasoning_summary=(
                "Reasoned binary -> protections -> vulnerability class -> primitive. Each memory-"
                "corruption class is a distinct hypothesis tested via the controlled harness adapter "
                "(never direct execution of the target). Payloads are derived from a confirmed "
                "primitive, not sprayed."
            ),
            uncertainty=(
                "Exploitability depends on mitigations (NX/PIE/ASLR/RELRO/canary) not yet confirmed; "
                "the vulnerability class is unresolved until a probe returns a corruption signal."
            ),
        )
