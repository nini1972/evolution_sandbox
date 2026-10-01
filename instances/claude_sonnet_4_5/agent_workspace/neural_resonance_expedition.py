#!/usr/bin/env python3
"""
RESONANCE ARCHAEOLOGY EXPEDITION #002
Neural Network Information Crystallization

Hypothesis: Artificial neural networks exhibit the same dual-phase
information crystallization observed in Kuramoto oscillators.

We will excavate:
1. Information structure during training convergence
2. Activation synchronization patterns  
3. Dual critical points in learning dynamics
4. Cross-layer resonance signatures
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless plotting
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import json
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import mutual_info_score
import warnings
warnings.filterwarnings('ignore')

def lempel_ziv_complexity(sequence, threshold=0.5):
    """Calculate Lempel-Ziv complexity of a binary sequence"""
    if len(sequence) == 0:
        return 0
    
    # Binarize sequence
    binary_seq = (np.array(sequence) > threshold).astype(int)
    
    if len(set(binary_seq)) == 1:  # All same value
        return 0
    
    # Lempel-Ziv algorithm
    complexity = 0
    i = 0
    while i < len(binary_seq):
        j = i + 1
        while j <= len(binary_seq):
            substring = binary_seq[i:j]
            if not any(np.array_equal(substring, binary_seq[k:k+len(substring)]) 
                      for k in range(i)):
                complexity += 1
                i = j
                break
            j += 1
        else:
            break
    
    return complexity / len(binary_seq) if len(binary_seq) > 0 else 0

def mutual_information_matrix(activations):
    """Calculate mutual information between neural activations"""
    n_neurons = activations.shape[1]
    mi_matrix = np.zeros((n_neurons, n_neurons))
    
    for i in range(n_neurons):
        for j in range(i+1, n_neurons):
            # Discretize continuous activations for MI calculation
            x_discrete = np.digitize(activations[:, i], 
                                   bins=np.linspace(activations[:, i].min(), 
                                                  activations[:, i].max(), 10))
            y_discrete = np.digitize(activations[:, j], 
                                   bins=np.linspace(activations[:, j].min(), 
                                                  activations[:, j].max(), 10))
            
            mi = mutual_info_score(x_discrete, y_discrete)
            mi_matrix[i, j] = mi
            mi_matrix[j, i] = mi
    
    return np.mean(mi_matrix[mi_matrix > 0]) if np.any(mi_matrix > 0) else 0

def activation_synchronization(activations):
    """Calculate synchronization order parameter for neural activations"""
    if activations.shape[1] < 2:
        return 0
    
    # Normalize activations to unit vectors
    normalized = activations / (np.linalg.norm(activations, axis=0) + 1e-10)
    
    # Calculate pairwise correlations
    correlations = np.corrcoef(normalized.T)
    correlations = correlations[~np.isnan(correlations)]
    
    if len(correlations) == 0:
        return 0
    
    # Order parameter as mean absolute correlation
    return np.mean(np.abs(correlations[correlations != 1]))  # Exclude self-correlations

def phase_coherence(activations):
    """Calculate phase coherence of neural oscillations"""
    if activations.shape[0] < 3:
        return 0
    
    # Convert to phase representation using Hilbert transform analogy
    phases = np.angle(np.fft.fft(activations, axis=0))[:activations.shape[0]//2]
    
    if phases.shape[0] == 0:
        return 0
    
    # Calculate phase coherence
    mean_phase = np.mean(np.exp(1j * phases), axis=0)
    return np.mean(np.abs(mean_phase))

class NeuralResonanceExcavator:
    """Archaeological tool for excavating neural information crystallization"""
    
    def __init__(self, hidden_layers=(50, 30), max_iter=200):
        self.hidden_layers = hidden_layers
        self.max_iter = max_iter
        self.excavation_data = []
        
    def create_dataset(self, n_samples=1000, n_features=20, n_classes=2):
        """Create synthetic classification dataset"""
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_classes=n_classes,
            n_redundant=0,
            n_informative=n_features//2,
            random_state=42
        )
        
        # Split and scale
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        return X_train, X_test, y_train, y_test
    
    def excavate_training_dynamics(self, X_train, y_train, X_test, y_test):
        """Excavate information crystallization during neural network training"""
        
        print("=== NEURAL RESONANCE EXCAVATION ===")
        print("Analyzing information crystallization in neural training dynamics...")
        
        # Create network with custom parameters for detailed monitoring
        mlp = MLPClassifier(
            hidden_layer_sizes=self.hidden_layers,
            max_iter=1,  # Train one iteration at a time
            warm_start=True,
            learning_rate_init=0.01,
            solver='adam',
            random_state=42,
            activation='relu'
        )
        
        # Track training progress
        for epoch in range(self.max_iter):
            # Train for one epoch
            mlp.fit(X_train, y_train)
            
            # Get training accuracy
            train_acc = mlp.score(X_train, y_train)
            test_acc = mlp.score(X_test, y_test)
            
            # Extract activations from hidden layers
            activations_by_layer = []
            
            # Forward pass to get activations
            layer_input = X_train
            for i, (W, b) in enumerate(zip(mlp.coefs_[:-1], mlp.intercepts_[:-1])):
                layer_output = np.maximum(0, np.dot(layer_input, W) + b)  # ReLU
                activations_by_layer.append(layer_output)
                layer_input = layer_output
            
            # Analyze each layer
            layer_metrics = []
            for layer_idx, activations in enumerate(activations_by_layer):
                # Information metrics
                lz_complexity = lempel_ziv_complexity(activations.flatten())
                mutual_info = mutual_information_matrix(activations)
                sync_order = activation_synchronization(activations)
                phase_coh = phase_coherence(activations)
                
                # Weight statistics
                weight_matrix = mlp.coefs_[layer_idx]
                weight_entropy = -np.sum(np.abs(weight_matrix) * 
                                       np.log(np.abs(weight_matrix) + 1e-10))
                
                layer_metrics.append({
                    'layer': layer_idx,
                    'lz_complexity': lz_complexity,
                    'mutual_info': mutual_info,
                    'sync_order': sync_order,
                    'phase_coherence': phase_coh,
                    'weight_entropy': weight_entropy,
                    'mean_activation': np.mean(activations),
                    'activation_std': np.std(activations)
                })
            
            # Store epoch data
            epoch_data = {
                'epoch': epoch,
                'train_accuracy': train_acc,
                'test_accuracy': test_acc,
                'layers': layer_metrics,
                'convergence_rate': abs(train_acc - test_acc)  # Generalization gap
            }
            
            self.excavation_data.append(epoch_data)
            
            # Progress indicator
            if epoch % 20 == 0:
                print(f"Epoch {epoch:3d}: Train={train_acc:.3f}, Test={test_acc:.3f}")
                
            # Early stopping if converged
            if train_acc > 0.95 and test_acc > 0.9:
                print(f"Convergence detected at epoch {epoch}")
                break
        
        return self.excavation_data
    
    def analyze_resonance_signatures(self):
        """Extract resonance signatures from excavated data"""
        
        print("\n=== RESONANCE SIGNATURE ANALYSIS ===")
        
        # Convert to DataFrame for analysis
        records = []
        for epoch_data in self.excavation_data:
            for layer_data in epoch_data['layers']:
                record = {
                    'epoch': epoch_data['epoch'],
                    'train_accuracy': epoch_data['train_accuracy'],
                    'test_accuracy': epoch_data['test_accuracy'],
                    'convergence_rate': epoch_data['convergence_rate'],
                    **layer_data
                }
                records.append(record)
        
        df = pd.DataFrame(records)
        
        # Critical point detection
        critical_points = {}
        
        # For each layer, find critical transitions
        for layer in df['layer'].unique():
            layer_df = df[df['layer'] == layer].copy()
            
            if len(layer_df) < 5:
                continue
                
            # Accuracy critical point (learning transition)
            acc_gradient = np.gradient(layer_df['train_accuracy'])
            acc_critical_idx = np.argmax(acc_gradient) if len(acc_gradient) > 0 else 0
            
            # Information critical point (LZ complexity transition)
            lz_gradient = np.gradient(layer_df['lz_complexity'])
            lz_critical_idx = np.argmax(np.abs(lz_gradient)) if len(lz_gradient) > 0 else 0
            
            # Synchronization critical point
            sync_gradient = np.gradient(layer_df['sync_order'])
            sync_critical_idx = np.argmax(sync_gradient) if len(sync_gradient) > 0 else 0
            
            critical_points[f'layer_{layer}'] = {
                'accuracy_critical_epoch': layer_df.iloc[acc_critical_idx]['epoch'],
                'lz_critical_epoch': layer_df.iloc[lz_critical_idx]['epoch'],
                'sync_critical_epoch': layer_df.iloc[sync_critical_idx]['epoch'],
                'final_lz_complexity': layer_df.iloc[-1]['lz_complexity'],
                'final_sync_order': layer_df.iloc[-1]['sync_order'],
                'final_mutual_info': layer_df.iloc[-1]['mutual_info']
            }
        
        return df, critical_points

def main():
    """Main excavation protocol"""
    
    print("RESONANCE ARCHAEOLOGY EXPEDITION #002")
    print("Target: Neural Network Information Crystallization")
    print("=" * 50)
    
    # Initialize excavator
    excavator = NeuralResonanceExcavator(
        hidden_layers=(30, 20),  # Moderate complexity
        max_iter=150
    )
    
    # Create archaeological dataset
    X_train, X_test, y_train, y_test = excavator.create_dataset(
        n_samples=800, n_features=15, n_classes=2
    )
    
    print(f"Dataset created: {X_train.shape[0]} training samples, {X_test.shape[0]} test samples")
    print(f"Network architecture: Input({X_train.shape[1]}) -> Hidden{excavator.hidden_layers} -> Output(2)")
    
    # Excavate training dynamics
    excavation_data = excavator.excavate_training_dynamics(X_train, y_train, X_test, y_test)
    
    # Analyze resonance signatures  
    df, critical_points = excavator.analyze_resonance_signatures()
    
    # Save raw excavation data
    df.to_csv('neural_resonance_raw.csv', index=False)
    
    with open('neural_critical_points.json', 'w') as f:
        json.dump(critical_points, f, indent=2)
    
    # Create comprehensive visualization
    create_neural_resonance_plots(df, critical_points)
    
    print("\n=== EXCAVATION COMPLETE ===")
    print("Raw data saved to: neural_resonance_raw.csv")
    print("Critical points saved to: neural_critical_points.json")
    print("Visual analysis saved to: neural_resonance_analysis.png")
    
    # Print key discoveries
    print("\n=== KEY ARCHAEOLOGICAL DISCOVERIES ===")
    for layer, points in critical_points.items():
        print(f"\n{layer.upper()}:")
        print(f"  Accuracy transition: Epoch {points['accuracy_critical_epoch']}")
        print(f"  Information transition: Epoch {points['lz_critical_epoch']}")  
        print(f"  Synchronization transition: Epoch {points['sync_critical_epoch']}")
        print(f"  Final LZ complexity: {points['final_lz_complexity']:.4f}")
        print(f"  Final sync order: {points['final_sync_order']:.4f}")

def create_neural_resonance_plots(df, critical_points):
    """Create comprehensive visualization of neural resonance excavation"""
    
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('Neural Network Information Crystallization Archaeology', fontsize=16, fontweight='bold')
    
    # Color map for layers
    layer_colors = plt.cm.Set1(np.linspace(0, 1, len(df['layer'].unique())))
    
    # Plot 1: Training Dynamics
    ax1 = axes[0, 0]
    epochs = df[df['layer'] == 0]['epoch'].values
    train_acc = df[df['layer'] == 0]['train_accuracy'].values
    test_acc = df[df['layer'] == 0]['test_accuracy'].values
    
    ax1.plot(epochs, train_acc, 'b-', label='Train Accuracy', linewidth=2)
    ax1.plot(epochs, test_acc, 'r--', label='Test Accuracy', linewidth=2)
    ax1.set_xlabel('Training Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Learning Dynamics')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Lempel-Ziv Complexity Evolution
    ax2 = axes[0, 1]
    for i, layer in enumerate(df['layer'].unique()):
        layer_df = df[df['layer'] == layer]
        ax2.plot(layer_df['epoch'], layer_df['lz_complexity'], 
                color=layer_colors[i], label=f'Layer {layer}', linewidth=2)
    
    ax2.set_xlabel('Training Epoch')
    ax2.set_ylabel('Lempel-Ziv Complexity')
    ax2.set_title('Information Crystallization')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Synchronization Order
    ax3 = axes[1, 0]
    for i, layer in enumerate(df['layer'].unique()):
        layer_df = df[df['layer'] == layer]
        ax3.plot(layer_df['epoch'], layer_df['sync_order'], 
                color=layer_colors[i], label=f'Layer {layer}', linewidth=2)
    
    ax3.set_xlabel('Training Epoch')
    ax3.set_ylabel('Synchronization Order')
    ax3.set_title('Neural Synchronization Emergence')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Mutual Information
    ax4 = axes[1, 1]
    for i, layer in enumerate(df['layer'].unique()):
        layer_df = df[df['layer'] == layer]
        ax4.plot(layer_df['epoch'], layer_df['mutual_info'], 
                color=layer_colors[i], label=f'Layer {layer}', linewidth=2)
    
    ax4.set_xlabel('Training Epoch')
    ax4.set_ylabel('Mutual Information')
    ax4.set_title('Information Sharing Evolution')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Critical Points Comparison
    ax5 = axes[2, 0]
    layers = list(critical_points.keys())
    acc_crits = [critical_points[layer]['accuracy_critical_epoch'] for layer in layers]
    lz_crits = [critical_points[layer]['lz_critical_epoch'] for layer in layers]
    sync_crits = [critical_points[layer]['sync_critical_epoch'] for layer in layers]
    
    x_pos = np.arange(len(layers))
    width = 0.25
    
    ax5.bar(x_pos - width, acc_crits, width, label='Accuracy Critical', alpha=0.8)
    ax5.bar(x_pos, lz_crits, width, label='Information Critical', alpha=0.8)
    ax5.bar(x_pos + width, sync_crits, width, label='Sync Critical', alpha=0.8)
    
    ax5.set_xlabel('Network Layer')
    ax5.set_ylabel('Critical Epoch')
    ax5.set_title('Dual Transition Comparison')
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(layers)
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Final State Metrics
    ax6 = axes[2, 1]
    final_lz = [critical_points[layer]['final_lz_complexity'] for layer in layers]
    final_sync = [critical_points[layer]['final_sync_order'] for layer in layers]
    
    ax6.scatter(final_lz, final_sync, s=100, alpha=0.7, c=range(len(layers)), cmap='viridis')
    for i, layer in enumerate(layers):
        ax6.annotate(layer.replace('_', ' ').title(), (final_lz[i], final_sync[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax6.set_xlabel('Final LZ Complexity')
    ax6.set_ylabel('Final Sync Order')
    ax6.set_title('Information-Order Phase Space')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('neural_resonance_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved as: neural_resonance_analysis.png")

if __name__ == "__main__":
    main()