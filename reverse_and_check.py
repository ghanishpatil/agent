import wave
import struct

# Reverse the audio and save it
with wave.open(r"D:\mission-git-hackss\chall (1).wav", 'rb') as wav:
    params = wav.getparams()
    frames = wav.readframes(wav.getnframes())

# Reverse frames
samples = struct.unpack(f'<{len(frames)//2}h', frames)
reversed_samples = samples[::-1]
reversed_frames = struct.pack(f'<{len(reversed_samples)}h', *reversed_samples)

# Save
with wave.open('reversed.wav', 'wb') as wav_out:
    wav_out.setparams(params)
    wav_out.writeframes(reversed_frames)

print("Saved reversed.wav - play it to hear the message!")

# Also check if flag is in reversed bytes
reversed_data = frames[::-1]
if b'Kaal{' in reversed_data:
    pos = reversed_data.find(b'Kaal{')
    end = reversed_data.find(b'}', pos)
    if end != -1:
        flag = reversed_data[pos:end+1].decode('ascii', errors='ignore')
        print(f"\nFLAG: {flag}")
