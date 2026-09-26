#!/usr/bin/env python3
"""
Use binwalk-like analysis to find embedded files
"""

import subprocess
import os

mp3_file = "chall_media/chall_media.mp3"

print("[*] Trying binwalk to extract embedded files...")

try:
    # Try binwalk
    result = subprocess.run(['binwalk', '-e', mp3_file], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
except FileNotFoundError:
    print("[-] binwalk not installed")

print("\n[*] Trying foremost...")
try:
    result = subprocess.run(['foremost', '-i', mp3_file, '-o', 'foremost_output'], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    
    # Check output
    if os.path.exists('foremost_output'):
        for root, dirs, files in os.walk('foremost_output'):
            for file in files:
                filepath = os.path.join(root, file)
                print(f"    Found: {filepath}")
                with open(filepath, 'rb') as f:
                    data = f.read()
                    if b'Kaal{' in data:
                        import re
                        flags = re.findall(rb'Kaal\{[^}]+\}', data)
                        for flag in flags:
                            print(f"    [+] FLAG: {flag.decode('utf-8', errors='ignore')}")
except FileNotFoundError:
    print("[-] foremost not installed")

print("\n[*] Manual carving for common file types...")

with open(mp3_file, 'rb') as f:
    data = f.read()

# Look for file signatures
signatures = {
    'PNG': b'\x89PNG\r\n\x1a\n',
    'JPEG': b'\xff\xd8\xff',
    'GIF': b'GIF89a',
    'PDF': b'%PDF',
    'ZIP': b'PK\x03\x04',
    'RAR': b'Rar!\x1a\x07',
    'TAR': b'ustar',
    'BMP': b'BM',
    'MP4': b'ftyp',
}

print("\n[*] Searching for embedded file signatures...")
for name, sig in signatures.items():
    positions = []
    pos = 0
    while True:
        pos = data.find(sig, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    
    if positions:
        print(f"    {name}: found at positions {positions}")
        
        # Try to extract
        for i, pos in enumerate(positions):
            if pos > 1000:  # Not at the beginning
                print(f"        Extracting {name} from position {pos}...")
                
                # Determine end position based on file type
                if name == 'PNG':
                    end_marker = b'IEND\xae\x42\x60\x82'
                    end_pos = data.find(end_marker, pos)
                    if end_pos != -1:
                        file_data = data[pos:end_pos + len(end_marker)]
                        output_file = f'extracted_{name}_{i}.png'
                        with open(output_file, 'wb') as f:
                            f.write(file_data)
                        print(f"            Saved to {output_file}")
                
                elif name == 'JPEG':
                    end_marker = b'\xff\xd9'
                    end_pos = data.find(end_marker, pos + 2)
                    if end_pos != -1:
                        file_data = data[pos:end_pos + 2]
                        output_file = f'extracted_{name}_{i}.jpg'
                        with open(output_file, 'wb') as f:
                            f.write(file_data)
                        print(f"            Saved to {output_file}")
                
                elif name == 'ZIP':
                    # ZIP files are tricky, just save from position to end
                    file_data = data[pos:]
                    output_file = f'extracted_{name}_{i}.zip'
                    with open(output_file, 'wb') as f:
                        f.write(file_data)
                    print(f"            Saved to {output_file}")
                    
                    # Try to extract
                    import zipfile
                    try:
                        with zipfile.ZipFile(output_file, 'r') as zf:
                            print(f"            ZIP contents: {zf.namelist()}")
                            zf.extractall(f'extracted_zip_{i}')
                            
                            # Check for flag
                            for filename in zf.namelist():
                                extracted_path = os.path.join(f'extracted_zip_{i}', filename)
                                if os.path.isfile(extracted_path):
                                    with open(extracted_path, 'rb') as ef:
                                        extracted_data = ef.read()
                                        import re
                                        flag_match = re.search(rb'Kaal\{[^}]+\}', extracted_data)
                                        if flag_match:
                                            print(f"            [+] FLAG IN {filename}: {flag_match.group().decode('utf-8', errors='ignore')}")
                    except Exception as e:
                        print(f"            Could not extract ZIP: {e}")

print("\n[*] Analysis complete!")
