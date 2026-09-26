#!/usr/bin/env python3
"""
Understand what triggers different status codes
"""

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("Understanding Status Codes")
print("="*60)

# Get a fresh challenge
resp = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(resp.text, 'html.parser')
challenge = soup.find('input', {'name': 'pow_challenge'})['value']

print(f"[*] Using challenge: {challenge}\n")

# Test different scenarios
tests = [
    # (description, data)
    ("No pow_nonce field", {
        'pow_challenge': challenge,
        'username': 'test',
        'password': 'test'
    }),
    ("Empty pow_nonce", {
        'pow_challenge': challenge,
        'pow_nonce': '',
        'username': 'test',
        'password': 'test'
    }),
    ("pow_nonce = 0", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': 'test',
        'password': 'test'
    }),
    ("pow_nonce = 1", {
        'pow_challenge': challenge,
        'pow_nonce': '1',
        'username': 'test',
        'password': 'test'
    }),
    ("No username", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'password': 'test'
    }),
    ("No password", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': 'test'
    }),
    ("Empty username", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': '',
        'password': 'test'
    }),
    ("Empty password", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': 'test',
        'password': ''
    }),
    ("Non-existent user", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': 'nonexistent123456',
        'password': 'test'
    }),
    ("Existing user (admin)", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': 'admin',
        'password': 'wrongpassword'
    }),
    ("Existing user (demo)", {
        'pow_challenge': challenge,
        'pow_nonce': '0',
        'username': 'demo',
        'password': 'wrongpassword'
    }),
]

for description, data in tests:
    resp = requests.post(f"{BASE_URL}/login", data=data)
    print(f"{description:30s} -> Status: {resp.status_code}")
    time.sleep(0.3)

print("\n[*] Pattern Analysis:")
print("  400 = Bad Request (missing fields, invalid format, or non-existent user)")
print("  429 = Too Many Requests (rate limiting, wrong PoW)")
print("  200 = Valid request but wrong password (user exists)")
print("  302 = Successful login")

print("\n[*] Complete!")
