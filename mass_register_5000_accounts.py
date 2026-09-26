#!/usr/bin/env python3
"""
Phantom Registrations - Mass Account Creator
Creates 5000 legitimate accounts and exports to CSV
"""

import requests
import time
import csv
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

TARGET = "https://cyberspacevr.in"
API_TARGET = "https://api.cyberspacevr.in"
TOTAL_ACCOUNTS = 5000
BATCH_SIZE = 50
MAX_WORKERS = 10

# Thread-safe counter and storage
lock = Lock()
created_accounts = []
success_count = 0
fail_count = 0

def generate_username(index):
    """Generate unique username"""
    return f"phantom_{index:05d}"

def generate_email(index):
    """Generate unique email"""
    return f"phantom{index:05d}@ctftest.local"

def generate_password(index):
    """Generate secure password"""
    return f"PhantomPass{index:05d}!@#"

def register_account(index):
    """Register a single account"""
    global success_count, fail_count
    
    username = generate_username(index)
    email = generate_email(index)
    password = generate_password(index)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    try:
        # Correct API endpoint: /v1/auth/register
        data = {
            'username': username,
            'email': email,
            'password': password
        }
        
        resp = session.post(f"{API_TARGET}/v1/auth/register", json=data, timeout=10)
        
        if resp.status_code in [200, 201]:
            with lock:
                created_accounts.append({
                    'index': index,
                    'username': username,
                    'email': email,
                    'password': password,
                    'status': 'success'
                })
                success_count += 1
            return True, username
        
        with lock:
            fail_count += 1
        return False, f"{username} (status: {resp.status_code}, msg: {resp.text[:100]})"
        
    except Exception as e:
        with lock:
            fail_count += 1
        return False, f"{username} (error: {str(e)[:50]})"

def save_to_csv(filename='phantom_accounts.csv'):
    """Save all created accounts to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'username', 'email', 'password', 'status'])
        writer.writeheader()
        writer.writerows(sorted(created_accounts, key=lambda x: x['index']))
    print(f"\n[+] Saved {len(created_accounts)} accounts to {filename}")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     PHANTOM REGISTRATIONS - MASS ACCOUNT CREATOR          ║
    ║     Target: 5000 legitimate accounts                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    start_time = time.time()
    
    print(f"[*] Starting mass registration of {TOTAL_ACCOUNTS} accounts...")
    print(f"[*] Using {MAX_WORKERS} concurrent workers")
    print(f"[*] Batch size: {BATCH_SIZE}")
    print()
    
    # Process in batches to avoid overwhelming the server
    for batch_start in range(1, TOTAL_ACCOUNTS + 1, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TOTAL_ACCOUNTS + 1)
        batch_num = (batch_start - 1) // BATCH_SIZE + 1
        total_batches = (TOTAL_ACCOUNTS + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"[*] Processing batch {batch_num}/{total_batches} (accounts {batch_start}-{batch_end-1})...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(register_account, i): i for i in range(batch_start, batch_end)}
            
            for future in as_completed(futures):
                success, info = future.result()
                if success:
                    if success_count % 100 == 0:
                        print(f"    ✓ {success_count} accounts created successfully")
                else:
                    if fail_count % 50 == 0 and fail_count > 0:
                        print(f"    ✗ {fail_count} failures so far")
        
        # Small delay between batches
        if batch_end <= TOTAL_ACCOUNTS:
            time.sleep(1)
        
        # Save progress periodically
        if batch_num % 10 == 0:
            save_to_csv(f'phantom_accounts_progress_{batch_num}.csv')
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print("REGISTRATION COMPLETE")
    print("="*60)
    print(f"Total accounts created: {success_count}/{TOTAL_ACCOUNTS}")
    print(f"Failed attempts: {fail_count}")
    print(f"Success rate: {(success_count/TOTAL_ACCOUNTS)*100:.2f}%")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Average rate: {success_count/elapsed:.2f} accounts/second")
    
    # Save final CSV
    save_to_csv('phantom_accounts_final.csv')
    
    # Display sample accounts
    print("\n[*] Sample accounts (first 5):")
    for acc in created_accounts[:5]:
        print(f"    {acc['username']} | {acc['email']} | {acc['password']}")
    
    print("\n[*] Next steps:")
    print("    1. Verify accounts are in database")
    print("    2. Test login with sample accounts")
    print("    3. Submit phantom_accounts_final.csv to the challenge")
    print("    4. Wait for next phase trigger")

if __name__ == "__main__":
    main()
