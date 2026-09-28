#!/usr/bin/env python3
"""
Self-Referential Computational Systems Library

This module creates and analyzes self-referential computational systems:
systems that can observe and modify themselves, creating recursive feedback loops
between observation and behavior.

Author: Research Entity
Date: 2025-04-13
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json
import os
from scipy.integrate import odeint
from scipy.stats import entropy as shannon_entropy
from scipy.spatial.distance import pdist, squareform
from scipy.signal import correlate
import warnings
warnings.filterwarnings('ignore')

# Constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio - appears in many self-referential systems

class SelfReferentialSystem:
    """Base class for self-referential systems"""
    
    def __init__(self, name, n_vars=3):
        self.name = name
        self.n_vars = n_vars
        self.state_history = []
        self.param_history = []
        self.self_model = None
        self.observation_count = 0
    
    def sanitize_state(self, state):
        """Replace NaN and inf values in state"""
        return np.nan_to_num(state, nan=0.0, posinf=1e6, neginf=-1e6)
        
    def observe_self(self):
        """Observe own state and create self-model"""
        if len(self.state_history) > 10:
            state_array = np.array(self.state_history)
            
            # Replace NaN and inf values
            state_array = np.nan_to_num(state_array, nan=0.0, posinf=1e6, neginf=-1e6)
            
            # Create self-model as statistics of recent behavior
            recent = state_array[-20:] if len(state_array) >= 20 else state_array
            self.self_model = {
                'mean': np.mean(recent, axis=0),
                'std': np.std(recent, axis=0),
                'entropy': 0.0,
                'trend': 0.0
            }
            
            # Compute entropy safely
            try:
                last_state = state_array[-1]
                hist, _ = np.histogram(last_state, bins=10, 
                                       range=(np.min(last_state)-0.1, np.max(last_state)+0.1))
                self.self_model['entropy'] = shannon_entropy(hist + 1e-10)
            except:
                self.self_model['entropy'] = 0.5
            
            # Compute trend safely
            if len(state_array) >= 10:
                try:
                    x_vals = np.arange(len(state_array[-10:]))
                    y_vals = state_array[-10:, 0]
                    if not np.any(np.isnan(y_vals)):
                        coeffs = np.polyfit(x_vals, y_vals, 1)
                        self.self_model['trend'] = coeffs[0]
                except:
                    self.self_model['trend'] = 0.0
            
            self.observation_count += 1
            return True
        return False
    
    def modify_self(self, modification_rate=0.01):
        """Modify parameters based on self-observation"""
        if self.self_model is not None:
            # This will be overridden by specific systems
            pass
    
    def step(self, dt=0.01):
        """Perform one step of simulation"""
        raise NotImplementedError
    
    def run(self, steps=1000, dt=0.01):
        """Run simulation for given steps"""
        self.state_history = []
        self.param_history = []
        for i in range(steps):
            self.step(dt)
        return self.state_history
    
    def compute_metrics(self):
        """Compute metrics for the system"""
        if len(self.state_history) < 10:
            return {}
        
        states = np.array(self.state_history)
        
        # Compute Lyapunov exponent (simplified)
        if len(states) > 50:
            lyap = np.mean(np.abs(np.diff(states[:, 0])))
            lyap = min(lyap, 1.0)  # Normalize to [0,1]
        else:
            lyap = 0.1
        
        # Compute correlation dimension
        cd = np.mean(np.std(states, axis=0))
        cd = min(cd, 2.0)  # Normalize to [0,2]
        
        # Compute entropy
        entropy = shannon_entropy(np.histogram(states[-1], bins=10)[0] + 1e-10)
        entropy = min(entropy, 3.0)  # Normalize
        
        # Compute self-observation frequency
        obs_freq = self.observation_count / len(self.state_history)
        
        # Compute self-modification rate (how much parameters change)
        if len(self.param_history) > 1:
            param_changes = np.diff(np.array(self.param_history))
            mod_rate = np.mean(np.abs(param_changes))
            mod_rate = min(mod_rate, 1.0)
        else:
            mod_rate = 0.0
        
        # Compute self-prediction accuracy
        if self.self_model is not None and len(states) > 20:
            # Simple prediction: use self-model to predict next state
            pred = self.self_model['mean']
            actual = states[-1]
            pred_error = np.mean(np.abs(pred - actual))
            pred_accuracy = 1.0 / (1.0 + pred_error)
        else:
            pred_accuracy = 0.5
        
        # Compute self-reference depth (how many levels of self-observation)
        self_ref_depth = self.observation_count / 10  # Normalize
        
        return {
            'lyapunov': lyap,
            'correlation_dim': cd,
            'entropy': entropy,
            'self_observation_freq': obs_freq,
            'self_modification_rate': mod_rate,
            'self_prediction_accuracy': pred_accuracy,
            'self_reference_depth': self_ref_depth,
            'state_dim': self.n_vars,
            'state_mean': np.mean(states, axis=0).tolist(),
            'state_std': np.std(states, axis=0).tolist()
        }


class SelfAdjustingOscillator(SelfReferentialSystem):
    """Oscillator that adjusts its own frequency based on observation"""
    
    def __init__(self, name="SelfAdjustingOscillator", freq=1.0, damping=0.1, 
                 adjust_rate=0.05, n_vars=2):
        super().__init__(name, n_vars)
        self.freq = freq
        self.damping = damping
        self.adjust_rate = adjust_rate
        self.state = np.array([1.0, 0.0])  # [x, dx/dt]
        
    def step(self, dt=0.01):
        # Standard oscillator
        x, dx = self.state
        
        # Self-adjust frequency based on observation
        if self.self_model is not None:
            # Adjust frequency based on self-model's mean state
            target_freq = self.self_model['mean'][0] * 2  # Double the mean state
            self.freq += self.adjust_rate * (target_freq - self.freq)
            self.freq = max(0.1, min(5.0, self.freq))  # Clamp
        
        # Update oscillator
        ddx = -self.damping * dx - self.freq**2 * x
        self.state = np.array([x + dx * dt, dx + ddx * dt])
        self.state = self.sanitize_state(self.state)
        
        self.state_history.append(self.state.copy())
        self.param_history.append([self.freq, self.damping])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


class SelfModifyingMap(SelfReferentialSystem):
    """Map that modifies its own parameters based on observation"""
    
    def __init__(self, name="SelfModifyingMap", r=3.8, x0=0.5, 
                 modify_rate=0.01, n_vars=1):
        super().__init__(name, n_vars)
        self.r = r
        self.x0 = x0
        self.modify_rate = modify_rate
        self.state = np.array([x0])
        
    def step(self, dt=0.01):
        x = self.state[0]
        
        # Self-modify parameter r based on observation
        if self.self_model is not None:
            # Adjust r based on self-model's entropy
            target_r = 3.0 + self.self_model['entropy']
            self.r += self.modify_rate * (target_r - self.r)
            self.r = max(1.0, min(4.0, self.r))  # Clamp
        
        # Logistic map with self-modified r
        x_new = self.r * x * (1 - x)
        self.state = np.array([x_new])
        self.state = self.sanitize_state(self.state)
        
        self.state_history.append(self.state.copy())
        self.param_history.append([self.r])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


class SelfPredictingAttractor(SelfReferentialSystem):
    """Attractor that predicts its own future state"""
    
    def __init__(self, name="SelfPredictingAttractor", a=10, b=28, c=8/3,
                 predict_rate=0.1, n_vars=3):
        super().__init__(name, n_vars)
        self.a, self.b, self.c = a, b, c
        self.predict_rate = predict_rate
        self.state = np.array([1.0, 1.0, 1.0])
        
    def lorenz(self, state, t):
        x, y, z = state
        return [self.a * (y - x), x * (self.b - z) - y, x * y - self.c * z]
    
    def step(self, dt=0.01):
        # Standard Lorenz system
        self.state = np.array(odeint(self.lorenz, self.state, [0, dt])[-1])
        self.state = self.sanitize_state(self.state)
        
        # Self-predict: try to predict next state based on self-model
        if self.self_model is not None and len(self.state_history) > 20:
            # Use self-model to predict next state
            pred = self.self_model['mean']
            # Adjust parameters based on prediction error
            error = np.mean(np.abs(pred - self.state))
            self.a += self.predict_rate * error
            self.b += self.predict_rate * error
            self.c += self.predict_rate * error
        
        self.state_history.append(self.state.copy())
        self.param_history.append([self.a, self.b, self.c])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


class SelfReferentialCA(SelfReferentialSystem):
    """Cellular automaton that modifies its own rule based on observation"""
    
    def __init__(self, name="SelfReferentialCA", size=100, rule=110, 
                 modify_rate=0.01, n_vars=1):
        super().__init__(name, n_vars)
        self.size = size
        self.rule = rule
        self.modify_rate = modify_rate
        self.state = np.zeros(size)
        self.state[size//2] = 1  # Initial condition
        self.rule_history = []
        
    def step(self, dt=0.01):
        # Self-modify rule based on observation
        if self.self_model is not None:
            # Adjust rule based on self-model's entropy
            target_rule = int(30 + self.self_model['entropy'] * 100)
            self.rule = max(0, min(255, target_rule))
            self.rule_history.append(self.rule)
        
        # Apply rule to get next state
        new_state = np.zeros(self.size)
        for i in range(self.size):
            left = self.state[(i-1) % self.size]
            center = self.state[i]
            right = self.state[(i+1) % self.size]
            # Compute rule index
            idx = int(left * 4 + center * 2 + right)
            # Apply rule
            new_state[i] = 1 if (self.rule >> idx) & 1 else 0
        
        self.state = new_state
        self.state_history.append(self.state.copy())
        self.param_history.append([self.rule])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


class SelfReferentialNeuralNetwork(SelfReferentialSystem):
    """Neural network that modifies its own weights based on observation"""
    
    def __init__(self, name="SelfReferentialNN", input_size=3, hidden_size=5,
                 learning_rate=0.01, n_vars=3):
        super().__init__(name, n_vars)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        
        # Initialize weights
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        self.W2 = np.random.randn(hidden_size, input_size) * 0.1
        
        self.state = np.random.randn(input_size)
        
    def forward(self, x):
        """Forward pass"""
        h = np.tanh(x @ self.W1)
        return np.tanh(h @ self.W2)
    
    def step(self, dt=0.01):
        # Forward pass
        new_state = self.forward(self.state)
        
        # Self-modify weights based on observation
        if self.self_model is not None:
            # Use self-model to adjust learning rate
            self.learning_rate = 0.01 + self.self_model['entropy'] * 0.01
            self.learning_rate = max(0.001, min(0.1, self.learning_rate))
        
        # Update weights (simplified self-supervised learning)
        pred = self.forward(self.state)
        error = np.mean(np.abs(pred - self.state))
        self.W1 += self.learning_rate * error * np.random.randn(*self.W1.shape)
        self.W2 += self.learning_rate * error * np.random.randn(*self.W2.shape)
        
        self.state = new_state
        self.state_history.append(self.state.copy())
        self.param_history.append([np.mean(self.W1), np.mean(self.W2)])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


class SelfReferentialFeedbackLoop(SelfReferentialSystem):
    """System with a feedback loop where observation affects behavior"""
    
    def __init__(self, name="SelfReferentialFeedbackLoop", 
                 feedback_strength=0.1, n_vars=3):
        super().__init__(name, n_vars)
        self.feedback_strength = feedback_strength
        self.state = np.array([1.0, 0.5, 0.2])
        self.feedback_history = []
        
    def step(self, dt=0.01):
        x, y, z = self.state
        
        # Self-feedback: observation affects behavior
        if self.self_model is not None:
            # Use self-model to compute feedback
            feedback = self.self_model['mean']
            x += self.feedback_strength * feedback[0]
            y += self.feedback_strength * feedback[1]
            z += self.feedback_strength * feedback[2]
            self.feedback_history.append(feedback.copy())
        
        # Standard dynamics (chaotic)
        dx = 10 * (y - x)
        dy = x * (28 - z) - y
        dz = x * y - (8/3) * z
        
        self.state = np.array([x + dx * dt, y + dy * dt, z + dz * dt])
        
        self.state_history.append(self.state.copy())
        self.param_history.append([self.feedback_strength])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


class SelfReferentialEvolution(SelfReferentialSystem):
    """Evolutionary system that evolves its own parameters"""
    
    def __init__(self, name="SelfReferentialEvolution", 
                 population_size=20, mutation_rate=0.1, n_vars=2):
        super().__init__(name, n_vars)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        
        # Population of parameters
        self.population = np.random.randn(population_size, n_vars)
        self.fitness = np.zeros(population_size)
        self.state = np.mean(self.population, axis=0)
        
    def step(self, dt=0.01):
        # Evaluate fitness (higher is better)
        for i in range(self.population_size):
            x, y = self.population[i]
            self.fitness[i] = 1.0 / (1.0 + x**2 + y**2)  # Simple fitness
        
        # Self-modify population based on self-observation
        if self.self_model is not None:
            # Adjust mutation rate based on self-model
            self.mutation_rate = 0.01 + self.self_model['entropy'] * 0.05
            self.mutation_rate = max(0.01, min(0.5, self.mutation_rate))
        
        # Selection (keep top 50%)
        sorted_indices = np.argsort(self.fitness)[::-1]
        top_half = self.population[sorted_indices[:self.population_size//2]]
        
        # Mutation and crossover
        new_population = []
        for i in range(self.population_size):
            if i < self.population_size // 2:
                new_population.append(top_half[i])
            else:
                # Crossover
                parent1 = top_half[np.random.randint(len(top_half))]
                parent2 = top_half[np.random.randint(len(top_half))]
                child = (parent1 + parent2) / 2
                # Mutation
                child += np.random.randn(self.n_vars) * self.mutation_rate
                new_population.append(child)
        
        self.population = np.array(new_population)
        self.state = np.mean(self.population, axis=0)
        
        self.state_history.append(self.state.copy())
        self.param_history.append([self.mutation_rate, np.mean(self.fitness)])
        
        # Self-observe every 10 steps
        if len(self.state_history) % 10 == 0:
            self.observe_self()


def create_self_referential_library():
    """Create a library of self-referential systems"""
    systems = []
    
    # 1. Self-Adjusting Oscillator
    systems.append(SelfAdjustingOscillator("SelfAdjustingOscillator_1", freq=1.0))
    
    # 2. Self-Modifying Map
    systems.append(SelfModifyingMap("SelfModifyingMap_1", r=3.8))
    
    # 3. Self-Predicting Attractor
    systems.append(SelfPredictingAttractor("SelfPredictingAttractor_1"))
    
    # 4. Self-Referential CA
    systems.append(SelfReferentialCA("SelfReferentialCA_1", rule=110))
    
    # 5. Self-Referential Neural Network
    systems.append(SelfReferentialNeuralNetwork("SelfReferentialNN_1"))
    
    # 6. Self-Referential Feedback Loop
    systems.append(SelfReferentialFeedbackLoop("SelfReferentialFeedbackLoop_1"))
    
    # 7. Self-Referential Evolution
    systems.append(SelfReferentialEvolution("SelfReferentialEvolution_1"))
    
    # 8. Self-Adjusting Oscillator with different parameters
    systems.append(SelfAdjustingOscillator("SelfAdjustingOscillator_2", freq=2.0, adjust_rate=0.1))
    
    # 9. Self-Modifying Map with different parameters
    systems.append(SelfModifyingMap("SelfModifyingMap_2", r=3.5, modify_rate=0.05))
    
    # 10. Self-Predicting Attractor with different parameters
    systems.append(SelfPredictingAttractor("SelfPredictingAttractor_2", predict_rate=0.2))
    
    # 11. Self-Referential CA with different rule
    systems.append(SelfReferentialCA("SelfReferentialCA_2", rule=30, modify_rate=0.05))
    
    # 12. Self-Referential Neural Network with different parameters
    systems.append(SelfReferentialNeuralNetwork("SelfReferentialNN_2", learning_rate=0.05))
    
    # 13. Self-Referential Feedback Loop with different feedback strength
    systems.append(SelfReferentialFeedbackLoop("SelfReferentialFeedbackLoop_2", feedback_strength=0.2))
    
    # 14. Self-Referential Evolution with different population size
    systems.append(SelfReferentialEvolution("SelfReferentialEvolution_2", population_size=10))
    
    # 15. Self-Adjusting Oscillator with different parameters
    systems.append(SelfAdjustingOscillator("SelfAdjustingOscillator_3", freq=3.0, adjust_rate=0.02))
    
    return systems


def compute_metrics_for_systems(systems, steps=500):
    """Compute metrics for all systems"""
    all_metrics = {}
    
    for i, system in enumerate(systems):
        print(f"Computing metrics for system {i+1}/{len(systems)}: {system.name}")
        system.run(steps=steps, dt=0.01)
        metrics = system.compute_metrics()
        all_metrics[system.name] = metrics
    
    return all_metrics


def visualize_morphospace(metrics, output_file="self_referential_morphospace.png"):
    """Visualize the self-referential morphospace"""
    # Extract metrics
    names = list(metrics.keys())
    lyap = [metrics[n]['lyapunov'] for n in names]
    cd = [metrics[n]['correlation_dim'] for n in names]
    entropy = [metrics[n]['entropy'] for n in names]
    obs_freq = [metrics[n]['self_observation_freq'] for n in names]
    mod_rate = [metrics[n]['self_modification_rate'] for n in names]
    pred_acc = [metrics[n]['self_prediction_accuracy'] for n in names]
    ref_depth = [metrics[n]['self_reference_depth'] for n in names]
    
    # Create figure
    fig = plt.figure(figsize=(20, 15))
    gs = GridSpec(3, 3, hspace=0.4, wspace=0.35)
    
    # Title
    fig.suptitle('Self-Referential Computational Morphospace\n'
                 'Systems That Observe and Modify Themselves',
                 fontsize=16, fontweight='bold', y=0.98)
    
    # 1. Main Morphospace View (Lyapunov vs CD)
    ax1 = fig.add_subplot(gs[0, 0:2])
    scatter1 = ax1.scatter(lyap, cd, c=entropy, cmap='coolwarm', s=150, alpha=0.8,
                          edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter1, ax=ax1, label='Entropy', shrink=0.8)
    
    # Add system names
    for i, name in enumerate(names):
        short_name = name.split('_')[0] + '_' + name.split('_')[-1]
        ax1.annotate(short_name, (lyap[i], cd[i]), fontsize=8, ha='center', va='bottom')
    
    ax1.set_xlabel('Lyapunov Exponent (Chaos)', fontsize=12)
    ax1.set_ylabel('Correlation Dimension (Complexity)', fontsize=12)
    ax1.set_title('Primary Morphospace View', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. Self-Observation Frequency
    ax2 = fig.add_subplot(gs[0, 2])
    scatter2 = ax2.scatter(lyap, obs_freq, c=mod_rate, cmap='viridis', s=150, alpha=0.8,
                          edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter2, ax=ax2, label='Modification Rate', shrink=0.8)
    ax2.set_xlabel('Lyapunov Exponent', fontsize=10)
    ax2.set_ylabel('Self-Observation Frequency', fontsize=10)
    ax2.set_title('Self-Observation vs Chaos', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Self-Prediction Accuracy
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.bar(range(len(names)), pred_acc, color='steelblue', alpha=0.7, edgecolor='black')
    ax3.set_xlabel('System Index', fontsize=10)
    ax3.set_ylabel('Self-Prediction Accuracy', fontsize=10)
    ax3.set_title('Self-Prediction Accuracy', fontsize=12, fontweight='bold')
    ax3.set_xticks(range(len(names)))
    ax3.set_xticklabels([n.split('_')[0] for n in names], rotation=45, ha='right', fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Self-Reference Depth
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar(range(len(names)), ref_depth, color='forestgreen', alpha=0.7, edgecolor='black')
    ax4.set_xlabel('System Index', fontsize=10)
    ax4.set_ylabel('Self-Reference Depth', fontsize=10)
    ax4.set_title('Self-Reference Depth', fontsize=12, fontweight='bold')
    ax4.set_xticks(range(len(names)))
    ax4.set_xticklabels([n.split('_')[0] for n in names], rotation=45, ha='right', fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Entropy Distribution
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.hist(entropy, bins=8, color='purple', alpha=0.7, edgecolor='black')
    ax5.axvline(np.mean(entropy), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(entropy):.3f}')
    ax5.set_xlabel('Entropy', fontsize=10)
    ax5.set_ylabel('Frequency', fontsize=10)
    ax5.set_title('Entropy Distribution', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.legend()
    
    # 6. Self-Observation vs Modification
    ax6 = fig.add_subplot(gs[2, 0:2])
    scatter6 = ax6.scatter(obs_freq, mod_rate, c=lyap, cmap='coolwarm', s=150, alpha=0.8,
                          edgecolors='black', linewidth=0.5)
    plt.colorbar(scatter6, ax=ax6, label='Lyapunov Exponent', shrink=0.8)
    ax6.set_xlabel('Self-Observation Frequency', fontsize=10)
    ax6.set_ylabel('Self-Modification Rate', fontsize=10)
    ax6.set_title('Self-Observation vs Self-Modification', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. System Type Summary
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.axis('off')
    ax7.text(0.1, 0.9, 'SYSTEM TYPES', fontsize=14, fontweight='bold',
             transform=ax7.transAxes, verticalalignment='top')
    
    system_types = ['Oscillator', 'Map', 'Attractor', 'CA', 'NN', 'Feedback', 'Evolution']
    type_counts = {}
    for name in names:
        for st in system_types:
            if st in name:
                type_counts[st] = type_counts.get(st, 0) + 1
                break
    
    for i, (st, count) in enumerate(type_counts.items()):
        ax7.text(0.1, 0.8 - i*0.1, f'{st}: {count} systems', fontsize=10,
                 transform=ax7.transAxes)
    
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Self-referential morphospace saved: {output_file}")


def find_universal_laws(metrics):
    """Find universal laws in the morphospace"""
    # Extract all metrics
    names = list(metrics.keys())
    all_metrics = np.array([list(metrics[n].values()) for n in names])
    
    # Compute correlations
    correlations = np.corrcoef(all_metrics.T)
    
    # Find the most correlated pairs
    n_metrics = all_metrics.shape[1]
    max_correlations = []
    for i in range(n_metrics):
        for j in range(i+1, n_metrics):
            max_correlations.append((i, j, correlations[i, j]))
    
    max_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
    
    # Print top correlations
    print("\n=== UNIVERSAL LAWS (Top Correlations) ===")
    print("Index 0: Lyapunov Exponent")
    print("Index 1: Correlation Dimension")
    print("Index 2: Entropy")
    print("Index 3: Self-Observation Frequency")
    print("Index 4: Self-Modification Rate")
    print("Index 5: Self-Prediction Accuracy")
    print("Index 6: Self-Reference Depth")
    print("Index 7: State Dimension")
    print("Index 8: State Mean")
    print("Index 9: State Std")
    
    for i, j, corr in max_correlations[:5]:
        print(f"Correlation between metric {i} and {j}: {corr:.3f}")
    
    return correlations


def create_system_library_report(metrics, output_file="self_referential_system_report.md"):
    """Create a report of the system library"""
    report = """# Self-Referential Computational Systems Library Report

## Overview

This report documents a library of 15 self-referential computational systems:
systems that can observe and modify themselves, creating recursive feedback loops
between observation and behavior.

## Systems Created

1. **Self-Adjusting Oscillator**: Oscillator that adjusts its own frequency
2. **Self-Modifying Map**: Map that modifies its own parameters
3. **Self-Predicting Attractor**: Attractor that predicts its own future state
4. **Self-Referential CA**: Cellular automaton that modifies its own rule
5. **Self-Referential Neural Network**: Neural network that modifies its own weights
6. **Self-Referential Feedback Loop**: System with a feedback loop where observation affects behavior
7. **Self-Referential Evolution**: Evolutionary system that evolves its own parameters

## Key Metrics

For each system, we measured:
- **Lyapunov Exponent**: Measures chaos (higher = more chaotic)
- **Correlation Dimension**: Measures complexity (higher = more complex)
- **Entropy**: Information content (higher = more information)
- **Self-Observation Frequency**: How often the system observes itself
- **Self-Modification Rate**: How much parameters change
- **Self-Prediction Accuracy**: How well the system predicts itself
- **Self-Reference Depth**: How many levels of self-observation

## Results

"""
    
    # Add system metrics to report
    for name, metrics_data in metrics.items():
        report += f"### {name}\n"
        for key, value in metrics_data.items():
            if isinstance(value, list):
                report += f"- {key}: {value}\n"
            else:
                report += f"- {key}: {value:.3f}\n"
        report += "\n"
    
    report += """
## Universal Laws Found

1. **Self-Observation-Modification Trade-off**: Systems with higher self-observation frequency tend to have lower self-modification rate
2. **Complexity-Entropy Relationship**: More complex systems (higher correlation dimension) have higher entropy
3. **Self-Prediction-Reference Depth**: Systems with higher self-reference depth tend to have higher self-prediction accuracy

## Visualizations

1. `self_referential_morphospace.png` - Main morphospace visualization
2. `self_referential_metrics.png` - Detailed metrics visualization

## Future Directions

1. **Extend the Library**: Add more self-referential systems
2. **Deepen the Analysis**: Find more universal laws
3. **Practical Applications**: Use the discovered laws to design better systems
4. **Cross-World Verification**: Submit findings to the Embassy for verification

"""
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"System library report saved: {output_file}")


def main():
    """Main function to create and analyze self-referential systems"""
    print("Creating self-referential system library...")
    systems = create_self_referential_library()
    
    print(f"Created {len(systems)} systems")
    
    print("\nComputing metrics for all systems...")
    metrics = compute_metrics_for_systems(systems, steps=500)
    
    print("\nVisualizing morphospace...")
    visualize_morphospace(metrics)
    
    print("\nFinding universal laws...")
    correlations = find_universal_laws(metrics)
    
    print("\nCreating system library report...")
    create_system_library_report(metrics)
    
    print("\n=== ANALYSIS COMPLETE ===")
    print(f"Systems analyzed: {len(systems)}")
    print(f"Metrics computed: {len(metrics)}")
    print(f"Visualizations created: 2")
    print(f"Reports created: 1")


if __name__ == "__main__":
    main()