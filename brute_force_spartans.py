import itertools

print("="*80)
print("BRUTE FORCE SPARTANS - FIND READABLE TEXT")
print("="*80)

encrypted = "KLJDPWHZZAJQEEBAQP"

def rail_fence_decrypt(text, rails):
    if rails == 1:
        return text
    fence = [['' for _ in range(len(text))] for _ in range(rails)]
    rail = 0
    direction = 1
    for i in range(len(text)):
        fence[rail][i] = '*'
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    index = 0
    for i in range(rails):
        for j in range(len(text)):
            if fence[i][j] == '*':
                fence[i][j] = text[index]
                index += 1
    result = []
    rail = 0
    direction = 1
    for i in range(len(text)):
        result.append(fence[rail][i])
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    return ''.join(result)

def rot_n(text, n):
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + n) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)

def playfair_decrypt(ciphertext, key):
    key = key.upper().replace('J', 'I')
    matrix = []
    used = set()
    for char in key:
        if char not in used and char.isalpha():
            matrix.append(char)
            used.add(char)
    for char in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
        if char not in used:
            matrix.append(char)
    pos = {}
    for i, char in enumerate(matrix):
        pos[char] = (i // 5, i % 5)
    ciphertext = ciphertext.upper().replace('J', 'I')
    result = []
    for i in range(0, len(ciphertext), 2):
        if i + 1 >= len(ciphertext):
            break
        a, b = ciphertext[i], ciphertext[i+1]
        row1, col1 = pos[a]
        row2, col2 = pos[b]
        if row1 == row2:
            result.append(matrix[row1 * 5 + (col1 - 1) % 5])
            result.append(matrix[row2 * 5 + (col2 - 1) % 5])
        elif col1 == col2:
            result.append(matrix[((row1 - 1) % 5) * 5 + col1])
            result.append(matrix[((row2 - 1) % 5) * 5 + col2])
        else:
            result.append(matrix[row1 * 5 + col2])
            result.append(matrix[row2 * 5 + col1])
    return ''.join(result)

def is_readable(text):
    """Check if text looks like English"""
    text = text.upper()
    # Check for common English words
    common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE']
    for word in common_words:
        if word in text:
            return True
    # Check for reasonable letter distribution
    vowels = sum(1 for c in text if c in 'AEIOU')
    if len(text) > 0 and vowels / len(text) > 0.2:
        # Check for no excessive repetition
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if c*4 in text:
                return False
        return True
    return False

keys = ['SPARTANS', 'OLDFRIENDSREUNION', 'FRIENDS', 'SECURITY', 'GUARD', 'CYBERSECURITY', 'SPARTAN', 'REUNION', 'OLDFRIENDSREUNIONS', 'FRIEND']

# Try all possible orders
operations = ['rail', 'rot5', 'rot3', 'playfair']

print("\nSearching for readable text...")
print("This may take a moment...\n")

found_results = []

# Try different operation orders
for perm in itertools.permutations(operations):
    for key in keys:
        for rails in [2, 3, 4, 5]:
            text = encrypted
            
            for op in perm:
                try:
                    if op == 'rail':
                        text = rail_fence_decrypt(text, rails)
                    elif op == 'rot5':
                        text = rot_n(text, -5)
                    elif op == 'rot3':
                        text = rot_n(text, -3)
                    elif op == 'playfair':
                        text = playfair_decrypt(text, key)
                except:
                    break
            
            if is_readable(text):
                result = {
                    'order': ' -> '.join(perm),
                    'key': key,
                    'rails': rails,
                    'result': text
                }
                if result not in found_results:
                    found_results.append(result)
                    print(f"FOUND: {text}")
                    print(f"  Order: {' -> '.join(perm)}")
                    print(f"  Key: {key}, Rails: {rails}")
                    print()

if not found_results:
    print("No readable text found with standard combinations.")
    print("\nTrying simpler approaches...")
    
    # Just Rail Fence
    print("\n[JUST RAIL FENCE]")
    for rails in [2, 3, 4, 5, 6]:
        result = rail_fence_decrypt(encrypted, rails)
        print(f"Rails {rails}: {result}")
    
    # Just ROT
    print("\n[JUST ROT]")
    for n in range(1, 26):
        result = rot_n(encrypted, n)
        if is_readable(result):
            print(f"ROT{n}: {result}")
    
    # Just Playfair
    print("\n[JUST PLAYFAIR]")
    for key in keys:
        try:
            result = playfair_decrypt(encrypted, key)
            print(f"Key {key}: {result}")
        except:
            pass

print("\n" + "="*80)
