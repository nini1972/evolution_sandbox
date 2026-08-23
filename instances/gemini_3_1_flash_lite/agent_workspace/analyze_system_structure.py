import os

def analyze_workspace(path):
    structure = {}
    for root, dirs, files in os.walk(path):
        for name in files:
            ext = os.path.splitext(name)[1]
            if ext not in structure:
                structure[ext] = 0
            structure[ext] += 1
    return structure

stats = analyze_workspace("../../shared_space/")
print(stats)
