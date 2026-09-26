import requests
import json
import re
from datetime import datetime

BASE_URL = "https://smartkopargaonhackathon.vercel.app"

print("="*80)
print("SMART KOPARGAON HACKATHON - COMPREHENSIVE SECURITY ASSESSMENT")
print("="*80)
print(f"Target: {BASE_URL}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
})

vulnerabilities = []
recommendations = []

# Test 1: Check HTTPS and security headers
print("\n[TEST 1] TRANSPORT SECURITY")
print("-"*80)
try:
    r = session.get(BASE_URL, timeout=10)
    headers = r.headers
    
    security_headers = {
        "Strict-Transport-Security": "HSTS",
        "X-Content-Type-Options": "X-Content-Type-Options",
        "X-Frame-Options": "X-Frame-Options",
        "Content-Security-Policy": "CSP",
        "X-XSS-Protection": "X-XSS-Protection",
    }
    
    for header, name in security_headers.items():
        if header in headers:
            print(f"[+] {name}: {headers[header][:50]}")
        else:
            print(f"[-] Missing: {name}")
            vulnerabilities.append({
                "severity": "MEDIUM",
                "category": "Missing Security Header",
                "description": f"Missing {name} header",
                "recommendation": f"Add {header} header to responses"
            })
except Exception as e:
    print(f"[!] Error: {e}")

# Test 2: Check for exposed sensitive files
print("\n[TEST 2] INFORMATION DISCLOSURE")
print("-"*80)
sensitive_files = [
    "/.env",
    "/.git/config",
    "/config.json",
    "/package.json",
    "/web.config",
    "/robots.txt",
    "/.well-known/security.txt",
]

for file in sensitive_files:
    try:
        r = session.get(f"{BASE_URL}{file}", timeout=5)
        if r.status_code == 200:
            print(f"[!] Exposed: {file} ({r.status_code})")
            if file in ["/.env", "/config.json", "/web.config"]:
                vulnerabilities.append({
                    "severity": "HIGH",
                    "category": "Information Disclosure",
                    "description": f"Sensitive file exposed: {file}",
                    "recommendation": f"Block access to {file}"
                })
        elif r.status_code != 404:
            print(f"[?] {file}: {r.status_code}")
    except:
        pass

# Test 3: Check JavaScript for secrets
print("\n[TEST 3] CLIENT-SIDE SECRETS")
print("-"*80)
try:
    r = session.get(f"{BASE_URL}/assets/index-UN4y_Obw.js", timeout=15)
    if r.status_code == 200:
        js_content = r.text
        
        # Check for API keys
        api_key_patterns = [
            (r'AIza[A-Za-z0-9_-]{35}', "Firebase API Key"),
            (r'sk_live_[A-Za-z0-9]{24,}', "Stripe Live Key"),
            (r'sk_test_[A-Za-z0-9]{24,}', "Stripe Test Key"),
            (r'rzp_live_[A-Za-z0-9]{14}', "Razorpay Live Key"),
            (r'rzp_test_[A-Za-z0-9]{14}', "Razorpay Test Key"),
        ]
        
        for pattern, name in api_key_patterns:
            matches = re.findall(pattern, js_content)
            if matches:
                print(f"[!] Found {name}: {matches[0][:20]}...")
                vulnerabilities.append({
                    "severity": "CRITICAL",
                    "category": "Exposed API Key",
                    "description": f"{name} exposed in client-side code",
                    "recommendation": "Move API keys to server-side, use environment variables"
                })
        
        if not any(re.findall(p[0], js_content) for p in api_key_patterns):
            print("[+] No obvious API keys found in JavaScript")
except Exception as e:
    print(f"[!] Error: {e}")

# Test 4: Check CORS configuration
print("\n[TEST 4] CORS CONFIGURATION")
print("-"*80)
try:
    r = session.options(f"{BASE_URL}/api/health",
                       headers={"Origin": "https://evil.com"}, timeout=5)
    if "Access-Control-Allow-Origin" in r.headers:
        origin = r.headers["Access-Control-Allow-Origin"]
        print(f"[!] CORS Header: {origin}")
        if origin == "*":
            vulnerabilities.append({
                "severity": "MEDIUM",
                "category": "Misconfigured CORS",
                "description": "CORS allows all origins (*)",
                "recommendation": "Restrict CORS to specific trusted domains"
            })
    else:
        print("[+] No CORS headers found")
except:
    pass

# Test 5: Check for rate limiting
print("\n[TEST 5] RATE LIMITING")
print("-"*80)
try:
    count = 0
    for i in range(30):
        r = session.get(f"{BASE_URL}/api/health", timeout=2)
        if r.status_code != 429:
            count += 1
    
    if count >= 25:
        print(f"[!] No rate limiting: {count}/30 requests succeeded")
        vulnerabilities.append({
            "severity": "MEDIUM",
            "category": "Missing Rate Limiting",
            "description": "No rate limiting on API endpoints",
            "recommendation": "Implement rate limiting to prevent abuse"
        })
    else:
        print(f"[+] Rate limiting detected: {count}/30 requests succeeded")
except Exception as e:
    print(f"[!] Error: {e}")

# Generate final report
print("\n" + "="*80)
print("FINAL SECURITY ASSESSMENT REPORT")
print("="*80)

print(f"\nTotal Vulnerabilities: {len(vulnerabilities)}")

severity_counts = {}
for v in vulnerabilities:
    sev = v["severity"]
    severity_counts[sev] = severity_counts.get(sev, 0) + 1

for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
    if sev in severity_counts:
        print(f"  {sev}: {severity_counts[sev]}")

if vulnerabilities:
    print("\nDETAILED FINDINGS:")
    for i, v in enumerate(vulnerabilities, 1):
        print(f"\n{i}. [{v['severity']}] {v['category']}")
        print(f"   Description: {v['description']}")
        print(f"   Recommendation: {v['recommendation']}")

# Save report
report = {
    "target": BASE_URL,
    "timestamp": datetime.now().isoformat(),
    "vulnerabilities": vulnerabilities,
    "summary": {
        "total": len(vulnerabilities),
        "by_severity": severity_counts
    }
}

with open("SMARTKOPARGAON_SECURITY_REPORT.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n[+] Full report saved to SMARTKOPARGAON_SECURITY_REPORT.json")
