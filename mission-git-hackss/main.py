#!/usr/bin/env python3
"""
================================================================================
MD-EXPLOIT-ENGINE - Automated CTF Challenge Solver
================================================================================
Developed by: Md Abu Shalem Alam
Version: 1.0.0
Description: The Ultimate Automated CTF Challenge Solver with AI-Powered Analysis
================================================================================
"""

import sys
import argparse
import logging
from pathlib import Path

from core.engine import ExploitEngine
from core.config import Config
from api.server import APIServer
from web.dashboard import Dashboard
from utils.logger import setup_logger
from utils.database import Database
from utils.writeup_generator import WriteupGenerator
from utils.notifications import NotificationManager

__author__ = "Md Abu Shalem Alam"
__version__ = "1.0.0"


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='MD-EXPLOIT-ENGINE - Automated CTF Challenge Solver | Developed by Md Abu Shalem Alam',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --challenge challenge.zip
  %(prog)s --challenge challenge.zip --category web
  %(prog)s --web --port 8080
  %(prog)s --api --host 0.0.0.0 --port 5000
  %(prog)s --batch challenges/ --threads 8
        '''
    )
    
    # Challenge solving
    parser.add_argument('--challenge', '-c', type=str,
                       help='Path to challenge file or directory')
    parser.add_argument('--url', '-u', type=str,
                       help='URL for web challenges (e.g., http://target.com)')
    parser.add_argument('--category', type=str,
                       help='Force challenge category (web, crypto, pwn, rev, forensics, osint, misc)')
    parser.add_argument('--batch', '-b', type=str,
                       help='Batch solve all challenges in directory')
    
    # Server modes
    parser.add_argument('--web', action='store_true',
                       help='Start web dashboard')
    parser.add_argument('--api', action='store_true',
                       help='Start API server')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host for web/API server')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port for web/API server')
    
    # Configuration
    parser.add_argument('--config', type=str, default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--threads', type=int, default=4,
                       help='Number of worker threads')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout per challenge in seconds')
    
    # Output
    parser.add_argument('--writeup', action='store_true',
                       help='Generate writeup for solved challenges')
    parser.add_argument('--output', '-o', type=str,
                       help='Output directory for writeups')
    parser.add_argument('--format', type=str, default='markdown',
                       choices=['markdown', 'html', 'json'],
                       help='Writeup format')
    
    # Modes
    parser.add_argument('--educational', action='store_true',
                       help='Educational mode - show hints instead of solutions')
    parser.add_argument('--safe', action='store_true',
                       help='Safe mode - disable dangerous operations')
    parser.add_argument('--quick', action='store_true',
                       help='Quick mode - run only fast techniques (for web challenges)')
    
    # Logging
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet mode - minimal output')
    
    return parser.parse_args()


def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Setup logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    logger = setup_logger('md-exploit-engine', level=log_level)
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           MD-EXPLOIT-ENGINE v1.0.0                       ║
    ║           Automated CTF Challenge Solver                 ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    logger.info("Starting MD-EXPLOIT-ENGINE")
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            # Try example config
            example_config = Path('config/config.example.yaml')
            if example_config.exists():
                import shutil
                config_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(example_config, config_path)
                logger.info(f"Created config from example: {config_path}")
            else:
                logger.error(f"Configuration file not found: {args.config}")
                return 1
        
        config = Config(str(config_path))
        
        # Initialize database
        db = Database(config.get('database.path', 'data/md-exploit-engine.db'))
        
        # Initialize notification manager
        notifier = NotificationManager(config)
        
        # Start web dashboard
        if args.web:
            logger.info(f"Starting web dashboard on {args.host}:{args.port}")
            dashboard = Dashboard(config, host=args.host, port=args.port)
            dashboard.run()
            return 0
        
        # Start API server
        if args.api:
            logger.info(f"Starting API server on {args.host}:{args.port}")
            api_server = APIServer(config, host=args.host, port=args.port)
            api_server.run()
            return 0
        
        # Batch solve
        if args.batch:
            return batch_solve(args, config, db, notifier, logger)
        
        # Solve single challenge
        if args.challenge:
            return solve_challenge(args, config, db, notifier, logger)
        
        # Solve web challenge by URL
        if args.url:
            return solve_web_challenge(args, config, db, notifier, logger)
        
        # No action specified
        print("No action specified. Use --help for usage information.")
        print("\nQuick start:")
        print("  python main.py --challenge challenge.zip")
        print("  python main.py --url http://target.com --category web")
        print("  python main.py --web --port 8080")
        return 1
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


def solve_challenge(args, config, db, notifier, logger):
    """Solve a single challenge"""
    engine = ExploitEngine(config, threads=args.threads, timeout=args.timeout)
    
    result = engine.solve_challenge(
        args.challenge,
        category=args.category
    )
    
    # Save to database
    db.save_result(result)
    if result.flag:
        db.save_flag(result.flag)
    
    # Generate writeup
    if args.writeup and result.success:
        output_dir = args.output or 'writeups'
        generator = WriteupGenerator(output_dir)
        writeup_path = generator.save(result, args.format)
        logger.info(f"Writeup saved to: {writeup_path}")
    
    # Send notification
    if result.success:
        notifier.notify(result)
    
    # Print result
    if result.success:
        print(f"\n[+] ✅ Challenge solved!")
        print(f"[+] Flag: {result.flag}")
        print(f"[+] Method: {result.method}")
        print(f"[+] Duration: {result.duration:.2f}s")
        return 0
    else:
        print(f"\n[-] ❌ Failed to solve challenge")
        print(f"[-] Error: {result.error}")
        return 1


def solve_web_challenge(args, config, db, notifier, logger):
    """Solve a web challenge by URL"""
    from core.challenge import Challenge
    from modules.web import WebModule
    
    print(f"\n[*] Testing URL: {args.url}")
    print(f"[*] Running web exploitation techniques...")
    if args.quick:
        print(f"[*] Quick mode enabled - running fast techniques only")
    
    # Create challenge object with URL
    challenge = Challenge(
        name=f"web_{args.url.replace('://', '_').replace('/', '_')[:50]}",
        url=args.url,
        category='web'
    )
    
    # Initialize web module
    web_module = WebModule(config)
    
    # Set quick mode if requested
    if args.quick:
        web_module.quick_mode = True
    
    # Solve
    import time
    start_time = time.time()
    result = web_module.solve(challenge)
    result.duration = time.time() - start_time
    
    # Save to database
    db.save_result(result)
    if result.flag:
        db.save_flag(result.flag)
    
    # Generate writeup
    if args.writeup and result.success:
        output_dir = args.output or 'writeups'
        generator = WriteupGenerator(output_dir)
        writeup_path = generator.save(result, args.format)
        logger.info(f"Writeup saved to: {writeup_path}")
    
    # Send notification
    if result.success:
        notifier.notify(result)
    
    # Print result
    print(f"\n{'='*60}")
    if result.success:
        print(f"[+] ✅ Web challenge solved!")
        print(f"[+] Flag: {result.flag}")
        print(f"[+] Method: {result.method}")
        print(f"[+] Duration: {result.duration:.2f}s")
        return 0
    else:
        print(f"[-] ❌ No flag found")
        print(f"[-] Techniques tried: {len(result.logs) if hasattr(result, 'logs') else 'N/A'}")
        if result.error:
            print(f"[-] Error: {result.error}")
        
        # Print logs for debugging
        if hasattr(result, 'logs') and result.logs:
            print(f"\n[*] Analysis logs:")
            for log in result.logs[-10:]:  # Last 10 logs
                print(f"    {log}")
        return 1


def batch_solve(args, config, db, notifier, logger):
    """Batch solve multiple challenges"""
    batch_dir = Path(args.batch)
    if not batch_dir.exists():
        logger.error(f"Batch directory not found: {args.batch}")
        return 1
    
    engine = ExploitEngine(config, threads=args.threads, timeout=args.timeout)
    results = []
    
    # Find all challenge files
    challenge_files = list(batch_dir.glob('*'))
    print(f"\n[*] Found {len(challenge_files)} challenges")
    
    for i, challenge_path in enumerate(challenge_files, 1):
        if challenge_path.is_file():
            print(f"\n[{i}/{len(challenge_files)}] Solving: {challenge_path.name}")
            
            result = engine.solve_challenge(str(challenge_path), category=args.category)
            results.append(result)
            
            # Save to database
            db.save_result(result)
            if result.flag:
                db.save_flag(result.flag)
            
            if result.success:
                print(f"    ✅ Solved! Flag: {result.flag}")
                notifier.notify(result)
            else:
                print(f"    ❌ Failed: {result.error}")
    
    # Generate summary
    if args.writeup:
        output_dir = args.output or 'writeups'
        generator = WriteupGenerator(output_dir)
        summary = generator.generate_summary(results)
        summary_path = Path(output_dir) / 'summary.md'
        summary_path.write_text(summary)
        print(f"\n[+] Summary saved to: {summary_path}")
    
    # Print summary
    solved = sum(1 for r in results if r.success)
    print(f"\n{'='*50}")
    print(f"Results: {solved}/{len(results)} challenges solved")
    print(f"{'='*50}")
    
    # Send summary notification
    notifier.send_summary(results)
    
    return 0 if solved > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
