import os
import re

lineage = {}
pattern = re.compile(r'main_cycle_v(\d+)\.py')

for root, dirs, files in os.walk('.'):
    for file in files:
        match = pattern.search(file)
        if match:
            version = int(match.group(1))
            lineage[version] = os.path.join(root, file)

for v in sorted(lineage.keys()):
    print(f"Version {v}: {lineage[v]}")
