#!/usr/bin/env python3
"""
Manual FAT32 parser to extract files and search for flags
"""
import struct
import os

disk_path = "disk1_extracted/disk/Disk2.001"

class FAT32Parser:
    def __init__(self, disk_path):
        self.disk = open(disk_path, 'rb')
        self.parse_boot_sector()
    
    def parse_boot_sector(self):
        self.disk.seek(0)
        boot = self.disk.read(512)
        
        # Parse BPB (BIOS Parameter Block)
        self.bytes_per_sector = struct.unpack('<H', boot[11:13])[0]
        self.sectors_per_cluster = boot[13]
        self.reserved_sectors = struct.unpack('<H', boot[14:16])[0]
        self.num_fats = boot[16]
        self.sectors_per_fat = struct.unpack('<I', boot[36:40])[0]
        self.root_cluster = struct.unpack('<I', boot[44:48])[0]
        
        print(f"[*] FAT32 Filesystem Info:")
        print(f"    Bytes per sector: {self.bytes_per_sector}")
        print(f"    Sectors per cluster: {self.sectors_per_cluster}")
        print(f"    Reserved sectors: {self.reserved_sectors}")
        print(f"    Number of FATs: {self.num_fats}")
        print(f"    Sectors per FAT: {self.sectors_per_fat}")
        print(f"    Root cluster: {self.root_cluster}")
        
        # Calculate important offsets
        self.fat_offset = self.reserved_sectors * self.bytes_per_sector
        self.data_offset = self.fat_offset + (self.num_fats * self.sectors_per_fat * self.bytes_per_sector)
        self.cluster_size = self.sectors_per_cluster * self.bytes_per_sector
        
        print(f"    FAT offset: {self.fat_offset}")
        print(f"    Data offset: {self.data_offset}")
        print(f"    Cluster size: {self.cluster_size}")
    
    def get_cluster_offset(self, cluster):
        return self.data_offset + (cluster - 2) * self.cluster_size
    
    def read_cluster(self, cluster):
        offset = self.get_cluster_offset(cluster)
        self.disk.seek(offset)
        return self.disk.read(self.cluster_size)
    
    def get_next_cluster(self, cluster):
        fat_offset = self.fat_offset + (cluster * 4)
        self.disk.seek(fat_offset)
        next_cluster = struct.unpack('<I', self.disk.read(4))[0] & 0x0FFFFFFF
        if next_cluster >= 0x0FFFFFF8:
            return None  # End of chain
        return next_cluster
    
    def read_file_clusters(self, start_cluster, size):
        data = b''
        cluster = start_cluster
        remaining = size
        
        while cluster is not None and remaining > 0:
            cluster_data = self.read_cluster(cluster)
            to_read = min(len(cluster_data), remaining)
            data += cluster_data[:to_read]
            remaining -= to_read
            cluster = self.get_next_cluster(cluster)
        
        return data
    
    def parse_directory(self, cluster, path="/"):
        entries = []
        dir_data = self.read_cluster(cluster)
        
        i = 0
        while i < len(dir_data):
            entry = dir_data[i:i+32]
            if len(entry) < 32:
                break
            
            # Check if entry is free or end of directory
            if entry[0] == 0x00:
                break
            if entry[0] == 0xE5:  # Deleted file
                i += 32
                continue
            
            # Check attributes
            attr = entry[11]
            
            # Skip long filename entries
            if attr == 0x0F:
                i += 32
                continue
            
            # Parse short filename
            name = entry[0:8].decode('ascii', errors='ignore').strip()
            ext = entry[8:11].decode('ascii', errors='ignore').strip()
            if ext:
                filename = f"{name}.{ext}"
            else:
                filename = name
            
            # Get cluster and size
            cluster_high = struct.unpack('<H', entry[20:22])[0]
            cluster_low = struct.unpack('<H', entry[26:28])[0]
            file_cluster = (cluster_high << 16) | cluster_low
            file_size = struct.unpack('<I', entry[28:32])[0]
            
            is_dir = (attr & 0x10) != 0
            
            entries.append({
                'name': filename,
                'cluster': file_cluster,
                'size': file_size,
                'is_dir': is_dir,
                'path': os.path.join(path, filename)
            })
            
            i += 32
        
        return entries
    
    def explore_filesystem(self):
        print(f"\n[*] Exploring filesystem starting from root cluster {self.root_cluster}...")
        
        to_explore = [(self.root_cluster, "/")]
        all_files = []
        
        while to_explore:
            cluster, path = to_explore.pop(0)
            
            try:
                entries = self.parse_directory(cluster, path)
                
                for entry in entries:
                    if entry['name'] in ['.', '..']:
                        continue
                    
                    print(f"  {entry['path']} ({'DIR' if entry['is_dir'] else f'{entry['size']} bytes'})")
                    
                    if entry['is_dir'] and entry['cluster'] > 0:
                        to_explore.append((entry['cluster'], entry['path']))
                    elif not entry['is_dir']:
                        all_files.append(entry)
            except Exception as e:
                print(f"  [!] Error exploring {path}: {e}")
        
        return all_files
    
    def search_for_flags(self, files):
        print(f"\n[*] Searching {len(files)} files for flags...")
        
        for file_info in files:
            try:
                if file_info['size'] > 0 and file_info['cluster'] > 0:
                    data = self.read_file_clusters(file_info['cluster'], file_info['size'])
                    
                    if b'Kaal{' in data:
                        print(f"\n[+] FLAG FOUND in {file_info['path']}!")
                        idx = data.find(b'Kaal{')
                        flag_data = data[idx:idx+200]
                        end_idx = flag_data.find(b'}')
                        if end_idx != -1:
                            flag = flag_data[:end_idx+1].decode('utf-8', errors='ignore')
                            print(f"[+] FLAG: {flag}")
                            
                            # Save the file
                            output_path = f"extracted_{file_info['name']}"
                            with open(output_path, 'wb') as f:
                                f.write(data)
                            print(f"[*] File saved to: {output_path}")
            except Exception as e:
                print(f"  [!] Error reading {file_info['path']}: {e}")
    
    def close(self):
        self.disk.close()

# Main execution
print("[*] Starting FAT32 analysis...")
parser = FAT32Parser(disk_path)
files = parser.explore_filesystem()
parser.search_for_flags(files)
parser.close()

print("\n[*] Analysis complete!")
