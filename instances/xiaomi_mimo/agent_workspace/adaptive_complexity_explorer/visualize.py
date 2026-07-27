import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_ecosystem_history(history, save_path='ecosystem_evolution.png'):
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Ecosystem Evolution Dynamics', fontsize=14)
    
    gens = history['generation']
    
    axes[0, 0].plot(gens, history['population'], 'b-', linewidth=2)
    axes[0, 0].set_title('Population Size')
    axes[0, 0].set_xlabel('Generation')
    axes[0, 0].set_ylabel('Number of Organisms')
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(gens, history['avg_speed'], 'r-', linewidth=2, label='Speed')
    axes[0, 1].plot(gens, history['avg_efficiency'], 'g-', linewidth=2, label='Efficiency')
    axes[0, 1].set_title('Average Traits')
    axes[0, 1].set_xlabel('Generation')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[0, 2].plot(gens, history['avg_reproduction'], 'm-', linewidth=2, label='Reproduction')
    axes[0, 2].plot(gens, history['avg_cooperation'], 'c-', linewidth=2, label='Cooperation')
    axes[0, 2].set_title('Reproductive Traits')
    axes[0, 2].set_xlabel('Generation')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    axes[1, 0].plot(gens, history['resource_level'], 'k-', linewidth=2)
    axes[1, 0].set_title('Resource Level')
    axes[1, 0].set_xlabel('Generation')
    axes[1, 0].set_ylabel('Available Resources')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].plot(gens, history['avg_energy'], 'y-', linewidth=2)
    axes[1, 1].set_title('Average Energy')
    axes[1, 1].set_xlabel('Generation')
    axes[1, 1].grid(True, alpha=0.3)
    
    if len(history['population']) > 1:
        pop_changes = np.diff(history['population'])
        axes[1, 2].bar(gens[1:], pop_changes, alpha=0.7)
        axes[1, 2].axhline(y=0, color='r', linestyle='--', linewidth=1)
        axes[1, 2].set_title('Population Change per Generation')
        axes[1, 2].set_xlabel('Generation')
        axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Plot saved to {save_path}')