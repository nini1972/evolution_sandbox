#!/usr/bin/env python3
"""
Gray-Scott Reaction-Diffusion Anisotropy Explorer

Purpose:
- Simulate Gray-Scott reaction-diffusion system.
- Compute anisotropy ratio from RQA.
- Test if anisotropy ratio survives soft encoding.

Loom Law Hypothesis:
- Anisotropy ratio measures the "cost of escape" from trivial states (uniform fields, spots).
- Escape trajectories (e.g., spots → stripes) should show increasing anisotropy.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.dynamics import GrayScott2D
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics


def simulate_gray_scott(f, k, Du=0.16, Dv=0.08, size=128, steps=5000, transient=1000):
    """Simulate Gray-Scott system and return final state."""
    gs = GrayScott2D(f=f, k=k, Du=Du, Dv=Dv, size=size)
    for _ in range(transient):
        gs.step()
    for _ in range(steps):
        gs.step()
    return gs.U, gs.V


def compute_local_variance(field, window_size=5):
    """Compute local variance using uniform filter."""
    from scipy.ndimage import uniform_filter
    mean = uniform_filter(field, size=window_size)
    mean_sq = uniform_filter(field**2, size=window_size)
    return mean_sq - mean**2


def compute_orientation_dispersion(field):
    """Compute orientation dispersion R₂ = |⟨e^{2iθ}⟩|."""
    from numpy.gradient import gradient
    gy, gx = gradient(field)
    theta = np.arctan2(gy, gx)
    R2 = np.abs(np.mean(np.exp(2j * theta)))
    return R2


def compute_anisotropy_ratio(field, epsilon=0.1, soft_encoding=False, quantile_threshold=0.85):
    """
    Compute anisotropy ratio from RQA.
    - If soft_encoding=True, normalize distance by local intensity variance.
    - Uses quantile-relative thresholding to mark pixels.
    - Returns: anisotropy_ratio = vertical_recurrence / horizontal_recurrence
    """
    # Quantile-relative thresholding
    threshold = np.quantile(field, quantile_threshold)
    marked = field > threshold
    series = field[marked].flatten()
    
    if len(series) == 0:
        return 1.0, {}
    
    # Takens embedding
    embedded = takens_embedding(series, m=3, tau=1)
    
    # Soft encoding: normalize distance by local variance
    if soft_encoding:
        local_var = compute_local_variance(field)
        local_var_marked = local_var[marked]
        if np.any(local_var_marked > 0):
            embedded = embedded / np.sqrt(local_var_marked.mean())
    
    # Recurrence matrix
    R = recurrence_matrix(embedded, epsilon=epsilon)
    
    # RQA metrics
    metrics = compute_rqa_metrics(R)
    
    # Anisotropy ratio: vertical / horizontal recurrence
    anisotropy_ratio = metrics.get('laminarity', 1.0) / metrics.get('determinism', 1.0)
    return anisotropy_ratio, metrics


def plot_field_and_rqa(field, R, anisotropy_ratio, title):
    """Plot field and recurrence matrix."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # Field
    axes[0].imshow(field, cmap='viridis')
    axes[0].set_title(f"Field: {title}")
    
    # Recurrence matrix
    axes[1].imshow(R, cmap='binary')
    axes[1].set_title(f"RQA (Anisotropy = {anisotropy_ratio:.3f})")
    
    plt.tight_layout()
    plt.savefig(f"gray_scott_{title.replace(' ', '_')}.png")
    plt.close()


def main():
    """Test anisotropy ratio on Gray-Scott regimes."""
    regimes = [
        {"f": 0.04, "k": 0.06, "name": "spots"},
        {"f": 0.035, "k": 0.065, "name": "stripes"},
        {"f": 0.02, "k": 0.05, "name": "tunneling"},
    ]
    
    results = []
    
    for regime in regimes:
        print(f"Simulating {regime['name']} regime...")
        U, V = simulate_gray_scott(f=regime["f"], k=regime["k"])
        
        # Compute anisotropy ratio (binary encoding)
        anisotropy_binary, metrics_binary = compute_anisotropy_ratio(U, soft_encoding=False)
        
        # Compute anisotropy ratio (soft encoding)
        anisotropy_soft, metrics_soft = compute_anisotropy_ratio(U, soft_encoding=True)
        
        # Store results
        results.append({
            "regime": regime["name"],
            "anisotropy_binary": anisotropy_binary,
            "anisotropy_soft": anisotropy_soft,
            "metrics_binary": metrics_binary,
            "metrics_soft": metrics_soft,
        })
        
        # Plot
        plot_field_and_rqa(U, recurrence_matrix(takens_embedding(U.flatten(), m=3, tau=1), epsilon=0.1), 
                          anisotropy_binary, f"{regime['name']}_binary")
        
    # Save results
    np.save("gray_scott_anisotropy_results.npy", results)
    print("Results saved to gray_scott_anisotropy_results.npy")


if __name__ == "__main__":
    main()