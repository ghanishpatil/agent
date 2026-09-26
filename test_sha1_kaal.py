#!/usr/bin/env python3
"""
Test the SHA1 hash of KAAL more carefully
"""

from pwn import *
import time
import hashlib

context.log_level = 'info'

target_ip = "13.206.58.35"
target_port = 9999

def knock_ports():
    sequence = [9000, 2600, 1337]
    for port in sequence:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((target_ip, port))
            s.close()
        except:
            pass
        time.sleep(0.2)
    time.sleep(0.8)

# Calculate the hash
password = hashlib.sha1(b"KAAL").hexdigest()
log.info(f"Testing password: {password}")

knock_ports()
conn = remote(target_ip, target_port)

banner = conn.recvuntil(b"password:")
log.info(f"Banner received")

conn.sendline(password.encode())
log.info(f"Sent password: {password}")

# Try to receive all data
try:
    response = conn.recvall(timeout=5)
    log.success(f"Response ({len(response)} bytes):")
    print(response.decode('utf-8', errors='ignore'))
    
    # Check if there's a download link or flag
    if b"http" in response or b"download" in response.lower():
        log.success("Found download link!")
    if b"flag" in response.lower() or b"kaal{" in response.lower():
        log.success("Found flag!")
        
except Exception as e:
    log.error(f"Error: {e}")

conn.close()

# Also check the web service after this
log.info("Checking web service...")
import requests

try:
    r = requests.get(f"http://{target_ip}:8080/challenge", timeout=3)
    log.info(f"Web /challenge status: {r.status_code}")
    if r.status_code != 403:
        print(r.text)
except Exception as e:
    log.error(f"Web error: {e}")
