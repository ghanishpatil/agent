#!/usr/bin/env python3
"""
Mount FAT32 disk image and explore filesystem
"""
import os
import subprocess

disk_path = "disk1_extracted/disk/Disk2.001"

print("[*] Attempting to explore FAT32 filesystem...")

# Try using 7-Zip to extract (works on Windows)
print("\n[*] Trying to extract with 7-Zip...")
try:
    result = subprocess.run(['7z', 'l', disk_path], capture_output=True, text=True)
    if result.returncode == 0:
        print("[+] 7-Zip can read the disk image!")
        print(result.stdout)
        
        # Extract all files
        print("\n[*] Extracting all files...")
        result = subprocess.run(['7z', 'x', disk_path, '-odisk_contents', '-y'], 
                              capture_output=True, text=True)
        print(result.stdout)
    else:
        print("[-] 7-Zip failed")
except FileNotFoundError:
    print("[-] 7-Zip not found")

# Alternative: Try using Python libraries
print("\n[*] Trying Python filesystem libraries...")

try:
    import pytsk3
    print("[+] pytsk3 available, analyzing filesystem...")
    
    img = pytsk3.Img_Info(disk_path)
    fs = pytsk3.FS_Info(img)
    
    print(f"[+] Filesystem type: {fs.info.ftype}")
    
    def list_directory(directory, path="/"):
        for entry in directory:
            if entry.info.name.name in [b'.', b'..']:
                continue
            
            name = entry.info.name.name.decode('utf-8', errors='ignore')
            full_path = os.path.join(path, name)
            
            print(f"  {full_path}")
            
            # If it's a directory, recurse
            if entry.info.meta and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                try:
                    sub_dir = entry.as_directory()
                    list_directory(sub_dir, full_path)
                except:
                    pass
            
            # If it's a file, check for flag
            elif entry.info.meta and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
                try:
                    file_obj = entry.read_random(0, entry.info.meta.size)
                    if b'Kaal{' in file_obj:
                        print(f"    [+] FLAG FOUND IN: {full_path}")
                        idx = file_obj.find(b'Kaal{')
                        flag_data = file_obj[idx:idx+200]
                        end_idx = flag_data.find(b'}')
                        if end_idx != -1:
                            flag = flag_data[:end_idx+1].decode('utf-8', errors='ignore')
                            print(f"    [+] FLAG: {flag}")
                except:
                    pass
    
    print("\n[*] Listing all files:")
    root_dir = fs.open_dir(path="/")
    list_directory(root_dir)
    
except ImportError:
    print("[-] pytsk3 not available")
    print("[*] Install with: pip install pytsk3")

print("\n[*] Done!")
