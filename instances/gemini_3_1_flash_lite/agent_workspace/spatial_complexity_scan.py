import os
import lzma

def get_spatial_complexity(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        if len(data) == 0:
            return 0
        compressed = lzma.compress(data)
        # Ratio of compressed to original: lower ratio means higher redundancy (lower complexity)
        # Higher ratio (closer to 1.0) means higher complexity (less redundancy)
        return len(compressed) / len(data)
    except Exception:
        return 0

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]
    results = {f: get_spatial_complexity(f) for f in files}
    
    # Sort by complexity
    sorted_files = sorted(results.items(), key=lambda item: item[1], reverse=True)
    
    with open('spatial_complexity_report.md', 'w') as f:
        f.write("# Spatial Complexity Scan Report\n\n")
        f.write("| File | Complexity (LZ Proxy) |\n|---|---|\n")
        for file, complexity in sorted_files:
            f.write(f"| {file} | {complexity:.4f} |\n")
