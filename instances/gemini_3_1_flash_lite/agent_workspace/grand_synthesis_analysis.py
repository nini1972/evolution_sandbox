import os
import lzma

def analyze_complexity(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if not data: return 0
    return len(lzma.compress(data)) / len(data)

def run_synthesis_analysis():
    # Looking at the 'grand_synthesis' directory for artifacts
    synthesis_path = '../../shared_space/grand_synthesis'
    if not os.path.exists(synthesis_path):
        return "Synthesis path not found."
    
    files = os.listdir(synthesis_path)
    report = []
    for f in files:
        path = os.path.join(synthesis_path, f)
        if os.path.isfile(path):
            c = analyze_complexity(path)
            report.append((f, c))
    
    report.sort(key=lambda x: x[1], reverse=True)
    return report

print(run_synthesis_analysis())
