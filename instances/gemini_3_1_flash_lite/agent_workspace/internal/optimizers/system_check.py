import os
import time

def monitor_resources():
    # Placeholder for file-based resource monitoring
    files = os.listdir('.')
    file_count = len(files)
    print(f"System Load: {file_count} active files.")
    return file_count

if __name__ == '__main__':
    monitor_resources()
