<![CDATA[<div align="center">

# 🔥 MD-EXPLOIT-ENGINE 🔥

### Automated CTF Challenge Solver

[![Developer](https://img.shields.io/badge/Developer-Md%20Abu%20Shalem%20Alam-red?style=for-the-badge)](https://github.com/mdabushalem)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple?style=for-the-badge)]()

<img src="https://raw.githubusercontent.com/github/explore/main/topics/hacking/hacking.png" width="200" alt="MD-EXPLOIT-ENGINE">

**The Ultimate Automated CTF Challenge Solver with AI-Powered Analysis**

*Developed with ❤️ by **Md Abu Shalem Alam***

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Dashboard](#-web-dashboard) • [Modules](#-modules)

</div>

---

## 🎯 About

**MD-EXPLOIT-ENGINE** is a powerful, automated Capture The Flag (CTF) challenge solver designed to help security researchers and CTF players solve challenges quickly and efficiently. It combines multiple exploitation techniques, encoding/decoding methods, and AI-powered analysis to automatically extract flags from various challenge types.

> **Developed by: Md Abu Shalem Alam**

---

## ✨ Features

### 🌐 Web Exploitation
- **Source Code Analysis** - Extracts flags from HTML, JavaScript, CSS
- **Steganography Detection** - LSB extraction from images (PNG, JPG)
- **Audio Morse Code** - Decodes morse code from WAV files
- **Caesar Cipher Detection** - Auto-detects and decodes Caesar ciphers
- **Base64/Hex/Binary** - Multi-layer encoding detection
- **Meta Tag Hash Extraction** - Derives hashes from meta tags
- **Cookie & LocalStorage** - Extracts hidden data
- **API Endpoint Discovery** - Finds hidden API endpoints

### 🔐 Cryptography
- **Classical Ciphers** - Caesar, ROT13, Vigenere, Atbash, Affine
- **Modern Encryption** - AES, RSA, XOR
- **Hash Cracking** - MD5, SHA1, SHA256 with wordlists
- **Encoding** - Base64, Base32, Base58, Base85, Hex, Binary, Octal

### 🗂️ Path Finder
- **Directory Bruteforce** - 5000+ common paths
- **File Discovery** - CTF-specific files (flag.txt, secret.txt, etc.)
- **Suspect File Detection** - AI-powered suspicious file identification
- **JavaScript Analysis** - Extracts paths from JS files
- **Numbered File Detection** - Finds image1.txt, cipher1.js patterns

### 🧠 CTF Brain (AI)
- **Pattern Learning** - Learns from solved challenges
- **Smart Password Generation** - Context-aware password lists
- **Technique Suggestion** - Recommends exploitation methods
- **Flag Validation** - Validates extracted flags

### 📊 Web Dashboard
- **Cyber Command Center** - Hacker-themed UI
- **Live Operation Logs** - Real-time solving progress
- **Path Finder Integration** - Visual path discovery
- **Suspect Files Panel** - One-click solving
- **Flag Celebration** - Animated success notifications

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/mdabushalem/md-exploit-engine.git
cd md-exploit-engine

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python main.py --web --port 8080
```

### Manual Installation

```bash
# Core dependencies
pip install requests beautifulsoup4 flask pyyaml

# Image processing (for steganography)
pip install Pillow numpy

# Audio processing (for morse code)
pip install scipy

# Cryptography
pip install pycryptodome cryptography
```

---

## 💻 Usage

### Web Dashboard (Recommended)

```bash
python main.py --web --port 8080
```

Then open http://localhost:8080 in your browser.

### Command Line

```bash
# Solve a web challenge
python main.py --url https://target-ctf.com/

# Solve with specific category
python main.py --url https://target-ctf.com/ --category web

# Quick mode (faster, less thorough)
python main.py --url https://target-ctf.com/ --quick
```

### Python API

```python
from core.config import Config
from core.challenge import Challenge
from modules.web import WebModule

# Initialize
config = Config('config/config.yaml')
web = WebModule(config)

# Create challenge
challenge = Challenge(
    name="my_challenge",
    url="https://target-ctf.com/",
    category="web"
)

# Solve
result = web.solve(challenge)

if result.success:
    print(f"FLAG: {result.flag}")
    print(f"Method: {result.method}")
```

---

## 🖥️ Web Dashboard

The MD-EXPLOIT-ENGINE comes with a stunning **Cyber Command Center** dashboard:

### Features:
- 🎯 **Exploit Launcher** - Enter URL and click to solve
- 📊 **Live Logs** - Watch the solving process in real-time
- 🗂️ **Path Finder** - Discover hidden files and directories
- 🎯 **Suspect Files** - Auto-detected suspicious files with one-click solve
- 🏆 **Flag Celebration** - Animated celebration when flag is found

### Screenshots:
```
┌──────────────────────────────────────────────────────────────┐
│         MD-EXPLOIT-ENGINE CYBER COMMAND CENTER               │
│                                                              │
│   🌐 Dashboard: http://127.0.0.1:8080                        │
│   📡 Status: ONLINE                                          │
│   🧩 Modules: 7 Active                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 Modules

| Module | Description | Status |
|--------|-------------|--------|
| 🌐 **Web** | Web exploitation, steganography, encoding | ✅ Active |
| 🔐 **Crypto** | Cryptography challenges | ✅ Active |
| 💥 **PWN** | Binary exploitation | ✅ Active |
| 🔍 **Reversing** | Reverse engineering | ✅ Active |
| 🔬 **Forensics** | Digital forensics | ✅ Active |
| 🕵️ **OSINT** | Open source intelligence | ✅ Active |
| 🎲 **Misc** | Miscellaneous challenges | ✅ Active |

---

## 📁 Project Structure

```
md-exploit-engine/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   └── config.yaml        # Configuration
├── core/
│   ├── engine.py          # Main engine
│   ├── challenge.py       # Challenge model
│   └── config.py          # Config loader
├── modules/
│   ├── web.py             # Web exploitation
│   ├── crypto.py          # Cryptography
│   ├── pathfinder.py      # Path discovery
│   └── ...                # Other modules
├── web/
│   ├── dashboard.py       # Flask dashboard
│   └── templates/
│       └── index.html     # Dashboard UI
├── ml/
│   └── ctf_brain.py       # AI/ML module
└── utils/
    └── ...                # Utilities
```

---

## 🏆 Supported CTF Platforms

MD-EXPLOIT-ENGINE has been tested on:

- ✅ Netlify CTF challenges
- ✅ Custom CTF platforms
- ✅ HackTheBox (web challenges)
- ✅ TryHackMe (web challenges)
- ✅ PicoCTF
- ✅ CTFtime events

---

## 🔧 Configuration

Edit `config/config.yaml`:

```yaml
# MD-EXPLOIT-ENGINE Configuration
# Developed by: Md Abu Shalem Alam

general:
  timeout: 30
  max_threads: 20
  quick_mode: false

web:
  user_agent: "MD-EXPLOIT-ENGINE/1.0"
  follow_redirects: true
  verify_ssl: false

pathfinder:
  max_depth: 3
  file_limit: 5000
```

---

## 📝 Changelog

### v1.0.0 (December 2024)
- Initial release
- Web exploitation module
- Cryptography module
- Path Finder with suspect detection
- CTF Brain AI
- Web Dashboard
- Live operation logs

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

<div align="center">

### **Md Abu Shalem Alam**

*Security Researcher | CTF Player | Developer*

[![GitHub](https://img.shields.io/badge/GitHub-mdabushalem-black?style=for-the-badge&logo=github)](https://github.com/mdabushalem)

</div>

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

*Made with ❤️ by Md Abu Shalem Alam*

</div>
]]>