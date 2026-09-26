#!/usr/bin/env python3
"""
Final attempt - The flag must be on actual social media
Let's construct the exact flag based on the pattern
"""

# Based on the clues:
# - Author: Harshil (from metadata)
# - Challenge author listed as: Haardik Bhagtani / catty_batty4
# - QR: "There are 2 season and 5 level!!!"
# - Metadata: "where author chose to exist socially"

# The typo "socically" might be intentional
# Maybe we need to search for variations

import requests

def try_common_flag_patterns():
    """Try common CTF flag patterns based on the challenge"""
    print("[*] Trying common flag patterns...")
    
    # Common patterns for OSINT challenges
    patterns = [
        "Kaal{raven_found_the_truth}",
        "Kaal{2_seasons_5_levels}",
        "Kaal{harshil_catty_batty4}",
        "Kaal{social_media_hunt}",
        "Kaal{osint_master}",
        "Kaal{follow_the_raven}",
        "Kaal{distant_lands}",
        "Kaal{author_truth}",
        "Kaal{haardik_bhagtani}",
        "Kaal{catty_batty4}",
        "Kaal{2seasons5levels}",
        "Kaal{harshil}",
        "Kaal{socially_exist}",
        "Kaal{raven_mystery}",
        "Kaal{pieces_of_truth}",
    ]
    
    print("\n[*] Possible flags to try:")
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern}")
    
    return patterns

def search_alternative_platforms():
    """Search for author on alternative platforms"""
    print("\n[*] Alternative platforms to check:")
    
    platforms = {
        "LinkedIn": "https://www.linkedin.com/search/results/all/?keywords=Haardik%20Bhagtani",
        "Facebook": "https://www.facebook.com/search/top?q=catty_batty4",
        "YouTube": "https://www.youtube.com/results?search_query=catty_batty4",
        "TikTok": "https://www.tiktok.com/search?q=catty_batty4",
        "Reddit": "https://www.reddit.com/search/?q=catty_batty4",
        "Discord": "Search for catty_batty4 in CTF Discord servers",
        "Telegram": "Search for @catty_batty4",
        "CTFtime": "https://ctftime.org/user/search?q=catty_batty4",
    }
    
    for platform, url in platforms.items():
        print(f"  {platform}: {url}")

def check_ctf_platform():
    """The challenge might have hints on the CTF platform itself"""
    print("\n[*] Check the CTF platform where this challenge is hosted!")
    print("    - Look at challenge comments/discussions")
    print("    - Check author's profile on the platform")
    print("    - Look for hints in challenge updates")
    print("    - Check if there are related challenges")

if __name__ == "__main__":
    print("="*70)
    print("FINAL RAVEN CHALLENGE ANALYSIS")
    print("="*70)
    print("\nKEY FINDINGS:")
    print("1. Image metadata author: Harshil")
    print("2. Challenge author: Haardik Bhagtani / catty_batty4")
    print("3. QR code: 'There are 2 season and 5 level!!!'")
    print("4. Metadata hint: 'where author chose to exist socially' (typo: socically)")
    print("5. Social media accounts (Instagram/Twitter) don't exist")
    print("="*70)
    
    patterns = try_common_flag_patterns()
    search_alternative_platforms()
    check_ctf_platform()
    
    print("\n" + "="*70)
    print("RECOMMENDED ACTIONS:")
    print("="*70)
    print("1. Try all the flag patterns listed above")
    print("2. Search for 'Haardik Bhagtani' on LinkedIn/Facebook")
    print("3. Search for 'Harshil' + 'CTF' or 'Harshil' + 'Raven'")
    print("4. Check the CTF platform's user profiles")
    print("5. Look for the author's other challenges on the same platform")
    print("6. The '2 seasons 5 levels' might refer to:")
    print("   - 2 social platforms, 5 posts each")
    print("   - Season 2 Episode 5 of something")
    print("   - 2nd and 5th letter of something")
    print("="*70)
