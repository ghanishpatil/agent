#!/usr/bin/env python3
"""
Investigate the /lore endpoint
"""

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "http://138.199.163.92:16969"

def check_lore():
    """Check the /lore endpoint"""
    print("[*] Checking /lore endpoint...")
    
    try:
        resp = requests.get(f"{BASE_URL}/lore", timeout=10)
        print(f"[+] Status: {resp.status_code}")
        print(f"[+] Length: {len(resp.text)}")
        print(f"\n[*] Content:")
        print(resp.text)
        
        # Save to file
        with open('lore_page.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("\n[+] Saved to lore_page.html")
        
        # Parse HTML
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for links
        links = soup.find_all('a')
        if links:
            print(f"\n[*] Found {len(links)} link(s):")
            for link in links:
                print(f"  {link.get('href')} - {link.text}")
        
        # Look for forms
        forms = soup.find_all('form')
        if forms:
            print(f"\n[*] Found {len(forms)} form(s)")
        
        # Look for comments
        comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
        if comments:
            print(f"\n[*] Found HTML comments:")
            for comment in comments:
                print(f"  {comment.strip()}")
        
        # Look for scripts
        scripts = soup.find_all('script')
        if scripts:
            print(f"\n[*] Found {len(scripts)} script(s)")
            for i, script in enumerate(scripts):
                if script.string:
                    print(f"\n  Script {i+1}:")
                    print(f"    {script.string[:300]}")
        
        return resp.text
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

def check_root():
    """Check the root endpoint"""
    print("\n[*] Checking / endpoint...")
    
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"[+] Status: {resp.status_code}")
        print(f"[+] Length: {len(resp.text)}")
        
        if resp.text != requests.get(f"{BASE_URL}/login").text:
            print("\n[*] Root is different from /login!")
            print(resp.text[:500])
            
            with open('root_page.html', 'w', encoding='utf-8') as f:
                f.write(resp.text)
        
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("Investigating QuantumVault Endpoints")
    print("="*60)
    
    check_root()
    time.sleep(2)
    check_lore()
