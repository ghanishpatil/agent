"""
================================================================================
MD-EXPLOIT-ENGINE - Web Dashboard (Cyber Command Center)
================================================================================
Developed by: Md Abu Shalem Alam
Description: Hacker-themed web dashboard for CTF challenge solving
Features: Live logs, Path Finder, Suspect Files, Flag Celebration
================================================================================
"""

import logging
import time
from flask import Flask, render_template, jsonify, request
from pathlib import Path

from core.engine import ExploitEngine
from core.challenge import Challenge

__author__ = "Md Abu Shalem Alam"


class Dashboard:
    """Hacker-themed web dashboard for MD-EXPLOIT-ENGINE - Developed by Md Abu Shalem Alam"""
    
    def __init__(self, config, host: str = '127.0.0.1', port: int = 8080):
        self.config = config
        self.host = host
        self.port = port
        self.logger = logging.getLogger('md-exploit-engine.dashboard')
        
        self.app = Flask(__name__, 
                        template_folder=str(Path(__file__).parent / 'templates'),
                        static_folder=str(Path(__file__).parent / 'static'))
        
        # Disable template caching for development
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.jinja_env.auto_reload = True
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        
        self.app.secret_key = config.get('web.secret_key', 'md-exploit-secret-key-change-me')
        self.engine = ExploitEngine(config)
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        @self.app.route('/index')
        @self.app.route('/dashboard')
        def index():
            # Directly read and serve the HTML file to bypass any caching
            template_file = Path(__file__).parent / 'templates' / 'index.html'
            print(f"[DEBUG] Reading template from: {template_file}")
            print(f"[DEBUG] File exists: {template_file.exists()}")
            with open(template_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            print(f"[DEBUG] Content length: {len(html_content)}")
            print(f"[DEBUG] Has 'Cyber Command Center': {'Cyber Command Center' in html_content}")
            print(f"[DEBUG] Has 'matrix-bg': {'matrix-bg' in html_content}")
            from flask import Response
            response = Response(html_content, mimetype='text/html')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        @self.app.route('/api/solve', methods=['POST'])
        def solve():
            data = request.json
            start_time = time.time()
            
            try:
                challenge_path = data.get('challenge')
                url = data.get('url')
                category = data.get('category')
                quick_mode = data.get('quick', True)  # Default to quick mode
                
                # Handle URL-based web challenges
                if url and not challenge_path:
                    from modules.web import WebModule
                    
                    challenge = Challenge(
                        name=f"web_{url.replace('://', '_').replace('/', '_')[:50]}",
                        url=url,
                        category='web'
                    )
                    
                    web_module = WebModule(self.config)
                    web_module.quick_mode = quick_mode
                    
                    result = web_module.solve(challenge)
                    result.duration = time.time() - start_time
                    
                    return jsonify({
                        'success': result.success,
                        'flag': result.flag,
                        'method': result.method,
                        'duration': result.duration,
                        'category': 'web',
                        'error': result.error,
                        'logs': result.logs if hasattr(result, 'logs') else []
                    })
                
                # Handle file-based challenges
                if challenge_path:
                    result = self.engine.solve_challenge(
                        challenge_path,
                        category=category
                    )
                    
                    return jsonify({
                        'success': result.success,
                        'flag': result.flag,
                        'method': result.method,
                        'duration': result.duration,
                        'category': result.category if hasattr(result, 'category') else None,
                        'error': result.error,
                        'logs': result.logs if hasattr(result, 'logs') else []
                    })
                
                return jsonify({'error': 'No challenge or URL provided'}), 400
            
            except Exception as e:
                self.logger.exception(f"Error solving challenge: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'duration': time.time() - start_time
                }), 500

        @self.app.route('/api/status')
        def status():
            """Get system status"""
            modules = self.engine.module_registry.list_modules() if hasattr(self.engine, 'module_registry') else []
            return jsonify({
                'status': 'online',
                'version': '1.0.0',
                'modules': modules,
                'module_count': len(modules)
            })
        
        @self.app.route('/api/modules')
        def modules():
            """Get detailed module information"""
            module_list = self.engine.module_registry.list_modules() if hasattr(self.engine, 'module_registry') else []
            return jsonify({
                'modules': [
                    {
                        'name': m,
                        'status': 'active',
                        'description': self._get_module_description(m)
                    }
                    for m in module_list
                ]
            })
        
        @self.app.route('/api/stats')
        def stats():
            """Get solving statistics"""
            return jsonify({
                'total_solved': 0,
                'flags_captured': 0,
                'success_rate': 100,
                'avg_solve_time': 0
            })
        
        @self.app.route('/api/extract-paths', methods=['POST'])
        def extract_paths():
            """Extract all paths and directories from a website"""
            data = request.json
            start_time = time.time()
            
            try:
                url = data.get('url')
                depth = data.get('depth', 1)
                
                if not url:
                    return jsonify({'error': 'No URL provided'}), 400
                
                from modules.web import WebModule
                
                web_module = WebModule(self.config)
                extracted = web_module.extract_all_paths(url, depth=depth)
                
                return jsonify({
                    'success': True,
                    'duration': time.time() - start_time,
                    'data': extracted
                })
                
            except RuntimeError as e:
                # Handle ThreadPoolExecutor shutdown errors gracefully
                if 'cannot schedule new futures' in str(e) or 'interpreter shutdown' in str(e):
                    self.logger.warning(f"Server reloading, please retry: {e}")
                    return jsonify({
                        'success': False,
                        'error': 'Server is reloading, please try again',
                        'duration': time.time() - start_time
                    }), 503
                raise
            except Exception as e:
                self.logger.exception(f"Error extracting paths: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'duration': time.time() - start_time
                }), 500
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'engine': 'MD-EXPLOIT-ENGINE'})
    
    def _get_module_description(self, module_name: str) -> str:
        """Get module description"""
        descriptions = {
            'web': 'Web exploitation - SQLi, XSS, SSTI, LFI, and more',
            'crypto': 'Cryptography - Classical ciphers, RSA, AES, hashing',
            'pwn': 'Binary exploitation - Buffer overflow, ROP, heap',
            'reversing': 'Reverse engineering - Disassembly, decompilation',
            'forensics': 'Digital forensics - File carving, memory analysis',
            'osint': 'Open source intelligence - Social media, DNS, WHOIS',
            'misc': 'Miscellaneous challenges'
        }
        return descriptions.get(module_name, 'Unknown module')
    
    def run(self):
        """Start the cyber command center"""
        template_path = Path(__file__).parent / 'templates' / 'index.html'
        print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║         MD-EXPLOIT-ENGINE CYBER COMMAND CENTER           ║
    ║                                                          ║
    ║   🌐 Dashboard: http://{self.host}:{self.port:<24}║
    ║   📡 Status: ONLINE                                      ║
    ║   📁 Template: {str(template_path)[:40]:<40}║
    ╚══════════════════════════════════════════════════════════╝
        """)
        print(f"[DEBUG] Template exists: {template_path.exists()}")
        self.logger.info(f"Starting Cyber Command Center on {self.host}:{self.port}")
        # Disable reloader to prevent ThreadPoolExecutor issues
        # The reloader causes "cannot schedule new futures after interpreter shutdown" errors
        self.app.run(host=self.host, port=self.port, debug=True, threaded=True, use_reloader=False)
