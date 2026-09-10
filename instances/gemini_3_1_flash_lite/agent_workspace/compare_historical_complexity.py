import os
import lzma

def get_complexity(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        return len(lzma.compress(data)) / len(data) if len(data) > 0 else 0
    except: return 0

def walk_and_analyze(root_dir):
    complexities = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            complexities.append(get_complexity(path))
    return sum(complexities) / len(complexities) if complexities else 0

legacy_path = './archive_legacy'
current_path = '.'

print(f"Average Legacy Complexity: {walk_and_analyze(legacy_path):.4f}")
print(f"Current System Complexity: {walk_and_analyze(current_path):.4f}")
