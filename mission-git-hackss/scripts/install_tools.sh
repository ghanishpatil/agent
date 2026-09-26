#!/bin/bash
# Install external tools for MD-EXPLOIT-ENGINE

set -e

echo "Installing external tools for MD-EXPLOIT-ENGINE..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"
    
    # Update package list
    sudo apt-get update
    
    # Install tools
    sudo apt-get install -y \
        binwalk \
        exiftool \
        steghide \
        nmap \
        netcat \
        john \
        hashcat \
        sqlmap \
        nikto \
        dirb \
        gobuster \
        hydra \
        aircrack-ng \
        wireshark \
        tshark \
        foremost \
        scalpel \
        volatility3 \
        radare2 \
        gdb \
        strace \
        ltrace
    
    echo "Linux tools installed successfully!"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install tools
    brew install \
        binwalk \
        exiftool \
        steghide \
        nmap \
        john \
        hashcat \
        sqlmap \
        nikto \
        gobuster \
        hydra \
        aircrack-ng \
        wireshark \
        foremost \
        radare2 \
        gdb
    
    echo "macOS tools installed successfully!"
    
else
    echo "Unsupported OS: $OSTYPE"
    echo "Please install tools manually."
    exit 1
fi

# Install Python tools
echo "Installing Python-based tools..."
pip install \
    pwntools \
    ropper \
    one_gadget \
    sectools

echo "All tools installed successfully!"
echo "Note: Some tools may require additional configuration."
