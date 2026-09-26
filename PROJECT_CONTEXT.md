# Project Context: HackWars / TDHT CTF Challenge Workspace

## Overview

This is a **Capture The Flag (CTF) competition workspace** for the **HackWars / TDHT (The Dark Hacker's Tournament)** CTF event. It contains hundreds of solver scripts, exploit code, analysis tools, forensic artifacts, and writeups targeting 30+ individual challenges across multiple categories.

The flag format is: `TDHT{...}` (with some challenges using `CTF{...}`)

---

## Infrastructure & Tools

### CTF-Solver (MCP Kali Server)
- A **Model Context Protocol (MCP) server** for AI-assisted offensive security
- Bridges AI assistants to a Kali Linux terminal for automated pentesting
- Tools exposed: nmap, gobuster, dirb, nikto, sqlmap, metasploit, hydra, john, wpscan, enum4linux
- Architecture: Flask API (Kali Linux) + FastMCP client (Windows)

### Tech Stack Used
- **Primary Language:** Python 3
- **Libraries:** requests, pwntools, PIL/Pillow, OpenCV, numpy, onnxruntime, pyzbar, BeautifulSoup, selenium, cryptography, pdfplumber, scipy
- **Tools:** Tesseract OCR, ffmpeg, binwalk, steghide, John the Ripper, hashcat, commix, skipfish, sqlmap

---

## Challenge Categories & Status

### Web Exploitation (Solved)
| Challenge | Flag | Technique |
|-----------|------|-----------|
| Don't Ping L1 | `TDHT{k03pzlXhPjBS3yy1DFVRT5Mz7A}` | Command injection (semicolon) |
| Don't Ping L5 | `TDHT{Cg6NjRspE4DBCHqHmMaMtTijSi946ica}` | Command injection (${IFS} space bypass) |
| Status Page (SSTI) | `TDHT{RA5uhZNprW6DnDCjOFpIIlGJk5}` | Jinja2 SSTI, base64 flag in source |
| Northline Market | `TDHT{SmlChucIb58jz7n1Md52Y1YmQp}` | LFI via image.php path parameter |
| Stolen Schematics | `TDHT{sync_c0mprom15ed_...}` | Docker container escape, chall-manager API leak |

### Web Exploitation (In Progress / Attempted)
- **Kohli Challenge** - Timing/burst attack, multiple solve attempts
- **QuantumVault** - Password cracking, race conditions
- **Equator Navigation** - JWT forging, exploit nav
- **Kaalchakra** - ML/crypto hybrid, SHA1, themed passwords
- **Ghost Pipeline / Ghost Draft** - SSTI, fragment exploitation
- **VaultNet** - Array poisoning, forgot-password exploit
- **ProfileHub** - Exploit chain
- **Online Store** - LFI/reference exploit
- **Note Taking** - Heap off-by-one, tcache poison
- **Phantom Registrations** - Mass account creation
- **Betrayal Challenge** - Login cracking
- **Lazy Admin** - Cookie manipulation
- **Calculator** - Expression injection
- **Sector7** - Buffer overflow, port knocking
- **HackWars SpaceCTF** - Full pentest assessment

### Steganography & Forensics
- **Audio Stego** (chall.wav) - RIFX/RIFF fixing, spectrogram, LSB
- **Raven** (Raven.png) - Image stego, LSB extraction
- **Mind/Time/Soul Stones** - WAV spectrogram analysis, hidden ZIP
- **Intel OSINT** (intel.png) - Image forensics
- **Corrupted QR** - QR code repair and decode
- **Board puzzle** - Chess/grid position extraction
- **Disk Forensics** (disk1.zip) - FAT32 parsing, file recovery
- **Emails PDF** - Redaction removal, OCR

### Cryptography
- **Spartans** - Playfair cipher, multi-stage decode
- **Stones RSA** - Hastad's attack, RSA parameter extraction from audio
- **Nonce Reuse** - AES nonce reuse exploitation
- **Crib Drag** - XOR crib dragging
- **AIML/ONNX Challenge** - Steganography hidden in neural network model weights

### Reverse Engineering
- **Crackme** - Binary analysis, XOR decode
- **KaalRaj APK** - Android app decompilation
- **Greetings/Greetings2** - APK/binary analysis, pickle exploit
- **TinyLang** - Custom language interpreter exploitation
- **Game (SDL2)** - Game binary patching
- **Automatons** - Automaton state decoding
- **Validator WASM** - WebAssembly reverse engineering

### OSINT
- **Timoplayzz** - YouTube/social media investigation
- **Budapest Intercept** - Location-based intelligence
- **Flight Record** - GPS/altitude data forensics

### Miscellaneous / Client-Side
- **Independence Day CTF** - `CTF{JAY_HIND}` (hardcoded in JS)
- **Tubular Druid** - Multi-page puzzle, Hindi/Sanskrit flags
- **Heart of Secrets** - LSB stego + Morse code
- **Hate.Breachpoint** - Client-side validation (Next.js/Vercel)
- **Game of Blocks** - SVG signal extraction with secret key
- **Joyful Mandazi** - Web puzzle
- **Webhook Pinger** - SSRF exploitation
- **Time Traveler** - MD5 collision challenge
- **Flag Market** - Race condition market exploit

---

## Key Files & Artifacts

### Writeups (Completed)
- `writeups/01_dont_ping_L1.txt` - Command injection L1
- `writeups/02_dont_ping_L5.txt` - Command injection L5
- `writeups/03_status_page.txt` - SSTI exploitation
- `writeups/04_stolen_schematics.txt` - Docker escape
- `writeups/05_northline_market.txt` - LFI

### Important Data Files
- `flight_record.dat` - Binary GPS/flight data
- `challenge_final.onnx` - Neural network with hidden flag
- `emails.pdf` / `emails_unredacted.pdf` - PDF forensics targets
- `chall.wav` / variants - Audio steganography
- `Corrupted_QR.png` - QR code repair target
- `KaalRaj.apk` - Android reversing target
- `validator.wasm` / `validator.wat` - WASM reversing
- `intel.png` / `Raven.png` / `board.png` - Image stego targets
- `stones_eMfRx10.zip` - RSA crypto challenge
- `disk1.zip` - Forensics disk image
- `hidden_secret.zip` - Password-protected archive

### Status Documents
- `CTF_BRAIN.md` - Master challenge tracker
- `SOLUTION_STATUS.md` - Game of Blocks progress
- Various `*_WRITEUP.md` files - Per-challenge documentation

---

## Patterns & Approaches Used

1. **Command Injection** - Semicolons, pipes, ${IFS} space bypass
2. **SSTI** - Jinja2 `{{config}}`, `lipsum.__globals__`
3. **LFI/Path Traversal** - Direct file read via PHP wrappers
4. **JWT Manipulation** - Forging tokens, secret key extraction
5. **Race Conditions** - Parallel requests for timing exploits
6. **Binary Exploitation** - Buffer overflow, off-by-one, tcache poison
7. **Steganography** - LSB extraction, spectrogram analysis, bit-plane analysis
8. **Cryptography** - RSA (Hastad), XOR crib drag, nonce reuse, MD5 collisions
9. **OSINT** - Social media, geolocation, metadata analysis
10. **Reverse Engineering** - APK decompilation, WASM disassembly, ONNX model inspection
11. **Docker/Container** - API enumeration, container escape
12. **SSRF** - Internal port scanning, service discovery

---

## Environment

- **OS:** Windows (PowerShell)
- **Python:** 3.x with extensive library ecosystem
- **Remote:** Kali Linux server accessible via MCP for offensive tools
- **Targets:** Various challenge URLs (breachpoint.live, netlify.app, custom CTF infra)

---

## Notes

- Many challenges have multiple solve attempts (indicating iterative approaches)
- Some challenges are blocked by rate limiting (Vercel/Cloudflare)
- The workspace is "messy by design" - rapid iteration during live competition
- Flag format consistency: `TDHT{...}` for main event, `CTF{...}` for side challenges
