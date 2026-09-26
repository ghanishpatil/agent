# How to Get SDL2 and Run the Game

## Quick Solution

### Option 1: Download SDL2 Runtime (Easiest)
1. Go to: https://github.com/libsdl-org/SDL/releases/latest
2. Download `SDL2-2.x.x-win32-x64.zip` (for 64-bit Windows)
3. Extract the ZIP file
4. Copy `SDL2.dll` from the extracted folder to the `game` directory
5. Run: `.\game\game_patched.exe`

### Option 2: Use PowerShell to Download (Automated)
Run this in PowerShell:
```powershell
# Download SDL2
$url = "https://github.com/libsdl-org/SDL/releases/download/release-2.28.5/SDL2-2.28.5-win32-x64.zip"
$output = "SDL2.zip"
Invoke-WebRequest -Uri $url -OutFile $output

# Extract
Expand-Archive -Path SDL2.zip -DestinationPath SDL2_temp

# Copy DLL to game directory
Copy-Item SDL2_temp\SDL2.dll game\

# Clean up
Remove-Item SDL2.zip
Remove-Item SDL2_temp -Recurse

# Run the patched game
.\game\game_patched.exe
```

### Option 3: Manual Download from Official Site
1. Visit: https://www.libsdl.org/download-2.0.php
2. Under "Runtime Binaries", download "SDL2-2.x.x-win32-x64.zip"
3. Extract and copy SDL2.dll to the game folder
4. Run the patched executable

## What the Patched Game Does
The patched `game_patched.exe` has the score check modified so that:
- It will immediately trigger the flag decode function
- The flag will be displayed without needing to play the game
- You should see output like: "Fetching flag..." followed by the actual flag

## If SDL2 Still Doesn't Work
The game might also need:
- SDL2_image.dll
- SDL2_ttf.dll
- SDL2_mixer.dll

Download these from the same SDL2 releases page if needed.

## Alternative: Use Wine on Linux/WSL
If you have WSL or Linux:
```bash
sudo apt-get install wine64
wine game/game_patched.exe
```

## Last Resort: Use a Disassembler
If SDL2 doesn't work, use Ghidra (free):
1. Download Ghidra: https://ghidra-sre.org/
2. Open game.exe in Ghidra
3. Search for the string "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"
4. Find cross-references to see where it's used
5. Analyze the decode function
6. Implement the algorithm in Python

## Expected Flag Format
```
Kaal{something_here}
```

The flag is definitely in the binary, we just need to decode it!
