import numpy as np
import matplotlib.pyplot as plt

# Simple test of the motif memory system
from motif_memory_experiment import MotifMemorySystem, generate_motif_sequence

def debug_single_case():
    """Debug a single case to see what's happening"""
    # Generate motif sequence
    T = 200
    input_seq, true_motif = generate_motif_sequence(
        T, motif_length=15, noise_sigma=0.1, noise_rho=0.0, seed=42
    )
    
    print(f"Input sequence shape: {input_seq.shape}")
    print(f"True motif shape: {true_motif.shape}")
    print(f"True motif sample: {true_motif[:5]}")
    
    # Initialize system
    system = MotifMemorySystem(
        n_neurons=50, stable_ratio=0.5, learning_rate=0.01, seed=142
    )
    
    print(f"Stable weight shape: {system.W_stable.shape}")
    print(f"Adaptive weight shape: {system.W_adaptive.shape}")
    print(f"Neuron states shape: {system.neuron_states.shape}")
    
    # Store true motif
    system.store_motif("test", true_motif)
    print(f"Stored motif shape: {system.motif_memory['test'].shape}")
    
    # Process input
    outputs = system.process_input(input_seq.reshape(-1, 1))
    print(f"Outputs shape: {outputs.shape}")
    print(f"Outputs sample: {outputs[-5:, :5]}")
    
    # Test recall with clean motif
    similarity = system.recall_motif("test", true_motif)
    print(f"Similarity: {similarity}")
    
    # Let's also check if the stored motif matches what we think
    stored = system.motif_memory["test"]
    print(f"Stored vs true correlation: {np.corrcoef(stored.flatten(), true_motif.flatten())[0,1]}")

if __name__ == "__main__":
    debug_single_case()