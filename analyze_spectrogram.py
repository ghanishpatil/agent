#!/usr/bin/env python3
"""
Analyze audio spectrogram for hidden data
"""

import wave
import struct
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from scipy import signal

def analyze_audio_spectrogram(filename, output_image):
    """Create spectrogram and look for hidden data"""
    print(f"\nAnalyzing: {filename}")
    
    with wave.open(filename, 'rb') as wav:
        sample_rate = wav.getframerate()
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
        
        # Convert to numpy array
        samples = np.frombuffer(frames, dtype=np.int16)
        
        # Create spectrogram
        plt.figure(figsize=(15, 8))
        
        # Plot waveform
        plt.subplot(2, 1, 1)
        time = np.linspace(0, len(samples) / sample_rate, len(samples))
        plt.plot(time[:10000], samples[:10000])  # First 10000 samples
        plt.title(f'Waveform - {filename}')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        
        # Plot spectrogram
        plt.subplot(2, 1, 2)
        f, t, Sxx = signal.spectrogram(samples, sample_rate)
        plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (s)')
        plt.title('Spectrogram')
        plt.colorbar(label='Power (dB)')
        
        plt.tight_layout()
        plt.savefig(output_image, dpi=150)
        plt.close()
        
        print(f"  Saved spectrogram to: {output_image}")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Duration: {len(samples) / sample_rate:.2f} seconds")
        print(f"  Max frequency in spectrogram: {f.max():.2f} Hz")
        
        # Check for patterns in frequency domain
        fft = np.fft.fft(samples)
        freqs = np.fft.fftfreq(len(samples), 1/sample_rate)
        
        # Find dominant frequencies
        magnitude = np.abs(fft)
        top_indices = np.argsort(magnitude)[-10:][::-1]
        
        print(f"  Top 10 frequencies:")
        for idx in top_indices:
            if freqs[idx] > 0:
                print(f"    {freqs[idx]:.2f} Hz (magnitude: {magnitude[idx]:.0f})")

# Analyze all three files
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    analyze_audio_spectrogram(
        f'stones_extracted/{stone}.wav',
        f'{stone}_spectrogram.png'
    )

print("\n" + "="*60)
print("Check the generated PNG files for visual clues!")
print("="*60)
