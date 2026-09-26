#!/usr/bin/env python3
"""
Analyze spectrogram data for patterns that might spell out text
"""

try:
    import numpy as np
    from scipy.io import wavfile
    from scipy import signal
    import os
    
    wav_file = "corrected_audio.wav"
    
    print("[*] Reading audio...")
    sample_rate, audio_data = wavfile.read(wav_file)
    
    if len(audio_data.shape) > 1:
        audio_data = audio_data[:, 0]
    
    print(f"[*] Sample rate: {sample_rate} Hz")
    print(f"[*] Duration: {len(audio_data) / sample_rate:.2f} seconds")
    
    # Create high-resolution spectrogram focusing on high frequencies
    print("\n[*] Creating high-resolution spectrogram...")
    
    # Use shorter window for better time resolution
    nperseg = 2048
    frequencies, times, Sxx = signal.spectrogram(
        audio_data, 
        sample_rate,
        nperseg=nperseg,
        noverlap=nperseg-100
    )
    
    print(f"    Frequency bins: {len(frequencies)}")
    print(f"    Time bins: {len(times)}")
    
    # Focus on high frequencies (15kHz - 24kHz) where text is usually hidden
    high_freq_start = 15000
    high_freq_end = 24000
    
    freq_mask = (frequencies >= high_freq_start) & (frequencies <= high_freq_end)
    high_freq_data = Sxx[freq_mask, :]
    high_frequencies = frequencies[freq_mask]
    
    print(f"\n[*] Analyzing high frequency range: {high_freq_start}-{high_freq_end} Hz")
    print(f"    Data shape: {high_freq_data.shape}")
    
    # Normalize and threshold
    high_freq_norm = (high_freq_data - np.min(high_freq_data)) / (np.max(high_freq_data) - np.min(high_freq_data))
    
    # Find regions with significant energy (potential text)
    threshold = 0.3
    binary_data = (high_freq_norm > threshold).astype(int)
    
    # Check if there are patterns
    total_active = np.sum(binary_data)
    total_pixels = binary_data.size
    activity_ratio = total_active / total_pixels
    
    print(f"    Activity ratio: {activity_ratio:.4f}")
    
    if activity_ratio > 0.01:
        print(f"    [+] Significant activity detected in high frequencies!")
        print(f"    [+] This suggests hidden text/image in spectrogram")
        
        # Try to extract text-like patterns
        # Save binary representation
        np.save('spectrogram_binary.npy', binary_data)
        print(f"    Saved binary data to spectrogram_binary.npy")
        
        # Create a simple visualization
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(20, 6))
            plt.imshow(binary_data, aspect='auto', cmap='binary', origin='lower',
                      extent=[times[0], times[-1], high_frequencies[0], high_frequencies[-1]])
            plt.ylabel('Frequency [Hz]')
            plt.xlabel('Time [sec]')
            plt.title('Binary Spectrogram - High Frequencies')
            plt.colorbar(label='Active')
            plt.savefig('spectrogram_binary.png', dpi=300, bbox_inches='tight')
            print(f"    Saved: spectrogram_binary.png")
            
            # Also save inverted (black on white, easier to read)
            plt.figure(figsize=(20, 6))
            plt.imshow(1 - binary_data, aspect='auto', cmap='binary', origin='lower',
                      extent=[times[0], times[-1], high_frequencies[0], high_frequencies[-1]])
            plt.ylabel('Frequency [Hz]')
            plt.xlabel('Time [sec]')
            plt.title('Inverted Binary Spectrogram - Look for Text')
            plt.colorbar(label='Active')
            plt.savefig('spectrogram_inverted.png', dpi=300, bbox_inches='tight')
            print(f"    Saved: spectrogram_inverted.png")
            
        except:
            pass
    else:
        print(f"    [-] Low activity in high frequencies")
        print(f"    Text might be in different frequency range or not present")
    
    # Check other frequency ranges
    print("\n[*] Checking other frequency ranges...")
    for freq_start, freq_end in [(5000, 10000), (10000, 15000), (18000, 22000)]:
        freq_mask = (frequencies >= freq_start) & (frequencies <= freq_end)
        range_data = Sxx[freq_mask, :]
        range_norm = (range_data - np.min(range_data)) / (np.max(range_data) - np.min(range_data))
        binary_range = (range_norm > threshold).astype(int)
        activity = np.sum(binary_range) / binary_range.size
        print(f"    {freq_start}-{freq_end} Hz: activity = {activity:.4f}")
        
        if activity > 0.02:
            print(f"        [+] Significant activity! Saving...")
            try:
                import matplotlib.pyplot as plt
                plt.figure(figsize=(20, 6))
                plt.imshow(1 - binary_range, aspect='auto', cmap='binary', origin='lower')
                plt.title(f'Spectrogram {freq_start}-{freq_end} Hz')
                plt.savefig(f'spectrogram_{freq_start}_{freq_end}.png', dpi=300, bbox_inches='tight')
                print(f"        Saved: spectrogram_{freq_start}_{freq_end}.png")
            except:
                pass

except ImportError as e:
    print(f"[-] Missing library: {e}")
    print("    Install with: pip install scipy numpy matplotlib")
except Exception as e:
    print(f"[-] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n[*] Analysis complete!")
print("[*] Check the generated PNG files for hidden text/flag")
