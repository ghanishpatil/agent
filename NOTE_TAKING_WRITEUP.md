# Note-Taking Service - Off-by-One Heap Exploitation

## Challenge Information
- **Host**: 212.2.250.33:31553
- **Category**: Pwnable
- **Difficulty**: Hard (500 points)
- **Flag Format**: ctf7{...}

## Vulnerability Analysis

### The Bug: Off-by-One Overflow
The challenge description states: "One byte too many might just be enough to bring the whole thing down."

Based on the hints:
1. **Hint 1**: The binary prints three addresses at startup. The difference between heap addresses matters for arithmetic.
2. **Hint 2**: Research what happens when the allocator's "previous chunk in use" assumption is violated.
3. **Hint 3**: When you append to a note that's already full, count very carefully how many bytes actually get written.

This is a classic **off-by-one heap overflow** vulnerability in the append/edit operation.

### Heap Chunk Structure
```
+------------------+
| prev_size (8)    |  <- Size of previous chunk (if free)
+------------------+
| size (8)         |  <- Size of this chunk | flags (3 LSBs)
+------------------+
| data             |  <- User data starts here
| ...              |
+------------------+
```

The size field's LSB is the `PREV_INUSE` bit:
- If set (1): Previous chunk is in use
- If clear (0): Previous chunk is free

### The Exploitation Path

#### Phase 1: Heap Layout Setup
Create three chunks:
```
Chunk A (0x90): [prev_size][0x91][data: 0x88 bytes]
Chunk B (0x90): [prev_size][0x91][data: 0x88 bytes]  <- Victim
Chunk C (0x90): [prev_size][0x91][data: 0x88 bytes]  <- Prevent top consolidation
```

#### Phase 2: Trigger Off-by-One
1. Fill Chunk A to exactly capacity (0x88 bytes)
2. Append one more byte - this overflows into Chunk B's size field
3. Overwrite `0x91` → `0x90` (clears PREV_INUSE bit)

```
Before:
Chunk A: [...data: 0x88 bytes...][0x00][0x91] <- Chunk B size
                                          ^
                                          PREV_INUSE bit set

After off-by-one:
Chunk A: [...data: 0x88 bytes...][0x00][0x90] <- Chunk B size
                                          ^
                                          PREV_INUSE bit CLEARED
```

#### Phase 3: Exploit Corrupted Metadata
When we free Chunk B:
- The allocator sees PREV_INUSE = 0
- It thinks Chunk A is free
- It attempts backward consolidation
- This creates overlapping chunks!

#### Phase 4: Overlapping Chunks
After freeing corrupted Chunk B and reallocating:
```
Chunk A: [normal chunk]
Chunk B': [overlaps with Chunk C]
Chunk C: [can be corrupted via Chunk B']
```

Now we can use Chunk B' to overwrite Chunk C's metadata, including its forward pointer (fd).

#### Phase 5: Tcache Poisoning
1. Overwrite Chunk C's fd pointer to point to `__free_hook`
2. Free Chunk C (puts poisoned pointer in tcache)
3. Allocate twice:
   - First allocation: normal chunk
   - Second allocation: chunk at `__free_hook`
4. Write `system` address to `__free_hook`

#### Phase 6: Get Shell
1. Create a chunk containing "/bin/sh"
2. Free it - this calls `__free_hook("/bin/sh")`
3. Since `__free_hook` points to `system`, this executes `system("/bin/sh")`
4. Shell!

## Exploitation Scripts

### Main Exploit
```bash
python final_note_taking_exploit.py
```

### Alternative Strategies
```bash
python note_exploit_variants.py
```

### Debug Mode
```bash
python note_exploit_variants.py --debug
```

## Key Techniques Used

1. **Off-by-One Overflow**: Writing one byte past buffer boundary
2. **Heap Metadata Corruption**: Clearing PREV_INUSE bit
3. **Backward Consolidation**: Exploiting free() logic
4. **Overlapping Chunks**: Creating chunks that share memory
5. **Tcache Poisoning**: Corrupting tcache bin linked list
6. **Hook Overwrite**: Overwriting `__free_hook` with `system`

## Libc Offsets (Adjust for Target)

Common libc 2.27-2.31 offsets:
```python
__free_hook = libc_base + 0x1eee48
__malloc_hook = libc_base + 0x1ecb70
system = libc_base + 0x52290
/bin/sh = libc_base + 0x1b45bd
```

For libc 2.32+, use `__malloc_hook` or other techniques since hooks may be removed.

## Debugging Tips

1. Use `gdb` with `pwndbg` or `gef`:
   ```bash
   gdb ./note_service
   pwndbg> heap
   pwndbg> bins
   pwndbg> vis_heap_chunks
   ```

2. Check chunk metadata:
   ```bash
   pwndbg> x/20gx <chunk_address>
   ```

3. Monitor tcache:
   ```bash
   pwndbg> tcache
   ```

## Common Issues

1. **Wrong libc version**: Adjust offsets based on actual libc
2. **ASLR**: Use leaked addresses to calculate base
3. **Tcache size mismatch**: Ensure allocated sizes match tcache bins
4. **Alignment**: Heap addresses must be properly aligned

## References

- [Heap Exploitation Techniques](https://heap-exploitation.dhavalkapil.com/)
- [How2Heap](https://github.com/shellphish/how2heap)
- [Tcache Poisoning](https://github.com/shellphish/how2heap/blob/master/glibc_2.26/tcache_poisoning.c)
- [Off-by-One Exploitation](https://github.com/shellphish/how2heap/blob/master/glibc_2.26/poison_null_byte.c)
