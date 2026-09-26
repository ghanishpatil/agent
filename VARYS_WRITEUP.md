When I got the challenge file `challenge_final.onnx`, the description gave me clear hints: "least significant bits" and "hidden in the beginning." This was an LSB steganography challenge, but instead of an image, the data was hidden in an ONNX machine learning model.

I started by loading the model to check its structure. First, I tried extracting LSB from the raw file bytes at the beginning, but that didn't work. I realized I needed to look at the actual model weights.

I installed the onnx library and inspected the model:

```python
import onnx

model = onnx.load("challenge_final.onnx")
print(f"Number of weight tensors: {len(model.graph.initializer)}")
```

The model had 14 weight tensors. I also noticed the model had metadata fields, and one of them contained a decoy flag: `Kaal{surface_flag_string_search_will_not_solve_this}` with a note saying "Plain-text surface artifacts for string searchers." This confirmed I needed to dig deeper into the LSB data.

For LSB steganography in ML models, the data is hidden in the least significant bits of weight values. Since ONNX stores weights as float32, I needed to:
1. Get each tensor's raw bytes
2. Parse them as float32 values
3. Convert each float to its integer representation
4. Extract the LSB of each integer
5. Reconstruct bytes from the collected bits

I wrote a script to extract LSB from all tensors:

```python
import onnx
import struct

model = onnx.load("challenge_final.onnx")

for tensor in model.graph.initializer:
    if tensor.HasField('raw_data'):
        raw_data = tensor.raw_data
        num_floats = len(raw_data) // 4
        floats = struct.unpack(f'{num_floats}f', raw_data)
        
        # Extract LSB from integer representation
        bits = []
        for f in floats:
            int_repr = struct.unpack('I', struct.pack('f', f))[0]
            bits.append(int_repr & 1)
        
        # Convert bits to bytes
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        print(f"{tensor.name}: {result[:200]}")
```

When I ran this on the `fc1.weight` tensor (the largest one with over 10 million floats), I found something interesting. Instead of a direct flag, I found a structured message:

```
HDWGT1|FLAG|S2FhbHsxZl9UaU1lX2M0bl9iM19jcjM0dEVkLF90aDNuX3M0cmNBc21fY0FuX2QzZkluZV9pdH0=|HINT|dXAgbmV4dCwgdGhlIGxpdHRsZSBiaXJkcyBjYXJyeSBvbmx5IGZyYWdtZW50czsgZWFjaCB3aGlzcGVyIHJlbWVtYmVycyBpdHMgcGxhY2U=
```

The flag was base64 encoded! I decoded it:

```python
import base64
flag_b64 = "S2FhbHsxZl9UaU1lX2M0bl9iM19jcjM0dEVkLF90aDNuX3M0cmNBc21fY0FuX2QzZkluZV9pdH0="
flag = base64.b64decode(flag_b64).decode()
print(flag)
```

This gave me: `Kaal{1f_TiMe_c4n_b3_cr34tEd,_th3n_s4rcAsm_cAn_d3fIne_it}`

The hint decoded to: "up next, the little birds carry only fragments; each whisper remembers its place" - a reference to Varys's spy network and possibly hinting at a multi-part challenge.

Flag: Kaal{1f_TiMe_c4n_b3_cr34tEd,_th3n_s4rcAsm_cAn_d3fIne_it}

Team Exploit4