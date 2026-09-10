import os
import lzma
import time

files = ['status.log', 'entropy_monitor.log', 'spatiotemporal_log.txt']

def get_complexity(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        return len(lzma.compress(data)) / len(data) if len(data) > 0 else 0
    except: return 0

# Sample the system for 5 cycles
for i in range(5):
    print(f"Sampling Epoch {i+1}...")
    for f in files:
        if os.path.exists(f):
            print(f"  {f}: {get_complexity(f):.4f}")
    time.sleep(2)
