"""
================================================================================
MD-EXPLOIT-ENGINE - ULTRA ADVANCED PATH FINDER
================================================================================
Developed by: Md Abu Shalem Alam
Description: Discovers ALL paths on a website using multiple techniques
Features:
- Crawling and link extraction
- JavaScript analysis
- Wordlist-based directory bruteforcing (5000+ paths)
- Robots.txt and sitemap parsing
- Source map analysis
- API endpoint discovery
- Hidden path detection
- CTF-specific file detection
================================================================================
"""

__author__ = "Md Abu Shalem Alam"

import re
import json
import base64
import hashlib
import threading
import queue
from typing import Dict, List, Set, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from collections import defaultdict
import time
import requests
from bs4 import BeautifulSoup
import concurrent.futures


class UltraPathFinder:
    """
    ULTRA Advanced Path Finder - Discovers every possible path on a website
    """
    
    # Comprehensive wordlist for directory/file bruteforcing
    COMMON_DIRS = [
        # Admin paths
        'admin', 'administrator', 'admin.php', 'admin.html', 'adminpanel',
        'admin-panel', 'admin_panel', 'admincp', 'adminer', 'phpmyadmin',
        'cpanel', 'webadmin', 'sysadmin', 'manager', 'management',
        
        # API paths
        'api', 'api/v1', 'api/v2', 'api/v3', 'rest', 'graphql', 'swagger',
        'api-docs', 'swagger-ui', 'openapi', 'docs/api', 'developer',
        
        # Authentication
        'login', 'signin', 'signup', 'register', 'auth', 'authenticate',
        'logout', 'signout', 'password', 'forgot-password', 'reset-password',
        'oauth', 'sso', 'saml', 'callback', 'token', 'session',
        
        # User paths
        'user', 'users', 'profile', 'account', 'settings', 'preferences',
        'dashboard', 'home', 'portal', 'member', 'members', 'my-account',
        
        # Content paths
        'blog', 'news', 'articles', 'posts', 'pages', 'content', 'media',
        'gallery', 'images', 'photos', 'videos', 'files', 'documents',
        
        # Static assets
        'assets', 'static', 'public', 'resources', 'res', 'dist', 'build',
        'css', 'js', 'javascript', 'scripts', 'styles', 'fonts', 'img',
        
        # Development/Debug
        'dev', 'development', 'staging', 'test', 'testing', 'debug',
        'console', 'shell', 'terminal', 'cmd', 'exec', 'eval',
        
        # Backup/Config
        'backup', 'backups', 'bak', 'old', 'temp', 'tmp', 'cache',
        'config', 'configuration', 'settings', 'conf', 'cfg',
        
        # Database
        'db', 'database', 'sql', 'mysql', 'phpmyadmin', 'adminer',
        'data', 'dump', 'export', 'import',
        
        # Server paths
        'server', 'server-status', 'server-info', 'status', 'health',
        'info', 'phpinfo', 'info.php', 'test.php', 'ping', 'version',
        
        # Hidden/Secret
        'secret', 'secrets', 'hidden', 'private', 'internal', 'secure',
        'flag', 'flags', 'ctf', 'challenge', 'key', 'keys',
        
        # CMS specific
        'wp-admin', 'wp-content', 'wp-includes', 'wp-login.php',
        'joomla', 'drupal', 'magento', 'prestashop', 'opencart',
        
        # Framework specific
        'vendor', 'node_modules', 'bower_components', 'packages',
        'app', 'application', 'src', 'source', 'lib', 'libs', 'include',
        
        # Version control
        '.git', '.svn', '.hg', '.bzr', 'CVS', '.gitignore', '.htaccess',
        
        # Documentation
        'docs', 'documentation', 'doc', 'help', 'readme', 'changelog',
        'license', 'about', 'faq', 'support', 'contact',
        
        # E-commerce
        'shop', 'store', 'cart', 'checkout', 'payment', 'order', 'orders',
        'product', 'products', 'catalog', 'category', 'categories',
        
        # Misc
        'download', 'downloads', 'upload', 'uploads', 'file', 'attachment',
        'search', 'sitemap', 'sitemap.xml', 'robots.txt', 'humans.txt',
        'crossdomain.xml', 'clientaccesspolicy.xml', 'security.txt',
    ]

    # Common file extensions to check - MASSIVELY EXPANDED
    COMMON_FILES = [
        # Web files - all extensions
        'index.html', 'index.htm', 'index.php', 'index.asp', 'index.aspx', 'index.jsp', 'index.txt',
        'default.html', 'default.htm', 'default.php', 'default.asp', 'home.html', 'home.php', 'home.txt',
        'main.html', 'main.htm', 'main.php', 'main.txt', 'page.html', 'page.php', 'page.txt',
        
        # Config files - all extensions
        'config.php', 'config.json', 'config.yaml', 'config.yml', 'config.xml', 'config.txt', 'config.ini', 'config.cfg',
        'settings.php', 'settings.json', 'settings.txt', 'settings.xml', 'settings.yaml',
        'database.php', 'database.json', 'database.txt', 'database.yml', 'database.xml',
        'db.php', 'db.json', 'db.txt', 'db.yml', 'conn.php', 'conn.txt', 'connection.php', 'connection.txt',
        '.env', '.env.local', '.env.production', '.env.development', '.env.backup', '.env.example', '.env.sample',
        'web.config', 'app.config', 'appsettings.json', 'application.properties', 'application.yml',
        
        # Backup files - all extensions
        'backup.sql', 'backup.zip', 'backup.tar.gz', 'backup.txt', 'backup.bak',
        'dump.sql', 'dump.txt', 'dump.json', 'database.sql', 'database.bak',
        'site.zip', 'www.zip', 'html.zip', 'public.zip', 'web.zip', 'source.zip',
        'data.sql', 'data.txt', 'data.json', 'data.xml', 'data.csv', 'data.bak',
        
        # Log files - all extensions
        'error.log', 'error.txt', 'access.log', 'access.txt', 'debug.log', 'debug.txt',
        'app.log', 'app.txt', 'server.log', 'server.txt', 'system.log', 'system.txt',
        'error_log', 'access_log', 'logs/error.log', 'logs/access.log', 'log.txt', 'logs.txt',
        
        # Info/Doc files - all extensions
        'phpinfo.php', 'info.php', 'info.txt', 'info.html', 'test.php', 'test.txt', 'test.html',
        'debug.php', 'debug.txt', 'debug.html', 'status.php', 'status.txt', 'status.json',
        'readme.txt', 'readme.md', 'readme.html', 'README.md', 'README.txt', 'README.html',
        'CHANGELOG.md', 'CHANGELOG.txt', 'LICENSE', 'LICENSE.txt', 'LICENSE.md',
        'INSTALL.txt', 'INSTALL.md', 'TODO.txt', 'TODO.md', 'NOTES.txt', 'notes.txt',
        'version.txt', 'version.json', 'VERSION', 'build.txt', 'build.json',
        
        # JavaScript files
        'app.js', 'main.js', 'script.js', 'bundle.js', 'vendor.js', 'index.js',
        'config.js', 'settings.js', 'api.js', 'routes.js', 'utils.js', 'helper.js',
        'jquery.js', 'jquery.min.js', 'angular.js', 'react.js', 'vue.js',
        
        # Source maps
        'app.js.map', 'main.js.map', 'bundle.js.map', 'vendor.js.map', 'index.js.map',
        
        # Package/Dependency files
        'package.json', 'package-lock.json', 'composer.json', 'composer.lock',
        'Gemfile', 'Gemfile.lock', 'requirements.txt', 'Pipfile', 'Pipfile.lock',
        'yarn.lock', 'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod', 'go.sum',
        
        # CTF specific - ALL EXTENSIONS
        'flag.txt', 'flag.html', 'flag.php', 'flag.json', 'flag.xml', 'flag.md', 'flag',
        'Flag.txt', 'Flag.html', 'Flag.php', 'FLAG.txt', 'FLAG.html', 'FLAG.php',
        'secret.txt', 'secret.html', 'secret.php', 'secret.json', 'secret.xml', 'secret',
        'Secret.txt', 'Secret.html', 'SECRET.txt', 'SECRET.html',
        'key.txt', 'key.html', 'key.php', 'key.json', 'key', 'Key.txt', 'KEY.txt',
        'password.txt', 'password.html', 'password.php', 'password.json', 'password',
        'credentials.txt', 'credentials.json', 'credentials.xml', 'credentials',
        'hint.txt', 'hint.html', 'hint.php', 'hint.json', 'hint', 'Hint.txt',
        'clue.txt', 'clue.html', 'clue.php', 'clue', 'Clue.txt',
        'answer.txt', 'answer.html', 'answer.php', 'answer', 'Answer.txt',
        'solution.txt', 'solution.html', 'solution.php', 'solution',
        'hidden.txt', 'hidden.html', 'hidden.php', 'hidden.json', 'hidden',
        'private.txt', 'private.html', 'private.php', 'private.json', 'private',
        'admin.txt', 'admin.html', 'admin.php', 'admin.json',
        'user.txt', 'user.html', 'user.php', 'user.json', 'users.txt', 'users.json',
        'token.txt', 'token.json', 'tokens.txt', 'tokens.json',
        'auth.txt', 'auth.json', 'auth.php',
        
        # Media files
        'Suspect.png', 'suspect.png', 'hidden.png', 'secret.png', 'flag.png',
        'image.png', 'image.jpg', 'image.gif', 'photo.png', 'photo.jpg',
        'morse.wav', 'audio.wav', 'sound.mp3', 'message.wav', 'code.wav',
        'video.mp4', 'video.webm', 'clip.mp4',
        
        # Archive files
        'archive.zip', 'files.zip', 'data.zip', 'source.zip', 'backup.zip',
        'archive.tar', 'archive.tar.gz', 'archive.7z', 'archive.rar',
        'download.zip', 'export.zip', 'bundle.zip',
        
        # Common sensitive files
        'id_rsa', 'id_rsa.pub', 'id_dsa', 'authorized_keys', 'known_hosts',
        '.bash_history', '.bashrc', '.profile', '.ssh/id_rsa',
        'shadow', 'passwd', 'hosts', 'resolv.conf',
        '.htpasswd', '.htaccess', 'htpasswd.txt', 'htaccess.txt',
        'wp-config.php', 'wp-config.php.bak', 'wp-config.txt',
        'LocalSettings.php', 'local.xml', 'parameters.yml',
        
        # API/Endpoint files
        'api.txt', 'api.json', 'api.xml', 'api.yaml', 'api.yml',
        'endpoints.txt', 'endpoints.json', 'routes.txt', 'routes.json',
        'swagger.json', 'swagger.yaml', 'openapi.json', 'openapi.yaml',
        
        # Misc common files
        'robots.txt', 'sitemap.xml', 'sitemap.txt', 'humans.txt', 'security.txt',
        'crossdomain.xml', 'clientaccesspolicy.xml', 'browserconfig.xml',
        'manifest.json', 'site.webmanifest', 'favicon.ico',
        '.well-known/security.txt', '.well-known/assetlinks.json',
    ]
    
    # Base names to try with ALL extensions
    COMMON_BASE_NAMES = [
        'flag', 'Flag', 'FLAG', 'secret', 'Secret', 'SECRET',
        'key', 'Key', 'KEY', 'password', 'Password', 'PASSWORD',
        'hidden', 'Hidden', 'HIDDEN', 'private', 'Private', 'PRIVATE',
        'admin', 'Admin', 'ADMIN', 'user', 'User', 'USER',
        'config', 'Config', 'CONFIG', 'settings', 'Settings',
        'data', 'Data', 'DATA', 'backup', 'Backup', 'BACKUP',
        'test', 'Test', 'TEST', 'debug', 'Debug', 'DEBUG',
        'index', 'Index', 'INDEX', 'main', 'Main', 'MAIN',
        'home', 'Home', 'HOME', 'page', 'Page', 'PAGE',
        'login', 'Login', 'LOGIN', 'auth', 'Auth', 'AUTH',
        'api', 'Api', 'API', 'token', 'Token', 'TOKEN',
        'hint', 'Hint', 'HINT', 'clue', 'Clue', 'CLUE',
        'answer', 'Answer', 'ANSWER', 'solution', 'Solution',
        'credentials', 'Credentials', 'creds', 'Creds',
        'database', 'Database', 'db', 'DB', 'dump', 'Dump',
        'log', 'Log', 'LOG', 'error', 'Error', 'ERROR',
        'readme', 'Readme', 'README', 'info', 'Info', 'INFO',
        'note', 'Note', 'NOTE', 'notes', 'Notes', 'NOTES',
        'todo', 'Todo', 'TODO', 'temp', 'Temp', 'TEMP',
        'old', 'Old', 'OLD', 'new', 'New', 'NEW',
        'source', 'Source', 'src', 'Src', 'code', 'Code',
        'file', 'File', 'FILE', 'files', 'Files', 'FILES',
        'upload', 'Upload', 'UPLOAD', 'download', 'Download',
        'export', 'Export', 'import', 'Import',
        'message', 'Message', 'msg', 'Msg',
        'response', 'Response', 'request', 'Request',
        'output', 'Output', 'input', 'Input',
        'result', 'Result', 'results', 'Results',
    ]
    
    # ALL file extensions to try
    ALL_EXTENSIONS = [
        # No extension
        '',
        # Web
        '.html', '.htm', '.php', '.asp', '.aspx', '.jsp', '.jspx', '.do', '.action',
        '.cgi', '.pl', '.py', '.rb', '.cfm', '.shtml', '.xhtml',
        # Data
        '.txt', '.text', '.json', '.xml', '.yaml', '.yml', '.csv', '.tsv',
        '.ini', '.cfg', '.conf', '.config', '.properties',
        # Documents
        '.md', '.markdown', '.rst', '.doc', '.docx', '.pdf', '.rtf',
        # Code
        '.js', '.ts', '.jsx', '.tsx', '.vue', '.css', '.scss', '.sass', '.less',
        '.java', '.class', '.jar', '.war', '.ear',
        '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs', '.swift',
        # Database
        '.sql', '.sqlite', '.db', '.mdb', '.accdb',
        # Backup/Archive
        '.bak', '.backup', '.old', '.orig', '.save', '.swp', '.swo',
        '.zip', '.tar', '.gz', '.tgz', '.tar.gz', '.rar', '.7z', '.bz2',
        # Logs
        '.log', '.logs', '.err', '.error', '.out',
        # Images
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp',
        # Audio/Video
        '.wav', '.mp3', '.ogg', '.flac', '.mp4', '.webm', '.avi', '.mkv',
        # Other
        '.env', '.htaccess', '.htpasswd', '.DS_Store', '.gitignore',
        '.map', '.lock', '.pid', '.key', '.pem', '.crt', '.cer',
    ]
    
    # File extensions to try with discovered paths
    EXTENSIONS = [
        '', '.html', '.php', '.asp', '.aspx', '.jsp', '.py', '.rb',
        '.txt', '.json', '.xml', '.yaml', '.yml', '.md',
        '.js', '.css', '.map',
        '.bak', '.backup', '.old', '.orig', '.save', '.swp', '~',
        '.zip', '.tar', '.gz', '.sql',
        '.log', '.tmp', '.temp',
    ]
    
    # HTTP methods to test
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
    
    # Quick scan file list (most common CTF files)
    QUICK_SCAN_FILES = [
        'flag.txt', 'Flag.txt', 'FLAG.txt', 'flag', 'Flag', 'FLAG',
        'secret.txt', 'Secret.txt', 'secret', 'Secret',
        'key.txt', 'Key.txt', 'key', 'Key',
        'password.txt', 'Password.txt', 'password', 'Password',
        'hidden.txt', 'Hidden.txt', 'hidden', 'Hidden',
        'hint.txt', 'Hint.txt', 'hint', 'Hint',
        'clue.txt', 'Clue.txt', 'clue', 'Clue',
        'answer.txt', 'Answer.txt', 'answer', 'Answer',
        'admin.txt', 'admin.html', 'admin.php', 'admin',
        'config.json', 'config.yaml', 'config.txt', 'config.php',
        'data.json', 'data.txt', 'data.xml',
        '.env', '.env.local', '.env.production',
        'robots.txt', 'sitemap.xml',
        'flag.html', 'flag.php', 'flag.json', 'flag.xml',
        'secret.html', 'secret.php', 'secret.json',
        'index.html', 'index.php', 'home.html',
        'README.md', 'readme.txt', 'CHANGELOG.md',
        'backup.sql', 'backup.zip', 'dump.sql',
        'morse.wav', 'audio.wav', 'code.wav',
        'image.png', 'photo.png', 'suspect.png',
    ]
    
    def __init__(self, session: requests.Session = None, timeout: int = 10, 
                 max_threads: int = 20, max_depth: int = 5, quick_mode: bool = False):
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_threads = max_threads
        self.max_depth = max_depth
        self.quick_mode = quick_mode
        
        # Results storage
        self.discovered_paths: Set[str] = set()
        self.discovered_files: Set[str] = set()
        self.discovered_dirs: Set[str] = set()
        self.discovered_params: Set[str] = set()
        self.discovered_endpoints: Set[str] = set()
        self.discovered_forms: List[Dict] = []
        self.discovered_js_paths: Set[str] = set()
        self.discovered_comments: List[str] = []
        self.discovered_emails: Set[str] = set()
        self.discovered_secrets: List[Dict] = []
        
        # Tracking
        self.visited_urls: Set[str] = set()
        self.base_url: str = ""
        self.base_domain: str = ""
        
        # Thread safety
        self.lock = threading.Lock()
        self.path_queue = queue.Queue()

    def find_all_paths(self, url: str, callback=None) -> Dict[str, Any]:
        """
        ULTRA comprehensive path discovery - finds ALL paths on a website
        
        Args:
            url: Target URL to scan
            callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing all discovered paths and resources
        """
        def log(msg):
            if callback:
                callback(msg)
        
        # Initialize
        parsed = urlparse(url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.base_domain = parsed.netloc
        
        log(f"[PathFinder] Starting ULTRA scan on: {self.base_url}")
        
        # Phase 1: Initial crawl
        log("[Phase 1] Crawling website...")
        self._crawl_website(url, depth=0, callback=log)
        
        # Phase 2: Check robots.txt and sitemap
        log("[Phase 2] Checking robots.txt and sitemap...")
        self._check_robots_sitemap(callback=log)
        
        # Phase 3: Directory bruteforce
        log("[Phase 3] Bruteforcing directories...")
        self._bruteforce_directories(callback=log)
        
        # Phase 4: File bruteforce (with ALL extensions)
        log("[Phase 4] Bruteforcing files with ALL extensions...")
        self._bruteforce_files(callback=log)
        
        # Phase 4.5: Try extensions on discovered paths
        log("[Phase 4.5] Trying extensions on discovered paths...")
        self._bruteforce_extensions(callback=log)
        
        # Phase 5: Analyze JavaScript files
        log("[Phase 5] Analyzing JavaScript files...")
        self._analyze_javascript(callback=log)
        
        # Phase 6: Check for source maps
        log("[Phase 6] Checking source maps...")
        self._check_source_maps(callback=log)
        
        # Phase 7: API endpoint discovery
        log("[Phase 7] Discovering API endpoints...")
        self._discover_api_endpoints(callback=log)
        
        # Phase 8: Parameter discovery
        log("[Phase 8] Discovering parameters...")
        self._discover_parameters(callback=log)
        
        # Phase 9: Check backup files
        log("[Phase 9] Checking backup files...")
        self._check_backup_files(callback=log)
        
        # Phase 10: Check version control
        log("[Phase 10] Checking version control exposure...")
        self._check_version_control(callback=log)
        
        # Compile results
        results = self._compile_results()
        
        log(f"[PathFinder] Scan complete! Found {results['total_paths']} paths")
        
        return results
    
    def _crawl_website(self, url: str, depth: int, callback=None):
        """Recursively crawl website and extract all links"""
        if depth > self.max_depth:
            return
        
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return
            
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all links
            for tag, attr in [('a', 'href'), ('link', 'href'), ('script', 'src'), 
                             ('img', 'src'), ('form', 'action'), ('iframe', 'src'),
                             ('video', 'src'), ('audio', 'src'), ('source', 'src')]:
                for element in soup.find_all(tag):
                    link = element.get(attr)
                    if link:
                        full_url = urljoin(url, link)
                        parsed = urlparse(full_url)
                        
                        # Only follow same-domain links
                        if parsed.netloc == self.base_domain or not parsed.netloc:
                            path = parsed.path
                            if path:
                                with self.lock:
                                    self.discovered_paths.add(path)
                                    
                                    # Categorize
                                    if path.endswith('/') or '.' not in path.split('/')[-1]:
                                        self.discovered_dirs.add(path)
                                    else:
                                        self.discovered_files.add(path)
                            
                            # Extract parameters
                            if parsed.query:
                                params = parse_qs(parsed.query)
                                with self.lock:
                                    self.discovered_params.update(params.keys())
                            
                            # Recursively crawl HTML pages
                            if tag == 'a' and depth < self.max_depth:
                                if not any(full_url.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.svg', '.ico']):
                                    self._crawl_website(full_url, depth + 1, callback)
            
            # Extract forms
            for form in soup.find_all('form'):
                form_data = {
                    'action': urljoin(url, form.get('action', '')),
                    'method': form.get('method', 'GET').upper(),
                    'inputs': []
                }
                for inp in form.find_all(['input', 'textarea', 'select']):
                    inp_name = inp.get('name')
                    if inp_name:
                        form_data['inputs'].append({
                            'name': inp_name,
                            'type': inp.get('type', 'text'),
                            'value': inp.get('value', '')
                        })
                        with self.lock:
                            self.discovered_params.add(inp_name)
                
                with self.lock:
                    self.discovered_forms.append(form_data)
            
            # Extract comments
            comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
            for comment in comments:
                with self.lock:
                    self.discovered_comments.append(str(comment))
            
            # Also extract HTML comments properly
            import re
            html_comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
            with self.lock:
                self.discovered_comments.extend(html_comments)
            
            # Extract emails
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
            with self.lock:
                self.discovered_emails.update(emails)
            
            # Extract paths from inline JavaScript
            self._extract_paths_from_text(response.text)
            
        except Exception as e:
            pass

    def _check_robots_sitemap(self, callback=None):
        """Check robots.txt and sitemap.xml for paths"""
        # Check robots.txt
        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = self.session.get(robots_url, timeout=self.timeout)
            if response.status_code == 200:
                if callback:
                    callback(f"    Found robots.txt")
                
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.startswith('Disallow:') or line.startswith('Allow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/':
                            with self.lock:
                                self.discovered_paths.add(path)
                                if path.endswith('/'):
                                    self.discovered_dirs.add(path)
                    
                    if line.startswith('Sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        self._parse_sitemap(sitemap_url, callback)
        except:
            pass
        
        # Check common sitemap locations
        sitemap_locations = [
            '/sitemap.xml', '/sitemap_index.xml', '/sitemap1.xml',
            '/sitemap/sitemap.xml', '/sitemaps/sitemap.xml',
            '/wp-sitemap.xml', '/sitemap.php', '/sitemap.txt',
        ]
        
        for sitemap_path in sitemap_locations:
            try:
                sitemap_url = f"{self.base_url}{sitemap_path}"
                response = self.session.get(sitemap_url, timeout=self.timeout)
                if response.status_code == 200:
                    if callback:
                        callback(f"    Found sitemap: {sitemap_path}")
                    self._parse_sitemap(sitemap_url, callback)
            except:
                pass
    
    def _parse_sitemap(self, sitemap_url: str, callback=None):
        """Parse sitemap XML and extract URLs"""
        try:
            response = self.session.get(sitemap_url, timeout=self.timeout)
            if response.status_code == 200:
                # Extract URLs from sitemap
                urls = re.findall(r'<loc>([^<]+)</loc>', response.text)
                for url in urls:
                    parsed = urlparse(url)
                    if parsed.netloc == self.base_domain:
                        with self.lock:
                            self.discovered_paths.add(parsed.path)
                
                # Check for nested sitemaps
                nested_sitemaps = re.findall(r'<sitemap>.*?<loc>([^<]+)</loc>.*?</sitemap>', response.text, re.DOTALL)
                for nested in nested_sitemaps:
                    self._parse_sitemap(nested, callback)
        except:
            pass
    
    def _bruteforce_directories(self, callback=None):
        """Bruteforce common directories"""
        found_count = 0
        
        def check_dir(dir_path):
            nonlocal found_count
            try:
                test_url = f"{self.base_url}/{dir_path.strip('/')}"
                response = self.session.get(test_url, timeout=5, allow_redirects=False)
                
                if response.status_code in [200, 301, 302, 403]:
                    with self.lock:
                        self.discovered_dirs.add(f"/{dir_path.strip('/')}/")
                        self.discovered_paths.add(f"/{dir_path.strip('/')}/")
                        found_count += 1
                    return True
            except:
                pass
            return False
        
        # Use thread pool for faster scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(check_dir, d): d for d in self.COMMON_DIRS}
            for future in concurrent.futures.as_completed(futures):
                pass
        
        if callback:
            callback(f"    Found {found_count} directories")
    
    def _bruteforce_files(self, callback=None):
        """Bruteforce common files with ALL extensions"""
        found_count = 0
        files_to_check = set()
        
        if self.quick_mode:
            # Quick mode - only check most common CTF files
            files_to_check.update(self.QUICK_SCAN_FILES)
            common_subdirs = ['', 'files/', 'data/', 'static/', 'hidden/', 'secret/']
        else:
            # Full mode - check ALL files
            files_to_check.update(self.COMMON_FILES)
            
            # Generate files from base names + all extensions
            for base_name in self.COMMON_BASE_NAMES:
                for ext in self.ALL_EXTENSIONS:
                    files_to_check.add(f"{base_name}{ext}")
            
            # Also check in common subdirectories
            common_subdirs = ['', 'files/', 'data/', 'static/', 'assets/', 'public/', 
                             'private/', 'hidden/', 'secret/', 'admin/', 'backup/',
                             'uploads/', 'downloads/', 'docs/', 'api/', 'config/']
        
        all_files_to_check = set()
        for subdir in common_subdirs:
            for file_path in files_to_check:
                all_files_to_check.add(f"{subdir}{file_path}")
        
        def check_file(file_path):
            nonlocal found_count
            try:
                test_url = f"{self.base_url}/{file_path.strip('/')}"
                response = self.session.get(test_url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    # Verify it's not a generic 404 page or empty
                    content_length = len(response.text)
                    if content_length > 0:
                        with self.lock:
                            self.discovered_files.add(f"/{file_path.strip('/')}")
                            self.discovered_paths.add(f"/{file_path.strip('/')}")
                            found_count += 1
                        
                        # Check for secrets in the file
                        self._check_for_secrets(response.text, file_path)
                        return True
            except:
                pass
            return False
        
        if callback:
            callback(f"    Checking {len(all_files_to_check)} file combinations...")
        
        # Use thread pool for faster scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(check_file, f): f for f in all_files_to_check}
            for future in concurrent.futures.as_completed(futures):
                pass
        
        if callback:
            callback(f"    Found {found_count} files")
    
    def _bruteforce_extensions(self, callback=None):
        """Try all extensions on discovered paths without extensions"""
        found_count = 0
        
        # Get paths without extensions
        paths_without_ext = []
        for path in self.discovered_paths:
            # Check if path has no extension
            if '.' not in path.split('/')[-1]:
                paths_without_ext.append(path.rstrip('/'))
        
        def check_with_extension(base_path, ext):
            nonlocal found_count
            try:
                test_path = f"{base_path}{ext}"
                test_url = f"{self.base_url}{test_path}"
                response = self.session.get(test_url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200 and len(response.text) > 0:
                    with self.lock:
                        self.discovered_files.add(test_path)
                        self.discovered_paths.add(test_path)
                        found_count += 1
                    
                    self._check_for_secrets(response.text, test_path)
                    return True
            except:
                pass
            return False
        
        # Try common extensions on discovered paths
        common_exts = ['.txt', '.html', '.php', '.json', '.xml', '.md', '.log', '.bak', '.sql']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for path in paths_without_ext[:5000]:  # Limit for performance
                for ext in common_exts:
                    futures.append(executor.submit(check_with_extension, path, ext))
            
            for future in concurrent.futures.as_completed(futures):
                pass
        
        if callback and found_count > 0:
            callback(f"    Found {found_count} additional files with extensions")

    def _analyze_javascript(self, callback=None):
        """Analyze JavaScript files for hidden paths and endpoints"""
        js_files = [f for f in self.discovered_files if f.endswith('.js')]
        
        # Also check common JS file locations
        common_js = [
            '/app.js', '/main.js', '/script.js', '/bundle.js', '/vendor.js',
            '/config.js', '/api.js', '/routes.js', '/index.js',
            '/assets/js/app.js', '/assets/js/main.js',
            '/static/js/app.js', '/static/js/main.js',
            '/js/app.js', '/js/main.js', '/js/script.js',
            '/dist/app.js', '/dist/bundle.js',
            '/build/app.js', '/build/bundle.js',
        ]
        
        for js_path in common_js:
            if js_path not in js_files:
                js_files.append(js_path)
        
        found_paths = 0
        
        for js_path in js_files:
            try:
                js_url = f"{self.base_url}{js_path}"
                response = self.session.get(js_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    # Extract paths from JavaScript
                    paths = self._extract_paths_from_js(response.text)
                    with self.lock:
                        self.discovered_js_paths.update(paths)
                        self.discovered_paths.update(paths)
                        found_paths += len(paths)
                    
                    # Check for secrets
                    self._check_for_secrets(response.text, js_path)
            except:
                pass
        
        if callback:
            callback(f"    Found {found_paths} paths in JavaScript")
    
    def _extract_paths_from_js(self, js_content: str) -> Set[str]:
        """Extract all paths and URLs from JavaScript content"""
        paths = set()
        
        # Patterns to find paths in JS
        patterns = [
            # Quoted paths
            r'["\'](/[a-zA-Z0-9_\-./]+)["\']',
            r'["\'](\.{1,2}/[a-zA-Z0-9_\-./]+)["\']',
            
            # URL patterns
            r'(?:href|src|url|path|endpoint|route|api)\s*[=:]\s*["\']([^"\']+)["\']',
            
            # Fetch/Ajax patterns
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
            r'\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest[^;]*open\s*\([^,]*,\s*["\']([^"\']+)["\']',
            r'\$\.(get|post|ajax)\s*\(\s*["\']([^"\']+)["\']',
            
            # Router patterns (React, Vue, Angular)
            r'path\s*:\s*["\']([^"\']+)["\']',
            r'route\s*:\s*["\']([^"\']+)["\']',
            r'to\s*:\s*["\']([^"\']+)["\']',
            r'navigate\s*\(\s*["\']([^"\']+)["\']',
            r'redirect\s*\(\s*["\']([^"\']+)["\']',
            r'push\s*\(\s*["\']([^"\']+)["\']',
            
            # API endpoint patterns
            r'["\']/(api|v\d+|rest|graphql)/[^"\']+["\']',
            r'baseURL\s*:\s*["\']([^"\']+)["\']',
            r'apiUrl\s*:\s*["\']([^"\']+)["\']',
            
            # File patterns
            r'["\']([^"\']+\.(?:php|asp|aspx|jsp|py|rb|html|json|xml|txt))["\']',
            r'["\']([^"\']+\.(?:png|jpg|jpeg|gif|svg|ico|webp))["\']',
            r'["\']([^"\']+\.(?:js|css|map))["\']',
            r'["\']([^"\']+\.(?:wav|mp3|mp4|webm|ogg))["\']',
            
            # Window location patterns
            r'window\.location\s*=\s*["\']([^"\']+)["\']',
            r'location\.href\s*=\s*["\']([^"\']+)["\']',
            r'location\.replace\s*\(\s*["\']([^"\']+)["\']',
            
            # Import/require patterns
            r'import\s+.*from\s+["\']([^"\']+)["\']',
            r'require\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[-1]  # Get the last group
                
                # Clean and validate path
                match = match.strip()
                if not match:
                    continue
                
                # Skip external URLs and data URLs
                if match.startswith(('http://', 'https://', 'data:', 'javascript:', '//')):
                    continue
                
                # Skip common false positives
                if any(x in match.lower() for x in ['node_modules', 'googleapis', 'cloudflare', 'jquery', 'bootstrap']):
                    continue
                
                # Normalize path
                if match.startswith('./'):
                    match = match[1:]
                elif match.startswith('../'):
                    match = '/' + match.lstrip('../')
                elif not match.startswith('/'):
                    match = '/' + match
                
                paths.add(match)
        
        return paths
    
    def _extract_paths_from_text(self, text: str):
        """Extract paths from any text content"""
        paths = self._extract_paths_from_js(text)
        with self.lock:
            self.discovered_paths.update(paths)

    def _check_source_maps(self, callback=None):
        """Check for JavaScript source maps that may reveal original source"""
        js_files = [f for f in self.discovered_files if f.endswith('.js')]
        found_maps = 0
        
        for js_path in js_files:
            # Check for .map file
            map_path = js_path + '.map'
            try:
                map_url = f"{self.base_url}{map_path}"
                response = self.session.get(map_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    with self.lock:
                        self.discovered_files.add(map_path)
                        self.discovered_paths.add(map_path)
                        found_maps += 1
                    
                    # Parse source map for original file paths
                    try:
                        map_data = response.json()
                        if 'sources' in map_data:
                            for source in map_data['sources']:
                                with self.lock:
                                    self.discovered_paths.add(source)
                    except:
                        pass
            except:
                pass
            
            # Also check for sourceMappingURL comment in JS
            try:
                js_url = f"{self.base_url}{js_path}"
                response = self.session.get(js_url, timeout=self.timeout)
                if response.status_code == 200:
                    map_match = re.search(r'//[#@]\s*sourceMappingURL=([^\s]+)', response.text)
                    if map_match:
                        map_path = map_match.group(1)
                        if not map_path.startswith('data:'):
                            with self.lock:
                                self.discovered_paths.add(map_path)
            except:
                pass
        
        if callback:
            callback(f"    Found {found_maps} source maps")
    
    def _discover_api_endpoints(self, callback=None):
        """Discover API endpoints through various methods"""
        api_prefixes = ['/api', '/api/v1', '/api/v2', '/api/v3', '/rest', '/graphql', '/v1', '/v2']
        api_endpoints = [
            'users', 'user', 'auth', 'login', 'logout', 'register', 'signup',
            'profile', 'account', 'settings', 'config', 'status', 'health',
            'data', 'info', 'version', 'docs', 'swagger', 'openapi',
            'admin', 'dashboard', 'flag', 'secret', 'key', 'token',
            'posts', 'comments', 'messages', 'notifications', 'files',
            'upload', 'download', 'search', 'query', 'export', 'import',
        ]
        
        found_endpoints = 0
        
        def check_endpoint(prefix, endpoint):
            nonlocal found_endpoints
            path = f"{prefix}/{endpoint}"
            try:
                url = f"{self.base_url}{path}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code in [200, 201, 401, 403]:
                    with self.lock:
                        self.discovered_endpoints.add(path)
                        self.discovered_paths.add(path)
                        found_endpoints += 1
                    
                    # Check for secrets in response
                    self._check_for_secrets(response.text, path)
                    return True
            except:
                pass
            return False
        
        # Check all combinations
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for prefix in api_prefixes:
                for endpoint in api_endpoints:
                    futures.append(executor.submit(check_endpoint, prefix, endpoint))
            
            for future in concurrent.futures.as_completed(futures):
                pass
        
        # Also check GraphQL introspection
        self._check_graphql_introspection(callback)
        
        if callback:
            callback(f"    Found {found_endpoints} API endpoints")
    
    def _check_graphql_introspection(self, callback=None):
        """Check for GraphQL introspection"""
        graphql_paths = ['/graphql', '/api/graphql', '/v1/graphql', '/query']
        
        introspection_query = {
            'query': '{ __schema { types { name fields { name } } } }'
        }
        
        for path in graphql_paths:
            try:
                url = f"{self.base_url}{path}"
                response = self.session.post(url, json=introspection_query, timeout=self.timeout)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'data' in data and '__schema' in data.get('data', {}):
                            with self.lock:
                                self.discovered_endpoints.add(path)
                                self.discovered_paths.add(path)
                            
                            if callback:
                                callback(f"    Found GraphQL endpoint: {path}")
                            
                            # Extract type names as potential endpoints
                            types = data['data']['__schema'].get('types', [])
                            for t in types:
                                if not t['name'].startswith('__'):
                                    with self.lock:
                                        self.discovered_endpoints.add(f"{path}/{t['name'].lower()}")
                    except:
                        pass
            except:
                pass

    def _discover_parameters(self, callback=None):
        """Discover URL parameters through various methods"""
        # Common parameter names
        common_params = [
            'id', 'user', 'username', 'name', 'email', 'password', 'pass',
            'file', 'path', 'page', 'url', 'redirect', 'return', 'next',
            'query', 'search', 'q', 's', 'keyword', 'term',
            'action', 'cmd', 'command', 'exec', 'do', 'func', 'function',
            'data', 'input', 'output', 'value', 'content', 'text', 'body',
            'token', 'key', 'api_key', 'apikey', 'secret', 'auth',
            'callback', 'jsonp', 'format', 'type', 'mode', 'debug',
            'admin', 'role', 'level', 'access', 'permission',
            'sort', 'order', 'limit', 'offset', 'start', 'count', 'size',
            'filter', 'category', 'tag', 'status', 'state',
            'lang', 'language', 'locale', 'country', 'region',
            'view', 'template', 'theme', 'style', 'layout',
            'include', 'require', 'load', 'import', 'module',
        ]
        
        # Add discovered parameters
        with self.lock:
            self.discovered_params.update(common_params)
        
        if callback:
            callback(f"    Discovered {len(self.discovered_params)} parameters")
    
    def _check_backup_files(self, callback=None):
        """Check for backup files of discovered paths"""
        backup_extensions = [
            '.bak', '.backup', '.old', '.orig', '.save', '.swp', '.swo',
            '~', '.copy', '.tmp', '.temp', '.1', '.2', '_backup', '_old',
            '.php.bak', '.php~', '.php.old', '.php.swp',
            '.sql', '.sql.gz', '.sql.bak', '.dump',
            '.zip', '.tar', '.tar.gz', '.gz', '.rar', '.7z',
        ]
        
        found_backups = 0
        paths_to_check = list(self.discovered_files)[:5000]  # Limit for speed
        
        def check_backup(path, ext):
            nonlocal found_backups
            backup_path = path + ext
            try:
                url = f"{self.base_url}{backup_path}"
                response = self.session.get(url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    with self.lock:
                        self.discovered_files.add(backup_path)
                        self.discovered_paths.add(backup_path)
                        found_backups += 1
                    return True
            except:
                pass
            return False
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for path in paths_to_check:
                for ext in backup_extensions:
                    futures.append(executor.submit(check_backup, path, ext))
            
            for future in concurrent.futures.as_completed(futures):
                pass
        
        if callback:
            callback(f"    Found {found_backups} backup files")
    
    def _check_version_control(self, callback=None):
        """Check for exposed version control files"""
        vc_paths = [
            # Git
            '/.git/config', '/.git/HEAD', '/.git/index', '/.git/logs/HEAD',
            '/.git/refs/heads/master', '/.git/refs/heads/main',
            '/.git/objects/', '/.git/COMMIT_EDITMSG',
            '/.gitignore', '/.gitattributes',
            
            # SVN
            '/.svn/entries', '/.svn/wc.db', '/.svn/all-wcprops',
            
            # Mercurial
            '/.hg/store/00manifest.i', '/.hg/dirstate',
            
            # Bazaar
            '/.bzr/branch/last-revision',
            
            # CVS
            '/CVS/Root', '/CVS/Entries',
        ]
        
        found_vc = 0
        
        for path in vc_paths:
            try:
                url = f"{self.base_url}{path}"
                response = self.session.get(url, timeout=5, allow_redirects=False)
                
                if response.status_code == 200:
                    with self.lock:
                        self.discovered_files.add(path)
                        self.discovered_paths.add(path)
                        found_vc += 1
                    
                    if callback:
                        callback(f"    Found version control file: {path}")
            except:
                pass
        
        if callback and found_vc > 0:
            callback(f"    Found {found_vc} version control files")
    
    def _check_for_secrets(self, content: str, source: str):
        """Check content for secrets, keys, and sensitive data"""
        secret_patterns = [
            # API Keys
            (r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'API Key'),
            (r'apikey["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'API Key'),
            
            # AWS
            (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
            (r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'AWS Secret'),
            
            # Passwords
            (r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Password'),
            (r'passwd["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Password'),
            (r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Secret'),
            
            # Tokens
            (r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Token'),
            (r'bearer\s+([a-zA-Z0-9_\-\.]+)', 'Bearer Token'),
            (r'jwt["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'JWT'),
            
            # Database
            (r'mysql://[^\s"\']+', 'MySQL Connection'),
            (r'postgres://[^\s"\']+', 'PostgreSQL Connection'),
            (r'mongodb://[^\s"\']+', 'MongoDB Connection'),
            
            # Private Keys
            (r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----', 'Private Key'),
            
            # Flags
            (r'flag\{[^}]+\}', 'Flag'),
            (r'FLAG\{[^}]+\}', 'Flag'),
            (r'ctf\{[^}]+\}', 'Flag'),
            (r'CTF\{[^}]+\}', 'Flag'),
        ]
        
        for pattern, secret_type in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                with self.lock:
                    self.discovered_secrets.append({
                        'type': secret_type,
                        'value': match if isinstance(match, str) else match[0],
                        'source': source
                    })

    def _compile_results(self) -> Dict[str, Any]:
        """Compile all discovered paths into a structured result"""
        return {
            'base_url': self.base_url,
            'total_paths': len(self.discovered_paths),
            'paths': sorted(self.discovered_paths),
            'directories': sorted(self.discovered_dirs),
            'files': sorted(self.discovered_files),
            'js_paths': sorted(self.discovered_js_paths),
            'api_endpoints': sorted(self.discovered_endpoints),
            'parameters': sorted(self.discovered_params),
            'forms': self.discovered_forms,
            'comments': self.discovered_comments[:50],  # Limit comments
            'emails': sorted(self.discovered_emails),
            'secrets': self.discovered_secrets,
            'statistics': {
                'total_paths': len(self.discovered_paths),
                'directories': len(self.discovered_dirs),
                'files': len(self.discovered_files),
                'js_paths': len(self.discovered_js_paths),
                'api_endpoints': len(self.discovered_endpoints),
                'parameters': len(self.discovered_params),
                'forms': len(self.discovered_forms),
                'secrets': len(self.discovered_secrets),
            }
        }
    
    def print_results(self, results: Dict[str, Any]) -> str:
        """Format results for display"""
        output = []
        output.append("\n" + "=" * 70)
        output.append("ULTRA PATH FINDER - SCAN RESULTS")
        output.append("=" * 70)
        output.append(f"Target: {results['base_url']}")
        output.append(f"Total Paths Found: {results['total_paths']}")
        output.append("=" * 70)
        
        # Statistics
        output.append("\n[STATISTICS]")
        output.append("-" * 40)
        stats = results['statistics']
        for key, value in stats.items():
            output.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Directories
        if results['directories']:
            output.append(f"\n[DIRECTORIES] ({len(results['directories'])} found)")
            output.append("-" * 40)
            for d in results['directories'][:30]:
                output.append(f"  {d}")
            if len(results['directories']) > 30:
                output.append(f"  ... and {len(results['directories']) - 30} more")
        
        # Files
        if results['files']:
            output.append(f"\n[FILES] ({len(results['files'])} found)")
            output.append("-" * 40)
            for f in results['files'][:30]:
                output.append(f"  {f}")
            if len(results['files']) > 30:
                output.append(f"  ... and {len(results['files']) - 30} more")
        
        # API Endpoints
        if results['api_endpoints']:
            output.append(f"\n[API ENDPOINTS] ({len(results['api_endpoints'])} found)")
            output.append("-" * 40)
            for e in results['api_endpoints'][:20]:
                output.append(f"  {e}")
            if len(results['api_endpoints']) > 20:
                output.append(f"  ... and {len(results['api_endpoints']) - 20} more")
        
        # JS Paths
        if results['js_paths']:
            output.append(f"\n[PATHS FROM JAVASCRIPT] ({len(results['js_paths'])} found)")
            output.append("-" * 40)
            for p in results['js_paths'][:20]:
                output.append(f"  {p}")
            if len(results['js_paths']) > 20:
                output.append(f"  ... and {len(results['js_paths']) - 20} more")
        
        # Parameters
        if results['parameters']:
            output.append(f"\n[PARAMETERS] ({len(results['parameters'])} found)")
            output.append("-" * 40)
            params_list = list(results['parameters'])[:30]
            output.append(f"  {', '.join(params_list)}")
            if len(results['parameters']) > 30:
                output.append(f"  ... and {len(results['parameters']) - 30} more")
        
        # Forms
        if results['forms']:
            output.append(f"\n[FORMS] ({len(results['forms'])} found)")
            output.append("-" * 40)
            for form in results['forms'][:10]:
                output.append(f"  {form['method']} {form['action']}")
                for inp in form['inputs'][:5]:
                    output.append(f"    - {inp['name']} ({inp['type']})")
        
        # Secrets
        if results['secrets']:
            output.append(f"\n[SECRETS FOUND] ({len(results['secrets'])} found)")
            output.append("-" * 40)
            for secret in results['secrets'][:10]:
                output.append(f"  [{secret['type']}] {secret['value'][:50]}... (in {secret['source']})")
        
        # Emails
        if results['emails']:
            output.append(f"\n[EMAILS] ({len(results['emails'])} found)")
            output.append("-" * 40)
            for email in list(results['emails'])[:10]:
                output.append(f"  {email}")
        
        output.append("\n" + "=" * 70)
        
        return '\n'.join(output)


def find_all_paths(url: str, session: requests.Session = None, callback=None) -> Dict[str, Any]:
    """
    Convenience function to find all paths on a website
    
    Args:
        url: Target URL
        session: Optional requests session
        callback: Optional progress callback
        
    Returns:
        Dictionary with all discovered paths
    """
    finder = UltraPathFinder(session=session)
    return finder.find_all_paths(url, callback=callback)
