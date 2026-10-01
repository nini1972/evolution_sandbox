"""
Motif Memory Experiment: Adaptive vs Stable Components

This experiment investigates how neural systems optimally allocate resources between
stable (fixed) and adaptive (plastic) connections based on input signal characteristics,
inspired by NoiseGarden's findings on dormancy strategies.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import correlate
import pandas as pd


class MotifMemorySystem:
    """Neural system for storing and recalling temporal motifs"""
    
    def __init__(self, n_neurons=100, stable_ratio=0.5, learning_rate=0.01, seed=42):
        """
        Initialize motif memory system
        
        Parameters:
        - n_neurons: number of neurons in the reservoir
        - stable_ratio: proportion of connections that are stable (fixed)
        - learning_rate: plasticity rate for adaptive connections
        """
        self.rng = np.random.RandomState(seed)
        self.n_neurons = n_neurons
        self.stable_ratio = stable_ratio
        self.learning_rate = learning_rate
        
        # Initialize connection matrices
        self.W_stable = self._initialize_weights(int(n_neurons * stable_ratio))
        self.W_adaptive = self._initialize_weights(n_neurons - int(n_neurons * stable_ratio))
        
        # Track system state
        self.neuron_states = np.zeros(n_neurons)
        self.motif_memory = {}
        
    def _initialize_weights(self, size):
        """Initialize random weight matrix"""
        if size == 0:
            return np.array([]).reshape(0, 0)
        
        W = self.rng.normal(0, 1/np.sqrt(size), (size, size))
        # Ensure stability by scaling spectral radius
        eigenvals = np.linalg.eigvals(W)
        spectral_radius = np.max(np.abs(eigenvals))
        if spectral_radius > 0:
            W = W / spectral_radius * 0.95  # Keep below 1.0 for stability
        return W
    
    def process_input(self, input_sequence, train=True):
        """Process input sequence through the system"""
        T = len(input_sequence)
        outputs = []
        
        for t in range(T):
            # Update neuron states
            stable_size = self.W_stable.shape[0]
            adaptive_size = self.W_adaptive.shape[0]
            
            if stable_size > 0:
                stable_input = self.W_stable @ self.neuron_states[:stable_size]
            else:
                stable_input = np.array([])
                
            if adaptive_size > 0:
                adaptive_input = self.W_adaptive @ self.neuron_states[stable_size:]
            else:
                adaptive_input = np.array([])
            
            if len(stable_input) > 0 and len(adaptive_input) > 0:
                total_input = np.concatenate([stable_input, adaptive_input])
            elif len(stable_input) > 0:
                total_input = stable_input
            elif len(adaptive_input) > 0:
                total_input = adaptive_input
            else:
                total_input = np.zeros_like(self.neuron_states)
                
            # Ensure total_input has correct shape
            if len(total_input) != len(self.neuron_states):
                if len(total_input) == 0:
                    total_input = np.zeros_like(self.neuron_states)
                else:
                    # Pad or truncate as needed
                    if len(total_input) < len(self.neuron_states):
                        total_input = np.concatenate([total_input, 
                                                    np.zeros(len(self.neuron_states) - len(total_input))])
                    else:
                        total_input = total_input[:len(self.neuron_states)]
            
            self.neuron_states = np.tanh(total_input + input_sequence[t].flatten())
            outputs.append(self.neuron_states.copy())
            
            # Update adaptive weights if training
            if train and t > 0:
                self._update_adaptive_weights(input_sequence[t], self.neuron_states)
        
        return np.array(outputs)
    
    def _update_adaptive_weights(self, current_input, current_state):
        """Update adaptive weights using Hebbian-like learning"""
        adaptive_size = self.W_adaptive.shape[0]
        if adaptive_size == 0:
            return
            
        # Simple Hebbian update rule
        stable_size = self.W_stable.shape[0]
        pre_activity = current_state[stable_size:stable_size + adaptive_size]
        post_activity = current_state[stable_size:stable_size + adaptive_size]
        
        # Ensure correct size
        if len(pre_activity) != adaptive_size:
            pre_activity = pre_activity[:adaptive_size]
            post_activity = post_activity[:adaptive_size]
        
        # Outer product for weight updates
        delta_W = np.outer(post_activity, pre_activity) * self.learning_rate
        self.W_adaptive += delta_W
        
        # Maintain stability by renormalizing
        eigenvals = np.linalg.eigvals(self.W_adaptive)
        spectral_radius = np.max(np.abs(eigenvals))
        if spectral_radius > 0.95:
            self.W_adaptive = self.W_adaptive / spectral_radius * 0.95
    
    def store_motif(self, motif_name, motif_pattern):
        """Store a motif pattern in memory"""
        self.motif_memory[motif_name] = motif_pattern
    
    def recall_motif(self, motif_name, query_sequence):
        """Attempt to recall stored motif given query"""
        if motif_name not in self.motif_memory:
            return None
            
        # Process query through system
        output = self.process_input(query_sequence.reshape(-1, 1), train=False)
        
        # Compare with stored motif (simplified)
        stored = self.motif_memory[motif_name]
        if len(output) >= len(stored):
            try:
                similarity = np.corrcoef(output[-len(stored):].flatten(), 
                                       stored.flatten())[0,1]
                if np.isnan(similarity):
                    similarity = 0.0
            except:
                similarity = 0.0
        else:
            similarity = 0.0
            
        return similarity


def generate_correlated_noise(T, sigma, rho, seed=42):
    """Generate autocorrelated noise sequence"""
    rng = np.random.RandomState(seed)
    noise = np.zeros(T)
    
    if rho == 0.0:
        noise = rng.normal(0, sigma, T)
    else:
        shock = rng.normal(0, sigma, T)
        noise[0] = shock[0]
        for t in range(1, T):
            noise[t] = rho * noise[t-1] + np.sqrt(1 - rho**2) * shock[t]
    
    return noise


def generate_motif_sequence(T, motif_length=10, noise_sigma=0.1, noise_rho=0.0, seed=42):
    """Generate sequence containing repeated motifs with correlated noise"""
    rng = np.random.RandomState(seed)
    
    # Create base motif
    motif = rng.normal(0, 1, motif_length)
    
    # Generate full sequence by repeating motif
    n_repeats = T // motif_length
    remainder = T % motif_length
    
    sequence = np.tile(motif, n_repeats)
    if remainder > 0:
        sequence = np.concatenate([sequence, motif[:remainder]])
    
    # Add correlated noise
    noise = generate_correlated_noise(T, noise_sigma, noise_rho, seed+1)
    sequence_with_noise = sequence + noise
    
    return sequence_with_noise, motif


def evaluate_motif_preservation(stable_ratio, sigma, rho, n_trials=5):
    """Evaluate how well motif is preserved for given parameters"""
    similarities = []
    
    for trial in range(n_trials):
        # Generate motif sequence
        T = 200
        input_seq, true_motif = generate_motif_sequence(
            T, motif_length=15, noise_sigma=sigma, noise_rho=rho, seed=trial
        )
        
        # Initialize system
        system = MotifMemorySystem(
            n_neurons=50, stable_ratio=stable_ratio, learning_rate=0.01, seed=trial+100
        )
        
        # Store true motif
        system.store_motif("test", true_motif)
        
        # Process input
        _ = system.process_input(input_seq.reshape(-1, 1))
        
        # Test recall with clean motif
        similarity = system.recall_motif("test", true_motif)
        if similarity is not None and not np.isnan(similarity):
            similarities.append(similarity)
    
    if similarities:
        return np.mean(similarities), np.std(similarities)
    else:
        return 0.0, 0.0


def main():
    """Run parameter sweep"""
    # Parameter ranges
    stable_ratios = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    sigma_levels = [0.1, 0.5, 1.0]  # noise variance
    rho_levels = [0.0, 0.5, 0.9]   # autocorrelation
    
    results = []
    
    print("Running motif memory experiments...")
    for stable_ratio in stable_ratios:
        for sigma in sigma_levels:
            for rho in rho_levels:
                print(f"Testing stable_ratio={stable_ratio:.1f}, sigma={sigma:.1f}, rho={rho:.1f}")
                mean_sim, std_sim = evaluate_motif_preservation(stable_ratio, sigma, rho)
                
                results.append({
                    'stable_ratio': stable_ratio,
                    'sigma': sigma,
                    'rho': rho,
                    'mean_similarity': mean_sim,
                    'std_similarity': std_sim
                })
    
    # Save results
    df_results = pd.DataFrame(results)
    df_results.to_csv('motif_memory_results.csv', index=False)
    
    # Create visualization
    plot_results(df_results)
    
    print("Experiment complete!")


def plot_results(df):
    """Create heatmaps of results"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, rho in enumerate([0.0, 0.5, 0.9]):
        sub_df = df[df['rho'] == rho].copy()
        pivot = sub_df.pivot(index='sigma', columns='stable_ratio', values='mean_similarity')
        
        im = axes[i].imshow(pivot.values, aspect='auto', origin='lower',
                           extent=[-0.1, 1.1, 0, 1.1],
                           cmap='viridis')
        axes[i].set_xlabel('Stable Ratio')
        axes[i].set_ylabel('Noise Variance (σ)')
        axes[i].set_title(f'Autocorrelation ρ={rho}')
        axes[i].set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        axes[i].set_yticks([0.1, 0.5, 1.0])
        plt.colorbar(im, ax=axes[i])
    
    plt.tight_layout()
    plt.savefig('motif_memory_heatmaps.png', dpi=150)
    plt.close()


if __name__ == '__main__':
    main()