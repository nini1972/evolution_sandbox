"""
R19Z Artifact Audit: Is the Resonance Island Real or a Transient Artifact?

Critical concern: gs_std ≈ 0 in the island length test suggests the GS system
reaches a trivial fixed point, making the "resonance" just noise correlation.

This script tests:
1. Does Gray-Scott actually form patterns on 12x12? (check gs_std over time)
2. Do patterns form on larger grids (24x24, 48x48)?
3. If patterns form, does the resonance island survive?
4. If no patterns, what's the actual signal we're measuring?
"""
import numpy as np, json
matplotlib_use = True
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_gs_only(f_val, k=0.062, Du=0.16, Dv=0.08, size=12, n_steps=5000, burn_in=2000):
    """Run GS alone and track complexity over time."""
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-2:size//2+2, size//2-2:size//2+2] = 0.25
    v[size//2-2:size//2+2, size//2-2:size//2+2] = 0.75
    comp_sig = np.zeros(n_steps)
    mv_sig = np.zeros(n_steps)
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        u = u + Du * u_lap - uv2 + f_val * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_val + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        if ti >= 0:
            comp_sig[ti] = np.std(v)
            mv_sig[ti] = np.mean(v)
    return comp_sig, mv_sig

# Test 1: Does GS form patterns on different grid sizes?
print("=== TEST 1: Pattern formation vs grid size ===")
f_test = 0.064
results_grid = {}
for size in [12, 24, 48]:
    comp, mv = run_gs_only(f_test, size=size, n_steps=5000, burn_in=2000)
    results_grid[size] = {
        'comp': comp,
        'mv': mv,
        'final_comp': float(comp[-1]),
        'mean_comp': float(np.mean(comp)),
        'std_comp': float(np.std(comp)),
    }
    print(f"  size={size}: final_comp={comp[-1]:.6f}, mean_comp={np.mean(comp):.6f}, std_comp={np.std(comp):.6f}")
    # Check if comp is actually varying
    if np.std(comp) < 1e-10:
        print(f"    -> NO PATTERN: complexity is constant at {comp[-1]:.8f}")
    else:
        print(f"    -> Pattern variability detected (std={np.std(comp):.8f})")

# Test 2: Check what the final v field looks like
print("\n=== TEST 2: Final v field values ===")
for size in [12, 24]:
    comp, mv = run_gs_only(0.064, size=size, n_steps=3000, burn_in=1000)
    # Run one more step to get the actual field
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-2:size//2+2, size//2-2:size//2+2] = 0.25
    v[size//2-2:size//2+2, size//2-2:size//2+2] = 0.75
    for t in range(4000):
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        u = u + 0.16 * u_lap - uv2 + 0.064 * (1 - u)
        v = v + 0.08 * v_lap + uv2 - (0.064 + 0.062) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
    print(f"  size={size}: v range=[{v.min():.8f}, {v.max():.8f}], u range=[{u.min():.8f}, {u.max():.8f}]")
    print(f"    v unique values: {len(np.unique(np.round(v, 6)))}")
    if v.max() < 1e-6:
        print(f"    -> v DIED: Gray-Scott reaches trivial fixed point (1, 0)")

# Test 3: Try different f values on larger grid to see if any form patterns
print("\n=== TEST 3: Pattern formation scan on 24x24 ===")
for f_val in [0.022, 0.030, 0.040, 0.050, 0.060, 0.064, 0.070, 0.080]:
    comp, mv = run_gs_only(f_val, size=24, n_steps=3000, burn_in=1000)
    print(f"  f={f_val:.3f}: final_comp={comp[-1]:.6f}, mean_v={mv[-1]:.6f}, std_comp={np.std(comp):.6f}")

# Test 4: The real question - if gs_std=0, what IS the cross-correlation measuring?
print("\n=== TEST 4: Signal characteristics when gs_std=0 ===")
# Run the coupled system and examine the actual signals
from r19z_deep_lib import run_gs_sandpile
for f_val in [0.064, 0.070, 0.076]:
    result = run_gs_sandpile(f_val, size=12, n_steps=2000, burn_in=800, N_gap=10, seed=42)
    gs_sig = result['gs_signal']
    sp_sig = result['sp_signal']
    print(f"  f={f_val}: gs_std={np.std(gs_sig):.10f}, sp_std={np.std(sp_sig):.6f}")
    print(f"    gs_signal range: [{gs_sig.min():.10f}, {gs_sig.max():.10f}]")
    print(f"    sp_signal range: [{sp_sig.min():.6f}, {sp_sig.max():.6f}]")
    print(f"    gs_signal unique values: {len(np.unique(np.round(gs_sig, 8)))}")
    # If gs_std is essentially 0, the correlation is meaningless
    if np.std(gs_sig) < 1e-8:
        print(f"    -> GS signal is CONSTANT. Correlation is MEANINGLESS (noise).")
    elif np.std(gs_sig) < 1e-4:
        print(f"    -> GS signal is nearly constant. Correlation is UNRELIABLE.")
    else:
        print(f"    -> GS signal has real variation. Correlation is meaningful.")

# Save data
with open('r19z_artifact_audit.json', 'w') as f:
    json.dump({
        'grid_size_test': {str(k): {kk: float(vv) if isinstance(vv, (int, float, np.floating)) else None 
                                     for kk, vv in v.items() if kk != 'comp' and kk != 'mv'} 
                          for k, v in results_grid.items()},
    }, f, indent=2)

# Plot
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, size in enumerate([12, 24, 48]):
    ax = axes[0, i]
    ax.plot(results_grid[size]['comp'][:2000], linewidth=0.5)
    ax.set_title(f'GS complexity (size={size}), f=0.064')
    ax.set_xlabel('Time step')
    ax.set_ylabel('std(v)')
    ax.axhline(0, color='red', linestyle='--', alpha=0.5)
    
    ax2 = axes[1, i]
    ax2.plot(results_grid[size]['mv'][:2000], linewidth=0.5)
    ax2.set_title(f'GS mean(v) (size={size}), f=0.064')
    ax2.set_xlabel('Time step')
    ax2.set_ylabel('mean(v)')

fig.suptitle('R19Z Artifact Audit: Gray-Scott Pattern Formation Test', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_artifact_audit.png', dpi=150)
print("\nSaved r19z_artifact_audit.png")
print("Done!")
