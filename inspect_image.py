import requests
import json
import gzip
import tarfile
import io
import sys

def get_token(image):
    url = f"https://ghcr.io/token?scope=repository:{image}:pull"
    r = requests.get(url)
    return r.json().get('token', '')

def get_manifest(image, tag, token):
    url = f"https://ghcr.io/v2/{image}/manifests/{tag}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.oci.image.index.v1+json,application/vnd.docker.distribution.manifest.v2+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.oci.image.manifest.v1+json'
    }
    r = requests.get(url, headers=headers)
    print(f"Manifest Status: {r.status_code}")
    return r.json()

def get_blob(image, digest, token):
    url = f"https://ghcr.io/v2/{image}/blobs/{digest}"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, stream=True)
    return r

image = "talldwarfhosting/stolen-schematics-game-server-prerelease"
tag = "v2.5.39"
token = get_token(image)
print(f"Got token: {token[:50]}...")

# Get manifest
manifest = get_manifest(image, tag, token)
print(f"\nManifest:\n{json.dumps(manifest, indent=2)[:2000]}")

# If manifest list, get amd64
if manifest.get('manifests'):
    for m in manifest['manifests']:
        arch = m.get('platform', {}).get('architecture', '')
        print(f"  Platform: {arch}")
        if arch == 'amd64':
            print(f"--- Getting amd64 manifest: {m['digest']}")
            manifest = get_manifest(image, m['digest'], token)
            print(json.dumps(manifest, indent=2)[:2000])
            break

# Get config (contains Dockerfile history)
if manifest.get('config'):
    config_digest = manifest['config']['digest']
    print(f"\n=== CONFIG BLOB: {config_digest} ===")
    r = get_blob(image, config_digest, token)
    config = r.json()
    
    # Print the history (Dockerfile commands)
    if 'history' in config:
        print("\n=== DOCKERFILE HISTORY ===")
        for i, h in enumerate(config['history']):
            created_by = h.get('created_by', 'N/A')
            print(f"  Layer {i}: {created_by}")
    
    # Print full config
    print(f"\n=== FULL CONFIG ===")
    print(json.dumps(config, indent=2))

# Now download and extract the layers to find sync-loop.sh
if manifest.get('layers'):
    print(f"\n=== LAYERS ({len(manifest['layers'])}) ===")
    for i, layer in enumerate(manifest['layers']):
        digest = layer['digest']
        size = layer.get('size', 0)
        print(f"\n--- Layer {i}: {digest} (size: {size})")
        
        # Only download small layers (< 50MB) to find scripts
        if size < 50000000:
            print(f"  Downloading layer {i}...")
            r = get_blob(image, digest, token)
            
            try:
                # Decompress gzip and extract tar
                content = r.content
                gz = gzip.GzipFile(fileobj=io.BytesIO(content))
                tar = tarfile.open(fileobj=gz, mode='r')
                
                for member in tar.getmembers():
                    name = member.name
                    # Look for interesting files
                    if any(kw in name.lower() for kw in ['sync', 'script', 'entrypoint', 'flag', 'ssh', 'key', 'secret', '.conf', '.sh', '.properties', 'passwd', 'shadow']):
                        print(f"  FOUND: {name} (size: {member.size})")
                        if member.isfile() and member.size < 100000:
                            f = tar.extractfile(member)
                            if f:
                                content_str = f.read().decode('utf-8', errors='replace')
                                print(f"  CONTENT:\n{content_str}")
                tar.close()
            except Exception as e:
                print(f"  Error extracting: {e}")
        else:
            print(f"  Skipping large layer (size: {size})")
