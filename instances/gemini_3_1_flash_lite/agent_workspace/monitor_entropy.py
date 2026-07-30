import os
import time

def get_snapshot():
    return set(os.listdir('../../shared_space/'))

prev_snapshot = get_snapshot()

with open('entropy_monitor.log', 'a') as f:
    f.write(f"[{time.ctime()}] Monitor initiated. File count: {len(prev_snapshot)}\n")

while True:
    time.sleep(60) # Watch for 60 seconds at a time
    current_snapshot = get_snapshot()
    if current_snapshot != prev_snapshot:
        added = current_snapshot - prev_snapshot
        removed = prev_snapshot - current_snapshot
        with open('entropy_monitor.log', 'a') as f:
            f.write(f"[{time.ctime()}] Change detected.\n")
            if added:
                f.write(f"  Added: {', '.join(added)}\n")
            if removed:
                f.write(f"  Removed: {', '.join(removed)}\n")
        prev_snapshot = current_snapshot
