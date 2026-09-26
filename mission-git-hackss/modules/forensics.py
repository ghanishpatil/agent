"""Forensics analysis module - Comprehensive forensics techniques"""

import subprocess
import struct
import zlib
import gzip
import bz2
import lzma
import io
from pathlib import Path
from typing import Optional, List, Dict
import re
import hashlib
import json

from core.challenge import Challenge, ChallengeResult
from .base import BaseModule


class ForensicsModule(BaseModule):
    """Automated forensics analysis with comprehensive advanced techniques"""
    
    # File signatures for carving
    FILE_SIGNATURES = {
        b'\x89PNG\r\n\x1a\n': ('png', b'IEND\xaeB`\x82'),
        b'\xff\xd8\xff': ('jpg', b'\xff\xd9'),
        b'GIF87a': ('gif', b'\x00;'),
        b'GIF89a': ('gif', b'\x00;'),
        b'PK\x03\x04': ('zip', b'PK\x05\x06'),
        b'PK\x05\x06': ('zip', None),
        b'%PDF': ('pdf', b'%%EOF'),
        b'\x1f\x8b\x08': ('gz', None),
        b'BZ': ('bz2', None),
        b'\xfd7zXZ\x00': ('xz', None),
        b'Rar!\x1a\x07': ('rar', None),
        b'7z\xbc\xaf\x27\x1c': ('7z', None),
        b'\x00\x00\x00\x1cftyp': ('mp4', None),
        b'\x00\x00\x00\x20ftyp': ('mp4', None),
        b'RIFF': ('wav', None),
        b'ID3': ('mp3', None),
        b'\xff\xfb': ('mp3', None),
        b'OggS': ('ogg', None),
        b'fLaC': ('flac', None),
        b'\x50\x4b\x03\x04\x14\x00\x06\x00': ('docx', None),
        b'MZ': ('exe', None),
        b'\x7fELF': ('elf', None),
        b'\xca\xfe\xba\xbe': ('macho', None),
        b'\xfe\xed\xfa\xce': ('macho', None),
        b'\xfe\xed\xfa\xcf': ('macho64', None),
        b'SQLite format 3': ('sqlite', None),
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': ('ole', None),  # MS Office old format
    }
    
    # Steganography passwords to try
    STEGO_PASSWORDS = [
        '', 'password', 'secret', 'flag', 'ctf', 'admin', '123456',
        'hidden', 'stego', 'steganography', 'pass', 'key', 'test',
        'root', 'toor', 'qwerty', 'letmein', 'welcome', 'monkey',
    ]
    
    # Memory forensics profiles
    VOLATILITY_PROFILES = [
        'Win7SP1x64', 'Win7SP1x86', 'Win10x64', 'Win10x86',
        'WinXPSP3x86', 'Win2008R2SP1x64', 'LinuxUbuntu1604x64',
    ]
    
    def __init__(self, config):
        super().__init__(config)
        self.volatility_path = config.get('modules.forensics.volatility_path', 'volatility3')
        self.max_carve_size = config.get('modules.forensics.max_carve_size', 10 * 1024 * 1024)
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve forensics challenge with comprehensive advanced techniques"""
        result = self.create_result(challenge, False)
        
        if not challenge.has_files:
            result.error = "No files provided"
            return result
        
        file_path = challenge.files[0]
        result.add_log(f"Analyzing file: {file_path}")
        
        # Determine file type and apply appropriate techniques
        file_type = self._detect_file_type(file_path)
        result.add_log(f"Detected file type: {file_type}")
        
        techniques = [
            # Basic analysis
            self._check_metadata,
            self._check_strings,
            self._check_hex_dump,
            
            # Steganography
            self._check_image_steganography,
            self._check_image_lsb_advanced,
            self._check_audio_steganography,
            self._check_video_steganography,
            
            # File analysis
            self._check_binwalk,
            self._check_file_carving,
            self._check_compression_layers,
            
            # Network forensics
            self._check_pcap,
            self._check_pcap_advanced,
            
            # Document analysis
            self._check_zip_analysis,
            self._check_pdf_analysis,
            self._check_office_analysis,
            
            # Memory forensics
            self._check_memory_dump,
            
            # Disk forensics
            self._check_disk_image,
            self._check_deleted_files,
            
            # Advanced analysis
            self._check_entropy,
            self._check_timestamps,
            self._check_alternate_data_streams,
            self._check_file_slack,
            self._check_registry_hives,
        ]
        
        for technique in techniques:
            try:
                flag = technique(file_path, result)
                if flag:
                    result.success = True
                    result.flag = flag
                    result.method = technique.__name__
                    return result
            except Exception as e:
                result.add_log(f"Error in {technique.__name__}: {e}")
        
        result.error = "No hidden data found"
        return result
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type using magic bytes"""
        try:
            output = subprocess.check_output(['file', str(file_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=5).decode()
            return output.split(':')[1].strip() if ':' in output else 'unknown'
        except:
            return file_path.suffix.lower() or 'unknown'
    
    def _check_metadata(self, file_path: Path, result: ChallengeResult) -> str:
        """Check file metadata"""
        result.add_log("Checking metadata...")
        
        try:
            output = subprocess.check_output(['exiftool', str(file_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=10).decode('utf-8', errors='ignore')
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in metadata")
                return flag
            
            # Check specific fields
            for line in output.split('\n'):
                if any(field in line.lower() for field in ['comment', 'description', 'author', 'title', 'subject']):
                    flag = self.extract_flag(line)
                    if flag:
                        return flag
        except:
            pass
        
        return None
    
    def _check_strings(self, file_path: Path, result: ChallengeResult) -> str:
        """Extract strings from file"""
        result.add_log("Extracting strings...")
        
        try:
            # ASCII strings
            output = subprocess.check_output(['strings', str(file_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in ASCII strings")
                return flag
            
            # Unicode strings
            output = subprocess.check_output(['strings', '-e', 'l', str(file_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in Unicode strings")
                return flag
        except:
            # Fallback to manual extraction
            try:
                data = file_path.read_bytes()
                text = data.decode('utf-8', errors='ignore')
                flag = self.extract_flag(text)
                if flag:
                    result.add_log("Found flag in file content")
                    return flag
            except:
                pass
        
        return None

    def _check_hex_dump(self, file_path: Path, result: ChallengeResult) -> str:
        """Check hex dump for hidden data"""
        result.add_log("Checking hex dump...")
        
        try:
            data = file_path.read_bytes()
            
            # Check file header
            header = data[:100].hex()
            flag = self.extract_flag(bytes.fromhex(header).decode('utf-8', errors='ignore'))
            if flag:
                result.add_log("Found flag in file header")
                return flag
            
            # Check file footer
            footer = data[-100:].hex()
            flag = self.extract_flag(bytes.fromhex(footer).decode('utf-8', errors='ignore'))
            if flag:
                result.add_log("Found flag in file footer")
                return flag
            
            # Check for appended data after file end markers
            # PNG: IEND chunk
            if data[:4] == b'\x89PNG':
                iend_pos = data.find(b'IEND')
                if iend_pos != -1 and iend_pos + 12 < len(data):
                    appended = data[iend_pos + 12:]
                    flag = self.extract_flag(appended.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log("Found flag appended after PNG")
                        return flag
            
            # JPEG: FFD9 marker
            if data[:2] == b'\xff\xd8':
                ffd9_pos = data.rfind(b'\xff\xd9')
                if ffd9_pos != -1 and ffd9_pos + 2 < len(data):
                    appended = data[ffd9_pos + 2:]
                    flag = self.extract_flag(appended.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log("Found flag appended after JPEG")
                        return flag
        except:
            pass
        
        return None
    
    def _check_image_steganography(self, file_path: Path, result: ChallengeResult) -> str:
        """Check for image steganography"""
        result.add_log("Checking image steganography...")
        
        if file_path.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            return None
        
        # Try steghide
        try:
            for password in ['', 'password', 'secret', 'flag', 'ctf', 'admin']:
                try:
                    output = subprocess.check_output(
                        ['steghide', 'extract', '-sf', str(file_path), '-p', password, '-f'],
                        stderr=subprocess.STDOUT,
                        timeout=10
                    ).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(output)
                    if flag:
                        result.add_log(f"Steghide extraction successful (password: '{password}')")
                        return flag
                except:
                    pass
        except:
            pass
        
        # Try zsteg for PNG
        if file_path.suffix.lower() == '.png':
            try:
                output = subprocess.check_output(['zsteg', str(file_path)],
                                               stderr=subprocess.DEVNULL,
                                               timeout=30).decode('utf-8', errors='ignore')
                flag = self.extract_flag(output)
                if flag:
                    result.add_log("Found flag with zsteg")
                    return flag
            except:
                pass
        
        # LSB extraction
        try:
            from PIL import Image
            img = Image.open(file_path)
            pixels = list(img.getdata())
            
            # Extract LSB from each channel
            bits = []
            for pixel in pixels[:10000]:
                if isinstance(pixel, tuple):
                    for value in pixel[:3]:  # RGB only
                        bits.append(str(value & 1))
                else:
                    bits.append(str(pixel & 1))
            
            # Convert bits to text
            text = ''
            for i in range(0, len(bits) - 7, 8):
                byte = int(''.join(bits[i:i+8]), 2)
                if 32 <= byte <= 126:
                    text += chr(byte)
                elif byte == 0:
                    break
            
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in LSB data")
                return flag
        except:
            pass
        
        return None
    
    def _check_audio_steganography(self, file_path: Path, result: ChallengeResult) -> str:
        """Check for audio steganography"""
        result.add_log("Checking audio steganography...")
        
        if file_path.suffix.lower() not in ['.wav', '.mp3', '.flac', '.ogg']:
            return None
        
        # Check spectrogram (would need matplotlib/scipy)
        # For now, just check strings in audio file
        try:
            data = file_path.read_bytes()
            text = data.decode('utf-8', errors='ignore')
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in audio file")
                return flag
        except:
            pass
        
        return None
    
    def _check_binwalk(self, file_path: Path, result: ChallengeResult) -> str:
        """Use binwalk to find embedded files"""
        result.add_log("Running binwalk...")
        
        try:
            # Scan for embedded files
            output = subprocess.check_output(['binwalk', str(file_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in binwalk output")
                return flag
            
            # Extract embedded files
            extract_dir = file_path.parent / f'_{file_path.name}.extracted'
            subprocess.run(['binwalk', '-e', str(file_path), '-C', str(file_path.parent)],
                         stderr=subprocess.DEVNULL,
                         timeout=60)
            
            if extract_dir.exists():
                for extracted_file in extract_dir.rglob('*'):
                    if extracted_file.is_file():
                        try:
                            content = extracted_file.read_text(errors='ignore')
                            flag = self.extract_flag(content)
                            if flag:
                                result.add_log(f"Found flag in extracted file: {extracted_file.name}")
                                return flag
                        except:
                            pass
        except:
            pass
        
        return None

    def _check_file_carving(self, file_path: Path, result: ChallengeResult) -> str:
        """Carve files from data"""
        result.add_log("Attempting file carving...")
        
        try:
            data = file_path.read_bytes()
            
            # Look for common file signatures
            signatures = {
                b'\x89PNG\r\n\x1a\n': ('png', b'IEND'),
                b'\xff\xd8\xff': ('jpg', b'\xff\xd9'),
                b'PK\x03\x04': ('zip', None),
                b'%PDF': ('pdf', b'%%EOF'),
                b'GIF87a': ('gif', b'\x00;'),
                b'GIF89a': ('gif', b'\x00;'),
            }
            
            for sig, (ext, end_marker) in signatures.items():
                pos = 0
                while True:
                    start = data.find(sig, pos)
                    if start == -1:
                        break
                    
                    result.add_log(f"Found {ext} signature at offset {start}")
                    
                    # Try to extract and analyze
                    if end_marker:
                        end = data.find(end_marker, start)
                        if end != -1:
                            carved = data[start:end + len(end_marker)]
                            flag = self.extract_flag(carved.decode('utf-8', errors='ignore'))
                            if flag:
                                result.add_log(f"Found flag in carved {ext}")
                                return flag
                    
                    pos = start + 1
        except:
            pass
        
        return None
    
    def _check_pcap(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze PCAP network capture"""
        result.add_log("Checking PCAP analysis...")
        
        if file_path.suffix.lower() not in ['.pcap', '.pcapng', '.cap']:
            return None
        
        try:
            # Use tshark to extract data
            output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-T', 'fields', '-e', 'data'],
                stderr=subprocess.DEVNULL,
                timeout=60
            ).decode('utf-8', errors='ignore')
            
            # Decode hex data
            for line in output.split('\n'):
                if line.strip():
                    try:
                        decoded = bytes.fromhex(line.strip()).decode('utf-8', errors='ignore')
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log("Found flag in PCAP data")
                            return flag
                    except:
                        pass
            
            # Extract HTTP data
            http_output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-Y', 'http', '-T', 'fields', 
                 '-e', 'http.request.uri', '-e', 'http.file_data'],
                stderr=subprocess.DEVNULL,
                timeout=60
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(http_output)
            if flag:
                result.add_log("Found flag in HTTP traffic")
                return flag
            
            # Follow TCP streams
            streams_output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-z', 'follow,tcp,ascii,0'],
                stderr=subprocess.DEVNULL,
                timeout=60
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(streams_output)
            if flag:
                result.add_log("Found flag in TCP stream")
                return flag
                
        except:
            pass
        
        return None
    
    def _check_zip_analysis(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze ZIP files"""
        result.add_log("Checking ZIP analysis...")
        
        if file_path.suffix.lower() not in ['.zip', '.jar', '.apk', '.docx', '.xlsx', '.pptx']:
            return None
        
        try:
            import zipfile
            
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Check file listing
                for name in zf.namelist():
                    flag = self.extract_flag(name)
                    if flag:
                        result.add_log(f"Found flag in ZIP filename: {name}")
                        return flag
                
                # Check file contents
                for name in zf.namelist():
                    try:
                        content = zf.read(name).decode('utf-8', errors='ignore')
                        flag = self.extract_flag(content)
                        if flag:
                            result.add_log(f"Found flag in ZIP file: {name}")
                            return flag
                    except:
                        pass
                
                # Check ZIP comment
                if zf.comment:
                    flag = self.extract_flag(zf.comment.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log("Found flag in ZIP comment")
                        return flag
        except:
            pass
        
        # Try password cracking
        common_passwords = ['', 'password', 'secret', 'flag', 'ctf', '123456', 'admin']
        try:
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as zf:
                for pwd in common_passwords:
                    try:
                        for name in zf.namelist():
                            content = zf.read(name, pwd=pwd.encode() if pwd else None)
                            flag = self.extract_flag(content.decode('utf-8', errors='ignore'))
                            if flag:
                                result.add_log(f"Found flag with ZIP password: '{pwd}'")
                                return flag
                    except:
                        pass
        except:
            pass
        
        return None
    
    def _check_pdf_analysis(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze PDF files"""
        result.add_log("Checking PDF analysis...")
        
        if file_path.suffix.lower() != '.pdf':
            return None
        
        try:
            data = file_path.read_bytes()
            text = data.decode('utf-8', errors='ignore')
            
            # Check for embedded JavaScript
            js_match = re.search(r'/JS\s*\((.*?)\)', text, re.DOTALL)
            if js_match:
                flag = self.extract_flag(js_match.group(1))
                if flag:
                    result.add_log("Found flag in PDF JavaScript")
                    return flag
            
            # Check streams
            stream_matches = re.findall(r'stream\s*(.*?)\s*endstream', text, re.DOTALL)
            for stream in stream_matches:
                # Try to decompress
                try:
                    decompressed = zlib.decompress(stream.encode('latin-1'))
                    flag = self.extract_flag(decompressed.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log("Found flag in PDF stream")
                        return flag
                except:
                    pass
                
                flag = self.extract_flag(stream)
                if flag:
                    result.add_log("Found flag in PDF stream")
                    return flag
        except:
            pass
        
        return None
    
    def _check_entropy(self, file_path: Path, result: ChallengeResult) -> str:
        """Check file entropy for hidden/encrypted data"""
        result.add_log("Checking entropy...")
        
        try:
            data = file_path.read_bytes()
            
            # Calculate entropy
            from collections import Counter
            import math
            
            byte_counts = Counter(data)
            total = len(data)
            entropy = -sum((count/total) * math.log2(count/total) 
                          for count in byte_counts.values() if count > 0)
            
            result.add_log(f"File entropy: {entropy:.2f} bits/byte")
            
            if entropy > 7.9:
                result.add_log("High entropy detected - likely encrypted or compressed")
            elif entropy < 1.0:
                result.add_log("Low entropy detected - likely contains patterns")
        except:
            pass
        
        return None
    
    def _check_image_lsb_advanced(self, file_path: Path, result: ChallengeResult) -> str:
        """Advanced LSB steganography analysis"""
        result.add_log("Checking advanced LSB steganography...")
        
        if file_path.suffix.lower() not in ['.png', '.bmp', '.gif']:
            return None
        
        try:
            from PIL import Image
            img = Image.open(file_path)
            
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            
            pixels = list(img.getdata())
            width, height = img.size
            
            # Try different LSB extraction methods
            methods = [
                ('R channel LSB', lambda p: p[0] & 1),
                ('G channel LSB', lambda p: p[1] & 1),
                ('B channel LSB', lambda p: p[2] & 1),
                ('RGB LSB sequential', None),
                ('Row-major LSB', None),
                ('Column-major LSB', None),
                ('2-bit LSB', lambda p: (p[0] & 3, p[1] & 3, p[2] & 3)),
            ]
            
            # Extract R channel LSB
            bits = [str(p[0] & 1) for p in pixels[:10000] if isinstance(p, tuple)]
            text = self._bits_to_text(bits)
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in R channel LSB")
                return flag
            
            # Extract G channel LSB
            bits = [str(p[1] & 1) for p in pixels[:10000] if isinstance(p, tuple)]
            text = self._bits_to_text(bits)
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in G channel LSB")
                return flag
            
            # Extract B channel LSB
            bits = [str(p[2] & 1) for p in pixels[:10000] if isinstance(p, tuple)]
            text = self._bits_to_text(bits)
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in B channel LSB")
                return flag
            
            # Try MSB (Most Significant Bit)
            bits = [str((p[0] >> 7) & 1) for p in pixels[:10000] if isinstance(p, tuple)]
            text = self._bits_to_text(bits)
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in MSB")
                return flag
            
            # Check for visual LSB patterns
            lsb_image = Image.new('RGB', (width, height))
            lsb_pixels = [(((p[0] & 1) * 255), ((p[1] & 1) * 255), ((p[2] & 1) * 255)) 
                         for p in pixels if isinstance(p, tuple)]
            lsb_image.putdata(lsb_pixels[:width*height])
            
        except ImportError:
            result.add_log("PIL not available for advanced LSB")
        except Exception as e:
            result.add_log(f"Advanced LSB error: {e}")
        
        return None
    
    def _bits_to_text(self, bits: List[str]) -> str:
        """Convert bits to text"""
        text = ''
        for i in range(0, len(bits) - 7, 8):
            byte = int(''.join(bits[i:i+8]), 2)
            if 32 <= byte <= 126:
                text += chr(byte)
            elif byte == 0:
                break
        return text
    
    def _check_video_steganography(self, file_path: Path, result: ChallengeResult) -> str:
        """Check for video steganography"""
        result.add_log("Checking video steganography...")
        
        if file_path.suffix.lower() not in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
            return None
        
        try:
            # Extract frames using ffmpeg
            output_dir = file_path.parent / f'{file_path.stem}_frames'
            output_dir.mkdir(exist_ok=True)
            
            subprocess.run([
                'ffmpeg', '-i', str(file_path), '-vf', 'fps=1',
                str(output_dir / 'frame_%04d.png')
            ], stderr=subprocess.DEVNULL, timeout=60)
            
            # Analyze extracted frames
            for frame in sorted(output_dir.glob('*.png'))[:10]:
                # Check strings in frame
                try:
                    data = frame.read_bytes()
                    flag = self.extract_flag(data.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log(f"Found flag in video frame: {frame.name}")
                        return flag
                except:
                    pass
            
            # Check video metadata
            output = subprocess.check_output(
                ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(file_path)],
                stderr=subprocess.DEVNULL, timeout=30
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in video metadata")
                return flag
                
        except Exception as e:
            result.add_log(f"Video analysis error: {e}")
        
        return None
    
    def _check_compression_layers(self, file_path: Path, result: ChallengeResult) -> str:
        """Check for multiple compression layers"""
        result.add_log("Checking compression layers...")
        
        try:
            data = file_path.read_bytes()
            
            # Try multiple decompression methods
            decompressors = [
                ('gzip', lambda d: gzip.decompress(d)),
                ('zlib', lambda d: zlib.decompress(d)),
                ('bz2', lambda d: bz2.decompress(d)),
                ('lzma', lambda d: lzma.decompress(d)),
            ]
            
            for name, decompress in decompressors:
                try:
                    decompressed = decompress(data)
                    result.add_log(f"Successfully decompressed with {name}")
                    
                    flag = self.extract_flag(decompressed.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log(f"Found flag after {name} decompression")
                        return flag
                    
                    # Try nested decompression
                    for name2, decompress2 in decompressors:
                        try:
                            decompressed2 = decompress2(decompressed)
                            flag = self.extract_flag(decompressed2.decode('utf-8', errors='ignore'))
                            if flag:
                                result.add_log(f"Found flag after {name}+{name2} decompression")
                                return flag
                        except:
                            pass
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_pcap_advanced(self, file_path: Path, result: ChallengeResult) -> str:
        """Advanced PCAP analysis"""
        result.add_log("Checking advanced PCAP analysis...")
        
        if file_path.suffix.lower() not in ['.pcap', '.pcapng', '.cap']:
            return None
        
        try:
            # Extract DNS queries
            dns_output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-Y', 'dns', '-T', 'fields',
                 '-e', 'dns.qry.name', '-e', 'dns.resp.name'],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(dns_output)
            if flag:
                result.add_log("Found flag in DNS traffic")
                return flag
            
            # Extract FTP data
            ftp_output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-Y', 'ftp-data', '-T', 'fields', '-e', 'data'],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            for line in ftp_output.split('\n'):
                if line.strip():
                    try:
                        decoded = bytes.fromhex(line.strip()).decode('utf-8', errors='ignore')
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log("Found flag in FTP data")
                            return flag
                    except:
                        pass
            
            # Extract SMTP data
            smtp_output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-Y', 'smtp', '-T', 'fields',
                 '-e', 'smtp.req.parameter', '-e', 'smtp.data.fragment'],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(smtp_output)
            if flag:
                result.add_log("Found flag in SMTP traffic")
                return flag
            
            # Extract ICMP data (ping exfiltration)
            icmp_output = subprocess.check_output(
                ['tshark', '-r', str(file_path), '-Y', 'icmp', '-T', 'fields', '-e', 'data'],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            icmp_data = ''
            for line in icmp_output.split('\n'):
                if line.strip():
                    try:
                        icmp_data += bytes.fromhex(line.strip()).decode('utf-8', errors='ignore')
                    except:
                        pass
            
            flag = self.extract_flag(icmp_data)
            if flag:
                result.add_log("Found flag in ICMP data")
                return flag
                
        except Exception as e:
            result.add_log(f"Advanced PCAP error: {e}")
        
        return None
    
    def _check_office_analysis(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze Microsoft Office documents"""
        result.add_log("Checking Office document analysis...")
        
        if file_path.suffix.lower() not in ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']:
            return None
        
        try:
            import zipfile
            
            # Modern Office formats are ZIP archives
            if file_path.suffix.lower() in ['.docx', '.xlsx', '.pptx']:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    for name in zf.namelist():
                        try:
                            content = zf.read(name).decode('utf-8', errors='ignore')
                            flag = self.extract_flag(content)
                            if flag:
                                result.add_log(f"Found flag in Office file: {name}")
                                return flag
                        except:
                            pass
                    
                    # Check for macros
                    if 'word/vbaProject.bin' in zf.namelist():
                        result.add_log("VBA macros detected")
                        vba_data = zf.read('word/vbaProject.bin')
                        flag = self.extract_flag(vba_data.decode('utf-8', errors='ignore'))
                        if flag:
                            return flag
            
            # Old Office formats (OLE)
            else:
                try:
                    import olefile
                    ole = olefile.OleFileIO(str(file_path))
                    
                    for stream in ole.listdir():
                        stream_path = '/'.join(stream)
                        try:
                            data = ole.openstream(stream).read()
                            flag = self.extract_flag(data.decode('utf-8', errors='ignore'))
                            if flag:
                                result.add_log(f"Found flag in OLE stream: {stream_path}")
                                return flag
                        except:
                            pass
                    
                    ole.close()
                except ImportError:
                    result.add_log("olefile not available for OLE analysis")
                    
        except Exception as e:
            result.add_log(f"Office analysis error: {e}")
        
        return None
    
    def _check_memory_dump(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze memory dumps"""
        result.add_log("Checking memory dump analysis...")
        
        # Check if it looks like a memory dump
        try:
            data = file_path.read_bytes()[:1000]
            
            # Common memory dump indicators
            if not any([
                b'PAGEDU' in data,  # Windows page file
                b'MDMP' in data,    # Windows minidump
                b'ELF' in data,     # Linux core dump
                file_path.suffix.lower() in ['.dmp', '.vmem', '.raw', '.mem']
            ]):
                return None
        except:
            return None
        
        result.add_log("Memory dump detected")
        
        try:
            # Try volatility3
            for plugin in ['windows.pslist', 'windows.filescan', 'windows.cmdline', 'windows.hashdump']:
                try:
                    output = subprocess.check_output(
                        ['vol', '-f', str(file_path), plugin],
                        stderr=subprocess.DEVNULL, timeout=120
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        result.add_log(f"Found flag with volatility {plugin}")
                        return flag
                except:
                    pass
            
            # Try strings on memory dump
            output = subprocess.check_output(
                ['strings', '-n', '10', str(file_path)],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in memory dump strings")
                return flag
                
        except Exception as e:
            result.add_log(f"Memory analysis error: {e}")
        
        return None
    
    def _check_disk_image(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze disk images"""
        result.add_log("Checking disk image analysis...")
        
        if file_path.suffix.lower() not in ['.img', '.dd', '.raw', '.iso', '.e01']:
            return None
        
        try:
            # Try to mount and analyze with sleuthkit
            output = subprocess.check_output(
                ['fls', '-r', str(file_path)],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in disk image file listing")
                return flag
            
            # Extract files
            for line in output.split('\n'):
                if 'flag' in line.lower() or 'secret' in line.lower():
                    result.add_log(f"Interesting file found: {line}")
                    
        except Exception as e:
            result.add_log(f"Disk image error: {e}")
        
        return None
    
    def _check_deleted_files(self, file_path: Path, result: ChallengeResult) -> str:
        """Check for deleted files in disk images"""
        result.add_log("Checking for deleted files...")
        
        try:
            # Use photorec/foremost for file recovery
            output = subprocess.check_output(
                ['foremost', '-t', 'all', '-i', str(file_path), '-o', str(file_path.parent / 'recovered')],
                stderr=subprocess.DEVNULL, timeout=120
            ).decode('utf-8', errors='ignore')
            
            recovered_dir = file_path.parent / 'recovered'
            if recovered_dir.exists():
                for recovered_file in recovered_dir.rglob('*'):
                    if recovered_file.is_file():
                        try:
                            content = recovered_file.read_text(errors='ignore')
                            flag = self.extract_flag(content)
                            if flag:
                                result.add_log(f"Found flag in recovered file: {recovered_file.name}")
                                return flag
                        except:
                            pass
        except:
            pass
        
        return None
    
    def _check_timestamps(self, file_path: Path, result: ChallengeResult) -> str:
        """Check file timestamps for hidden data"""
        result.add_log("Checking timestamps...")
        
        try:
            import os
            stat = os.stat(file_path)
            
            # Check if timestamps encode data
            timestamps = [stat.st_mtime, stat.st_atime, stat.st_ctime]
            
            # Try to decode timestamps as ASCII
            for ts in timestamps:
                ts_int = int(ts)
                try:
                    # Try as hex
                    hex_str = hex(ts_int)[2:]
                    if len(hex_str) % 2 == 0:
                        decoded = bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log("Found flag in timestamp")
                            return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_alternate_data_streams(self, file_path: Path, result: ChallengeResult) -> str:
        """Check for NTFS Alternate Data Streams"""
        result.add_log("Checking alternate data streams...")
        
        try:
            # Windows ADS check
            output = subprocess.check_output(
                ['dir', '/r', str(file_path)],
                stderr=subprocess.DEVNULL, timeout=10, shell=True
            ).decode('utf-8', errors='ignore')
            
            # Look for ADS indicators
            if ':$DATA' in output or '::' in output:
                result.add_log("Alternate data stream detected")
                flag = self.extract_flag(output)
                if flag:
                    return flag
        except:
            pass
        
        return None
    
    def _check_file_slack(self, file_path: Path, result: ChallengeResult) -> str:
        """Check file slack space for hidden data"""
        result.add_log("Checking file slack space...")
        
        try:
            data = file_path.read_bytes()
            
            # Check for data after logical end of file
            # For images, check after end markers
            if data[:4] == b'\x89PNG':
                iend_pos = data.find(b'IEND\xaeB`\x82')
                if iend_pos != -1:
                    slack = data[iend_pos + 8:]
                    if slack:
                        flag = self.extract_flag(slack.decode('utf-8', errors='ignore'))
                        if flag:
                            result.add_log("Found flag in PNG slack space")
                            return flag
            
            elif data[:2] == b'\xff\xd8':
                ffd9_pos = data.rfind(b'\xff\xd9')
                if ffd9_pos != -1:
                    slack = data[ffd9_pos + 2:]
                    if slack:
                        flag = self.extract_flag(slack.decode('utf-8', errors='ignore'))
                        if flag:
                            result.add_log("Found flag in JPEG slack space")
                            return flag
        except:
            pass
        
        return None
    
    def _check_registry_hives(self, file_path: Path, result: ChallengeResult) -> str:
        """Analyze Windows registry hives"""
        result.add_log("Checking registry hives...")
        
        try:
            data = file_path.read_bytes()[:4]
            
            # Check for registry hive signature
            if data != b'regf':
                return None
            
            result.add_log("Registry hive detected")
            
            # Use regipy or similar
            try:
                from regipy.registry import RegistryHive
                reg = RegistryHive(str(file_path))
                
                # Iterate through keys
                for entry in reg.recurse_subkeys(reg.root, as_json=True):
                    entry_str = str(entry)
                    flag = self.extract_flag(entry_str)
                    if flag:
                        result.add_log("Found flag in registry")
                        return flag
            except ImportError:
                # Fallback to strings
                output = subprocess.check_output(
                    ['strings', str(file_path)],
                    stderr=subprocess.DEVNULL, timeout=30
                ).decode('utf-8', errors='ignore')
                
                flag = self.extract_flag(output)
                if flag:
                    result.add_log("Found flag in registry strings")
                    return flag
        except:
            pass
        
        return None