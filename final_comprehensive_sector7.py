#!/usr/bin/env python3
"""
Final comprehensive SECTOR-7 password attempt
Every possible interpretation of the hint
"""

import socket
import time
import hashlib

TARGET_IP = "13.206.58.35"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    for port in KNOCK_SEQUENCE:
        try:
            s = socket.socket()
            s.settimeout(0.3)
            s.connect((TARGET_IP, port))
            s.close()
        except:
            pass
        time.sleep(0.2)

def try_pwd(pwd):
    try:
        knock_ports()
        time.sleep(0.3)
        
        s = socket.socket()
        s.settimeout(3)
        s.connect((TARGET_IP, SERVICE_PORT))
        
        s.recv(4096)
        s.send((pwd + "\n").encode())
        time.sleep(0.3)
        
        resp = s.recv(4096).decode('utf-8', errors='ignore')
        s.close()
        
        if "denied" not in resp.lower() and "incorrect" not in resp.lower():
            print(f"\n[!!!] SUCCESS: '{pwd}'")
            print(resp)
            return True
        return False
    except:
        return False

passwords = []

# 1. Alexander Graham Bell references
passwords.extend([
    "AlexanderGrahamBell",
    "alexandergrahambell",
    "Bell",
    "bell",
    "AGB",
    "agb",
    "Graham",
    "graham",
])

# 2. First telephone number (historical)
passwords.extend([
    "1876",  # Year telephone was invented
    "18760310",  # March 10, 1876
    "MrWatson",
    "mrwatson",
    "Watson",
    "watson",
])

# 3. Test/dummy phone numbers
passwords.extend([
    "555-1212",
    "5551212",
    "555-0100",
    "5550100",
    "867-5309",  # Tommy Tutone song
    "8675309",
])

# 4. IMEI Luhn check digit
passwords.extend([
    "Luhn",
    "luhn",
    "checkdigit",
    "CheckDigit",
])

# 5. Specific IMEI patterns (TAC codes for major manufacturers)
passwords.extend([
    "35",  # Common IMEI start
    "356",
    "3569",
    "35699680",  # Apple TAC
])

# 6. Maybe "His" = God/Creator number
passwords.extend([
    "777",
    "666",
    "000",
    "111",
])

# 7. Pi, E, or other mathematical constants (phone-related)
passwords.extend([
    "314159",  # Pi
    "271828",  # E
    "161803",  # Golden ratio
])

# 8. Maybe it's a hash of something
for word in ["KAAL", "SECTOR-7", "9000-2600-1337", "IMEI"]:
    passwords.append(hashlib.md5(word.encode()).hexdigest()[:16])
    passwords.append(hashlib.md5(word.encode()).hexdigest()[:8])

# 9. Phone system special numbers
passwords.extend([
    "*#*#*#",
    "###",
    "***",
    "*0*",
    "#0#",
])

# 10. Maybe it's about SIM card
passwords.extend([
    "SIM",
    "sim",
    "ICCID",
    "iccid",
    "IMSI",
    "imsi",
])

# 11. Network codes
passwords.extend([
    "MCC",
    "mcc",
    "MNC",
    "mnc",
])

# 12. Maybe "His number" = the challenge number/ID
passwords.extend([
    "SECTOR7",
    "sector7",
    "7",
    "seven",
    "Seven",
    "SEVEN",
])

# 13. Try with the hint itself
passwords.extend([
    "HisNumber",
    "hisnumber",
    "his-number",
    "EveryPhone",
    "everyphone",
])

# 14. Phone phreaking boxes
passwords.extend([
    "blue",
    "red",
    "black",
    "beige",
    "box",
])

# 15. Maybe it's the service port itself
passwords.extend([
    "9999",
    "8080",
    "port9999",
    "port8080",
])

# Remove duplicates
passwords = list(dict.fromkeys(passwords))

print(f"[*] Final Comprehensive Test - {len(passwords)} passwords\n")

for i, pwd in enumerate(passwords, 1):
    print(f"[{i}/{len(passwords)}] {pwd}", end="... ")
    if try_pwd(pwd):
        break
    else:
        print("✗")
    time.sleep(0.3)

print("\n[-] All attempts exhausted")
print("[*] This challenge likely requires:")
print("    1. Binary analysis (need to get the binary somehow)")
print("    2. Or a very specific password we haven't thought of")
print("    3. Or exploitation via buffer overflow")
