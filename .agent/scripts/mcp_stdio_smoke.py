"""Real stdio MCP smoke test: spawn the CTF Agent MCP server as a subprocess and drive it through
an MCP client over stdio, proving Kiro -> MCP -> gateway -> KiroBridge -> AgentSession -> pipeline.

Run:  python scripts/mcp_stdio_smoke.py   (from .agent/)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SRC = str(Path(__file__).resolve().parents[1] / "src")


def _payload(result):
    # CallToolResult -> parsed JSON from the first text content block
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
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            print("TOOLS:", names)
            assert "execute_pwsh" not in names and "shell" not in names, "execution tool exposed!"

            started = _payload(await session.call_tool("ctf_start", {
                "name": "demo-ssti", "category": "web", "description": "A web app.",
                "flag_format": "CTF{...}", "urls": ["http://local.invalid/app"],
                "driver": "internal",   # this smoke exercises the internal reasoning path
            }))
            sid = started["session_id"]
            print("ctf_start:", started["status"], "session", sid[:8])

            run = _payload(await session.call_tool("ctf_run", {"session_id": sid}))
            print("ctf_run:", run["status"], "flag:", run["verified_flag"], "lifecycle:", run["lifecycle"])

            result = _payload(await session.call_tool("ctf_result", {"session_id": sid}))
            print("ctf_result:", result["result_type"], "verified:", result["verified"])

            # a forbidden/unknown tool must be rejected by the protocol (not executed). This SDK
            # returns an error CallToolResult (isError=True) rather than raising; either is fine as
            # long as NOTHING executes.
            rejected = False
            try:
                r = await session.call_tool("execute_pwsh", {"cmd": "whoami"})
                rejected = bool(getattr(r, "isError", False))
            except Exception as exc:  # noqa: BLE001
                rejected = True
                print("UNKNOWN-TOOL raised:", type(exc).__name__)
            print("UNKNOWN-TOOL rejected as expected:" if rejected else "UNKNOWN-TOOL NOT rejected:", rejected)
            if not rejected:
                return 2

            ok = run["status"] == "SOLVED" and result["verified"] and result["result_type"] == "VERIFIED_FLAG"
            print("SMOKE:", "PASS" if ok else "FAIL")
            return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
