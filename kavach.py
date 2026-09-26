import requests, re, json, base64

BASE = 'https://kavach-x.onrender.com'
s = requests.Session()

def verify(layer_id, code):
    r = s.post(f'{BASE}/verify', json={'layer_id': str(layer_id), 'code': code}, timeout=12)
    print(f'L{layer_id} [{code}]: {r.text[:200]}')
    return r.json()

verify('1', 'ABHIMANYU')
verify('2', 'DRONACHARYA')

# Layer 3
print('\n=== LAYER 3 ===')
r = s.get(f'{BASE}/challenge/3', timeout=12)
comments = re.findall(r'<!--(.*?)-->', r.text, re.S)
print('Comments:', comments)
data_boxes = re.findall(r'class="data-box".*?>(.*?)</div>', r.text, re.S)
print('Data boxes:', [d.strip() for d in data_boxes])

t = re.sub(r'<script.*?</script>', '', r.text, flags=re.S)
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', '', t)
t = re.sub(r'\s+', ' ', t).strip()
print('Readable:', t[:2000])
