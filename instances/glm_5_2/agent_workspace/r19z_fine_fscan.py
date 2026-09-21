"""
Fine-grained f scan: Map the exact boundaries of the resonance island.
Run coupled GS-sandpile at f = 0.060 to 0.078 in steps of 0.001.
Multi-seed averaged, measure cross-correlation and GS internal dynamics.
"""
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ============ Gray-Scott solver ============
def gs_step(u, v, Du, Dv, f, k, dt, dx):
    du = np.zeros_like(u)
    dv = np.zeros_like(v)
    du[1:-1,1:-1] = Du * (u[:-2,1:-1] + u[2:,1:-1] + u[1:-1,:-2] + u[1:-1,2:] - 4*u[1:-1,1:-1]) / dx**2
    dv[1:-1,1:-1] = Dv * (v[:-2,1:-1] + v[2:,1:-1] + v[1:-1,:-2] + v[1:-1,2:] - 4*v[1:-1,1:-1]) / dx**2
    lap_u = np.zeros_like(u); lap_v = np.zeros_like(v)
    lap_u[1:-1,1:-1] = (u[:-2,1:-1]+u[2:,1:-1]+u[1:-1,:-2]+u[1:-1,2:]-4*u[1:-1,1:-1])/dx**2
    lap_v[1:-1,1:-1] = (v[:-2,1:-1]+v[2:,1:-1]+v[1:-1,:-2]+v[1:-1,2:]-4*v[1:-1,1:-1])/dx**2
    u_new = u + dt * (Du*lap_u - u*v*v + f*(1-u))
    v_new = v + dt * (Dv*lap_v + u*v*v - (f+k)*v)
    return np.clip(u_new,0,1), np.clip(v_new,0,1)

# ============ BTW sandpile ============
def sandpile_step(heights, threshold):
    n = heights.shape[0]
    additions = np.random.random(heights.shape) < 0.05
    heights = heights + additions.astype(float)
    total_avs = 0
    for _ in range(20):
        unstable = heights > threshold
        if not unstable.any(): break
        total_avs += unstable.sum()
        for i in range(n):
            for j in range(n):
                if heights[i,j] > threshold:
                    grains = int(heights[i,j] // threshold)
                    heights[i,j] -= grains * threshold
                    for _ in range(grains):
                        for di,dj in [(0,1),(0,-1),(1,0),(-1,0)]:
                            ni,nj = i+di,j+dj
                            if 0<=ni<n and 0<=nj<n:
                                heights[ni,nj] += 1
    return heights, total_avs

# ============ Coupled run ============
def run_coupled(f_val, k_val=0.062, seed=42, n_steps=1500, N=20):
    np.random.seed(seed)
    gs_size = 12
    sp_size = 6
    Du, Dv = 0.16, 0.08
    dt, dx = 1.0, 1.0
    
    u = np.ones((gs_size, gs_size))
    v = np.zeros((gs_size, gs_size))
    u[4:8, 4:8] = 0.5
    v[4:8, 4:8] = 0.25
    
    heights = np.random.uniform(0, 3, (sp_size, sp_size))
    base_threshold = 4.0
    
    gs_complexity = []
    sp_activity = []
    
    for t in range(n_steps):
        # GS update (N sub-steps)
        for _ in range(N):
            u, v = gs_step(u, v, Du, Dv, f_val, k_val, dt, dx)
        
        complexity = np.std(v)
        gs_complexity.append(complexity)
        
        # Sandpile update
        threshold = base_threshold * (1.0 + 0.1 * complexity)
        heights, avs = sandpile_step(heights, threshold)
        sp_activity.append(avs)
        
        # Feedback: sandpile → GS
        if avs > 0 and complexity > 0.01:
            noise = np.random.randn(gs_size, gs_size) * 0.01 * np.log1p(avs)
            u = np.clip(u + noise, 0, 1)
        
        # Reset if dead
        if t > 200 and complexity < 1e-8:
            u[4:8, 4:8] = 0.5
            v[4:8, 4:8] = 0.25
    
    gs_complexity = np.array(gs_complexity)
    sp_activity = np.array(sp_activity, dtype=float)
    
    # Normalize
    gs_norm = (gs_complexity - gs_complexity.mean()) / (gs_complexity.std() + 1e-10)
    sp_norm = (sp_activity - sp_activity.mean()) / (sp_activity.std() + 1e-10)
    
    # Cross-correlation
    corr = np.correlate(gs_norm, sp_norm, mode='full')
    lags = np.arange(-len(gs_norm)+1, len(gs_norm))
    max_idx = np.argmax(np.abs(corr))
    max_corr = corr[max_idx]
    max_lag = lags[max_idx]
    
    # Autocorrelation of GS at lag 50
    def autocorr(x, lag):
        if len(x) <= lag: return 0.0
        return np.corrcoef(x[:-lag], x[lag:])[0,1]
    
    ac50 = autocorr(gs_complexity, 50) if len(gs_complexity) > 50 else 0.0
    
    return {
        'f': f_val,
        'C': float(max_corr),
        'lag': int(max_lag),
        'C_zero': float(np.corrcoef(gs_complexity, sp_activity)[0,1]),
        'gs_complexity_mean': float(gs_complexity.mean()),
        'gs_ac50': float(ac50),
        'sp_activity_mean': float(sp_activity.mean()),
    }

# ============ Run the scan ============
f_values = np.arange(0.060, 0.078, 0.002)
seeds = [42, 123, 7]

results = []
print("Running fine-grained f scan (3 seeds each)...")
for f_val in f_values:
    seed_results = []
    for s in seeds:
        r = run_coupled(f_val, seed=s, n_steps=1500, N=20)
        seed_results.append(r)
    
    avg_C = np.mean([abs(r['C']) for r in seed_results])
    avg_C_signed = np.mean([r['C'] for r in seed_results])
    avg_C_zero = np.mean([r['C_zero'] for r in seed_results])
    avg_complexity = np.mean([r['gs_complexity_mean'] for r in seed_results])
    avg_ac50 = np.mean([r['gs_ac50'] for r in seed_results])
    sign = '+' if avg_C_signed > 0 else '-'
    
    results.append({
        'f': float(f_val),
        'avg_C': float(avg_C),
        'avg_C_signed': float(avg_C_signed),
        'avg_C_zero': float(avg_C_zero),
        'sign': sign,
        'gs_complexity': float(avg_complexity),
        'gs_ac50': float(avg_ac50),
    })
    print(f"  f={f_val:.3f}: |C|={avg_C:.3f}, C_signed={avg_C_signed:.3f}, sign={sign}, "
          f"complexity={avg_complexity:.4f}, ac50={avg_ac50:.3f}")

# Save data
with open('r19z_fine_fscan_data.json', 'w') as f:
    json.dump(results, f, indent=2)

# ============ Plot ============
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

fs = [r['f'] for r in results]
Cs = [r['avg_C'] for r in results]
Cs_signed = [r['avg_C_signed'] for r in results]
C_zeros = [r['avg_C_zero'] for r in results]
complexities = [r['gs_complexity'] for r in results]
ac50s = [r['gs_ac50'] for r in results]

# Panel 1: Signed correlation vs f
ax = axes[0,0]
ax.plot(fs, Cs_signed, 'b-o', label='Signed C (max-lag)', markersize=6)
ax.plot(fs, C_zeros, 'r--s', label='C (zero-lag)', markersize=5)
ax.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax.axvspan(0.064, 0.070, alpha=0.15, color='green', label='Resonance island (prev.)')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Cross-correlation')
ax.set_title('A) Resonance Island: Fine-Grained f Scan')
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 2: |C| vs f
ax = axes[0,1]
ax.plot(fs, Cs, 'k-o', markersize=6)
ax.axvspan(0.064, 0.070, alpha=0.15, color='green')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('|C|')
ax.set_title('B) Resonance Strength |C|')
ax.grid(True, alpha=0.3)

# Panel 3: GS complexity and ac50
ax = axes[1,0]
ax2 = ax.twinx()
ax.plot(fs, complexities, 'b-o', markersize=6, label='GS complexity')
ax2.plot(fs, ac50s, 'r-s', markersize=6, label='GS ac(50)')
ax.axhline(y=0, color='r', linestyle=':', alpha=0.5)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('GS complexity (std of v)', color='b')
ax2.set_ylabel('GS autocorrelation at lag 50', color='r')
ax.set_title('C) GS Internal Dynamics')
ax.grid(True, alpha=0.3)

# Panel 4: Combined view — C_signed and ac50
ax = axes[1,1]
ax.plot(fs, Cs_signed, 'b-o', markersize=6, label='C signed')
ax3 = ax.twinx()
ax3.plot(fs, ac50s, 'r-s', markersize=6, label='ac(50)')
ax.axhline(y=0, color='k', linestyle=':', alpha=0.3)
ax3.axhline(y=0, color='r', linestyle=':', alpha=0.5)
ax.axvspan(0.064, 0.070, alpha=0.15, color='green')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Signed C', color='b')
ax3.set_ylabel('ac(50)', color='r')
ax.set_title('D) Correlation Sign vs Internal Oscillation')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('r19z_fine_fscan.png', dpi=150, bbox_inches='tight')
print("\nSaved r19z_fine_fscan.png")

# Identify exact island boundaries
positive_fs = [r['f'] for r in results if r['sign'] == '+']
if positive_fs:
    print(f"\nResonance island boundaries: f = {min(positive_fs):.3f} to f = {max(positive_fs):.3f}")
    print(f"Island width: {max(positive_fs) - min(positive_fs):.3f}")
else:
    print("\nNo positive resonance found in this range")

# Check where ac50 changes sign
ac_neg = [r['f'] for r in results if r['gs_ac50'] < 0]
if ac_neg:
    print(f"GS internal oscillation (ac50<0): f = {min(ac_neg):.3f} to f = {max(ac_neg):.3f}")
