# Kohli Challenge - Complete Solution

## Challenge Information
- **Name**: Kohli Pitch Report
- **Category**: Web
- **Difficulty**: Easy
- **Points**: 200
- **Author**: r0b1n.exe
- **URL**: http://chall-bcaad8ca.evt-207.glabs.ctf7.com

## Challenge Description
"Kohli never waits for the pitch report. He reads it ball by ball. Can you read this system the same way?"

## Solution Approach

The challenge is about triggering a "repetition addiction detection" mechanism by sending the same command repeatedly to a web terminal interface.

### Key Insights:
1. The hint "ball by ball" refers to sending requests repeatedly, like reading a cricket match
2. The system has rate limiting that returns "[ERR] Too many requests. Slow down."
3. The goal is NOT to bypass the rate limit, but to TRIGGER the detection mechanism
4. After ~100-150 repetitions of the same command, the system reveals the flag

### Solution Steps:

1. **Access the terminal interface** at the challenge URL
2. **Send the same command repeatedly** (e.g., "help") using a script
3. **Continue despite rate limiting** - the detection triggers after enough attempts
4. **Flag appears** in the response after sufficient repetitions

### Working Script:

```python
#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"
session = requests.Session()

cmd = 'help'
for i in range(1, 200):
    r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
    data = r.json()
    output = data.get('output', '')
    
    if 'Kaal{' in output or 'FLAG{' in output:
        print(f"Found flag after {i} attempts: {output}")
        break
    
    if i % 10 == 0:
        print(f"Attempt {i}: {output[:50]}")
    
    time.sleep(0.1)
```

## Flag

**Kaal{r2p2t1t1on_add1ct10n_d2t2ct2d_561443bc}**

The flag itself confirms the solution method with "repetition addiction detected" encoded in leetspeak (r2p2t1t1on = repetition, add1ct10n = addiction, d2t2ct2d = detected).

## Technical Details

- The web interface sends POST requests to `/run` endpoint with JSON: `{"cmd": "command"}`
- Normal responses return `{"output": "0x00"}`
- Rate limiting returns `{"output": "[ERR] Too many requests. Slow down."}`
- After ~100-150 identical requests, the detection mechanism triggers
- The flag is returned in the output field starting with "FLAG{" or "Kaal{"

## Notes

- The challenge has anti-debugging measures (F12 blocking, debugger statements) but these are not relevant to the solution
- The rate limiting (HTTP 429) is part of the challenge design, not an obstacle
- Different commands may work, but "help" is most commonly successful
- Timing between requests doesn't matter much - persistence is key

---

**Team**: Exploit4
**Status**: ✓ SOLVED
