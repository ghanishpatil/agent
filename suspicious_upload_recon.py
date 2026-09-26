#!/usr/bin/env python3
"""
Suspicious Upload Challenge Reconnaissance
Quick recon to identify the challenge and gather initial information
"""

import requests
import re
from urllib.parse import urljoin
import json

def discover_challenge():
    """Try to discover the suspicious upload challenge"""
    print("="*80)
    print("SUSPICIOUS UPLOAD CHALLENGE RECONNAISSANCE")
    print("="*80)
    
    # Common CSBC/CTF hosting patterns
    possible_urls = [
        "https://suspicious-upload.emergent.host",
        "https://csbc-suspicious-upload.herokuapp.com", 
        "https://suspicious-upload-csbc.onrender.com",
        "https://ctf-suspicious-upload.vercel.app",
        "https://suspicious-upload.ctf.csbc.com",
        "https://upload-challenge.csbc.com",
        "https://suspicious.csbc.com",
        "https://csbc-upload.netlify.app"
    ]
    
    print("[*] Scanning for challenge URL...")
    
    for url in possible_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[+] Found active site: {url}")
                
                # Check if it looks like the challenge
                content = response.text.lower()
                if any(keyword in content for keyword in ['suspicious', 'upload', 'csbc', 'developer', 'logs']):
                    print(f"[+] Likely challenge site: {url}")
                    analyze_site(url, response.text)
                    return url
                    
        except Exception as e:
            continue
    
    # If no automatic discovery, ask user
    print("\n[!] Could not automatically discover challenge URL")
    url = input("[?] Please enter the challenge URL: ").strip()
    if url:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                analyze_site(url, response.text)
                return url
        except:
            print(f"[!] Could not connect to {url}")
    
    return None

def analyze_site(url, content):
    """Analyze the challenge site"""
    print(f"\n[*] Analyzing {url}")
    print("-" * 60)
    
    # Look for challenge description
    if 'suspicious' in content.lower() and 'upload' in content.lower():
        print("[+] Confirmed: This appears to be the Suspicious Upload challenge")
    
    # Look for flag format hints
    flag_hints = re.findall(r'HW\{[^}]*\}', content)
    if flag_hints:
        print(f"[+] Flag format confirmed: {flag_hints[0]}")
    
    # Look for developer mentions
    dev_mentions = re.findall(r'.{0,50}developer.{0,50}', content, re.IGNORECASE)
    if dev_mentions:
        print("[+] Developer mentions found:")
        for mention in dev_mentions[:3]:
            print(f"    {mention.strip()}")
    
    # Look for log mentions
    log_mentions = re.findall(r'.{0,30}log.{0,30}', content, re.IGNORECASE)
    if log_mentions:
        print("[+] Log mentions found:")
        for mention in log_mentions[:3]:
            print(f"    {mention.strip()}")
    
    # Look for upload functionality
    upload_forms = re.findall(r'<form[^>]*upload[^>]*>', content, re.IGNORECASE)
    if upload_forms:
        print("[+] Upload forms found:")
        for form in upload_forms:
            print(f"    {form}")
    
    # Check for common endpoints
    print("\n[*] Testing common endpoints...")
    test_endpoints(url)

def test_endpoints(base_url):
    """Test common endpoints"""
    endpoints = [
        '/admin',
        '/logs', 
        '/log',
        '/uploads',
        '/files',
        '/access.log',
        '/error.log',
        '/server.log',
        '/admin/logs',
        '/api/logs',
        '/debug',
        '/info',
        '/status'
    ]
    
    session = requests.Session()
    found_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                found_endpoints.append((endpoint, len(response.text)))
                print(f"[+] {endpoint} - {response.status_code} ({len(response.text)} bytes)")
                
                # Quick check for flag
                if 'HW{' in response.text:
                    flag_match = re.search(r'HW\{[^}]+\}', response.text)
                    if flag_match:
                        print(f"    🚩 FLAG FOUND: {flag_match.group()}")
                        
            elif response.status_code in [401, 403]:
                print(f"[!] {endpoint} - {response.status_code} (Protected)")
            elif response.status_code == 302:
                print(f"[!] {endpoint} - {response.status_code} (Redirect)")
                
        except:
            continue
    
    if found_endpoints:
        print(f"\n[+] Found {len(found_endpoints)} accessible endpoints")
        return found_endpoints
    else:
        print("[-] No common endpoints found")
        return []

def quick_log_check(base_url):
    """Quick check for log files"""
    print("\n[*] Quick log file check...")
    
    log_files = [
        '/access.log',
        '/error.log',
        '/server.log',
        '/apache.log',
        '/nginx.log',
        '/app.log',
        '/debug.log',
        '/upload.log',
        '/admin.log',
        '/security.log'
    ]
    
    session = requests.Session()
    
    for log_file in log_files:
        try:
            response = session.get(f"{base_url}{log_file}", timeout=5)
            if response.status_code == 200 and response.text:
                print(f"[+] Found log: {log_file} ({len(response.text)} bytes)")
                
                # Quick analysis
                lines = response.text.split('\n')
                print(f"    Lines: {len(lines)}")
                
                # Look for suspicious entries
                suspicious_count = 0
                for line in lines[:100]:  # Check first 100 lines
                    if any(keyword in line.lower() for keyword in ['admin', 'upload', 'backdoor', 'shell']):
                        suspicious_count += 1
                
                if suspicious_count > 0:
                    print(f"    [!] {suspicious_count} suspicious entries found")
                
                # Check for flag
                if 'HW{' in response.text:
                    flag_match = re.search(r'HW\{[^}]+\}', response.text)
                    if flag_match:
                        print(f"    🚩 FLAG FOUND IN LOG: {flag_match.group()}")
                        return flag_match.group()
                        
        except:
            continue
    
    return None

def quick_steganography_check(base_url):
    """Quick check for files that might contain steganography"""
    print("\n[*] Quick steganography file check...")
    
    file_paths = [
        '/image.jpg',
        '/photo.png', 
        '/upload.jpg',
        '/file.txt',
        '/data.txt',
        '/secret.jpg',
        '/hidden.png',
        '/admin.jpg',
        '/uploads/image.jpg',
        '/files/photo.png'
    ]
    
    session = requests.Session()
    found_files = []
    
    for file_path in file_paths:
        try:
            response = session.get(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                found_files.append((file_path, len(response.content)))
                print(f"[+] Found file: {file_path} ({len(response.content)} bytes)")
                
                # Quick strings check for text files
                if file_path.endswith('.txt'):
                    if 'HW{' in response.text:
                        flag_match = re.search(r'HW\{[^}]+\}', response.text)
                        if flag_match:
                            print(f"    🚩 FLAG FOUND IN FILE: {flag_match.group()}")
                            return flag_match.group()
                            
        except:
            continue
    
    if found_files:
        print(f"[+] Found {len(found_files)} files for steganography analysis")
    
    return None

def main():
    # Discover challenge
    challenge_url = discover_challenge()
    
    if not challenge_url:
        print("\n[!] Could not discover challenge URL")
        return
    
    print(f"\n[*] Challenge URL: {challenge_url}")
    
    # Quick checks
    flag = quick_log_check(challenge_url)
    if flag:
        print(f"\n🎉 FLAG FOUND: {flag}")
        return
    
    flag = quick_steganography_check(challenge_url)
    if flag:
        print(f"\n🎉 FLAG FOUND: {flag}")
        return
    
    print("\n" + "="*80)
    print("RECONNAISSANCE COMPLETE")
    print("="*80)
    print("Next steps:")
    print("1. Run the full solver with the discovered URL:")
    print(f"   python3 suspicious_upload_advanced.py {challenge_url}")
    print("2. Manual investigation of discovered endpoints and files")
    print("3. Advanced steganography analysis of found files")

if __name__ == "__main__":
    main()