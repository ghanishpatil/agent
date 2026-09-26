#!/usr/bin/env python3
"""
Comprehensive analysis of all page resources
"""

import requests
import re

URL = "http://138.199.163.92:12871"

def analyze_all_resources():
    """Check HTML, CSS, JS, and image for hidden data"""
    
    # Check HTML
    print("="*70)
    print("HTML Analysis")
    print("="*70)
    r = requests.get(URL)
    html = r.text
    
    # Look for HTML comments
    comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
    if comments:
        print("[+] HTML Comments found:")
        for c in comments:
            print(f"    {c.strip()}")
    else:
        print("[-] No HTML comments")
    
    # Look for hidden divs or data attributes
    hidden_divs = re.findall(r'<div[^>]*style="display:\s*none"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if hidden_divs:
        print("[+] Hidden divs found:")
        for d in hidden_divs:
            print(f"    {d.strip()}")
    
    # Look for data attributes
    data_attrs = re.findall(r'data-[a-z-]+="([^"]+)"', html, re.IGNORECASE)
    if data_attrs:
        print("[+] Data attributes found:")
        for attr in data_attrs:
            print(f"    {attr}")
    
    # Check CSS
    print("\n" + "="*70)
    print("CSS Analysis")
    print("="*70)
    r = requests.get(f"{URL}/style.css")
    css = r.text
    
    # Look for CSS comments
    css_comments = re.findall(r'/\*(.*?)\*/', css, re.DOTALL)
    if css_comments:
        print("[+] CSS Comments found:")
        for c in css_comments:
            clean = c.strip()
            if len(clean) > 10:  # Skip short comments
                print(f"    {clean[:200]}")
    
    # Look for content properties (can hide text)
    content_props = re.findall(r'content:\s*["\']([^"\']+)["\']', css)
    if content_props:
        print("[+] CSS content properties:")
        for prop in content_props:
            print(f"    {prop}")
    
    # Check JavaScript
    print("\n" + "="*70)
    print("JavaScript Analysis")
    print("="*70)
    r = requests.get(f"{URL}/script.js")
    js = r.text
    
    # Look for JS comments
    js_comments = re.findall(r'/\*(.*?)\*/|//(.+)$', js, re.DOTALL | re.MULTILINE)
    if js_comments:
        print("[+] JS Comments found:")
        for c in js_comments:
            comment_text = c[0] if c[0] else c[1]
            if comment_text.strip() and len(comment_text.strip()) > 5:
                print(f"    {comment_text.strip()}")
    
    # Look for suspicious strings
    strings = re.findall(r'["\']([^"\']{20,})["\']', js)
    if strings:
        print("[+] Long strings in JS:")
        for s in strings[:10]:  # First 10
            if 'http' not in s and 'font' not in s:
                print(f"    {s[:100]}")
    
    # Look for base64 or hex strings
    b64_pattern = re.findall(r'[A-Za-z0-9+/]{40,}={0,2}', js)
    if b64_pattern:
        print("[+] Possible base64 strings:")
        for b in b64_pattern[:5]:
            print(f"    {b[:80]}")
    
    # Check image
    print("\n" + "="*70)
    print("Image Analysis")
    print("="*70)
    r = requests.get(f"{URL}/image.png")
    img_data = r.content
    
    # Check for text strings in image
    text_strings = re.findall(b'[A-Za-z0-9_]{10,}', img_data)
    if text_strings:
        print("[+] Text strings in image:")
        for s in text_strings[:20]:
            decoded = s.decode('utf-8', errors='ignore')
            if 'kaal' in decoded.lower() or 'flag' in decoded.lower():
                print(f"    [!] {decoded}")
            elif len(decoded) > 15:
                print(f"    {decoded}")
    
    # Check for Kaal{ pattern
    if b'Kaal{' in img_data:
        print("[!] Found 'Kaal{' in image!")
        idx = img_data.find(b'Kaal{')
        flag_area = img_data[idx:idx+100]
        print(f"    {flag_area}")
    
    # Check PNG chunks for text
    print("\n[*] Checking PNG text chunks...")
    pos = 8  # Skip PNG signature
    while pos < len(img_data) - 12:
        try:
            length = int.from_bytes(img_data[pos:pos+4], 'big')
            chunk_type = img_data[pos+4:pos+8].decode('ascii', errors='ignore')
            chunk_data = img_data[pos+8:pos+8+length]
            
            if chunk_type in ['tEXt', 'zTXt', 'iTXt', 'tIME']:
                print(f"[+] {chunk_type} chunk: {chunk_data[:100]}")
            
            pos += 12 + length
        except:
            break

if __name__ == "__main__":
    analyze_all_resources()
