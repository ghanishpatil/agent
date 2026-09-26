#!/usr/bin/env python3
"""
Manual Testing Guide for Hate.Breachpoint.live
This script provides instructions and test cases
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║     HATE.BREACHPOINT.LIVE - MANUAL TESTING GUIDE            ║
╚══════════════════════════════════════════════════════════════╝

CHALLENGE: 🔥 Hate Is Simple 🔥
URL: https://hate.breachpoint.live/

═══════════════════════════════════════════════════════════════

STEP 1: OPEN IN BROWSER
------------------------
1. Open https://hate.breachpoint.live/ in your browser
2. Open Developer Tools (F12 or Ctrl+Shift+I)
3. Go to the Network tab
4. Refresh the page

═══════════════════════════════════════════════════════════════

STEP 2: ANALYZE PAGE SOURCE
----------------------------
1. View Page Source (Ctrl+U)
2. Look for the HTML comment: <!--U0kcfdLN_WhDhNldOLdHJ-->
3. Search for "CTF{" or "FLAG{" in source
4. Check all <script> tags for embedded data

═══════════════════════════════════════════════════════════════

STEP 3: TEST INPUT SUBMISSIONS
-------------------------------
Try submitting these values in order:

Test Case 1: The Encoded String
Input: U0kcfdLN_WhDhNldOLdHJ
Reason: It's in the HTML comment

Test Case 2: Philosophical Answers
Input: hate
Input: nothing
Input: no reason
Input: you don't
Input: chaos
Input: destruction
Reason: Answer to "Give me a reason to exist"

Test Case 3: Decoded Values
Input: 53491c7dd2cd5a10e136574e2dd1c9
Reason: Base64 decoded to hex

Test Case 4: Reversed String
Input: JHdLOdlNhDhW_NLdfck0U
Reason: Reverse of encoded string

Test Case 5: Empty/Special
Input: (empty)
Input: (space)
Reason: Edge cases

Test Case 6: Love Reference
Input: love
Input: LOVE
Input: complicated
Input: COMPLICATED
Reason: Reference to previous challenge

═══════════════════════════════════════════════════════════════

STEP 4: INSPECT JAVASCRIPT
---------------------------
1. In Developer Tools, go to Sources tab
2. Look for these files:
   - 4b9eae0c8dc7e975.js
   - 2f236954d6a65e12.js
   - 3609827fead881d6.js
3. Search for:
   - "CTF{"
   - "FLAG{"
   - "submit"
   - "validate"
   - "check"
4. Set breakpoints on form submission

═══════════════════════════════════════════════════════════════

STEP 5: CHECK NETWORK REQUESTS
-------------------------------
1. Submit any value in the form
2. Watch Network tab for:
   - POST requests
   - API calls
   - Redirects
3. Check request/response headers
4. Look for cookies being set

═══════════════════════════════════════════════════════════════

STEP 6: CONSOLE ANALYSIS
-------------------------
1. Go to Console tab
2. Type: document.cookie
3. Type: localStorage
4. Type: sessionStorage
5. Look for hidden variables

═══════════════════════════════════════════════════════════════

STEP 7: ADVANCED CHECKS
------------------------
1. Check Application tab → Storage
2. Check for Service Workers
3. Check for Web Workers
4. Inspect all loaded resources
5. Check for WebSocket connections

═══════════════════════════════════════════════════════════════

KEY CLUES TO REMEMBER:
----------------------
✓ HTML Comment: U0kcfdLN_WhDhNldOLdHJ
✓ Base64 Decoded: 53491c7dd2cd5a10e136574e2dd1c9
✓ Placeholder: "Give me a reason to exist."
✓ Title: "Hate Is Simple"
✓ Reference: "LOVE IS Complicated" challenge
✓ Theme: Minefield during solar flare

═══════════════════════════════════════════════════════════════

EXPECTED FLAG FORMAT:
---------------------
CTF{...} or FLAG{...}

═══════════════════════════════════════════════════════════════

TROUBLESHOOTING:
----------------
- If you get 403 errors: Wait a few minutes (rate limiting)
- If nothing happens: Check JavaScript console for errors
- If form doesn't submit: It might be client-side validation
- If you see "Vercel Security": You're being rate limited

═══════════════════════════════════════════════════════════════

GOOD LUCK! 🔥

""")

# Also provide a quick reference
print("\nQUICK TEST INPUTS (copy-paste ready):")
print("-" * 60)
test_inputs = [
    "U0kcfdLN_WhDhNldOLdHJ",
    "hate",
    "nothing",
    "no reason",
    "you don't",
    "53491c7dd2cd5a10e136574e2dd1c9",
    "JHdLOdlNhDhW_NLdfck0U",
    "love",
    "chaos",
    "destruction",
    "simple",
    "minefield",
    "solar flare",
    ""
]

for i, inp in enumerate(test_inputs, 1):
    print(f"{i:2d}. {inp if inp else '(empty)'}")
