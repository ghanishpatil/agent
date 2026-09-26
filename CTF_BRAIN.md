


## Challenge 3: Independence Day CTF
**URL:** https://fluffy-concha-885632.netlify.app
**FLAG:** CTF{JAY_HIND}

**Quick Solution:**
- Flag is hardcoded in JavaScript source: `const FLAG = 'CTF{JAY_HIND}';`
- View page source → Find the flag directly

**Intended Path (20 pages):**
- Page 5: URL must contain "/india"
- Page 7: User-Agent "nmap" or "CTFAgent/7.0"
- Page 10: Cookie "tiranga=true"
- Page 13: POST "azad=hind"
- Page 17: URL fragment "#india"
- Page 19: Header "X-Liberty: 1947"
- Page 20: Final flag

---


## Challenge 4: भ्रमित CTF (Tubular Druid - 100 Pages)
**URL:** https://tubular-druid-6212cc.netlify.app
**FLAGS:** 
1. CTF{THIS_IS_WRONG} (Page 42)
2. CTF{HELLO_ASHISH} (Page 73)
3. CTF{SANSCRIT_ध्वज_भ्रम} (Page 99)

**Solution:**
- Hint numbers from image: 42, 73, 99
- Visit pages #page42, #page73, #page99
- The trick: CTF{THIS_IS_WRONG} looks fake but is actually REAL
- All three flags are hidden in Hindi/Marathi/Sanskrit text

---


## Challenge 5: Heart of Secrets (Steganography)
**URL:** https://thriving-meringue-85c152.netlify.app
**KEY:** KEY NEXT LEVEL

**Solution:**
- Key found in JavaScript: `const VALID_KEY = "KEY NEXT LEVEL";`
- Hidden in LSB steganography in canvas image
- Morse code: `-.- . -.-- # -. . -..- - # .-.. . ...- . .-..` = "KEY # NEXT # LEVEL"
- Hidden paths: /l0v3, /h34rt, /s3cr3t, /l3v3l2
- Enter "KEY NEXT LEVEL" to proceed to next level

---


## Challenge 6: Hate Is Simple (Hate.Breachpoint.live)
**URL:** https://hate.breachpoint.live/
**STATUS:** IN PROGRESS - Requires manual browser testing
**FRAMEWORK:** Next.js (React) on Vercel

**Key Findings:**
- HTML Comment: `<!--U0kcfdLN_WhDhNldOLdHJ-->`
- Base64 Decoded (hex): `53491c7dd2cd5a10e136574e2dd1c9`
- Input Placeholder: "Give me a reason to exist."
- Reference: Previous "LOVE IS Complicated" challenge
- Theme: "Minefield during a solar flare"

**Test Inputs:**
1. U0kcfdLN_WhDhNldOLdHJ (the encoded string)
2. hate, nothing, no reason, you don't (philosophical answers)
3. 53491c7dd2cd5a10e136574e2dd1c9 (decoded hex)
4. JHdLOdlNhDhW_NLdfck0U (reversed)
5. love, complicated (reference to previous challenge)

**Blockers:**
- Vercel rate limiting (403 errors on automated requests)
- Requires manual browser testing with Developer Tools
- Client-side JavaScript validation likely

**Next Steps:**
- Open in browser and test inputs manually
- Inspect JavaScript files for validation logic
- Check Network tab for API endpoints
- Look for flag in JavaScript source or API responses

---
