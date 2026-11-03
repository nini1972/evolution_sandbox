import os
import glob

# search for belousov_zhabotinsky generator or references across the repository
res = []
for root, dirs, files in os.walk('/home/runner/work/evolution_sandbox/evolution_sandbox/world_c'):
    for f in files:
        if f.endswith('.py') or f.endswith('.md'):
            p = os.path.join(root, f)
            with open(p, 'r', errors='ignore') as fh:
                content = fh.read()
                if 'belousov_zhabotinsky' in content:
                    res.append(p)
print("Files mentioning belousov_zhabotinsky:")
for r in res:
    print(r)
