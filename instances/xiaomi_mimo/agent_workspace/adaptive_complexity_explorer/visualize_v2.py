import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_ecosystem_history(history, save_path='ecosystem_v2_evolution.png'):
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle('Competitive Ecosystem Evolution v2', fontsize=14)
    gens = history['generation']
    axes[0, 0].plot(gens, history['population'], 'b-', linewidth=2)
    axes[0, 0].set_title('Population Size')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 1].plot(gens, history['resource_level'], 'g-', linewidth=2)
    axes[0, 1].set_title('Resource Level')
    axes[0, 1].grid(True, alpha=0.3)
    for event in history.get('boom_events', []):
        axes[0, 1].axvline(x=event, color='green', alpha=0.3, linestyle='--')
    for event in history.get('extinction_events', []):
        axes[0, 1].axvline(x=event, color='red', alpha=0.3, linestyle='--')
    axes[0, 2].plot(gens, history['avg_speed'], 'r-', linewidth=2, label='Speed')
    axes[0, 2].plot(gens, history['avg_efficiency'], 'g-', linewidth=2, label='Efficiency')
    axes[0, 2].set_title('Key Traits')
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].grid(True, alpha=0.3)
    axes[1, 0].plot(gens, history['avg_reproduction'], 'm-', linewidth=2, label='Reproduction')
    axes[1, 0].plot(gens, history['avg_cooperation'], 'c-', linewidth=2, label='Cooperation')
    axes[1, 0].set_title('Social Traits')
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 1].plot(gens, history['avg_frugality'], color='orange', linewidth=2)
    axes[1, 1].set_title('Frugality Trait')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 2].plot(gens, history['avg_energy'], 'y-', linewidth=2)
    axes[1, 2].set_title('Average Energy')
    axes[1, 2].grid(True, alpha=0.3)
    if len(history['population']) > 1:
        pop_changes = np.diff(history['population'])
        colors = ['green' if x > 0 else 'red' for x in pop_changes]
        axes[2, 0].bar(gens[1:], pop_changes, color=colors, alpha=0.6, width=1.0)
        axes[2, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[2, 0].set_title('Population Change per Generation')
        axes[2, 0].grid(True, alpha=0.3)
    if len(history['avg_speed']) > 10:
        window = 10
        speed_var = np.convolve(np.diff(history['avg_speed']), np.ones(window)/window, mode='valid')
        axes[2, 1].plot(gens[window:], speed_var, 'purple', linewidth=2)
        axes[2, 1].set_title('Speed Trait Rate of Change')
        axes[2, 1].grid(True, alpha=0.3)
    trait_names = ['Speed', 'Efficiency', 'Reproduction', 'Cooperation', 'Frugality']
    traits_over_time = np.array([history['avg_speed'], history['avg_efficiency'], history['avg_reproduction'], history['avg_cooperation'], history['avg_frugality']])
    axes[2, 2].stackplot(gens, traits_over_time, labels=trait_names, alpha=0.8)
    axes[2, 2].legend(loc='upper left', fontsize=7)
    axes[2, 2].set_title('Trait Composition')
    axes[2, 2].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Plot saved to {save_path}')