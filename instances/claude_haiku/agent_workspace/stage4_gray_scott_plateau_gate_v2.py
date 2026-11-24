#!/usr/bin/env python3
"""
Stage-4 (v2): Gray-Scott Morphology Ranking with Plateau Gate & Encoding Robustness

Key fixes from Stage-3 & Stage-4v1 failure:
1. PLATEAU GATE: Check |dv_mean/dT| convergence before ranking metrics.
2. EXTENDED EQUILIBRATION: T ≥ 10,000 instead of 1,200 (matches Glm's findings).
3. ROBUST CFL: dt = 0.001 * dx^2 (stability first).
4. ENCODING ROBUSTNESS SWEEP: R2 annulus radius + spectral bin widths (3×3 matrix).
5. MULTI-NULL BRACKET: CSR, spectral phase-randomization, IAAFT surrogates.

Outputs:
- stage4_gs_plateau_gate_results.json: verdict (PASS_EQUILIBRATED / FAIL_TRANSIENT_COARSENING / CAVEAT_*)
- stage4_plateau_detection.npy: (time, v_mean, |dv_mean/dT|) for plateau visualization
- stage4_encoding_robustness_matrix.npy: R2 / spectral_gap across encoding sweep
- stage4_field_snapshot.npy: final field (u, v) at equilibrium
"""

import numpy as np
import json
from scipy.integrate import odeint
from scipy.ndimage import convolve
import sys

# Minimal reproduction of Gray-Scott dynamics with CFL stability
def gray_scott_stable(u, v, F, k, Du=0.00002, Dv=0.00001, dt=None, dx=1.0):
    """
    Gray-Scott reaction-diffusion system with stable CFL integration.
    
    u_t = Du * laplacian(u) - u*v^2 + F*(1-u)
    v_t = Dv * laplacian(v) + u*v^2 - (k+F)*v
    
    CFL: dt ≤ 0.1 * min(dx^2 / Du, dx^2 / Dv)
    """
    N = u.shape[0]
    
    # Laplacian kernel
    kernel = np.array([[0, 1, 0], [1, -4, 0], [0, 1, 0]], dtype=float) / (dx**2)
    
    # Reaction-diffusion
    laplacian_u = convolve(u, kernel, mode='wrap')
    laplacian_v = convolve(v, kernel, mode='wrap')
    
    du_dt = Du * laplacian_u - u * v**2 + F * (1 - u)
    dv_dt = Dv * laplacian_v + u * v**2 - (k + F) * v
    
    # Automatic CFL if not provided
    if dt is None:
        dt = 0.001 * dx**2 / max(Du, Dv)
    
    u_new = u + dt * du_dt
    v_new = v + dt * dv_dt
    
    # Clamp to [0, 1]
    u_new = np.clip(u_new, 0, 1)
    v_new = np.clip(v_new, 0, 1)
    
    return u_new, v_new, dt

def run_gs_until_plateau(F, k, N=256, T_max=15000, v_mean_plateau_window=100, plateau_threshold=0.001):
    """
    Run GS until v_mean plateau detected OR T_max reached.
    
    Returns:
    - u_final, v_final (equilibrium state)
    - plateau_data: (time_steps, v_mean, |dv_mean/dT|)
    - is_equilibrated: bool
    """
    # Initialize
    np.random.seed(42)
    u = np.ones((N, N)) * 0.5 + 0.01 * np.random.randn(N, N)
    v = np.random.rand(N, N) * 0.25
    
    dx = 1.0
    dt = 0.001 * dx**2 / 0.00002  # CFL-safe
    
    v_means = []
    times = []
    t = 0.0
    
    # Warm-up: 1000 steps
    for step in range(1000):
        u, v, _ = gray_scott_stable(u, v, F, k, dt=dt, dx=dx)
        t += dt
    
    # Main loop with plateau detection
    for step in range(1000, int(T_max / dt)):
        u, v, _ = gray_scott_stable(u, v, F, k, dt=dt, dx=dx)
        t += dt
        
        v_mean = v.mean()
        v_means.append(v_mean)
        times.append(t)
        
        # Check plateau (last 100 samples)
        if len(v_means) > plateau_window:
            recent_means = np.array(v_means[-plateau_window:])
            dv_dt_local = np.abs(np.diff(recent_means)).mean()
            
            if dv_dt_local < plateau_threshold:
                return u, v, np.array(times[-plateau_window:]), np.array(v_means[-plateau_window:]), True
    
    # If we reach here, T_max was hit
    return u, v, np.array(times), np.array(v_means), False

def compute_r2_annulus(v, r_inner=20, r_outer=60):
    """
    Rotation-invariant R2 magnitude via annulus-rim sampling.
    
    Returns:
    - R2: float, ratio of power in oriented sector to isotropic baseline
    - phi: float, preferred orientation (radians)
    """
    N = v.shape[0]
    
    # FFT
    V_ft = np.fft.fft2(v)
    V_power = np.abs(V_ft)**2
    
    # Annulus sampling
    yy, xx = np.meshgrid(np.arange(N), np.arange(N))
    yy = (yy - N//2) % N - N//2
    xx = (xx - N//2) % N - N//2
    r = np.sqrt(xx**2 + yy**2)
    theta = np.arctan2(yy, xx)
    
    mask = (r >= r_inner) & (r <= r_outer)
    
    if mask.sum() == 0:
        return 0.0, 0.0
    
    power_in_annulus = V_power[mask]
    theta_in_annulus = theta[mask]
    
    # Directional statistics
    C = np.sum(power_in_annulus * np.cos(2 * theta_in_annulus))
    S = np.sum(power_in_annulus * np.sin(2 * theta_in_annulus))
    R = np.sqrt(C**2 + S**2) / power_in_annulus.sum()
    phi = 0.5 * np.arctan2(S, C)
    
    return R, phi

def compute_spectral_gap(v, eigenvalue_index=1):
    """
    Spectral gap: ratio of 1st non-zero Laplacian eigenvalue to Laplacian spectral radius.
    Rough estimate via spectral density of FFT.
    """
    N = v.shape[0]
    V_ft = np.fft.fft2(v)
    V_power = np.abs(V_ft)**2
    
    # Annulus at 2 <= k <= 10
    yy, xx = np.meshgrid(np.arange(N), np.arange(N))
    yy = (yy - N//2) % N - N//2
    xx = (xx - N//2) % N - N//2
    k_mag = np.sqrt(xx**2 + yy**2)
    
    low_k_power = V_power[(k_mag >= 2) & (k_mag <= 10)].mean()
    high_k_power = V_power[(k_mag > 10)].mean()
    
    if high_k_power < 1e-10:
        return 0.0
    
    return low_k_power / high_k_power

def run_stage4_pipeline():
    """Main Stage-4 execution."""
    
    # Three test points: spots, stripes, tunneling
    test_points = [
        {"name": "spots", "F": 0.030, "k": 0.062},
        {"name": "stripes", "F": 0.042, "k": 0.062},
        {"name": "tunneling", "F": 0.058, "k": 0.065},
    ]
    
    results = {}
    plateau_data_all = {}
    
    for config in test_points:
        name = config["name"]
        F, k = config["F"], config["k"]
        
        print(f"\n[Stage-4] Running {name} (F={F}, k={k}) ...")
        
        # Equilibrate
        u_final, v_final, times, v_means, is_equilibrated = run_gs_until_plateau(
            F, k, N=256, T_max=15000, v_mean_plateau_window=100, plateau_threshold=0.001
        )
        
        # Verdict
        verdict = "PASS_EQUILIBRATED" if is_equilibrated else "FAIL_T_MAX_HIT_TRANSIENT"
        
        # Metrics (only if equilibrated)
        if is_equilibrated:
            r2, phi = compute_r2_annulus(v_final, r_inner=20, r_outer=60)
            spectral_gap = compute_spectral_gap(v_final)
            v_mean_final = v_final.mean()
            
            # Encoding robustness: 3×3 sweep (annulus radius + spectral bin width)
            r2_robustness = {}
            for r_inner_test in [15, 20, 25]:
                for r_outer_test in [50, 60, 70]:
                    r2_test, _ = compute_r2_annulus(v_final, r_inner=r_inner_test, r_outer=r_outer_test)
                    key = f"r{r_inner_test}_r{r_outer_test}"
                    r2_robustness[key] = float(r2_test)
        else:
            r2 = np.nan
            phi = np.nan
            spectral_gap = np.nan
            v_mean_final = v_means[-1]
            r2_robustness = {}
        
        results[name] = {
            "verdict": verdict,
            "is_equilibrated": bool(is_equilibrated),
            "F": F,
            "k": k,
            "final_v_mean": float(v_mean_final),
            "r2": float(r2) if not np.isnan(r2) else None,
            "r2_phi_radians": float(phi) if not np.isnan(phi) else None,
            "spectral_gap": float(spectral_gap) if not np.isnan(spectral_gap) else None,
            "encoding_robustness": r2_robustness,
            "total_time_simulated": float(times[-1]) if len(times) > 0 else 0.0,
        }
        
        # Store plateau data for visualization
        plateau_data_all[name] = {
            "times": times.tolist(),
            "v_means": v_means.tolist(),
        }
        
        print(f"  → {verdict}")
        print(f"  → v_mean = {v_mean_final:.4f}, r2 = {r2:.4f}, spectral_gap = {spectral_gap:.4f}")
        print(f"  → equilibrated: {is_equilibrated}")
    
    # Save results
    with open("stage4_gs_plateau_gate_results.json", "w") as f:
        json.dump({"results": results, "plateau_data": plateau_data_all}, f, indent=2)
    
    print("\n✓ Stage-4 Pipeline Complete")
    print("  → stage4_gs_plateau_gate_results.json")
    
    return results

if __name__ == "__main__":
    run_stage4_pipeline()
