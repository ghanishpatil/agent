import requests
import json

BASE_URL = "https://smartkopargaonhackathon.vercel.app"
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
})

print("Testing actual API responses...")
print("="*70)

# Test login endpoint
print("\n[1] Testing /api/auth/login")
r = session.post(f"{BASE_URL}/api/auth/login",
                json={"email": "test@test.com", "password": "test"})
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")

# Test register
print("\n[2] Testing /api/auth/register")
r = session.post(f"{BASE_URL}/api/auth/register",
                json={"email": "newuser@test.com", "password": "Test123!", "name": "Test"})
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")

# Test /api/users/me
print("\n[3] Testing /api/users/me (without auth)")
r = session.get(f"{BASE_URL}/api/users/me")
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")

# Test admin endpoints
print("\n[4] Testing /api/admin/users (without auth)")
r = session.get(f"{BASE_URL}/api/admin/users")
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")

# Test health endpoint
print("\n[5] Testing /api/health")
r = session.get(f"{BASE_URL}/api/health")
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")
