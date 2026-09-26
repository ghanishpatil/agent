import requests
import json
import re
from datetime import datetime

BASE_URL = "https://cyberspacevr.in"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
})

print("="*80)
print("SPACECTF BUG BOUNTY - VULNERABILITY ASSESSMENT")
print("Target: cyberspacevr.in")
print("="*80)

vulnerabilities = []

# Test 1: Security Headers
print("\n[TEST 1] SECURITY HEADERS")
print("-"*80)
try:
    r = session.get(BASE_URL, timeout=10)
    headers = r.headers
    
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY/SAMEORIGIN",
        "Content-Security-Policy": "CSP",
        "Strict-Transport-Security": "HSTS",
        "X-XSS-Protection": "1; mode=block",
    }
    
    for header, desc in security_headers.items():
        if header not in headers:
            print(f"[-] Missing: {header}")
            vulnerabilities.append({
                "severity": "MEDIUM",
                "title": f"Missing {header} Header",
                "description": f"The application does not implement {header} security header",
                "impact": "Increased risk of XSS, clickjacking, or MIME sniffing attacks"
            })
        else:
            print(f"[+] Found: {header}")
except Exception as e:
    print(f"[!] Error: {e}")

# Test 2: Information Disclosure
print("\n[TEST 2] INFORMATION DISCLOSURE")
print("-"*80)

sensitive_files = [
    "/.env",
    "/.git/config",
    "/.git/HEAD",
    "/config.json",
    "/package.json",
    "/.env.local",
    "/.env.production",
    "/web.config",
    "/.htaccess",
    "/robots.txt",
    "/sitemap.xml",
]

for file in sensitive_files:
    try:
        r = session.get(f"{BASE_URL}{file}", timeout=5)
        if r.status_code == 200 and len(r.text) > 10:
            print(f"[!] EXPOSED: {file} ({r.status_code}, {len(r.text)} bytes)")
            if file in ["/.env", "/.git/config", "/config.json"]:
                vulnerabilities.append({
                    "severity": "HIGH",
                    "title": f"Sensitive File Exposure: {file}",
                    "description": f"Sensitive configuration file {file} is publicly accessible",
                    "impact": "Potential exposure of API keys, credentials, or system configuration",
                    "evidence": r.text[:200]
                })
    except:
        pass

# Test 3: API Endpoint Discovery
print("\n[TEST 3] API ENDPOINT ENUMERATION")
print("-"*80)

api_endpoints = [
    "/api",
    "/api/v1",
    "/api/users",
    "/api/admin",
    "/api/config",
    "/api/health",
    "/api/status",
    "/graphql",
    "/api/graphql",
]

for ep in api_endpoints:
    try:
        r = session.get(f"{BASE_URL}{ep}", timeout=5)
        if r.status_code != 404:
            print(f"[+] {ep}: {r.status_code}")
            if r.status_code == 200:
                print(f"    Response: {r.text[:150]}")
    except:
        pass

# Test 4: CORS Misconfiguration
print("\n[TEST 4] CORS CONFIGURATION")
print("-"*80)
try:
    r = session.options(f"{BASE_URL}/api",
                       headers={"Origin": "https://evil.com"}, timeout=5)
    if "Access-Control-Allow-Origin" in r.headers:
        origin = r.headers["Access-Control-Allow-Origin"]
        print(f"[!] CORS Header: {origin}")
        if origin == "*" or origin == "https://evil.com":
            vulnerabilities.append({
                "severity": "MEDIUM",
                "title": "CORS Misconfiguration",
                "description": f"CORS allows origin: {origin}",
                "impact": "Potential for cross-origin data theft"
            })
except:
    pass

# Test 5: Rate Limiting
print("\n[TEST 5] RATE LIMITING")
print("-"*80)
count = 0
for i in range(50):
    try:
        r = session.get(f"{BASE_URL}/", timeout=2)
        if r.status_code != 429:
            count += 1
    except:
        pass

if count >= 45:
    print(f"[!] No rate limiting: {count}/50 requests succeeded")
    vulnerabilities.append({
        "severity": "MEDIUM",
        "title": "Missing Rate Limiting",
        "description": "No rate limiting detected on endpoints",
        "impact": "Vulnerable to brute force and DoS attacks"
    })
else:
    print(f"[+] Rate limiting detected: {count}/50")

# Test 6: SQL Injection (Basic)
print("\n[TEST 6] SQL INJECTION TESTING")
print("-"*80)
sqli_payloads = ["'", "1' OR '1'='1", "admin'--", "' OR 1=1--"]
test_params = ["id", "user", "search", "q"]

for param in test_params:
    for payload in sqli_payloads:
        try:
            r = session.get(f"{BASE_URL}/api?{param}={payload}", timeout=3)
            if any(x in r.text.lower() for x in ["sql", "mysql", "syntax error", "postgresql"]):
                print(f"[!] Potential SQLi: ?{param}={payload}")
                vulnerabilities.append({
                    "severity": "CRITICAL",
                    "title": "SQL Injection Vulnerability",
                    "description": f"Parameter '{param}' appears vulnerable to SQL injection",
                    "impact": "Complete database compromise possible",
                    "evidence": r.text[:200]
                })
                break
        except:
            pass

# Test 7: XSS Testing
print("\n[TEST 7] XSS TESTING")
print("-"*80)
xss_payloads = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
]

for payload in xss_payloads:
    try:
        r = session.get(f"{BASE_URL}/?search={payload}", timeout=3)
        if payload in r.text:
            print(f"[!] Reflected XSS: {payload[:30]}")
            vulnerabilities.append({
                "severity": "HIGH",
                "title": "Reflected XSS Vulnerability",
                "description": "User input is reflected without sanitization",
                "impact": "Session hijacking, credential theft possible"
            })
            break
    except:
        pass

print("\n[*] Vulnerability scan complete")
print(f"[*] Found {len(vulnerabilities)} vulnerabilities")

# Save report
report = {
    "target": BASE_URL,
    "timestamp": datetime.now().isoformat(),
    "vulnerabilities": vulnerabilities,
    "summary": {
        "total": len(vulnerabilities),
        "critical": len([v for v in vulnerabilities if v["severity"] == "CRITICAL"]),
        "high": len([v for v in vulnerabilities if v["severity"] == "HIGH"]),
        "medium": len([v for v in vulnerabilities if v["severity"] == "MEDIUM"]),
    }
}

with open("CYBERSPACE_VULN_REPORT.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n[+] Report saved to CYBERSPACE_VULN_REPORT.json")
