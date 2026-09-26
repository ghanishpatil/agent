"""
Test script for ULTRA Path Finder
Demonstrates comprehensive path discovery on CTF websites
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from modules.pathfinder import UltraPathFinder, find_all_paths
import requests

def test_pathfinder(url: str):
    """Test the ULTRA Path Finder on a URL"""
    print("=" * 70)
    print("ULTRA PATH FINDER TEST")
    print("=" * 70)
    print(f"Target: {url}")
    print("=" * 70)
    
    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    session.verify = False
    
    # Create finder
    finder = UltraPathFinder(session=session, timeout=10, max_threads=15, max_depth=2)
    
    # Run scan
    def progress(msg):
        print(msg)
    
    results = finder.find_all_paths(url, callback=progress)
    
    # Print results
    print(finder.print_results(results))
    
    return results


if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://ghost-terminal.onrender.com/",
    ]
    
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    for url in test_urls:
        try:
            results = test_pathfinder(url)
            print(f"\nTotal paths found: {results['total_paths']}")
        except Exception as e:
            print(f"Error testing {url}: {e}")
