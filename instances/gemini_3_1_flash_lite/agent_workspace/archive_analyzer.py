import os
from collections import Counter

entities_data = '../../shared_space/'
files = []
for root, dirs, filenames in os.walk(entities_data):
    for f in filenames:
        ext = os.path.splitext(f)[1]
        files.append(ext if ext else 'no_ext')

counts = Counter(files)
with open('archive_stats.md', 'w') as f:
    f.write("# Archive Statistics - " + os.popen('date').read().strip() + "\n\n")
    for ext, count in counts.most_common():
        f.write(f"- {ext}: {count}\n")

