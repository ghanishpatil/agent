import subprocess
import os
from PIL import Image
import numpy as np

image_path = r"D:\mission-git-hackss\board.png"

print("="*80)
print("COMPREHENSIVE STEGANOGRAPHY ANALYSIS")
print("="*80)

# Check if file exists locally
if not os.path.exists("board.png"):
    import shutil
    shutil.copy(image_path, "board.png")
    print("Copied image to local directory: board.png")
else:
    print("Using local board.png")

# 1. STRINGS - Look for embedded strings
print("\n[1. STRINGS ANALYSIS]")
try:
    result = subprocess.run(['strings', 'board.png'], capture_output=True, text=True, timeout=10)
    output = result.stdout
    if 'KAAL' in output or 'FLAG' in output or 'flag' in output:
        print("FOUND FLAG IN STRINGS:")
        for line in output.split('\n'):
            if 'KAAL' in line or 'FLAG' in line or 'flag' in line:
                print(f"  {line}")
    else:
        print("No obvious flags in strings output")
        # Show interesting strings
        lines = [l for l in output.split('\n') if len(l) > 10]
        if lines:
            print(f"Found {len(lines)} strings, showing first 10:")
            for line in lines[:10]:
                print(f"  {line}")
except Exception as e:
    print(f"strings command failed: {e}")
    # Try manual string extraction
    with open('board.png', 'rb') as f:
        data = f.read()
        # Extract printable strings
        current = []
        strings_found = []
        for byte in data:
            if 32 <= byte <= 126:
                current.append(chr(byte))
            else:
                if len(current) >= 4:
                    strings_found.append(''.join(current))
                current = []
        
        # Check for flags
        for s in strings_found:
            if 'KAAL' in s or 'FLAG' in s:
                print(f"FOUND: {s}")

# 2. EXIFTOOL - Check metadata
print("\n[2. EXIFTOOL METADATA]")
try:
    result = subprocess.run(['exiftool', 'board.png'], capture_output=True, text=True, timeout=10)
    print(result.stdout)
    if 'KAAL' in result.stdout or 'FLAG' in result.stdout:
        print("*** FLAG FOUND IN METADATA ***")
except Exception as e:
    print(f"exiftool not available: {e}")

# 3. BINWALK - Check for embedded files
print("\n[3. BINWALK - EMBEDDED FILES]")
try:
    result = subprocess.run(['binwalk', 'board.png'], capture_output=True, text=True, timeout=10)
    print(result.stdout)
    
    # Extract if found
    if 'Zlib' in result.stdout or 'compressed' in result.stdout.lower():
        print("Attempting extraction...")
        subprocess.run(['binwalk', '-e', 'board.png'], timeout=30)
except Exception as e:
    print(f"binwalk not available: {e}")

# 4. FOREMOST - File carving
print("\n[4. FOREMOST - FILE CARVING]")
try:
    os.makedirs('foremost_output', exist_ok=True)
    result = subprocess.run(['foremost', '-i', 'board.png', '-o', 'foremost_output'], 
                          capture_output=True, text=True, timeout=30)
    print(result.stdout)
    
    # Check what was extracted
    if os.path.exists('foremost_output'):
        for root, dirs, files in os.walk('foremost_output'):
            for file in files:
                filepath = os.path.join(root, file)
                print(f"Extracted: {filepath}")
                with open(filepath, 'rb') as f:
                    content = f.read()
                    if b'KAAL' in content:
                        print(f"*** FLAG FOUND IN {filepath} ***")
except Exception as e:
    print(f"foremost not available: {e}")

# 5. ZSTEG - PNG/BMP steganography
print("\n[5. ZSTEG - PNG STEGANOGRAPHY]")
try:
    result = subprocess.run(['zsteg', 'board.png'], capture_output=True, text=True, timeout=30)
    print(result.stdout)
    if 'KAAL' in result.stdout or 'FLAG' in result.stdout:
        print("*** FLAG FOUND BY ZSTEG ***")
except Exception as e:
    print(f"zsteg not available: {e}")

# 6. STEGSOLVE - Try different bit planes
print("\n[6. BIT PLANE ANALYSIS]")
img = Image.open('board.png')
img_array = np.array(img)

for channel_idx, channel_name in enumerate(['R', 'G', 'B', 'A'][:img_array.shape[2] if len(img_array.shape) > 2 else 3]):
    for bit in range(8):
        print(f"  Extracting {channel_name} bit plane {bit}...")
        if len(img_array.shape) == 3:
            bit_plane = (img_array[:, :, channel_idx] >> bit) & 1
        else:
            bit_plane = (img_array >> bit) & 1
        
        # Convert to image
        bit_img = Image.fromarray((bit_plane * 255).astype(np.uint8))
        bit_img.save(f'bitplane_{channel_name}_{bit}.png')
        
        # Check if it looks like it has content
        unique_vals = np.unique(bit_plane)
        if len(unique_vals) > 1:
            # Check for patterns
            variance = np.var(bit_plane.astype(float))
            if variance > 0.1:  # Some variation
                print(f"    Bit plane {channel_name}_{bit} has interesting variance: {variance:.4f}")

# 7. STEGDETECT - Detect steganography
print("\n[7. STEGDETECT]")
try:
    result = subprocess.run(['stegdetect', 'board.png'], capture_output=True, text=True, timeout=10)
    print(result.stdout)
except Exception as e:
    print(f"stegdetect not available: {e}")

# 8. STEGHIDE - Try to extract (needs password)
print("\n[8. STEGHIDE EXTRACTION]")
passwords = ['', 'password', 'kaal', 'KAAL', 'board', 'chess', 'winner', 'black', 'white']
for pwd in passwords:
    try:
        result = subprocess.run(['steghide', 'extract', '-sf', 'board.png', '-p', pwd, '-xf', f'steghide_out_{pwd}.txt'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"SUCCESS with password: '{pwd}'")
            with open(f'steghide_out_{pwd}.txt', 'r') as f:
                content = f.read()
                print(f"Content: {content}")
                if 'KAAL' in content:
                    print("*** FLAG FOUND ***")
        elif 'could not extract' not in result.stderr.lower():
            print(f"Password '{pwd}': {result.stderr[:100]}")
    except Exception as e:
        pass

# 9. OUTGUESS
print("\n[9. OUTGUESS]")
try:
    result = subprocess.run(['outguess', '-r', 'board.png', 'outguess_output.txt'], 
                          capture_output=True, text=True, timeout=10)
    if os.path.exists('outguess_output.txt'):
        with open('outguess_output.txt', 'r') as f:
            content = f.read()
            if content:
                print(f"Extracted: {content}")
                if 'KAAL' in content:
                    print("*** FLAG FOUND ***")
except Exception as e:
    print(f"outguess not available: {e}")

# 10. STEGPY
print("\n[10. STEGPY]")
try:
    result = subprocess.run(['stegpy', 'board.png'], capture_output=True, text=True, timeout=10)
    print(result.stdout)
except Exception as e:
    print(f"stegpy not available: {e}")

print("\n" + "="*80)
print("Analysis complete. Check generated files for hidden data.")
print("="*80)
