#!/usr/bin/env python3
"""
Analyze audio spectrogram for hidden messages
Install: pip install scipy numpy matplotlib
"""

try:
    import numpy as np
    from scipy.io import wavfile
    import matplotlib.pyplot as plt
    import os
    
    wav_file = "corrected_audio.wav"
    
    if not os.path.exists(wav_file):
        print("[*] Creating corrected WAV...")
        with open('chall_media/chall_media.mp3', 'rb') as f:
            data = f.read()
        corrected = b'RIFF' + data[4:]
        with open(wav_file, 'wb') as f:
            f.write(corrected)
    
    print("[*] Reading WAV file...")
    try:
        sample_rate, audio_data = wavfile.read(wav_file)
        print(f"    Sample rate: {sample_rate} Hz")
        print(f"    Audio shape: {audio_data.shape}")
        print(f"    Duration: {len(audio_data) / sample_rate:.2f} seconds")
        
        # If stereo, use first channel
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]
        
        # Create spectrogram
        print("\n[*] Creating spectrogram...")
        from scipy import signal
        
        frequencies, times, spectrogram = signal.spectrogram(audio_data, sample_rate)
        
        # Plot and save
        plt.figure(figsize=(15, 8))
        plt.pcolormesh(times, frequencies, 10 * np.log10(spectrogram + 1e-10), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Spectrogram - Look for hidden text/patterns')
        plt.colorbar(label='Power [dB]')
        plt.ylim([0, sample_rate/2])  # Show full frequency range
        plt.savefig('spectrogram_full.png', dpi=300, bbox_inches='tight')
        print("    Saved: spectrogram_full.png")
        
        # High frequency spectrogram (where text is usually hidden)
        plt.figure(figsize=(15, 8))
        plt.pcolormesh(times, frequencies, 10 * np.log10(spectrogram + 1e-10), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Spectrogram - High Frequencies (Text Hidden Here)')
        plt.colorbar(label='Power [dB]')
        plt.ylim([10000, sample_rate/2])  # Focus on high frequencies
        plt.savefig('spectrogram_high_freq.png', dpi=300, bbox_inches='tight')
        print("    Saved: spectrogram_high_freq.png")
        
        print("\n[+] Check the PNG files for hidden text in the spectrogram!")
        print("    - spectrogram_full.png")
        print("    - spectrogram_high_freq.png")
        
    except Exception as e:
        print(f"[-] Error reading WAV: {e}")
        print("    The file might be corrupted or not a valid WAV")

except ImportError:
    print("[-] scipy/numpy/matplotlib not installed")
    print("    Install with: pip install scipy numpy matplotlib")

print("\n[*] Done!")
