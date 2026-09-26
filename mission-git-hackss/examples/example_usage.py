#!/usr/bin/env python3
"""Example usage of MD-EXPLOIT-ENGINE"""

from pathlib import Path
from core.engine import ExploitEngine
from core.config import Config
from core.challenge import Challenge


def example_solve_file():
    """Example: Solve challenge from file"""
    print("Example 1: Solving challenge from file")
    print("-" * 50)
    
    config = Config('config/config.yaml')
    engine = ExploitEngine(config)
    
    # Solve a challenge file
    result = engine.solve_challenge('challenges/crypto_challenge.txt')
    
    if result.success:
        print(f"✓ Success! Flag: {result.flag}")
    else:
        print(f"✗ Failed: {result.error}")
    
    print()


def example_solve_web():
    """Example: Solve web challenge"""
    print("Example 2: Solving web challenge")
    print("-" * 50)
    
    config = Config('config/config.yaml')
    engine = ExploitEngine(config)
    
    # Create web challenge
    challenge = Challenge(
        name="web_challenge",
        category="web",
        url="http://example.com/challenge",
        description="Find the flag in this web application"
    )
    
    # Solve
    result = engine.solve_challenge(challenge.name, category='web')
    
    if result.success:
        print(f"✓ Success! Flag: {result.flag}")
        print(f"Method: {result.method}")
        print(f"Duration: {result.duration:.2f}s")
    else:
        print(f"✗ Failed: {result.error}")
    
    print()


def example_solve_crypto():
    """Example: Solve crypto challenge"""
    print("Example 3: Solving crypto challenge")
    print("-" * 50)
    
    from modules.crypto import CryptoModule
    
    config = Config('config/config.yaml')
    module = CryptoModule(config)
    
    # Create challenge with base64 encoded flag
    challenge = Challenge(
        name="crypto_challenge",
        category="crypto",
        description="ZmxhZ3t0aGlzX2lzX2FfZmxhZ30="  # base64: flag{this_is_a_flag}
    )
    
    result = module.solve(challenge)
    
    if result.success:
        print(f"✓ Success! Flag: {result.flag}")
    else:
        print(f"✗ Failed: {result.error}")
    
    print()


def example_batch_solve():
    """Example: Solve multiple challenges"""
    print("Example 4: Batch solving challenges")
    print("-" * 50)
    
    config = Config('config/config.yaml')
    engine = ExploitEngine(config, threads=4)
    
    challenges = [
        'challenges/challenge1.txt',
        'challenges/challenge2.zip',
        'challenges/challenge3.bin',
    ]
    
    results = []
    for challenge_path in challenges:
        if Path(challenge_path).exists():
            result = engine.solve_challenge(challenge_path)
            results.append(result)
            
            status = "✓" if result.success else "✗"
            print(f"{status} {challenge_path}: {result.flag or result.error}")
    
    # Summary
    solved = sum(1 for r in results if r.success)
    print(f"\nSolved: {solved}/{len(results)}")
    print()


def example_custom_module():
    """Example: Using a specific module directly"""
    print("Example 5: Using specific module")
    print("-" * 50)
    
    from modules.forensics import ForensicsModule
    
    config = Config('config/config.yaml')
    module = ForensicsModule(config)
    
    challenge = Challenge(
        name="forensics_challenge",
        category="forensics",
        files=[Path("challenges/image.png")]
    )
    
    if challenge.files[0].exists():
        result = module.solve(challenge)
        
        if result.success:
            print(f"✓ Success! Flag: {result.flag}")
            print(f"Method: {result.method}")
        else:
            print(f"✗ Failed: {result.error}")
    else:
        print("Challenge file not found")
    
    print()


def main():
    """Run all examples"""
    print("=" * 50)
    print("MD-EXPLOIT-ENGINE Examples")
    print("=" * 50)
    print()
    
    try:
        example_solve_crypto()
        # Uncomment to run other examples:
        # example_solve_file()
        # example_solve_web()
        # example_batch_solve()
        # example_custom_module()
    except Exception as e:
        print(f"Error: {e}")
    
    print("=" * 50)
    print("Examples completed")
    print("=" * 50)


if __name__ == '__main__':
    main()
