import requests
from bs4 import BeautifulSoup
import re

base_url = "http://138.199.163.92:10675"

# Get the docs page HTML
print("=== Fetching /docs page ===")
response = requests.get(f"{base_url}/docs")
html = response.text

# Look for any hidden flags or hints in the HTML
print("\n=== Searching for flags in HTML ===")
if "Kaal{" in html:
    print("FLAG FOUND IN HTML!")
    # Extract the flag
    flags = re.findall(r'Kaal\{[^}]+\}', html)
    for flag in flags:
        print(f"Flag: {flag}")
else:
    print("No flag found in HTML")

# Look for JavaScript or hidden comments
print("\n=== Checking for hints in HTML ===")
soup = BeautifulSoup(html, 'html.parser')

# Check comments
comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
if comments:
    print("HTML Comments found:")
    for comment in comments:
        print(f"  {comment}")

# Check for script tags
scripts = soup.find_all('script')
print(f"\nFound {len(scripts)} script tags")
for i, script in enumerate(scripts):
    if script.string and ('flag' in script.string.lower() or 'kaal' in script.string.lower()):
        print(f"\nScript {i} contains 'flag' or 'kaal':")
        print(script.string[:500])

# Check meta tags
metas = soup.find_all('meta')
print(f"\nFound {len(metas)} meta tags")
for meta in metas:
    if meta.get('content') and ('flag' in str(meta.get('content')).lower() or 'kaal' in str(meta.get('content')).lower()):
        print(f"Meta tag: {meta}")

# Look for any data attributes or hidden fields
print("\n=== Checking for data attributes ===")
all_tags = soup.find_all(attrs={"data-flag": True})
if all_tags:
    print("Found tags with data-flag attribute:")
    for tag in all_tags:
        print(f"  {tag}")

# Check if there's a robots.txt or other common files
print("\n=== Checking common files ===")
common_files = ["/robots.txt", "/sitemap.xml", "/.well-known/security.txt", "/flag.txt", "/secret.txt"]
for file in common_files:
    try:
        response = requests.get(f"{base_url}{file}")
        if response.status_code == 200:
            print(f"\n{file} exists!")
            print(f"Content: {response.text[:200]}")
    except:
        pass

# Save the HTML for manual inspection
with open("kaalchakra_docs.html", "w", encoding="utf-8") as f:
    f.write(html)
print("\n\nHTML saved to kaalchakra_docs.html for manual inspection")
