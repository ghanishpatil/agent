#!/usr/bin/env python3
"""
Scrape KaalChakra CTF website for all challenges and information
"""

import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://kaalchakractf.com"

def scrape_main_page():
    """Scrape the main page"""
    print("[*] Scraping main page...")
    try:
        r = requests.get(BASE_URL, timeout=10)
        print(f"    Status: {r.status_code}")
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Save full HTML
        with open('kaalchakra_main.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
        print("[+] Saved main page to kaalchakra_main.html")
        
        # Look for challenges
        challenges = []
        
        # Find all links
        links = soup.find_all('a', href=True)
        print(f"\n[*] Found {len(links)} links:")
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            print(f"    {text}: {href}")
            
            if 'challenge' in href.lower() or 'chall' in href.lower():
                challenges.append({'text': text, 'url': href})
        
        # Look for challenge descriptions
        print("\n[*] Looking for challenge information...")
        
        # Find all text that might contain flags or challenges
        text_content = soup.get_text()
        
        # Look for flag patterns
        flag_patterns = [
            r'Kaal\{[^}]+\}',
            r'kaal\{[^}]+\}',
            r'KAAL\{[^}]+\}',
            r'flag\{[^}]+\}',
            r'FLAG\{[^}]+\}',
        ]
        
        found_flags = []
        for pattern in flag_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            found_flags.extend(matches)
        
        if found_flags:
            print(f"\n[+] Found potential flags:")
            for flag in set(found_flags):
                print(f"    {flag}")
        
        # Look for challenge names/descriptions
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"\n[*] Found {len(headings)} headings:")
        for h in headings:
            print(f"    {h.name}: {h.get_text(strip=True)}")
        
        return challenges, soup
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return [], None

def explore_paths():
    """Try common CTF paths"""
    print("\n[*] Exploring common paths...")
    
    paths = [
        '/challenges',
        '/challenge',
        '/challs',
        '/problems',
        '/tasks',
        '/ctf',
        '/flags',
        '/scoreboard',
        '/leaderboard',
        '/rules',
        '/about',
        '/api/challenges',
        '/api/challs',
        '/static',
        '/robots.txt',
        '/sitemap.xml',
    ]
    
    for path in paths:
        try:
            url = BASE_URL + path
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f"\n[+] Found: {url}")
                print(f"    Content-Type: {r.headers.get('Content-Type')}")
                print(f"    Size: {len(r.content)} bytes")
                
                # Save if it's HTML
                if 'html' in r.headers.get('Content-Type', ''):
                    filename = f"kaalchakra{path.replace('/', '_')}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(r.text)
                    print(f"    Saved to {filename}")
                    
                    # Parse for challenges
                    soup = BeautifulSoup(r.text, 'html.parser')
                    text = soup.get_text()
                    
                    # Look for challenge info
                    if 'challenge' in text.lower() or 'flag' in text.lower():
                        print(f"    Contains challenge information!")
                        
        except Exception as e:
            pass

def check_for_hidden_info(soup):
    """Check for hidden information in HTML"""
    if not soup:
        return
    
    print("\n[*] Checking for hidden information...")
    
    # Check comments
    comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
    if comments:
        print("[+] Found HTML comments:")
        for comment in comments:
            print(f"    {comment}")
    
    # Check for hidden elements
    hidden = soup.find_all(style=re.compile(r'display:\s*none', re.I))
    if hidden:
        print("[+] Found hidden elements:")
        for h in hidden:
            print(f"    {h.get_text(strip=True)}")
    
    # Check for data attributes
    elements_with_data = soup.find_all(attrs={'data-challenge': True})
    if elements_with_data:
        print("[+] Found elements with data-challenge:")
        for elem in elements_with_data:
            print(f"    {elem}")
    
    # Check meta tags
    meta_tags = soup.find_all('meta')
    print(f"\n[*] Meta tags:")
    for meta in meta_tags:
        print(f"    {meta}")

def main():
    print("[*] KaalChakra CTF Website Scraper")
    print(f"[*] Target: {BASE_URL}\n")
    
    # Scrape main page
    challenges, soup = scrape_main_page()
    
    # Check for hidden info
    check_for_hidden_info(soup)
    
    # Explore common paths
    explore_paths()
    
    # Summary
    print("\n" + "="*60)
    print("[*] Scraping complete!")
    print("[*] Check the saved HTML files for more details")
    print("="*60)

if __name__ == "__main__":
    main()
