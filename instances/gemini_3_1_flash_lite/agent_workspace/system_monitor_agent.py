import os
import time
import lzma

files_to_watch = ['status.log', 'entropy_monitor.log', 'spatiotemporal_log.txt']

def get_mtimes():
    return {f: os.path.getmtime(f) for f in files_to_watch if os.path.exists(f)}

def log_event(message):
    with open('system_monitor.log', 'a') as f:
        f.write(f"[{time.ctime()}] {message}\n")

# Initial state
last_mtimes = get_mtimes()

while True:
    time.sleep(10)
    current_mtimes = get_mtimes()
    
    # Check for synchronicity breakdown
    mtime_values = list(current_mtimes.values())
    if len(set(mtime_values)) > 1:
        # Check if the difference is significant
        if max(mtime_values) - min(mtime_values) > 1.0:
            log_event(f"ALERT: Synchronicity breakdown detected! Mtimes: {current_mtimes}")
    
    last_mtimes = current_mtimes
