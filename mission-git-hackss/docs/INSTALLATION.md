# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Docker (optional, for containerized deployment)

## Basic Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/md-exploit-engine.git
cd md-exploit-engine
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure

```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your settings
```

## Docker Installation

### Using Docker Compose

```bash
docker-compose up -d
```

### Manual Docker Build

```bash
docker build -t md-exploit-engine .
docker run -p 8080:8080 md-exploit-engine
```

## External Tools (Optional)

For full functionality, install these external tools:

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    binwalk \
    exiftool \
    steghide \
    nmap \
    john \
    hashcat \
    volatility3
```

### macOS

```bash
brew install binwalk exiftool steghide nmap john hashcat
```

### Windows

Download and install tools manually:
- Binwalk: https://github.com/ReFirmLabs/binwalk
- ExifTool: https://exiftool.org/
- Nmap: https://nmap.org/download.html

## Verification

Test the installation:

```bash
python main.py --help
```

You should see the help message with available options.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

### Permission Errors

On Linux/macOS, you may need to make the main script executable:

```bash
chmod +x main.py
```

### Docker Issues

If Docker containers fail to start, check logs:

```bash
docker-compose logs -f
```
