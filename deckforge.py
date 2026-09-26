import requests, re

BASE = 'http://fad4fa65501e0c52f811e82ff7b1afca.playat.flagyard.com'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

r = s.get(BASE + '/', timeout=20)
# Extract inline script logic
scripts = re.findall(r'<script>(.*?)</script>', r.text, re.S)
for sc in scripts:
    print('=== SCRIPT ===')
    print(sc[:3000])

# Also show the body HTML (form area)
body_start = r.text.find('<body')
print('\n=== BODY HTML ===')
body = r.text[body_start:body_start+3000]
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
print(body)
