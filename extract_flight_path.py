#!/usr/bin/env python3
"""
Extract and analyze flight path from flight_record.dat
GPS coordinates might spell out letters or form a pattern
"""

import struct
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

def extract_coordinates(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    records = []
    offset = 256  # Data starts here
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            try:
                marker = struct.unpack('<H', data[offset:offset+2])[0]
                rec_type = struct.unpack('<H', data[offset+2:offset+4])[0]
                timestamp = struct.unpack('<I', data[offset+4:offset+8])[0]
                
                # Extract three doubles (lat, lon, alt)
                lat = struct.unpack('<d', data[offset+12:offset+20])[0]
                lon = struct.unpack('<d', data[offset+20:offset+28])[0]
                alt = struct.unpack('<d', data[offset+28:offset+36])[0]
                
                records.append({
                    'timestamp': timestamp,
                    'lat': lat,
                    'lon': lon,
                    'alt': alt
                })
                
                offset += 40
            except:
                offset += 1
        else:
            offset += 1
    
    return records

def analyze_path(records):
    print(f"Total records: {len(records)}")
    
    if not records:
        return
    
    lats = [r['lat'] for r in records]
    lons = [r['lon'] for r in records]
    alts = [r['alt'] for r in records]
    
    print(f"\nLatitude range: {min(lats):.6f} to {max(lats):.6f}")
    print(f"Longitude range: {min(lons):.6f} to {max(lons):.6f}")
    print(f"Altitude range: {min(alts):.2f} to {max(alts):.2f}")
    
    # Plot the flight path
    plt.figure(figsize=(12, 10))
    plt.plot(lons, lats, 'b-', linewidth=0.5, alpha=0.6)
    plt.plot(lons[0], lats[0], 'go', markersize=10, label='Start')
    plt.plot(lons[-1], lats[-1], 'ro', markersize=10, label='End')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Flight Path')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('flight_path.png', dpi=300)
    print("\nFlight path saved to flight_path.png")
    
    # Check if path spells something
    # Normalize coordinates to see pattern
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    
    # Normalize to 0-1 range
    norm_lats = [(lat - lat_min) / (lat_max - lat_min) if lat_max != lat_min else 0 for lat in lats]
    norm_lons = [(lon - lon_min) / (lon_max - lon_min) if lon_max != lon_min else 0 for lon in lons]
    
    # Try to detect segments (when plane "lifts pen")
    # Look for large jumps in position
    segments = []
    current_segment = [(norm_lons[0], norm_lats[0])]
    
    threshold = 0.1  # 10% of range
    for i in range(1, len(norm_lons)):
        dx = abs(norm_lons[i] - norm_lons[i-1])
        dy = abs(norm_lats[i] - norm_lats[i-1])
        
        if dx > threshold or dy > threshold:
            # New segment
            if len(current_segment) > 5:
                segments.append(current_segment)
            current_segment = [(norm_lons[i], norm_lats[i])]
        else:
            current_segment.append((norm_lons[i], norm_lats[i]))
    
    if len(current_segment) > 5:
        segments.append(current_segment)
    
    print(f"\nDetected {len(segments)} segments in flight path")
    
    # Plot segments separately
    plt.figure(figsize=(15, 10))
    colors = plt.cm.rainbow([i/len(segments) for i in range(len(segments))])
    
    for i, segment in enumerate(segments):
        xs = [p[0] for p in segment]
        ys = [p[1] for p in segment]
        plt.plot(xs, ys, color=colors[i], linewidth=2, label=f'Segment {i+1}')
    
    plt.xlabel('Normalized Longitude')
    plt.ylabel('Normalized Latitude')
    plt.title(f'Flight Path Segments ({len(segments)} segments)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('flight_segments.png', dpi=300)
    print("Flight segments saved to flight_segments.png")
    
    # Try ASCII art interpretation
    print("\n=== ASCII Art Interpretation ===")
    # Create a grid
    grid_size = 50
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    
    for lon, lat in zip(norm_lons, norm_lats):
        x = int(lon * (grid_size - 1))
        y = int((1 - lat) * (grid_size - 1))  # Flip Y axis
        if 0 <= x < grid_size and 0 <= y < grid_size:
            grid[y][x] = '#'
    
    for row in grid:
        print(''.join(row))

if __name__ == '__main__':
    records = extract_coordinates(r'D:\mission-git-hackss\flight_record.dat')
    analyze_path(records)
