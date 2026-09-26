import requests, re

BASE = 'https://outfjord-your-notes-1860d6ea0037.chall.nnsc.tf'
s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0'})

def clean(h):
    t=re.sub(r'<script.*?</script>','',h,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'<[^>]+>','',t); return re.sub(r'\s+',' ',t).strip()

r = s.get(BASE+'/', timeout=20)
print('Status:', r.status_code)
print('=== RAW (first 5000) ===')
print(r.text[:5000])
print('\n=== JS ===')
print(re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text))
print('\n=== forms/endpoints ===')
print('forms:', re.findall(r'<form[^>]*>', r.text))
print('fetch:', re.findall(r'fetch\(["\'`]([^"\'`]+)', r.text))
print('actions:', re.findall(r'action=["\']([^"\']+)', r.text))
