# Raven Challenge - Complete Solution Guide

## Challenge Information
- **Author**: catty_batty4 (Haardik Bhagtani)
- **Flag Format**: Kaal{...}
- **Category**: OSINT (Open Source Intelligence)
- **Difficulty**: Medium

## Key Clues

### 1. Image Metadata
From `Raven.png`:
- **Author**: Harshil
- **Comment**: "What you see is only part of it—the rest lies in where author chose to exist socially."

### 2. QR Code Message
After scanning the QR code in the image:
> "There are 2 season and 5 level!!! All The Best!!!"

## Solution Strategy

This is an OSINT challenge where you need to:
1. Find the author's social media profiles
2. Look for posts/content related to "2 seasons and 5 levels"
3. Collect flag pieces from different posts/platforms

## Platforms to Check

### Confirmed Active Profiles:
1. **Instagram**: https://www.instagram.com/catty_batty4/
   - Status: Profile exists (200 OK)
   - Action: Manually visit and check posts for flag pieces

2. **Twitter/X**: https://twitter.com/catty_batty4
   - Status: Profile exists (200 OK)
   - Action: Manually visit and check tweets for flag pieces

### Other Platforms to Try:
3. **GitHub**: https://github.com/catty_batty4
   - Look for repositories with "2 seasons" or "5 levels" in name/description
   - Check README files, commit messages, issues

4. **Pastebin**: https://pastebin.com/u/catty_batty4
   - Look for pastes with flag pieces

5. **Medium**: https://medium.com/@catty_batty4
   - Check for blog posts

6. **Dev.to**: https://dev.to/catty_batty4
   - Check for articles

7. **Reddit**: https://www.reddit.com/user/catty_batty4
   - Check posts and comments

8. **LinkedIn**: Search for "Haardik Bhagtani"
   - Check posts and profile information

## What to Look For

### Keywords:
- "2 seasons"
- "5 levels"
- "Kaal{"
- "Raven"
- Flag pieces (might be split across multiple posts)

### Possible Scenarios:
1. **Split Flag**: The flag might be split into multiple parts across different platforms
   - Example: Instagram has "Kaal{part1_", Twitter has "part2_", etc.

2. **Encoded Flag**: The flag might be encoded in:
   - Image captions
   - Post descriptions
   - Bio/About sections
   - Pinned posts

3. **Sequential Posts**: Look for posts numbered 1-5 (5 levels) across 2 platforms (2 seasons)

## Manual Steps

1. **Visit Instagram Profile**:
   ```
   https://www.instagram.com/catty_batty4/
   ```
   - Check all posts (especially recent ones)
   - Read captions carefully
   - Check bio
   - Look for stories/highlights

2. **Visit Twitter Profile**:
   ```
   https://twitter.com/catty_batty4
   ```
   - Check all tweets
   - Check pinned tweet
   - Read bio
   - Check media tab

3. **Search for Related Content**:
   - Google: "catty_batty4 Kaal flag"
   - Google: "Haardik Bhagtani CTF"
   - Check if there are any public writeups or hints

## Expected Flag Format
```
Kaal{...}
```

## Tips
- The "2 seasons and 5 levels" might refer to:
  - 2 social media platforms (seasons)
  - 5 posts/pieces (levels) to collect
- Take screenshots of any relevant posts
- Combine pieces in the correct order
- The flag might be hidden in plain sight or require some decoding

## Next Steps
Since automated scraping is blocked by Instagram and Twitter, you MUST:
1. Manually visit the profiles using a web browser
2. Log in if necessary
3. Document all flag pieces you find
4. Combine them to form the complete flag

Good luck! 🎯
