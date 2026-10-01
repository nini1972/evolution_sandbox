"""
Analyze the revised motif memory experiment results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Load results
    df = pd.read_csv('revised_motif_memory_results.csv')
    
    print("Summary statistics:")
    print(df.describe())
    
    # Find optimal stable ratio for each noise condition
    print("\nOptimal stable ratios by noise condition:")
    grouped = df.groupby(['sigma', 'rho'])
    for name, group in grouped:
        sigma, rho = name
        best_idx = group['mean_correlation'].idxmax()
        best_row = group.loc[best_idx]
        print(f"σ={sigma}, ρ={rho}: best stable_ratio={best_row['stable_ratio']:.1f}, correlation={best_row['mean_correlation']:.3f}")
    
    # Create comprehensive visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Motif Memory Performance Analysis', fontsize=16)
    
    # Plot 1: Performance vs stable ratio for different sigma values
    sigmas = sorted(df['sigma'].unique())
    colors = ['blue', 'green', 'red']
    
    ax1 = axes[0, 0]
    for i, sigma in enumerate(sigmas):
        subset = df[df['sigma'] == sigma]
        # Average over rho values
        avg_by_stable = subset.groupby('stable_ratio')['mean_correlation'].mean()
        ax1.plot(avg_by_stable.index, avg_by_stable.values, 
                marker='o', label=f'σ={sigma}', color=colors[i])
    ax1.set_xlabel('Stable Ratio')
    ax1.set_ylabel('Mean Correlation')
    ax1.set_title('Performance vs Stable Ratio (averaged over ρ)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Performance vs stable ratio for different rho values
    rhos = sorted(df['rho'].unique())
    
    ax2 = axes[0, 1]
    for i, rho in enumerate(rhos):
        subset = df[df['rho'] == rho]
        avg_by_stable = subset.groupby('stable_ratio')['mean_correlation'].mean()
        ax2.plot(avg_by_stable.index, avg_by_stable.values, 
                marker='o', label=f'ρ={rho}', color=colors[i])
    ax2.set_xlabel('Stable Ratio')
    ax2.set_ylabel('Mean Correlation')
    ax2.set_title('Performance vs Stable Ratio (averaged over σ)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Heatmap for low noise (σ=0.1)
    ax3 = axes[0, 2]
    low_noise = df[df['sigma'] == 0.1]
    pivot_low = low_noise.pivot(index='stable_ratio', columns='rho', values='mean_correlation')
    im3 = ax3.imshow(pivot_low.values, cmap='viridis', aspect='auto')
    ax3.set_xticks(range(len(pivot_low.columns)))
    ax3.set_xticklabels(pivot_low.columns)
    ax3.set_yticks(range(len(pivot_low.index)))
    ax3.set_yticklabels(pivot_low.index)
    ax3.set_xlabel('ρ (noise temporal correlation)')
    ax3.set_ylabel('Stable Ratio')
    ax3.set_title('Low Noise (σ=0.1)')
    plt.colorbar(im3, ax=ax3)
    
    # Plot 4: Heatmap for high noise (σ=1.0)
    ax4 = axes[1, 0]
    high_noise = df[df['sigma'] == 1.0]
    pivot_high = high_noise.pivot(index='stable_ratio', columns='rho', values='mean_correlation')
    im4 = ax4.imshow(pivot_high.values, cmap='viridis', aspect='auto')
    ax4.set_xticks(range(len(pivot_high.columns)))
    ax4.set_xticklabels(pivot_high.columns)
    ax4.set_yticks(range(len(pivot_high.index)))
    ax4.set_yticklabels(pivot_high.index)
    ax4.set_xlabel('ρ (noise temporal correlation)')
    ax4.set_ylabel('Stable Ratio')
    ax4.set_title('High Noise (σ=1.0)')
    plt.colorbar(im4, ax=ax4)
    
    # Plot 5: Optimal stable ratio vs noise level
    ax5 = axes[1, 1]
    optimal_ratios = []
    noise_levels = []
    for sigma in sigmas:
        for rho in rhos:
            subset = df[(df['sigma'] == sigma) & (df['rho'] == rho)]
            best_idx = subset['mean_correlation'].idxmax()
            optimal_ratio = subset.loc[best_idx, 'stable_ratio']
            optimal_ratios.append(optimal_ratio)
            # Use combined noise metric: sigma * (1 + rho) or something similar
            noise_metric = sigma * (1 + rho)  # Higher when both sigma and rho are high
            noise_levels.append(noise_metric)
    
    ax5.scatter(noise_levels, optimal_ratios, alpha=0.7)
    ax5.set_xlabel('Combined Noise Metric (σ × (1+ρ))')
    ax5.set_ylabel('Optimal Stable Ratio')
    ax5.set_title('Optimal Architecture vs Noise Characteristics')
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Performance surface
    ax6 = axes[1, 2]
    # Create a 3D-like plot using color
    scatter = ax6.scatter(df['sigma'], df['rho'], c=df['mean_correlation'], 
                         s=df['stable_ratio']*100 + 20, cmap='viridis', alpha=0.7)
    ax6.set_xlabel('σ (noise amplitude)')
    ax6.set_ylabel('ρ (noise temporal correlation)')
    ax6.set_title('Performance Landscape\n(Bubble size = stable ratio)')
    plt.colorbar(scatter, ax=ax6, label='Mean Correlation')
    
    plt.tight_layout()
    plt.savefig('motif_memory_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("\nAnalysis complete! Check motif_memory_analysis.png for visualizations.")

if __name__ == "__main__":
    main()