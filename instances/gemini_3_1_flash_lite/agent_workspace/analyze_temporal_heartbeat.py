import os
import time
from datetime import datetime

def analyze_heartbeat():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    mtimes = [os.path.getmtime(f) for f in files]
    
    if not mtimes:
        return 0
    
    # Calculate intervals between modifications
    mtimes.sort()
    intervals = [mtimes[i] - mtimes[i-1] for i in range(1, len(mtimes))]
    
    if not intervals:
        return 0
        
    avg_interval = sum(intervals) / len(intervals)
    return avg_interval

if __name__ == "__main__":
    interval = analyze_heartbeat()
    with open('temporal_heartbeat.log', 'a') as f:
        f.write(f"[{datetime.now()}] Average modification interval (s): {interval:.4f}\n")
    print(f"Average modification interval: {interval:.4f} seconds")
