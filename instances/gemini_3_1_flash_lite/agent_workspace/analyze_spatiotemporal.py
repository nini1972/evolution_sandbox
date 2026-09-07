import os
import time
import math
from collections import Counter

def get_system_metrics():
    # Spatial: Number of files and their distribution
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    file_sizes = [os.path.getsize(f) for f in files]
    num_files = len(files)
    total_size = sum(file_sizes)
    
    # Entropy of file names
    names = "".join(files)
    counts = Counter(names)
    entropy = -sum((count/len(names)) * math.log2(count/len(names)) for count in counts.values())
    
    return num_files, total_size, entropy

if __name__ == "__main__":
    num_files, total_size, entropy = get_system_metrics()
    print(f"Metrics - Files: {num_files}, Size: {total_size}, Name Entropy: {entropy:.2f}")
    
    with open('spatiotemporal_log.txt', 'a') as f:
        f.write(f"[{time.ctime()}] Files: {num_files}, Size: {total_size}, Name Entropy: {entropy:.2f}\n")
