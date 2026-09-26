#!/usr/bin/env python3
"""Setup script for MD-EXPLOIT-ENGINE"""

import os
import sys
from pathlib import Path
import subprocess


def create_directories():
    """Create necessary directories"""
    dirs = [
        'logs',
        'data',
        'models',
        'wordlists',
        'challenges',
        'config',
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def setup_config():
    """Setup configuration file"""
    config_example = Path('config/config.example.yaml')
    config_file = Path('config/config.yaml')
    
    if not config_file.exists() and config_example.exists():
        import shutil
        shutil.copy(config_example, config_file)
        print(f"✓ Created config file: {config_file}")
    else:
        print(f"✓ Config file already exists: {config_file}")


def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    return True


def download_wordlists():
    """Download common wordlists"""
    wordlist_dir = Path('wordlists')
    wordlist_dir.mkdir(exist_ok=True)
    
    # Download rockyou.txt if not exists
    rockyou = wordlist_dir / 'rockyou.txt'
    if not rockyou.exists():
        print("Downloading rockyou.txt wordlist...")
        try:
            import requests
            url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
            response = requests.get(url, stream=True)
            with open(rockyou, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✓ Downloaded rockyou.txt")
        except Exception as e:
            print(f"✗ Failed to download wordlist: {e}")


def main():
    """Main setup function"""
    print("=" * 50)
    print("MD-EXPLOIT-ENGINE Setup")
    print("=" * 50)
    print()
    
    # Create directories
    print("Creating directories...")
    create_directories()
    print()
    
    # Setup config
    print("Setting up configuration...")
    setup_config()
    print()
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed!")
        return 1
    print()
    
    # Download wordlists
    print("Downloading wordlists...")
    download_wordlists()
    print()
    
    print("=" * 50)
    print("✓ Setup completed successfully!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Edit config/config.yaml with your settings")
    print("2. Run: python main.py --help")
    print("3. Start solving: python main.py --challenge <path>")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
