"""Architecture A stdio smoke: drive the observe -> propose loop over the REAL MCP transport.

This script plays the role of Kiro's model with DETERMINISTIC reasoning (reads observe() output,
decides the next typed proposal). It proves the Kiro-driven path works end-to-end over stdio:
ctf_start(driver=kiro) -> ctf_observe -> ctf_propose(probe) -> ctf_observe -> ctf_propose(verify)
-> VERIFIED_FLAG. Nothing is executed by this script; the agent executes via trusted adapters.

Run:  python scripts/mcp_kiro_smoke.py   (from .agent/)
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SRC = str(Path(__file__).resolve().parents[1] / "src")


def _payload(result):
    for block in result.content:
        if getattr(block, "type", "") == "text":
            return json.loads(block.text)
    return None


async def main() -> int:
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    params = StdioServerParameters(command=sys.executable, args=["-m", "ctf_runtime.mcp_server"], env=env)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            started = _payload(await session.call_tool("ctf_start", {
                "name": "kiro-ssti", "category": "web", "description": "A web app with live preview.",
                "flag_format": "CTF{...}", "urls": ["http://local.invalid/app"], "driver": "kiro",
            }))
            sid = started["session_id"]
            print("ctf_start:", started["status"], "driver:", started.get("driver"))

            # observe #1 — decide from available_tools that a template probe is the cheapest test
            obs1 = _payload(await session.call_tool("ctf_observe", {"session_id": sid}))
            assert "http_probe" in obs1["available_tools"], obs1["available_tools"]
            ssti_url = "http://local.invalid/app?name=%7B%7B7%2A7%7D%7D"

            p1 = _payload(await session.call_tool("ctf_propose", {
                "session_id": sid,
                "hypotheses": [{"hypothesis_id": "web-ssti", "statement": "name is server-side templated",
                                "mechanism": "ssti", "technique": "Server-Side Template Injection"}],
                "actions": [{"hypothesis_id": "web-ssti", "objective": "probe {{7*7}}",
                             "tool": "http_probe", "target": ssti_url, "expected_observation": "EVAL=49"}],
            }))
            print("propose#1 executed:", len(p1["executed"]), "verified:", p1["verified"])

            # observe #2 — read the flag out of the REAL observed evidence
            obs2 = _payload(await session.call_tool("ctf_observe", {"session_id": sid}))
            blob = " ".join(o["output"] for o in obs2["recent_observations"])
            seen = re.search(r"CTF\{[A-Za-z0-9_]+\}", blob)
            print("observed EVAL=49:", "EVAL=49" in blob, "flag seen:", bool(seen))
            if not seen:
                print("KIRO SMOKE: FAIL (no flag in evidence)"); return 1

            p2 = _payload(await session.call_tool("ctf_propose", {
                "session_id": sid, "hypotheses": [],
                "actions": [{"hypothesis_id": "web-ssti", "objective": "submit observed flag",
                             "tool": "flag_verifier", "target": "local-grader", "candidate_flag": seen.group(0)}],
            }))
            res = _payload(await session.call_tool("ctf_result", {"session_id": sid}))
            print("propose#2 verified:", p2["verified"], "result:", res["result_type"], "flag:", res["verified_flag"])

            ok = res["result_type"] == "VERIFIED_FLAG" and res["verified"] and res["verified_flag"] == seen.group(0)
            print("KIRO SMOKE:", "PASS" if ok else "FAIL")
            return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
