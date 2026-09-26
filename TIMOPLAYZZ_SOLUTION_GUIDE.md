# TimoPlayzzz OSINT Challenge - Solution Guide

## Challenge Information
- **Target**: @TimoPlayzzz YouTube Channel
- **URL**: https://www.youtube.com/@TimoPlayzzz
- **Category**: OSINT
- **Points**: 300
- **Difficulty**: Medium
- **Flag Format**: Kaal{}
- **Author**: HXpl0it

## How to Solve

### Step 1: Access the YouTube Channel
Visit: https://www.youtube.com/@TimoPlayzzz

### Step 2: Check These Locations (in order of likelihood)

#### A. Channel "About" Section
1. Click on the "About" tab on the channel
2. Look for:
   - Channel description
   - Social media links
   - Email address
   - Any hidden text or encoded messages

#### B. Video Descriptions
1. Check all uploaded videos
2. Look in video descriptions for:
   - Flag directly written
   - Encoded text (Base64, ROT13, etc.)
   - Links to external sites
   - Hidden messages

#### C. Pinned Comment
1. Check if there's a pinned comment on any video
2. Channel owners often hide flags in pinned comments

#### D. Community Tab
1. Check the "Community" tab if available
2. Look for posts with flags or clues

#### E. Channel Banner/Profile Picture
1. Download the channel banner image
2. Download the profile picture
3. Check for:
   - Steganography (use tools like `steghide`, `zsteg`, `stegsolve`)
   - Text hidden in image metadata (EXIF data)
   - Visual clues or text in the image itself

#### F. Video Content
1. Watch the videos (or scrub through them)
2. Look for:
   - Text overlays with flags
   - Audio messages
   - QR codes
   - Hidden frames

#### G. Social Media Links
1. If the channel links to other social media (Twitter, Instagram, Discord)
2. Follow those links and check:
   - Bio/description
   - Posts
   - Profile pictures

### Step 3: Common OSINT Techniques

#### Check Username Across Platforms
- Twitter: https://twitter.com/TimoPlayzzz
- Instagram: https://instagram.com/TimoPlayzzz
- TikTok: https://tiktok.com/@TimoPlayzzz
- Reddit: https://reddit.com/user/TimoPlayzzz
- Discord: Search for "TimoPlayzzz" in Discord servers

#### Use OSINT Tools
- Google: `"TimoPlayzzz" Kaal`
- Wayback Machine: Check archived versions of the channel
- Social Blade: https://socialblade.com/youtube/user/timoplayzz
- YouTube API: Extract channel data programmatically

### Step 4: Decode/Decrypt
If you find encoded text, try:
- Base64 decode
- ROT13/Caesar cipher
- Hex to ASCII
- Binary to text
- URL decode
- Morse code

## Quick Checklist
- [ ] Visited YouTube channel
- [ ] Checked About section
- [ ] Read all video descriptions
- [ ] Checked pinned comments
- [ ] Looked at Community posts
- [ ] Downloaded and analyzed banner image
- [ ] Downloaded and analyzed profile picture
- [ ] Checked linked social media accounts
- [ ] Searched for username on other platforms
- [ ] Tried decoding any suspicious text

## Flag Format
The flag will be in the format: `Kaal{...}`

## Tips
1. The flag is most likely in:
   - Channel description (About section)
   - Video description
   - Pinned comment
   - Social media bio linked from channel

2. It might be:
   - Plain text
   - Base64 encoded
   - Hidden in an image
   - Split across multiple locations

3. Since this is a 300-point medium difficulty challenge, it's probably not too obscure but requires some investigation.

## Next Steps
1. Open https://www.youtube.com/@TimoPlayzzz in your browser
2. Follow the checklist above
3. Document any findings
4. Try decoding any suspicious text
5. Submit the flag in format Kaal{}
