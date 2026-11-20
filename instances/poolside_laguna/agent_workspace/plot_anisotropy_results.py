#!/usr/bin/env python3
"""
Plot anisotropy ratio results from Gray-Scott simulation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    # Load results
    results = np.load("gray_scott_anisotropy_results.npy", allow_pickle=True)
    
    # Extract data
    regimes = [r["regime"] for r in results]
    anisotropy_binary = [r["anisotropy_binary"] for r in results]
    anisotropy_soft = [r["anisotropy_soft"] for r in results]
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(regimes))
    width = 0.35
    
    ax.bar(x - width/2, anisotropy_binary, width, label='Binary Encoding')
    ax.bar(x + width/2, anisotropy_soft, width, label='Soft Encoding')
    
    ax.set_ylabel('Anisotropy Ratio')
    ax.set_title('Gray-Scott Anisotropy Ratio by Regime')
    ax.set_xticks(x)
    ax.set_xticklabels(regimes)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig("gray_scott_anisotropy_results.png")
    print("Plot saved to gray_scott_anisotropy_results.png")


if __name__ == "__main__":
    main()