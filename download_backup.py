#!/usr/bin/env python3
"""
Download and analyze the secret backup file
"""

import requests
import zipfile
import os

def download_backup():
    """Download the secret backup file"""
    url = "https://admin-panel-ctf.onrender.com/secret-backup.zip"
    
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            with open("secret-backup.zip", "wb") as f:
                f.write(response.content)
            print(f"Downloaded {len(response.content)} bytes")
            return True
        else:
            print(f"Failed to download: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading backup: {e}")
        return False

def analyze_backup():
    """Analyze the backup file"""
    if not os.path.exists("secret-backup.zip"):
        print("Backup file not found")
        return
    
    try:
        with zipfile.ZipFile("secret-backup.zip", 'r') as zip_ref:
            print("Backup file contents:")
            for file_info in zip_ref.filelist:
                print(f"  {file_info.filename} ({file_info.file_size} bytes)")
            
            # Extract all files
            print("\nExtracting files...")
            zip_ref.extractall("backup_extracted")
            
            # Read and display contents
            for file_info in zip_ref.filelist:
                if not file_info.is_dir():
                    file_path = os.path.join("backup_extracted", file_info.filename)
                    if os.path.exists(file_path):
                        print(f"\n=== {file_info.filename} ===")
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                print(content)
                        except UnicodeDecodeError:
                            print("Binary file - showing hex dump:")
                            with open(file_path, 'rb') as f:
                                data = f.read()
                                print(data.hex()[:200] + "..." if len(data) > 100 else data.hex())
                        except Exception as e:
                            print(f"Error reading file: {e}")
                            
    except zipfile.BadZipFile:
        print("Invalid zip file")
    except Exception as e:
        print(f"Error analyzing backup: {e}")

def main():
    print("=== Secret Backup Analysis ===")
    
    if download_backup():
        analyze_backup()
    else:
        print("Failed to download backup file")

if __name__ == "__main__":
    main()