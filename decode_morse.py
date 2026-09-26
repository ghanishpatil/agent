import numpy as np
import wave, struct, re

MORSE = {
    '.-':'A','-.':'B','-.-.':'C','-..':'D','.':'E','..-.':'F',
    '--.':'G','....':'H','..':'I','.---':'J','-.-':'K','.-..':'L',
    '--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R',
    '...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X',
    '-.--':'Y','--..':'Z',
    '-----':'0','.----':'1','..---':'2','...--':'3','....-':'4',
    '.....':'5','-....':'6','--...':'7','---..':'8','----.':'9',
    '..--..':'?','.-.-.-':'.','--..--':',',
}

with wave.open(r'f:\mission-git-hackss\mission-git-hackss\layer2_audio.wav') as w:
    nch = w.getnchannels()
    sw = w.getsampwidth()
    fr = w.getframerate()
    nf = w.getnframes()
    raw = w.readframes(nf)
    print(f'Channels:{nch} SampleWidth:{sw} FrameRate:{fr} Frames:{nf} Duration:{nf/fr:.2f}s')

# Convert to numpy
if sw == 2:
    data = np.frombuffer(raw, dtype=np.int16)
else:
    data = np.frombuffer(raw, dtype=np.uint8).astype(np.int16) - 128

if nch == 2:
    data = data[::2]  # take left channel

# Rectify and smooth
data = np.abs(data.astype(np.float32))
# smooth with window
window = int(fr * 0.01)  # 10ms window
kernel = np.ones(window) / window
smoothed = np.convolve(data, kernel, mode='same')

# Threshold
threshold = smoothed.max() * 0.3
signal = (smoothed > threshold).astype(np.int8)

# Find transitions
transitions = np.diff(signal, prepend=signal[0])
starts = np.where(transitions == 1)[0]
ends = np.where(transitions == -1)[0]

if len(starts) == 0 or len(ends) == 0:
    print('No signal detected, trying lower threshold')
    threshold = smoothed.max() * 0.1
    signal = (smoothed > threshold).astype(np.int8)
    transitions = np.diff(signal, prepend=signal[0])
    starts = np.where(transitions == 1)[0]
    ends = np.where(transitions == -1)[0]

print(f'Detected {len(starts)} tones')

# Calculate durations in seconds
if len(starts) > 0 and len(ends) > 0:
    # align starts and ends
    if signal[0] == 1:  # starts with tone
        ends = ends[1:] if len(ends) > len(starts) else ends
    
    min_len = min(len(starts), len(ends))
    starts = starts[:min_len]
    ends = ends[:min_len]
    
    on_durations = (ends - starts) / fr
    off_durations = []
    for i in range(len(starts)-1):
        off_durations.append((starts[i+1] - ends[i]) / fr)
    
    print('On durations (first 20):', [f'{d:.3f}' for d in on_durations[:20]])
    print('Off durations (first 20):', [f'{d:.3f}' for d in off_durations[:20]])
    
    # Determine dot/dash threshold (midpoint of min and max on-duration)
    if len(on_durations) > 0:
        dot_thresh = (min(on_durations) + max(on_durations)) / 2
        print(f'Dot/dash threshold: {dot_thresh:.3f}s')
        
        # Build morse string
        morse_seq = []
        current_char = []
        
        for i, dur in enumerate(on_durations):
            sym = '-' if dur >= dot_thresh else '.'
            current_char.append(sym)
            
            if i < len(off_durations):
                gap = off_durations[i]
                # word gap = ~7x dot, char gap = ~3x dot, symbol gap = ~1x dot
                dot_unit = min(on_durations)
                if gap > dot_unit * 5:  # word gap
                    morse_seq.append(''.join(current_char))
                    morse_seq.append(' ')
                    current_char = []
                elif gap > dot_unit * 2:  # char gap
                    morse_seq.append(''.join(current_char))
                    current_char = []
        
        if current_char:
            morse_seq.append(''.join(current_char))
        
        print('Morse sequence:', morse_seq)
        
        # Decode
        result = ''
        for item in morse_seq:
            if item == ' ':
                result += ' '
            else:
                result += MORSE.get(item, f'[{item}]')
        
        print('DECODED:', result)
