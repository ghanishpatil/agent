#!/usr/bin/env python3
"""
Final solve for Insider challenge
Using cracked credentials to get the flag
"""

import hashlib
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Known username
username = "hello"
username_hash = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"

# Password hash to crack
password_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("=" * 60)
print("INSIDER CTF7 - FINAL SOLVE")
print("=" * 60)

# Try to crack password using online API
print("\n[*] Attempting to crack password hash...")
print(f"Hash: {password_hash}")

# Try hashes.com API
try:
    url = f"https://hashes.com/en/api/identifier"
    response = requests.post(url, data={'hashes': password_hash}, timeout=10)
    print(f"Hashes.com response: {response.text[:200]}")
except Exception as e:
    print(f"Hashes.com error: {e}")

# The encrypted token from the challenge
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

# The base64 string from the comment might be related
comment_string = "KRgda0-jlu6DtCQ8dUE5XyMJHI23ubzxASpu9fzy8V8="

print(f"\n[*] Encrypted token: {encrypted_token}")
print(f"[*] Comment string: {comment_string}")

# Try common CTF passwords related to the challenge
ctf_passwords = [
    'betrayal', 'insider', 'confidential', 'stolen', 'employee',
    'harddisk', 'storage', 'encrypted', 'data', 'trust',
    'Betrayal', 'Insider', 'Confidential', 'Stolen', 'Employee',
    'world', 'World', 'WORLD', 'hello', 'Hello', 'HELLO',
    'helloworld', 'HelloWorld', 'hello world', 'Hello World',
    'kaalchakra', 'Kaalchakra', 'KAALCHAKRA',
    'insiderctf', 'InsiderCTF', 'INSIDERCTF',
    'le0', 'Le0', 'LE0', 'leo', 'Leo', 'LEO'
]

print("\n[*] Trying CTF-related passwords...")
for pwd in ctf_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == password_hash:
        print(f"\n[+] PASSWORD FOUND: {pwd}")
        print(f"    Hash: {h}")
        
        print(f"\n[+] Credentials:")
        print(f"    Username: {username}")
        print(f"    Password: {pwd}")
        
        # Now we need to login and get the flag
        print("\n[*] Attempting to retrieve flag...")
        print("[!] Manual login required at: https://login-page-auqw.vercel.app/")
        print(f"[!] Use credentials: {username} / {pwd}")
        break
else:
    print("\n[-] Password not found in common list")
    print("[!] Try manual cracking at: https://crackstation.net/")
    print(f"[!] Hash: {password_hash}")

# Check if there's a flag endpoint after login
print("\n[*] Checking for flag endpoints...")
base_url = "https://login-page-auqw.vercel.app"
endpoints = ['/flag', '/api/flag', '/admin', '/dashboard', '/data', '/files', '/storage']

for endpoint in endpoints:
    try:
        url = base_url + endpoint
        response = requests.get(url, timeout=5)
        if response.status_code != 404:
            print(f"[+] {endpoint} - Status: {response.status_code}")
            if 'kaal{' in response.text.lower():
                print(f"[+] FOUND FLAG: {response.text}")
    except:
        pass
