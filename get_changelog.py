import requests
import json
import gzip
import tarfile
import io

def get_token(image):
    url = f"https://ghcr.io/token?scope=repository:{image}:pull"
    r = requests.get(url)
    return r.json().get('token', '')

def get_blob(image, digest, token):
    url = f"https://ghcr.io/v2/{image}/blobs/{digest}"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, stream=True)
    return r

image = "talldwarfhosting/stolen-schematics-game-server-prerelease"
token = get_token(image)

# Layer 3 is the CHANGELOG.md layer (size 547)
layer_digest = "sha256:40c2cdce1490945ee12e1759c15f760351639678bf9b8520b6c86775398690bd"
print("Downloading CHANGELOG.md layer...")
r = get_blob(image, layer_digest, token)
content = r.content
gz = gzip.GzipFile(fileobj=io.BytesIO(content))
tar = tarfile.open(fileobj=gz, mode='r')

for member in tar.getmembers():
    print(f"File: {member.name} (size: {member.size})")
    if member.isfile():
        f = tar.extractfile(member)
        if f:
            print(f.read().decode('utf-8', errors='replace'))
tar.close()
