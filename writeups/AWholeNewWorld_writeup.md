# A Whole New World / "get fixed boi" (forensics, 500)

**Flag:** `K17{cr1ms0n_0r_corrup73d}`

## Challenge
> I've been playing Terraria with my friend, but I think he's cheating. He sent me the world but it won't open... can you help me out? (Note - you do NOT need to own the game Terraria to solve this challenge)

File: `AWholeNewWorld.wld`

## Analysis
The file is a **Terraria world save (version 319 = 1.4.5.6)**. It "won't open" because the
file-format header was tampered with:
- The 7-byte `relogic` magic string (offset 4) was **zeroed out**.
- Section pointer[0] (world header) and pointer[1] (tiles) in the pointer table were **corrupted**
  (garbage / `11946`), while the trailing pointers (chests, signs, npcs, ... footer) were intact.

Standard tools (and the game) reject it on the missing magic string. `lihzahrd` also only supports
1.4.4.9, so it can't be used directly.

## Approach
1. Parsed the header manually. Real layout:
   - pointer table at 0x18 (11 sections), tileframeimportant bitfield (753 bits) right after.
   - **World header starts at offset 167**: name `crimson`, seed `1192594496`, size **4200 x 1200**.
2. Walked the v1.4.x header field-by-field to locate the **tile data start = offset 599**.
3. Implemented the Terraria tile block + RLE decoder (flags1-4, extended IDs, frame-important,
   paint, walls, liquids, single/double-byte RLE) and decoded all 4200 columns (ended cleanly at
   offset 2714109, confirming correct alignment).
4. Rendered tiles to a PNG. The world builder placed **Obsidian Brick blocks (tile type 122)**
   floating in the sky spelling out text. Isolating type 122 as black-on-white made it readable.

## Result
The tiles spell (leetspeak for "crimson or corrupted", tying into the `crimson` world name and
Terraria's Crimson/Corruption evil biomes):

```
cr1ms0n_0r_corrup73d
```

**Flag:** `K17{cr1ms0n_0r_corrup73d}`

## Tooling (in repo)
- `wld_tiles.py` - full tile parser + colored world render (`world_render.png`)
- `wld_letters.py` - isolate tile type 122 (`letters_only.png`, `letters_crop.png`)
- `wld_zoom.py` / `wld_char.py` - per-character zoom for verification
