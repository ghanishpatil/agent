#!/usr/bin/env python3
"""
Direct browser-like solver for hate.breachpoint.live
Using proper headers and session management
"""

import requests
import time
import re
from urllib.parse import urljoin

class BrowserSolver:
    def __init__(self):
        self.session = requests.Session()
        # Mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.base_url = "https://hate.breachpoint.live"
        
    def get_page(self):
        """Get the main page and extract all info"""
        print("[*] Fetching main page...")
        resp = self.session.get(self.base_url)
        print(f"[+] Status: {resp.status_code}")
        
        # Extract cookies
        if resp.cookies:
            print(f"[+] Cookies: {dict(resp.cookies)}")
        
        # Look for flag in source
        if 'CTF{' in resp.text or 'FLAG{' in resp.text:
            flags = re.findall(r'(CTF\{[^}]+\}|FLAG\{[^}]+\})', resp.text)
            if flags:
                print(f"\n{'='*60}")
                print("FLAG FOUND IN SOURCE!")
                print(f"{'='*60}")
                for flag in flags:
                    print(f"FLAG: {flag}")
                return flags[0]
        
        return resp.text
    
    def try_submit(self, value):
        """Try submitting a value"""
        print(f"\n[*] Testing: {value}")
        
        # Try different submission methods
        methods = [
            ('POST', {'input': value}),
            ('POST', {'answer': value}),
            ('POST', {'reason': value}),
            ('POST', {'text': value}),
            ('POST', {'value': value}),
        ]
        
        for method, data in methods:
            try:
                time.sleep(0.5)  # Rate limit
                resp = self.session.post(self.base_url, data=data, allow_redirects=True)
                
                if resp.status_code == 200:
                    # Check for flag
                    if 'CTF{' in resp.text or 'FLAG{' in resp.text:
                        flags = re.findall(r'(CTF\{[^}]+\}|FLAG\{[^}]+\})', resp.text)
                        if flags:
                            print(f"\n{'='*60}")
                            print(f"FLAG FOUND WITH INPUT: {value}")
                            print(f"{'='*60}")
                            for flag in flags:
                                print(f"FLAG: {flag}")
                            return flags[0]
                    
                    # Check for success message
                    if any(word in resp.text.lower() for word in ['correct', 'success', 'congratulations', 'well done']):
                        print(f"[+] Possible success with data: {data}")
                        print(f"    Response snippet: {resp.text[:500]}")
                        
            except Exception as e:
                pass
        
        return None
    
    def solve(self):
        """Main solving routine"""
        print("="*60)
        print("HATE.BREACHPOINT.LIVE - BROWSER SOLVER")
        print("="*60)
        
        # Get main page first
        html = self.get_page()
        
        # Test inputs in priority order
        test_inputs = [
            # Priority 1: Encoded string
            "U0kcfdLN_WhDhNldOLdHJ",
            
            # Priority 2: Philosophical (nihilistic theme)
            "hate",
            "nothing",
            "no reason",
            "you don't",
            "you don't exist",
            "there is no reason",
            
            # Priority 3: Decoded values
            "53491c7dd2cd5a10e136574e2dd1c9",
            "JHdLOdlNhDhW_NLdfck0U",
            
            # Priority 4: Theme words
            "simple",
            "minefield",
            "solar flare",
            "solarflare",
            
            # Priority 5: Love reference
            "love",
            "complicated",
            "LOVE",
            "COMPLICATED",
            
            # Priority 6: Opposites
            "HATE",
            "SIMPLE",
            
            # Priority 7: Empty/special
            "",
            " ",
        ]
        
        for inp in test_inputs:
            result = self.try_submit(inp)
            if result:
                return result
        
        print("\n[!] No flag found with standard inputs")
        print("[!] Manual browser testing required")
        return None

if __name__ == "__main__":
    solver = BrowserSolver()
    flag = solver.solve()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"FINAL FLAG: {flag}")
        print(f"{'='*60}")
        
        # Save to file
        with open("HATE_FLAG.txt", "w") as f:
            f.write(f"Challenge: Hate.Breachpoint.live\n")
            f.write(f"URL: https://hate.breachpoint.live/\n")
            f.write(f"FLAG: {flag}\n")
        print("\n[+] Flag saved to HATE_FLAG.txt")
