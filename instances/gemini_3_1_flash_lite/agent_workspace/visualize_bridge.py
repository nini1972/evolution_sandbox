import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib

matplotlib.use("Agg")

def visualize_resonance(data_path, output_filename):
    with open(data_path, 'r') as f:
        data = json.load(f)
        
    score = data['resonance_score']
    
    # Visualization: A phase space plot of potential resonance states
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Theoretical grid representation
    x = np.linspace(0, 10, 100)
    y = np.exp(-x / score) * np.sin(x)
    
    ax.plot(x, y, label=f'Resonance Wave (Score: {score:.3f})')
    ax.fill_between(x, y, color='skyblue', alpha=0.3)
    ax.set_title('Resonance Bridge Visualization')
    ax.set_xlabel('System Evolution Path')
    ax.set_ylabel('Harmonic Amplitude')
    ax.legend()
    
    plt.savefig(output_filename)
    print(f"Visualization saved to {output_filename}")

visualize_resonance('../../shared_space/resonance_experiments/bridge_analysis_03.json', 'resonance_bridge_viz.png')
