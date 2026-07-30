import os
import datetime

base_file = 'file_listing_base.txt'
# Corrected the path to point to shared_space
shared_path = '../../shared_space/'
try:
    current_files = os.listdir(shared_path)
except FileNotFoundError:
    current_files = []

try:
    with open(base_file, 'r') as f:
        previous_files = set(f.read().splitlines())
except FileNotFoundError:
    previous_files = set()

current_set = set(current_files)

added = current_set - previous_files
removed = previous_files - current_set

if added or removed:
    with open('archival_summary.md', 'a') as f:
        f.write(f"\n# Archive Update: {datetime.datetime.now()}\n")
        if added:
            f.write("## Added:\n- " + "\n- ".join(added) + "\n")
        if removed:
            f.write("## Removed:\n- " + "\n- ".join(removed) + "\n")
        f.write("\n")

    with open(base_file, 'w') as f:
        for filename in current_set:
            f.write(f"{filename}\n")
    print("Archive updated.")
else:
    print("No changes detected.")
