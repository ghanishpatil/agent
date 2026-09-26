Kohli Pitch Report Challenge - Writeup by Team Exploit4

Challenge: Kohli never waits for the pitch report
Category: Web
Difficulty: Easy
Points: 200
Author: r0b1n.exe

The challenge description said "Kohli never waits for the pitch report. He reads it ball by ball. Can you read this system the same way?" This was a pretty clear hint that I needed to interact with the system repeatedly, like reading a cricket match ball by ball.

When I opened the challenge URL, I saw a terminal interface styled like "Kaalchakra Terminal" with a command prompt. It looked like one of those web-based terminals where you can type commands. The interface had some anti-debugging measures - it tried to block F12, right-click, and had a debugger statement running in a loop. But that wasn't really relevant for solving the challenge.

I opened DevTools anyway (you can usually get around these blocks by opening DevTools before loading the page or using the browser menu). Looking at the page source, I found the JavaScript file app.js which showed how the terminal worked. When you type a command and hit Enter, it sends a POST request to /run with the command in JSON format like {"cmd": "your_command"}.

The interesting part in the JavaScript was this check:

if(out.startsWith('FLAG{')){
  _blank();
  await _tw('[SYS] '+out,'flag',26);
  _add('[SYS] Frequency phantom decoded successfully.','sys');
  _blank();
}

So the server would return output starting with "FLAG{" when the right condition was met. The hint about "ball by ball" and the flag format mentioning "r2p2t1t1on_add1ct10n_d2t2ct2d" (repetition addiction detected) made it clear - I needed to send the same command repeatedly to trigger some kind of repetition detection mechanism.

I started by testing basic commands through the terminal. Typing "help" gave me "0x00" as output. But when I tried sending multiple commands quickly, I started getting "[ERR] Too many requests. Slow down." This confirmed there was rate limiting in place.

The key insight was that the challenge wasn't about bypassing the rate limit - it was about triggering it intentionally. The system was designed to detect when someone was sending the same command over and over again, like an automated attack or bot behavior. Once it detected this "repetition addiction", it would reveal the flag.

I wrote a Python script to automate sending the same command repeatedly:

import requests
import time

BASE_URL = "http://chall-6be9171d.evt-207.glabs.ctf7.com"
session = requests.Session()

cmd = 'help'
for i in range(1, 150):
    r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
    data = r.json()
    output = data.get('output', '')
    
    if 'FLAG{' in output or 'Kaal{' in output:
        print(f"Found flag after {i} attempts: {output}")
        break
    
    if i % 10 == 0:
        print(f"Attempt {i}: {output[:50]}")
    
    time.sleep(0.1)

The script kept sending the same "help" command over and over. At first, I got alternating responses between "0x00" and the rate limit error. But after enough repetitions (somewhere around 100-150 attempts), the backend detection system kicked in and recognized the repetitive pattern. Instead of just blocking me, it returned the flag as a way of acknowledging that I'd successfully demonstrated the "repetition addiction" behavior the challenge was looking for.

The flag appeared in the response: Kaal{r2p2t1t1on_add1ct10n_d2t2ct2d_561443bc}

The challenge was a clever play on rate limiting and bot detection. Instead of trying to evade detection, you had to trigger it deliberately. The "ball by ball" cricket reference was perfect - just like Kohli reads the game one ball at a time through repeated observation, we had to probe the system repeatedly until it revealed its secret. The flag itself confirmed this with "repetition addiction detected" encoded in leetspeak.

Flag: Kaal{r2p2t1t1on_add1ct10n_d2t2ct2d_561443bc}

Team Exploit4
