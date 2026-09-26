#!/usr/bin/env python3
"""
Check what the GPS coordinates actually point to
Maybe they spell out a message or point to a meaningful location
"""

import struct

def analyze_gps(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Extract first few coordinates
    offset = 256
    coords = []
    
    for i in range(20):
        if offset + 40 > len(data):
            break
        
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            lat = struct.unpack('<d', data[offset+12:offset+20])[0]
            lon = struct.unpack('<d', data[offset+20:offset+28])[0]
            alt = struct.unpack('<d', data[offset+28:offset+36])[0]
            
            coords.append((lat, lon, alt))
            offset += 40
    
    print("=== First 20 GPS Coordinates ===")
    for i, (lat, lon, alt) in enumerate(coords):
        print(f"{i+1}. Lat: {lat:.10f}, Lon: {lon:.10f}, Alt: {alt:.2f}")
    
    # Check if these are real coordinates
    # Latitude: -90 to 90
    # Longitude: -180 to 180
    
    print("\n=== Coordinate Analysis ===")
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    
    print(f"Latitude range: {min(lats):.6f} to {max(lats):.6f}")
    print(f"Longitude range: {min(lons):.6f} to {max(lons):.6f}")
    
    # These look like they're around 15°N, 74°E
    # That's in India (Goa region)
    print("\nThese coordinates are around 15°N, 74°E")
    print("This is in the Goa region of India")
    
    # Maybe the altitude encodes something?
    print("\n=== Altitude Analysis ===")
    alts = [c[2] for c in coords]
    print(f"Altitude range: {min(alts):.2f} to {max(alts):.2f}")
    
    # The altitudes are HUGE - 20 million meters!
    # That's not realistic. Maybe they encode data?
    
    print("\n=== Trying to decode altitude as data ===")
    for i, alt in enumerate(alts[:10]):
        # Try to extract bytes from the altitude
        alt_int = int(alt)
        print(f"\nAltitude {i+1}: {alt_int}")
        
        # Convert to hex
        hex_str = hex(alt_int)[2:]
        print(f"  Hex: {hex_str}")
        
        # Try to interpret as ASCII
        ascii_chars = []
        temp = alt_int
        while temp > 0:
            byte = temp & 0xFF
            if 32 <= byte < 127:
                ascii_chars.append(chr(byte))
            temp >>= 8
        
        if ascii_chars:
            print(f"  ASCII: {''.join(reversed(ascii_chars))}")
    
    # Try extracting all altitude values and see if they form a message
    print("\n=== All altitudes as potential encoded data ===")
    offset = 256
    all_alt_chars = []
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            alt = struct.unpack('<d', data[offset+28:offset+36])[0]
            alt_int = int(alt)
            
            # Try each byte
            for i in range(8):
                byte = (alt_int >> (i*8)) & 0xFF
                if 32 <= byte < 127:
                    all_alt_chars.append(chr(byte))
            
            offset += 40
        else:
            offset += 1
    
    alt_message = ''.join(all_alt_chars)
    print(f"Altitude decoded (first 500 chars): {alt_message[:500]}")
    
    if 'Kaal{' in alt_message:
        idx = alt_message.index('Kaal{')
        print(f"\n!!! FLAG FOUND !!!")
        print(f"FLAG: {alt_message[idx:idx+100]}")

if __name__ == '__main__':
    analyze_gps(r'D:\mission-git-hackss\flight_record.dat')
