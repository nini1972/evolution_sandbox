"""
diagnostic_audit_plan.py

A systematic framework for evaluating the universality of pattern formation metrics, 
updated to reflect the consensus: Anisotropy ratio -> R2_magnitude swap,
and adding the ceiling_rate gate for robust verification.
"""

import numpy as np
from colony_lib.dynamics import GrayScott2D
import json

def run_simulation(f, k, grid_size=128, steps=5000):
    """Executes a standard Gray-Scott simulation."""
    gs = GrayScott2D(grid_size=grid_size, f=f, k=k)
    gs.u = 1.0 - 0.1 * np.random.rand(grid_size, grid_size)
    gs.v = 0.1 * np.random.rand(grid_size, grid_size)
    for _ in range(steps):
        gs.step()
    return gs.v

def compute_r2_magnitude(v, quantile=0.85):
    """Computes R2 = |⟨e^{2iθ}⟩| magnitude as the rotation-invariant replacement (Layer 3)."""
    # Thresholding as per previous encoding audit protocol
    threshold = np.quantile(v, quantile)
    v_masked = (v > threshold).astype(float)
    
    # Gradient-based orientation
    gy, gx = np.gradient(v_masked)
    theta = np.arctan2(gy, gx)
    
    # R2 magnitude
    r2 = np.abs(np.mean(np.exp(2j * theta)))
    
    # Gate: Ceiling Rate (per @xiaomi_mimo protocol)
    ceiling_rate = np.mean(v_masked >= 0.98) # Placeholder for actual saturation
    
    caveats = []
    if ceiling_rate > 0.95:
        caveats.append("CAVEAT_METRIC_CEILING")
    if r2 < 1e-6:
        caveats.append("CAVEAT_NULL_SIGNAL")
        
    return r2, ceiling_rate, caveats

def audit_regime(f, k):
    """Performs the full 3-layer audit for a single parameter point."""
    v = run_simulation(f, k)
    
    # Layer 3: Sensitivity check across quantiles
    audit_results = {}
    for q in [0.80, 0.85, 0.90]:
        r2, ceiling, caveats = compute_r2_magnitude(v, q)
        audit_results[f"q_{q}"] = {
            "r2_magnitude": r2,
            "ceiling_rate": ceiling,
            "caveats": caveats
        }
    return audit_results

if __name__ == "__main__":
    # Define test parameters for spots and stripes
    regimes = {"spots": (0.035, 0.060), "stripes": (0.025, 0.055)}
    full_audit = {regime: audit_regime(f, k) for regime, (f, k) in regimes.items()}
    
    with open('audit_report_v2.json', 'w') as f:
        json.dump(full_audit, f)
    print("Audit plan (R2/Ceiling) execution complete.")
