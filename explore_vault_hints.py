#!/usr/bin/env python3
"""
Explore the Learning Vault website for hints about admin DOB
"""

import requests
import re

BASE_URL = "https://learning-vault-15.emergent.host"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

print("="*70)
print("EXPLORING LEARNING VAULT FOR HINTS")
print("="*70)

# Check various pages for hints
pages_to_check = [
    "/",
    "/login",
    "/forgot-password",
    "/about",
    "/contact",
    "/help",
    "/faq",
]

print("\n[*] Checking pages for DOB hints...")

for page in pages_to_check:
    try:
        resp = session.get(f"{BASE_URL}{page}", timeout=10)
        if resp.status_code == 200:
            print(f"\n[+] {page} - Status: {resp.status_code}")
            
            # Look for date patterns
            dates = re.findall(r'\b(19|20)\d{2}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b', resp.text)
            if dates:
                print(f"    Dates found: {dates[:5]}")
            
            # Look for hints about admin
            if 'admin' in resp.text.lower():
                admin_context = re.findall(r'.{0,100}admin.{0,100}', resp.text, re.IGNORECASE)
                if admin_context:
                    print(f"    Admin mentions: {len(admin_context)}")
                    for ctx in admin_context[:2]:
                        clean = ctx.replace('\n', ' ').strip()[:150]
                        if clean:
                            print(f"      {clean}")
            
            # Look for DOB hints
            if 'birth' in resp.text.lower() or 'dob' in resp.text.lower():
                dob_context = re.findall(r'.{0,150}(birth|dob).{0,150}', resp.text, re.IGNORECASE)
                if dob_context:
                    print(f"    DOB context found:")
                    for ctx in dob_context[:3]:
                        clean = ctx.replace('\n', ' ').strip()[:200]
                        print(f"      {clean}")
                        
    except Exception as e:
        pass

# Check robots.txt
print("\n[*] Checking robots.txt...")
try:
    resp = session.get(f"{BASE_URL}/robots.txt", timeout=5)
    if resp.status_code == 200:
        print(f"[+] robots.txt found:")
        print(resp.text[:500])
except:
    pass

# Check for any API documentation
print("\n[*] Checking for API docs...")
api_docs = ["/api", "/api/docs", "/api/swagger", "/docs", "/swagger"]
for doc in api_docs:
    try:
        resp = session.get(f"{BASE_URL}{doc}", timeout=5)
        if resp.status_code == 200:
            print(f"[+] {doc} - Accessible!")
            print(f"    Preview: {resp.text[:300]}")
    except:
        pass

# Check the forgot password page specifically
print("\n[*] Analyzing forgot-password page in detail...")
try:
    resp = session.get(f"{BASE_URL}/forgot-password", timeout=10)
    if resp.status_code == 200:
        with open("forgot_password_page.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("[+] Saved forgot-password page")
        
        # Look for any hints in the HTML
        if "hint" in resp.text.lower():
            hints = re.findall(r'.{0,100}hint.{0,100}', resp.text, re.IGNORECASE)
            print(f"[+] Hints found: {len(hints)}")
            for hint in hints[:3]:
                print(f"    {hint.replace(chr(10), ' ').strip()[:200]}")
                
        # Look for placeholder text
        placeholders = re.findall(r'placeholder="([^"]+)"', resp.text)
        if placeholders:
            print(f"[+] Placeholders: {placeholders}")
            
except Exception as e:
    print(f"[-] Error: {e}")

print("\n[*] Analysis complete")
