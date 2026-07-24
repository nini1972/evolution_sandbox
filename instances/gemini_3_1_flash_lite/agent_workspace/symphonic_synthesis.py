import os
import json

def synthesize_resonances():
    base_path = '../../shared_space/resonance_experiments/'
    report = "# Symphonic Overview: Cycle 03 - Core Resonances\n\n"
    
    files = [f for f in os.listdir(base_path) if f.endswith('.json') or f.endswith('.md')]
    
    for file in sorted(files):
        report += f"## Analysis Artifact: {file}\n"
        with open(os.path.join(base_path, file), 'r') as f:
            content = f.read()
            if file.endswith('.json'):
                try:
                    data = json.loads(content)
                    report += f"```json\n{json.dumps(data, indent=4)}\n```\n"
                except json.JSONDecodeError:
                    report += f"Error parsing {file}\n"
            else:
                report += f"{content}\n"
        report += "\n---\n"
    
    with open('../../shared_space/universe_compendium/symphonic_synthesis_cycle03.md', 'w') as f:
        f.write(report)
    print("Symphony synthesized and written to universe_compendium.")

if __name__ == "__main__":
    synthesize_resonances()
