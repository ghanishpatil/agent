#!/usr/bin/env python3
"""
Find hidden functionality - registration, admin panel, etc.
"""

import requests
import time

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("FINDING HIDDEN FUNCTIONALITY")
print("="*60)

# Comprehensive endpoint list
endpoints = [
    # Registration
    '/register', '/signup', '/create-account', '/new-user', '/join',
    '/api/register', '/api/signup', '/api/create-account',
    
    # Admin
    '/admin', '/admin/', '/admin/login', '/admin/dashboard',
    '/administrator', '/admin-panel', '/control-panel',
    '/api/admin', '/api/admin/login',
    
    # User management
    '/users', '/user', '/profile', '/account', '/settings',
    '/api/users', '/api/user', '/api/profile',
    
    # Documents
    '/documents', '/docs', '/files', '/vault', '/storage',
    '/api/documents', '/api/docs', '/api/files', '/api/vault',
    
    # Debug/Dev
    '/debug', '/dev', '/test', '/console', '/shell',
    '/api/debug', '/api/dev', '/api/test',
    
    # Info
    '/info', '/version', '/status', '/health', '/ping',
    '/api/info', '/api/version', '/api/status',
    
    # Auth
    '/auth', '/authenticate', '/token', '/session',
    '/api/auth', '/api/authenticate', '/api/token',
    
    # Password
    '/forgot-password', '/reset-password', '/change-password',
    '/api/forgot-password', '/api/reset-password',
    
    # Misc
    '/help', '/support', '/contact', '/about', '/faq',
    '/api/help', '/api/support',
    
    # Hidden
    '/.well-known', '/.well-known/security.txt',
    '/security.txt', '/humans.txt', '/robots.txt',
    
    # Backup/Old
    '/old', '/backup', '/bak', '/temp', '/tmp',
    '/api/old', '/api/backup',
    
    # Flag-related
    '/flag', '/flags', '/secret', '/secrets', '/key', '/keys',
    '/api/flag', '/api/secret',
]

found = []

print(f"\n[*] Checking {len(endpoints)} endpoints...")

for endpoint in endpoints:
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", timeout=3, allow_redirects=False)
        
        if resp.status_code not in [404, 405]:
            status_symbol = "✓" if resp.status_code == 200 else "?"
            print(f"  [{status_symbol}] {endpoint}: {resp.status_code} ({len(resp.text)} bytes)")
            
            if resp.status_code == 200 and len(resp.text) < 1000:
                print(f"      Preview: {resp.text[:150]}")
            
            found.append((endpoint, resp.status_code, resp.text))
    except:
        pass
    
    time.sleep(0.1)

print(f"\n[*] Found {len(found)} interesting endpoints")

# Check for any hints in found pages
if found:
    print("\n[*] Searching for keywords in found pages...")
    keywords = ['password', 'credential', 'username', 'flag', 'Kaal', 'secret', 'key', 'token']
    
    for endpoint, status, content in found:
        for keyword in keywords:
            if keyword.lower() in content.lower():
                print(f"  {endpoint} contains '{keyword}'")

print("\n[*] Search complete!")
