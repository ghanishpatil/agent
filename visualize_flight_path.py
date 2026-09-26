#!/usr/bin/env python3
"""
Properly visualize the flight path - it might draw letters/flag
"""

import struct
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def extract_and_plot(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Extract coordinates
    coords = []
    offset = 256
    
    while offset < len(data) - 40:
        if data[offset] == 0x01 and data[offset+1] == 0x55:
            try:
                timestamp = struct.unpack('<I', data[offset+4:offset+8])[0]
                lat = struct.unpack('<d', data[offset+12:offset+20])[0]
                lon = struct.unpack('<d', data[offset+20:offset+28])[0]
                alt = struct.unpack('<d', data[offset+28:offset+36])[0]
                
                coords.append((timestamp, lat, lon, alt))
                offset += 40
            except:
                offset += 1
        else:
            offset += 1
    
    print(f"Extracted {len(coords)} coordinates")
    
    if not coords:
        return
    
    timestamps = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    lons = [c[2] for c in coords]
    alts = [c[3] for c in coords]
    
    print(f"Lat range: {min(lats):.10f} to {max(lats):.10f}")
    print(f"Lon range: {min(lons):.10f} to {max(lons):.10f}")
    print(f"Alt range: {min(alts):.2f} to {max(alts):.2f}")
    
    # Plot 1: Raw flight path
    plt.figure(figsize=(20, 15))
    plt.subplot(2, 2, 1)
    plt.plot(lons, lats, 'b-', linewidth=1, alpha=0.7)
    plt.plot(lons[0], lats[0], 'go', markersize=10, label='Start')
    plt.plot(lons[-1], lats[-1], 'ro', markersize=10, label='End')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Raw Flight Path')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Altitude over time
    plt.subplot(2, 2, 2)
    plt.plot(timestamps, alts, 'r-', linewidth=1)
    plt.xlabel('Timestamp')
    plt.ylabel('Altitude')
    plt.title('Altitude Profile')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Normalized coordinates (this might show letters)
    plt.subplot(2, 2, 3)
    # Normalize to 0-1
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    
    norm_lats = [(lat - lat_min) / (lat_max - lat_min) if lat_max != lat_min else 0 for lat in lats]
    norm_lons = [(lon - lon_min) / (lon_max - lon_min) if lon_max != lon_min else 0 for lon in lons]
    
    plt.plot(norm_lons, norm_lats, 'g-', linewidth=2)
    plt.xlabel('Normalized Longitude')
    plt.ylabel('Normalized Latitude')
    plt.title('Normalized Flight Path')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    # Plot 4: Try to detect segments (pen up/down)
    plt.subplot(2, 2, 4)
    
    # Calculate distances between consecutive points
    distances = []
    for i in range(len(norm_lons) - 1):
        dx = norm_lons[i+1] - norm_lons[i]
        dy = norm_lats[i+1] - norm_lats[i]
        dist = (dx**2 + dy**2)**0.5
        distances.append(dist)
    
    # Find large jumps (pen lifts)
    threshold = np.percentile(distances, 95)  # Top 5% of distances
    print(f"\nDistance threshold for pen lifts: {threshold:.6f}")
    
    # Plot segments
    current_segment_x = [norm_lons[0]]
    current_segment_y = [norm_lats[0]]
    colors = plt.cm.rainbow(np.linspace(0, 1, 50))
    color_idx = 0
    
    for i in range(len(distances)):
        if distances[i] > threshold:
            # End current segment
            if len(current_segment_x) > 1:
                plt.plot(current_segment_x, current_segment_y, 
                        color=colors[color_idx % len(colors)], linewidth=3)
                color_idx += 1
            # Start new segment
            current_segment_x = [norm_lons[i+1]]
            current_segment_y = [norm_lats[i+1]]
        else:
            current_segment_x.append(norm_lons[i+1])
            current_segment_y.append(norm_lats[i+1])
    
    # Plot last segment
    if len(current_segment_x) > 1:
        plt.plot(current_segment_x, current_segment_y, 
                color=colors[color_idx % len(colors)], linewidth=3)
    
    plt.xlabel('Normalized Longitude')
    plt.ylabel('Normalized Latitude')
    plt.title(f'Segmented Path ({color_idx + 1} segments)')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    plt.tight_layout()
    plt.savefig('flight_visualization.png', dpi=300, bbox_inches='tight')
    print("\nVisualization saved to flight_visualization.png")
    
    # Create ASCII art with higher resolution
    print("\n=== High-Resolution ASCII Art ===")
    grid_size = 80
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    
    for lon, lat in zip(norm_lons, norm_lats):
        x = int(lon * (grid_size - 1))
        y = int((1 - lat) * (grid_size - 1))  # Flip Y
        if 0 <= x < grid_size and 0 <= y < grid_size:
            grid[y][x] = '#'
    
    for row in grid:
        print(''.join(row))
    
    # Try different aspect ratios
    print("\n=== Stretched Horizontally (2:1) ===")
    grid_w, grid_h = 120, 60
    grid2 = [[' ' for _ in range(grid_w)] for _ in range(grid_h)]
    
    for lon, lat in zip(norm_lons, norm_lats):
        x = int(lon * (grid_w - 1))
        y = int((1 - lat) * (grid_h - 1))
        if 0 <= x < grid_w and 0 <= y < grid_h:
            grid2[y][x] = '#'
    
    for row in grid2:
        print(''.join(row))

if __name__ == '__main__':
    extract_and_plot(r'D:\mission-git-hackss\flight_record.dat')
