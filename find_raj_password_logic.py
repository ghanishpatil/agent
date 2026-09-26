#!/usr/bin/env python3
"""Find the password logic and complete flag"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("FINDING PASSWORD LOGIC AND COMPLETE FLAG")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dex'):
            content = z.read(name)
            
            # Look for strings that might be the complete flag
            # Try different patterns
            patterns = [
                rb'Kaal\{[^}]{30,}\}',  # Long flag
                rb'FLAG[^}]{10,}\}',
                rb'flag[^}]{10,}\}',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"\nPattern {pattern} in {name}:")
                    for m in matches:
                        print(f"  {m[:100]}")
            
            # Look for the password checking logic
            # Search for strings that might be compared
            if b'password' in content.lower():
                print(f"\n[Password logic in {name}]")
                
                # Look for strings near password validation
                # Common patterns: equals, check, verify, etc.
                password_checks = re.findall(rb'[A-Za-z0-9_]{6,20}', content)
                
                # Filter for likely passwords (mixed case, numbers)
                likely_passwords = []
                for p in password_checks:
                    try:
                        s = p.decode('utf-8')
                        # Check if it has both letters and might be a password
                        if any(c.isupper() for c in s) and any(c.islower() for c in s):
                            if 'raj' in s.lower() or 'RAJ' in s:
                                likely_passwords.append(s)
                    except:
                        pass
                
                if likely_passwords:
                    print("Potential passwords with RAJ:")
                    for p in set(likely_passwords[:20]):
                        print(f"  {p}")
            
            # Look for base64 encoded strings (might be the flag)
            base64_pattern = rb'[A-Za-z0-9+/]{20,}={0,2}'
            base64_matches = re.findall(base64_pattern, content)
            if base64_matches:
                print(f"\n[Base64-like strings in {name}]")
                for b64 in base64_matches[:10]:
                    try:
                        decoded = b64.decode('utf-8')
                        if 'Kaal' in decoded or 'FLAG' in decoded:
                            print(f"  {decoded}")
                    except:
                        pass
            
            # Look for the actual flag by searching for patterns after the partial flags
            if b'Kaal{GOOD_PROGRESS}' in content:
                print(f"\n[Context around partial flags in {name}]")
                pos = content.find(b'Kaal{GOOD_PROGRESS}')
                
                # Get a larger context
                context = content[pos:pos+500]
                print(f"Raw bytes: {context[:200]}")
                
                # Try to find if there are more parts
                all_parts = re.findall(rb'Kaal\{[^}]+\}', context)
                print(f"\nAll flag parts found:")
                for part in all_parts:
                    print(f"  {part.decode('utf-8', errors='ignore')}")
                
                # Check if they should be combined
                if len(all_parts) >= 2:
                    # Try combining them
                    combined = b''.join(all_parts).decode('utf-8', errors='ignore')
                    print(f"\nCombined: {combined}")
                    
                    # Try removing the Kaal{ } wrappers and combining content
                    contents = []
                    for part in all_parts:
                        match = re.search(rb'Kaal\{([^}]+)\}', part)
                        if match:
                            contents.append(match.group(1))
                    
                    if contents:
                        combined_content = b'_'.join(contents).decode('utf-8', errors='ignore')
                        print(f"Combined content: Kaal{{{combined_content}}}")

print("\n" + "="*80)
print("\nBased on the challenge description:")
print("'One is meant to be seen' - This is the main app (Kaal{GOOD_PROGRESS})")
print("'The other was never meant to be found' - This is the second app (Kaal{IT_My_BE})")
print("\nThe complete flag might be: Kaal{GOOD_PROGRESS_IT_My_BE}")
print("Or it could be hidden in the embedded APK that needs the password to access")
print("\n" + "="*80)
