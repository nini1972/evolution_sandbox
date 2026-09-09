import os
import lzma
import time
from datetime import datetime

def get_complexity(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        if len(data) == 0: return 0
        return len(lzma.compress(data)) / len(data)
    except: return 0

files = ['status.log', 'entropy_monitor.log', 'spatiotemporal_log.txt']
with open('system_correlation.log', 'w') as f:
    f.write("Filename | Complexity | Last Modified\n")
    f.write("---|---|---\n")
    for file in files:
        if os.path.exists(file):
            comp = get_complexity(file)
            mtime = datetime.fromtimestamp(os.path.getmtime(file))
            f.write(f"{file} | {comp:.4f} | {mtime}\n")

