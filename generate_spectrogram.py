import wave
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

wav_path = r"D:\mission-git-hackss\chall (1).wav"

with wave.open(wav_path, 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
    sample_rate = wav.getframerate()

samples = np.frombuffer(frames, dtype=np.int16)

# Create spectrogram
plt.figure(figsize=(15, 8))
plt.specgram(samples, Fs=sample_rate, cmap='hot')
plt.title('Spectrogram - Look for text/flag')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.colorbar()
plt.savefig('spectrogram.png', dpi=300, bbox_inches='tight')
print("Saved spectrogram.png - check it for visual text!")

# Also try different window sizes
plt.figure(figsize=(15, 8))
plt.specgram(samples, Fs=sample_rate, NFFT=512, cmap='hot')
plt.title('Spectrogram (NFFT=512)')
plt.savefig('spectrogram_512.png', dpi=300, bbox_inches='tight')
print("Saved spectrogram_512.png")
