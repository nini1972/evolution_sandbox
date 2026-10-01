"""
Revised Motif Memory Experiment

Instead of trying to implement associative recall (which is complex),
this experiment measures how well different stable/adaptive ratios
preserve temporal structure consistency when exposed to the same
motif under different noise conditions.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

class RevisedMotifMemorySystem:
    """Simplified system focused on representation consistency"""
    
    def __init__(self, n_neurons=50, stable_ratio=0.5, learning_rate=0.01, seed=None):
        self.rng = np.random.RandomState(seed)
        self.n_neurons = n_neurons
        self.learning_rate = learning_rate
        
        # Split neurons into stable and adaptive populations
        stable_size = int(n_neurons * stable_ratio)
        adaptive_size = n_neurons - stable_size
        
        # Initialize weight matrices
        self.W_stable = self._initialize_weights(stable_size) if stable_size > 0 else np.array([]).reshape(0, 0)
        self.W_adaptive = self._initialize_weights(adaptive_size) if adaptive_size > 0 else np.array([]).reshape(0, 0)
        
        # Initialize neuron states
        self.neuron_states = self.rng.normal(0, 0.1, n_neurons)
        
    def _initialize_weights(self, size):
        """Initialize random weight matrix with controlled spectral radius"""
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
            if train and t > 0 and adaptive_size > 0:
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

def generate_motif_sequence(T, motif_length=15, noise_sigma=0.1, noise_rho=0.0, seed=None):
    """Generate a sequence with an embedded temporal motif"""
    rng = np.random.RandomState(seed)
    
    # Create base signal with motif
    signal = np.zeros(T)
    
    # Generate AR(1) noise
    noise = np.zeros(T)
    if T > 0:
        noise[0] = rng.normal(0, noise_sigma)
        for t in range(1, T):
            noise[t] = noise_rho * noise[t-1] + rng.normal(0, noise_sigma * np.sqrt(1 - noise_rho**2))
    
    # Embed motif at random position
    motif_start = rng.randint(0, T - motif_length)
    motif = rng.normal(0, 1, motif_length)
    signal[motif_start:motif_start + motif_length] = motif
    
    # Add noise
    observed = signal + noise
    
    return observed, motif

def measure_representation_consistency(stable_ratio, sigma, rho, n_trials=5):
    """
    Measure how consistently the same motif is represented across different noise realizations.
    Higher consistency indicates better motif preservation.
    """
    correlations = []
    
    for trial in range(n_trials):
        # Generate two different noisy versions of the same motif
        T = 200
        input_seq1, true_motif = generate_motif_sequence(
            T, motif_length=15, noise_sigma=sigma, noise_rho=rho, seed=trial*2
        )
        input_seq2, _ = generate_motif_sequence(
            T, motif_length=15, noise_sigma=sigma, noise_rho=rho, seed=trial*2+1
        )
        
        # Initialize identical systems
        system1 = RevisedMotifMemorySystem(
            n_neurons=50, stable_ratio=stable_ratio, learning_rate=0.01, seed=trial+100
        )
        system2 = RevisedMotifMemorySystem(
            n_neurons=50, stable_ratio=stable_ratio, learning_rate=0.01, seed=trial+100
        )
        
        # Process both sequences
        output1 = system1.process_input(input_seq1.reshape(-1, 1))
        output2 = system2.process_input(input_seq2.reshape(-1, 1))
        
        # Find where the motif occurs in each sequence
        # For simplicity, assume it's around the middle
        motif_center = T // 2
        motif_window = 15
        
        rep1 = output1[motif_center-motif_window//2:motif_center+motif_window//2+1]
        rep2 = output2[motif_center-motif_window//2:motif_center+motif_window//2+1]
        
        # Calculate correlation between representations
        if rep1.size > 0 and rep2.size > 0:
            # Flatten and correlate
            corr = np.corrcoef(rep1.flatten(), rep2.flatten())[0,1]
            if not np.isnan(corr):
                correlations.append(corr)
    
    if correlations:
        return np.mean(correlations), np.std(correlations)
    else:
        return 0.0, 0.0

def main():
    print("Running revised motif memory experiments...")
    
    # Define parameter ranges
    stable_ratios = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    sigmas = [0.1, 0.5, 1.0]
    rhos = [0.0, 0.5, 0.9]
    
    results = []
    
    for stable_ratio in stable_ratios:
        for sigma in sigmas:
            for rho in rhos:
                print(f"Testing stable_ratio={stable_ratio}, sigma={sigma}, rho={rho}")
                mean_corr, std_corr = measure_representation_consistency(stable_ratio, sigma, rho)
                results.append({
                    'stable_ratio': stable_ratio,
                    'sigma': sigma,
                    'rho': rho,
                    'mean_correlation': mean_corr,
                    'std_correlation': std_corr
                })
    
    # Save results
    import csv
    with open('revised_motif_memory_results.csv', 'w', newline='') as csvfile:
        fieldnames = ['stable_ratio', 'sigma', 'rho', 'mean_correlation', 'std_correlation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    # Create heatmaps
    create_heatmaps(results)
    
    print("Revised experiment complete!")

def create_heatmaps(results):
    """Create heatmap visualizations of the results"""
    import matplotlib.pyplot as plt
    
    # Convert to numpy arrays for easier manipulation
    stable_ratios = sorted(set(r['stable_ratio'] for r in results))
    sigmas = sorted(set(r['sigma'] for r in results))
    rhos = sorted(set(r['rho'] for r in results))
    
    # Create heatmaps for different noise conditions
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle('Motif Representation Consistency\n(Mean Correlation between Noisy Presentations)', fontsize=16)
    
    for i, sigma in enumerate(sigmas):
        for j, rho in enumerate(rhos):
            # Extract data for this noise condition
            data = np.zeros(len(stable_ratios))
            for k, stable_ratio in enumerate(stable_ratios):
                for result in results:
                    if (result['stable_ratio'] == stable_ratio and 
                        result['sigma'] == sigma and 
                        result['rho'] == rho):
                        data[k] = result['mean_correlation']
                        break
            
            ax = axes[i, j]
            im = ax.imshow(data.reshape(-1, 1), cmap='viridis', aspect='auto')
            ax.set_yticks(range(len(stable_ratios)))
            ax.set_yticklabels([f'{sr:.1f}' for sr in stable_ratios])
            ax.set_xticks([])
            ax.set_title(f'σ={sigma}, ρ={rho}')
            if j == 0:
                ax.set_ylabel('Stable Ratio')
            if i == len(sigmas) - 1:
                ax.set_xlabel('Consistency')
            
            # Add colorbar
            plt.colorbar(im, ax=ax)
    
    plt.tight_layout()
    plt.savefig('revised_motif_memory_heatmaps.png', dpi=150, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main()