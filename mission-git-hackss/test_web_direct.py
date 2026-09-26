import sys
sys.stdout.reconfigure(encoding='utf-8')

from core.config import Config
from core.challenge import Challenge
from modules.web import WebModule

config = Config('config/config.yaml')
web = WebModule(config)

# Test CTF sites
test_urls = [
    ("idcardfound", "https://idcardfound.netlify.app/"),
    ("sheleftmebro", "https://sheleftmebro.netlify.app/"),
    ("beastboyshubh", "https://beastboyshubh.netlify.app/"),
    ("retrokanima", "https://retrokanima.netlify.app/"),
    ("thehiddenmystery", "https://thehiddenmystery.netlify.app/"),
    ("theunknownman", "https://theunknownman.netlify.app/"),
    ("lighthearted200", "https://lighthearted200.netlify.app/"),
    ("hidden-in-plain-csbc", "https://hidden-in-plain-csbc.netlify.app/"),
    ("the-chember-of-secreat", "https://the-chember-of-secreat.netlify.app/"),
    ("creel-house-theclock", "https://csbc-ctf-theclock.netlify.app/"),
    ("ghost-terminal", "https://ghost-terminal.onrender.com/"),
    ("sayoonara", "https://sayoonara.netlify.app/"),
    ("melodiousdesk", "https://melodiousdesk.netlify.app/"),
    ("idiotmute", "https://idiotmute.netlify.app/"),
    ("funnykitty", "https://funnykitty.netlify.app/"),
    ("level-8", "https://level-8.vercel.app/"),  # Bot-protected SQL injection + steganography
    ("andthesaturdaycontinues", "https://andthesaturdaycontinues.netlify.app/"),  # robots.txt + path discovery
    ("littlelittle", "https://littlelittle.netlify.app/"),  # Steganography challenge
]

print("=" * 70)
print("MD-EXPLOIT-ENGINE - CTF Challenge Solver Test")
print("=" * 70)

success_count = 0
for name, url in test_urls:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    challenge = Challenge(
        name=f"test_{name}",
        url=url,
        category="web"
    )
    
    # Use quick mode for faster testing
    web.quick_mode = True
    result = web.solve(challenge)
    
    print(f"\nSuccess: {result.success}")
    print(f"Flag: {result.flag}")
    print(f"Method: {result.method}")
    if result.success:
        success_count += 1
    if hasattr(result, 'logs'):
        print("\nLogs:")
        for log in result.logs[-12:]:
            print(f"  {log}")

print(f"\n{'='*70}")
print(f"RESULTS: {success_count}/{len(test_urls)} challenges solved successfully!")
print("=" * 70)
