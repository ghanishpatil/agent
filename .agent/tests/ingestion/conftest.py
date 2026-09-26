from __future__ import annotations

from pathlib import Path

import pytest

WEB_WRITEUP = """# Baby SSTI

Category: web
Points: 150 pts

## Description
We are given a profile page that renders our name with a server-side template.

## Recon
We notice the name parameter is reflected. Interesting: the hint mentions Jinja2.

## Approach
This could be a server-side template injection. Hypothesis: the template evaluates
input. To test, we submit {{7*7}} as the name.

## Observation
The response was 49, which means the template evaluated our expression. This confirms SSTI.

## Exploit
We craft a payload to read the config. The final script dumps the secret.

## Flag
The flag is CTF{ssti_is_fun}
"""

CRYPTO_WRITEUP = """# Single Byte XOR

Category: crypto

## Description
We are given a binary blob. It could be base64 or a single-byte XOR cipher.

## Analysis
We tried base64 first but it didn't work. Instead, it turned out to be single-byte XOR.
We notice repeating structure suggesting XOR with one key byte.

## Solution
Brute force all 256 keys. The flag is CTF{xor_key_0x42}.
"""

HTML_WRITEUP = """<html><head><title>PCAP Fun</title></head><body>
<h1>PCAP Fun</h1>
<h2>Description</h2>
<p>Category: forensics. We are given a pcap capture from wireshark.</p>
<h2>Solution</h2>
<p>We follow the TCP stream and recover the flag CTF{pcap_stream}.</p>
</body></html>
"""


@pytest.fixture
def writeups_dir(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "web").mkdir(parents=True)
    (root / "crypto").mkdir(parents=True)
    (root / "forensics").mkdir(parents=True)
    (root / "web" / "ssti.md").write_text(WEB_WRITEUP, encoding="utf-8")
    (root / "crypto" / "xor.md").write_text(CRYPTO_WRITEUP, encoding="utf-8")
    (root / "forensics" / "pcap.html").write_text(HTML_WRITEUP, encoding="utf-8")
    # A binary/no-text file that must be ignored by the crawler.
    (root / "artifact.bin").write_bytes(b"\x00\x01\x02not text")
    return root
