# Game Reverse Engineering Challenge - Status

## Challenge Details
- **File**: game.exe (37MB Windows PE executable)
- **Goal**: Reach score ≥ 0x12C (300) to get the flag
- **Flag Format**: Kaal{}
- **Category**: Reverse Engineering
- **Difficulty**: Medium (300 points)

## What We Found

### 1. Encoded Flag String
```
AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc
```
- Located at offset: 0x2404018 in the binary
- Length: 35 characters
- Appears to be base64-like encoding with custom alphabet

### 2. Key Functions Found
- `fetch_flag` - Function that retrieves/decodes the flag
- `parse_flag` - Function that processes the flag
- Encode functions: `a1`, `a2`, `a3`, `a4`
- Decode functions: `d1`, `d2`

### 3. Score Check
- Target score: 0x12C (300 decimal)
- Score check bytes found at offset: 0x20fc
- Multiple occurrences of the value in the binary

### 4. Base64 Decode Attempts
When decoded as base64 (with _ as /), we get:
```
Hex: 0001ca84dfd6a997a571bb678e20faf0e36abf235ee99ed34467
```
- First two bytes (0x00 0x01) might be a length prefix or header
- Remaining bytes don't directly decode to readable text
- Likely requires additional XOR or custom decoding

## Attempted Solutions

### 1. Binary Patching
Created multiple patched versions:
- `game_patched.exe` - Patched score check
- `game_collision_patched.exe` - Patched collision detection
- `game_direct_flag.exe` - Attempted to call flag function directly

**Issue**: Game requires SDL2 DLLs to run, which aren't available

### 2. Decode Algorithm Reverse Engineering
Tried:
- Standard base64
- URL-safe base64
- Custom alphabet base64
- XOR with single-byte keys (0-255)
- XOR with multi-byte keys
- ROT13/Caesar cipher
- String reversal

**Result**: None produced readable flag text

## Why We're Stuck

1. **Can't Run the Game**: Missing SDL2 dependencies
   - SDL2.dll
   - SDL2_image.dll
   - SDL2_ttf.dll
   - SDL2_mixer.dll (possibly)

2. **Custom Decode Algorithm**: The flag uses a proprietary encoding that requires:
   - Either running the game to trigger the decode function
   - Or fully reverse engineering the decode algorithm from assembly

3. **Complex Binary**: 37MB executable with lots of code makes manual reverse engineering time-consuming

## Solutions to Try

### Option 1: Install SDL2 (Recommended)
1. Download SDL2 development libraries for Windows
2. Copy SDL2.dll, SDL2_image.dll, SDL2_ttf.dll to the game directory
3. Run the patched executable
4. The game should display the flag when score >= 300

### Option 2: Use a Disassembler
1. Open game.exe in IDA Pro or Ghidra
2. Find the `fetch_flag` or decode function
3. Reverse engineer the exact algorithm
4. Implement it in Python to decode the string

### Option 3: Use a Debugger
1. Use x64dbg or WinDbg
2. Set breakpoint at the fetch_flag function (offset 0x2410512)
3. Patch the score value in memory to >= 300
4. Step through the decode function
5. Watch the flag being constructed in memory

### Option 4: Dynamic Analysis
1. Use a tool like Process Monitor or API Monitor
2. Run the game (if SDL2 is available)
3. Capture any file/registry/network operations
4. The flag might be written somewhere

## Most Likely Flag Format
Based on the encoded string length (35 chars) and typical CTF flags:
```
Kaal{some_text_here_about_20-25_chars}
```

The decoded flag is probably around 30-40 characters total.

## Next Steps
1. Try to get SDL2 DLLs and run the patched game
2. Or use IDA/Ghidra to reverse engineer the decode function
3. The flag IS in the binary, we just need to decode it properly

## Files Created
- `game_patched.exe` - Score check patched
- `analyze_game.py` - Binary analysis script
- `game_final_solve.py` - Decode attempts
- `extract_flag_from_binary.py` - Binary extraction attempts
