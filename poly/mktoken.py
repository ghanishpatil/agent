import requests
r = requests.post("https://webhook.site/token", json={}, timeout=30)
print("status", r.status_code)
print(r.text[:400])
