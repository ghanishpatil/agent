"""OSINT (Open Source Intelligence) module - Comprehensive intelligence gathering"""

import re
import requests
import json
import hashlib
import time
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from typing import Optional, List, Dict

from core.challenge import Challenge, ChallengeResult
from .base import BaseModule


class OSINTModule(BaseModule):
    """Automated OSINT gathering with comprehensive advanced techniques"""
    
    # Social media platforms
    SOCIAL_PLATFORMS = {
        'twitter': 'https://twitter.com/{}',
        'github': 'https://github.com/{}',
        'instagram': 'https://instagram.com/{}',
        'facebook': 'https://facebook.com/{}',
        'linkedin': 'https://linkedin.com/in/{}',
        'reddit': 'https://reddit.com/user/{}',
        'medium': 'https://medium.com/@{}',
        'keybase': 'https://keybase.io/{}',
        'telegram': 'https://t.me/{}',
        'youtube': 'https://youtube.com/@{}',
        'tiktok': 'https://tiktok.com/@{}',
        'pinterest': 'https://pinterest.com/{}',
        'tumblr': 'https://{}.tumblr.com',
        'flickr': 'https://flickr.com/people/{}',
        'vimeo': 'https://vimeo.com/{}',
        'soundcloud': 'https://soundcloud.com/{}',
        'spotify': 'https://open.spotify.com/user/{}',
        'twitch': 'https://twitch.tv/{}',
        'discord': None,  # Requires different approach
        'slack': None,
        'mastodon': None,
    }
    
    # Code hosting platforms
    CODE_PLATFORMS = {
        'github': 'https://api.github.com/users/{}',
        'gitlab': 'https://gitlab.com/api/v4/users?username={}',
        'bitbucket': 'https://api.bitbucket.org/2.0/users/{}',
        'sourceforge': 'https://sourceforge.net/u/{}/profile',
        'codeberg': 'https://codeberg.org/api/v1/users/{}',
    }
    
    # Paste sites
    PASTE_SITES = [
        'pastebin.com',
        'ghostbin.com',
        'paste.ee',
        'dpaste.org',
        'hastebin.com',
        'paste.mozilla.org',
        'gist.github.com',
    ]
    
    # Data breach APIs
    BREACH_APIS = {
        'haveibeenpwned': 'https://haveibeenpwned.com/api/v3/breachedaccount/{}',
        'dehashed': 'https://api.dehashed.com/search?query={}',
    }
    
    def __init__(self, config):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.timeout = 15
        
        # API keys from config
        self.shodan_key = config.get('modules.osint.api_keys.shodan', '')
        self.virustotal_key = config.get('modules.osint.api_keys.virustotal', '')
        self.hunter_key = config.get('modules.osint.api_keys.hunter', '')
        self.censys_id = config.get('modules.osint.api_keys.censys_id', '')
        self.censys_secret = config.get('modules.osint.api_keys.censys_secret', '')
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve OSINT challenge with comprehensive advanced techniques"""
        result = self.create_result(challenge, False)
        
        # Extract targets from description
        targets = self._extract_targets(challenge.description)
        result.add_log(f"Found {len(targets)} potential targets")
        
        if not targets and not challenge.has_files:
            result.error = "No targets found in challenge description"
            return result
        
        # Process files if present
        if challenge.has_files:
            for file in challenge.files:
                try:
                    content = file.read_text(errors='ignore')
                    targets.extend(self._extract_targets(content))
                except:
                    pass
        
        # Try various OSINT techniques
        for target in targets:
            techniques = [
                # Web search
                self._search_web,
                self._search_google_dorks,
                
                # Archive
                self._check_wayback,
                self._check_archive_today,
                
                # Social media
                self._check_social_media,
                self._check_social_media_advanced,
                
                # Technical
                self._check_dns,
                self._check_dns_history,
                self._check_whois,
                self._check_ssl_certificates,
                self._check_subdomains,
                
                # Code
                self._check_github,
                self._check_github_advanced,
                self._check_gitlab,
                
                # Paste sites
                self._check_pastebin,
                self._check_paste_sites,
                
                # Breach data
                self._check_breach_data,
                
                # Image
                self._reverse_image_search,
                self._check_exif_gps,
                
                # Advanced
                self._check_shodan,
                self._check_censys,
                self._check_virustotal,
                self._check_urlscan,
            ]
            
            for technique in techniques:
                try:
                    flag = technique(target, result)
                    if flag:
                        result.success = True
                        result.flag = flag
                        result.method = technique.__name__
                        return result
                except Exception as e:
                    result.add_log(f"Error in {technique.__name__}: {e}")
        
        result.error = "No intelligence gathered"
        return result
    
    def _extract_targets(self, text: str) -> list:
        """Extract potential OSINT targets from text"""
        if not text:
            return []
        
        targets = []
        
        # URLs
        urls = re.findall(r'https?://[^\s<>"\']+', text)
        targets.extend(urls)
        
        # Domains
        domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', text)
        targets.extend([d for d in domains if '.' in d and len(d) > 4])
        
        # Usernames (@ mentions)
        usernames = re.findall(r'@([a-zA-Z0-9_]+)', text)
        targets.extend(usernames)
        
        # Email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        targets.extend(emails)
        
        # IP addresses
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        targets.extend(ips)
        
        # Phone numbers
        phones = re.findall(r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b', text)
        targets.extend(phones)
        
        # Remove duplicates
        return list(set(targets))
    
    def _search_web(self, target: str, result: ChallengeResult) -> str:
        """Search web for target"""
        result.add_log(f"Searching web for: {target}")
        
        try:
            # DuckDuckGo search (doesn't require API)
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(target)}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log("Found flag in search results")
                return flag
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', class_='result__url'):
                href = link.get('href', '')
                flag = self.extract_flag(href)
                if flag:
                    return flag
        except:
            pass
        
        return None

    def _check_wayback(self, target: str, result: ChallengeResult) -> str:
        """Check Wayback Machine"""
        result.add_log(f"Checking Wayback Machine for: {target}")
        
        if not target.startswith('http'):
            target = f"http://{target}"
        
        try:
            # Get available snapshots
            api_url = f"https://archive.org/wayback/available?url={quote_plus(target)}"
            response = self.session.get(api_url, timeout=self.timeout)
            data = response.json()
            
            if data.get('archived_snapshots', {}).get('closest'):
                snapshot_url = data['archived_snapshots']['closest']['url']
                result.add_log(f"Found snapshot: {snapshot_url}")
                
                # Fetch snapshot
                snapshot_response = self.session.get(snapshot_url, timeout=self.timeout)
                flag = self.extract_flag(snapshot_response.text)
                if flag:
                    result.add_log("Found flag in Wayback snapshot")
                    return flag
            
            # Check CDX API for all snapshots
            cdx_url = f"https://web.archive.org/cdx/search/cdx?url={quote_plus(target)}&output=json"
            cdx_response = self.session.get(cdx_url, timeout=self.timeout)
            
            flag = self.extract_flag(cdx_response.text)
            if flag:
                return flag
                
        except:
            pass
        
        return None
    
    def _check_social_media(self, target: str, result: ChallengeResult) -> str:
        """Check social media platforms"""
        result.add_log(f"Checking social media for: {target}")
        
        # Clean username
        username = target.lstrip('@')
        
        platforms = [
            f"https://twitter.com/{username}",
            f"https://github.com/{username}",
            f"https://instagram.com/{username}",
            f"https://facebook.com/{username}",
            f"https://linkedin.com/in/{username}",
            f"https://reddit.com/user/{username}",
            f"https://medium.com/@{username}",
            f"https://keybase.io/{username}",
        ]
        
        for platform_url in platforms:
            try:
                response = self.session.get(platform_url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    result.add_log(f"Found profile: {platform_url}")
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag on {platform_url}")
                        return flag
            except:
                pass
        
        return None
    
    def _check_dns(self, target: str, result: ChallengeResult) -> str:
        """Check DNS records"""
        result.add_log(f"Checking DNS for: {target}")
        
        # Extract domain from URL if needed
        if target.startswith('http'):
            from urllib.parse import urlparse
            target = urlparse(target).netloc
        
        try:
            import socket
            
            # A record
            try:
                ip = socket.gethostbyname(target)
                result.add_log(f"A record: {ip}")
            except:
                pass
            
            # Try dig for more records
            record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
            
            for rtype in record_types:
                try:
                    import subprocess
                    output = subprocess.check_output(
                        ['dig', '+short', rtype, target],
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    ).decode('utf-8', errors='ignore')
                    
                    if output.strip():
                        result.add_log(f"{rtype}: {output.strip()}")
                        
                        flag = self.extract_flag(output)
                        if flag:
                            result.add_log(f"Found flag in {rtype} record")
                            return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_whois(self, target: str, result: ChallengeResult) -> str:
        """Check WHOIS information"""
        result.add_log(f"Checking WHOIS for: {target}")
        
        # Extract domain
        if target.startswith('http'):
            from urllib.parse import urlparse
            target = urlparse(target).netloc
        
        try:
            import subprocess
            output = subprocess.check_output(
                ['whois', target],
                stderr=subprocess.DEVNULL,
                timeout=15
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in WHOIS data")
                return flag
            
            # Log interesting fields
            for line in output.split('\n'):
                if any(field in line.lower() for field in ['registrant', 'admin', 'tech', 'email']):
                    result.add_log(line.strip())
        except:
            pass
        
        return None
    
    def _check_github(self, target: str, result: ChallengeResult) -> str:
        """Check GitHub for information"""
        result.add_log(f"Checking GitHub for: {target}")
        
        username = target.lstrip('@')
        
        try:
            # Check user profile
            api_url = f"https://api.github.com/users/{username}"
            response = self.session.get(api_url, timeout=self.timeout)
            
            if response.status_code == 200:
                user_data = response.json()
                result.add_log(f"Found GitHub user: {user_data.get('name', username)}")
                
                # Check bio
                bio = user_data.get('bio', '')
                flag = self.extract_flag(bio)
                if flag:
                    result.add_log("Found flag in GitHub bio")
                    return flag
                
                # Check repos
                repos_url = user_data.get('repos_url', '')
                if repos_url:
                    repos_response = self.session.get(repos_url, timeout=self.timeout)
                    if repos_response.status_code == 200:
                        repos = repos_response.json()
                        for repo in repos[:10]:  # Check first 10 repos
                            repo_name = repo.get('name', '')
                            flag = self.extract_flag(repo_name)
                            if flag:
                                return flag
                            
                            # Check repo description
                            desc = repo.get('description', '')
                            flag = self.extract_flag(desc or '')
                            if flag:
                                return flag
        except:
            pass
        
        return None
    
    def _check_pastebin(self, target: str, result: ChallengeResult) -> str:
        """Check Pastebin for information"""
        result.add_log(f"Checking Pastebin for: {target}")
        
        try:
            # Search Google for pastebin results
            search_url = f"https://html.duckduckgo.com/html/?q=site:pastebin.com+{quote_plus(target)}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log("Found flag in Pastebin search")
                return flag
        except:
            pass
        
        return None
    
    def _search_google_dorks(self, target: str, result: ChallengeResult) -> str:
        """Use Google dorks for advanced searching"""
        result.add_log(f"Trying Google dorks for: {target}")
        
        dorks = [
            f'"{target}" filetype:txt',
            f'"{target}" filetype:log',
            f'"{target}" filetype:sql',
            f'"{target}" filetype:conf',
            f'"{target}" password',
            f'"{target}" secret',
            f'"{target}" flag',
            f'site:pastebin.com "{target}"',
            f'site:github.com "{target}"',
            f'site:gitlab.com "{target}"',
            f'inurl:"{target}"',
            f'intitle:"{target}"',
        ]
        
        for dork in dorks:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(dork)}"
                response = self.session.get(search_url, timeout=self.timeout)
                
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Found flag with dork: {dork}")
                    return flag
                
                time.sleep(1)  # Rate limiting
            except:
                pass
        
        return None
    
    def _check_archive_today(self, target: str, result: ChallengeResult) -> str:
        """Check archive.today for snapshots"""
        result.add_log(f"Checking archive.today for: {target}")
        
        if not target.startswith('http'):
            target = f"http://{target}"
        
        try:
            api_url = f"https://archive.ph/{quote_plus(target)}"
            response = self.session.get(api_url, timeout=self.timeout)
            
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log("Found flag in archive.today")
                return flag
        except:
            pass
        
        return None
    
    def _check_social_media_advanced(self, target: str, result: ChallengeResult) -> str:
        """Advanced social media enumeration"""
        result.add_log(f"Advanced social media check for: {target}")
        
        username = target.lstrip('@')
        
        # Check all platforms
        for platform, url_template in self.SOCIAL_PLATFORMS.items():
            if url_template is None:
                continue
            
            try:
                url = url_template.format(username)
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                
                if response.status_code == 200:
                    result.add_log(f"Found profile on {platform}: {url}")
                    
                    # Parse page for flag
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check bio/description
                    for tag in soup.find_all(['meta', 'p', 'span', 'div']):
                        text = tag.get_text() if hasattr(tag, 'get_text') else str(tag.get('content', ''))
                        flag = self.extract_flag(text)
                        if flag:
                            result.add_log(f"Found flag on {platform}")
                            return flag
            except:
                pass
        
        return None
    
    def _check_dns_history(self, target: str, result: ChallengeResult) -> str:
        """Check DNS history"""
        result.add_log(f"Checking DNS history for: {target}")
        
        if target.startswith('http'):
            target = urlparse(target).netloc
        
        try:
            # SecurityTrails (if API key available)
            # ViewDNS.info
            api_url = f"https://viewdns.info/dnsrecord/?domain={quote_plus(target)}"
            response = self.session.get(api_url, timeout=self.timeout)
            
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log("Found flag in DNS history")
                return flag
        except:
            pass
        
        return None
    
    def _check_ssl_certificates(self, target: str, result: ChallengeResult) -> str:
        """Check SSL certificate transparency logs"""
        result.add_log(f"Checking SSL certificates for: {target}")
        
        if target.startswith('http'):
            target = urlparse(target).netloc
        
        try:
            # crt.sh
            api_url = f"https://crt.sh/?q={quote_plus(target)}&output=json"
            response = self.session.get(api_url, timeout=self.timeout)
            
            if response.status_code == 200:
                certs = response.json()
                
                for cert in certs[:20]:
                    name = cert.get('name_value', '')
                    flag = self.extract_flag(name)
                    if flag:
                        result.add_log("Found flag in SSL certificate")
                        return flag
                    
                    # Log interesting subdomains
                    if 'flag' in name.lower() or 'secret' in name.lower():
                        result.add_log(f"Interesting cert: {name}")
        except:
            pass
        
        return None
    
    def _check_subdomains(self, target: str, result: ChallengeResult) -> str:
        """Enumerate subdomains"""
        result.add_log(f"Enumerating subdomains for: {target}")
        
        if target.startswith('http'):
            target = urlparse(target).netloc
        
        # Common subdomains to check
        subdomains = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'test', 'staging',
            'api', 'app', 'beta', 'demo', 'flag', 'secret', 'hidden', 'ctf',
            'vpn', 'remote', 'portal', 'login', 'secure', 'internal', 'private',
        ]
        
        for sub in subdomains:
            try:
                import socket
                hostname = f"{sub}.{target}"
                ip = socket.gethostbyname(hostname)
                result.add_log(f"Found subdomain: {hostname} -> {ip}")
                
                # Try to fetch the subdomain
                try:
                    response = self.session.get(f"http://{hostname}", timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag on {hostname}")
                        return flag
                except:
                    pass
            except:
                pass
        
        return None
    
    def _check_github_advanced(self, target: str, result: ChallengeResult) -> str:
        """Advanced GitHub reconnaissance"""
        result.add_log(f"Advanced GitHub check for: {target}")
        
        username = target.lstrip('@')
        
        try:
            # Check gists
            gists_url = f"https://api.github.com/users/{username}/gists"
            response = self.session.get(gists_url, timeout=self.timeout)
            
            if response.status_code == 200:
                gists = response.json()
                for gist in gists[:10]:
                    for filename, file_info in gist.get('files', {}).items():
                        raw_url = file_info.get('raw_url', '')
                        if raw_url:
                            try:
                                content = self.session.get(raw_url, timeout=self.timeout).text
                                flag = self.extract_flag(content)
                                if flag:
                                    result.add_log(f"Found flag in gist: {filename}")
                                    return flag
                            except:
                                pass
            
            # Check starred repos
            starred_url = f"https://api.github.com/users/{username}/starred"
            response = self.session.get(starred_url, timeout=self.timeout)
            
            if response.status_code == 200:
                starred = response.json()
                for repo in starred[:5]:
                    name = repo.get('full_name', '')
                    flag = self.extract_flag(name)
                    if flag:
                        return flag
            
            # Search code
            search_url = f"https://api.github.com/search/code?q=user:{username}+flag"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                results = response.json()
                for item in results.get('items', [])[:10]:
                    html_url = item.get('html_url', '')
                    result.add_log(f"Potential flag file: {html_url}")
                    
        except:
            pass
        
        return None
    
    def _check_gitlab(self, target: str, result: ChallengeResult) -> str:
        """Check GitLab for information"""
        result.add_log(f"Checking GitLab for: {target}")
        
        username = target.lstrip('@')
        
        try:
            api_url = f"https://gitlab.com/api/v4/users?username={username}"
            response = self.session.get(api_url, timeout=self.timeout)
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    user = users[0]
                    user_id = user.get('id')
                    
                    # Get user's projects
                    projects_url = f"https://gitlab.com/api/v4/users/{user_id}/projects"
                    proj_response = self.session.get(projects_url, timeout=self.timeout)
                    
                    if proj_response.status_code == 200:
                        projects = proj_response.json()
                        for project in projects[:10]:
                            name = project.get('name', '')
                            desc = project.get('description', '') or ''
                            
                            flag = self.extract_flag(name + ' ' + desc)
                            if flag:
                                result.add_log("Found flag in GitLab project")
                                return flag
        except:
            pass
        
        return None
    
    def _check_paste_sites(self, target: str, result: ChallengeResult) -> str:
        """Check multiple paste sites"""
        result.add_log(f"Checking paste sites for: {target}")
        
        for site in self.PASTE_SITES:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q=site:{site}+{quote_plus(target)}"
                response = self.session.get(search_url, timeout=self.timeout)
                
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Found flag on {site}")
                    return flag
            except:
                pass
        
        return None
    
    def _check_breach_data(self, target: str, result: ChallengeResult) -> str:
        """Check for data breaches"""
        result.add_log(f"Checking breach data for: {target}")
        
        # Check if target is an email
        if '@' in target:
            try:
                # HaveIBeenPwned (requires API key)
                api_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote_plus(target)}"
                headers = {'hibp-api-key': self.config.get('modules.osint.api_keys.hibp', '')}
                
                response = self.session.get(api_url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    breaches = response.json()
                    result.add_log(f"Found {len(breaches)} breaches for {target}")
                    
                    for breach in breaches:
                        name = breach.get('Name', '')
                        flag = self.extract_flag(name)
                        if flag:
                            return flag
            except:
                pass
        
        return None
    
    def _reverse_image_search(self, target: str, result: ChallengeResult) -> str:
        """Perform reverse image search"""
        result.add_log(f"Reverse image search for: {target}")
        
        # If target is a URL to an image
        if target.startswith('http') and any(ext in target.lower() for ext in ['.jpg', '.png', '.gif', '.jpeg']):
            try:
                # TinEye API or Google Images
                search_url = f"https://www.google.com/searchbyimage?image_url={quote_plus(target)}"
                result.add_log(f"Google reverse image: {search_url}")
                
                # Yandex
                yandex_url = f"https://yandex.com/images/search?url={quote_plus(target)}&rpt=imageview"
                result.add_log(f"Yandex reverse image: {yandex_url}")
            except:
                pass
        
        return None
    
    def _check_exif_gps(self, target: str, result: ChallengeResult) -> str:
        """Check EXIF data for GPS coordinates"""
        result.add_log(f"Checking EXIF GPS for: {target}")
        
        # If target is an image URL
        if target.startswith('http') and any(ext in target.lower() for ext in ['.jpg', '.jpeg']):
            try:
                response = self.session.get(target, timeout=self.timeout)
                
                # Try to extract EXIF
                from PIL import Image
                from PIL.ExifTags import TAGS, GPSTAGS
                import io
                
                img = Image.open(io.BytesIO(response.content))
                exif = img._getexif()
                
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'GPSInfo':
                            result.add_log(f"GPS data found: {value}")
                        
                        flag = self.extract_flag(str(value))
                        if flag:
                            result.add_log("Found flag in EXIF data")
                            return flag
            except:
                pass
        
        return None
    
    def _check_shodan(self, target: str, result: ChallengeResult) -> str:
        """Check Shodan for information"""
        result.add_log(f"Checking Shodan for: {target}")
        
        if not self.shodan_key:
            return None
        
        try:
            # Check if target is IP
            import socket
            try:
                ip = socket.gethostbyname(target.replace('http://', '').replace('https://', '').split('/')[0])
            except:
                ip = target
            
            api_url = f"https://api.shodan.io/shodan/host/{ip}?key={self.shodan_key}"
            response = self.session.get(api_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check banners
                for service in data.get('data', []):
                    banner = service.get('data', '')
                    flag = self.extract_flag(banner)
                    if flag:
                        result.add_log("Found flag in Shodan banner")
                        return flag
                
                # Check hostnames
                for hostname in data.get('hostnames', []):
                    flag = self.extract_flag(hostname)
                    if flag:
                        return flag
        except:
            pass
        
        return None
    
    def _check_censys(self, target: str, result: ChallengeResult) -> str:
        """Check Censys for information"""
        result.add_log(f"Checking Censys for: {target}")
        
        if not self.censys_id or not self.censys_secret:
            return None
        
        try:
            import socket
            try:
                ip = socket.gethostbyname(target.replace('http://', '').replace('https://', '').split('/')[0])
            except:
                ip = target
            
            api_url = f"https://search.censys.io/api/v2/hosts/{ip}"
            response = self.session.get(
                api_url,
                auth=(self.censys_id, self.censys_secret),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                flag = self.extract_flag(json.dumps(data))
                if flag:
                    result.add_log("Found flag in Censys data")
                    return flag
        except:
            pass
        
        return None
    
    def _check_virustotal(self, target: str, result: ChallengeResult) -> str:
        """Check VirusTotal for information"""
        result.add_log(f"Checking VirusTotal for: {target}")
        
        if not self.virustotal_key:
            return None
        
        try:
            # Domain/URL lookup
            if target.startswith('http'):
                url_id = hashlib.sha256(target.encode()).hexdigest()
                api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            else:
                api_url = f"https://www.virustotal.com/api/v3/domains/{target}"
            
            headers = {'x-apikey': self.virustotal_key}
            response = self.session.get(api_url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                flag = self.extract_flag(json.dumps(data))
                if flag:
                    result.add_log("Found flag in VirusTotal data")
                    return flag
        except:
            pass
        
        return None
    
    def _check_urlscan(self, target: str, result: ChallengeResult) -> str:
        """Check urlscan.io for information"""
        result.add_log(f"Checking urlscan.io for: {target}")
        
        try:
            search_url = f"https://urlscan.io/api/v1/search/?q=domain:{target}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                for result_item in data.get('results', [])[:10]:
                    page = result_item.get('page', {})
                    
                    # Check various fields
                    for field in ['url', 'domain', 'title']:
                        value = page.get(field, '')
                        flag = self.extract_flag(value)
                        if flag:
                            result.add_log("Found flag in urlscan data")
                            return flag
        except:
            pass
        
        return None