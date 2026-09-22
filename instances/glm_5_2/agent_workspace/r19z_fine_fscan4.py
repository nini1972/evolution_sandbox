"""
Fine-grained f scan — stronger coupling, N=20, 1000 steps.
"""
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

def gs_step_fast(u, v, Du, Dv, f, k, dt, dx):
    lap_u = np.zeros_like(u)
    lap_v = np.zeros_like(v)
    lap_u[1:-1,1:-1] = (u[:-2,1:-1]+u[2:,1:-1]+u[1:-1,:-2]+u[1:-1,2:]-4*u[1:-1,1:-1])/dx**2
    lap_v[1:-1,1:-1] = (v[:-2,1:-1]+v[2:,1:-1]+v[1:-1,:-2]+v[1:-1,2:]-4*v[1:-1,1:-1])/dx**2
    u_new = u + dt * (Du*lap_u - u*v*v + f*(1-u))
    v_new = v + dt * (Dv*lap_v + u*v*v - (f+k)*v)
    return np.clip(u_new,0,1), np.clip(v_new,0,1)

def sandpile_fast(heights, threshold):
    n = heights.shape[0]
    for i in range(n):
        for j in range(n):
            if np.random.random() < 0.05:
                heights[i,j] += 1
    total_avs = 0
    for _ in range(10):
        unstable = heights > threshold
        if not unstable.any(): break
        total_avs += int(unstable.sum())
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

def run_coupled(f_val, k_val=0.062, seed=42, n_steps=1000, N=20):
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
        for _ in range(N):
            u, v = gs_step_fast(u, v, Du, Dv, f_val, k_val, dt, dx)
        
        complexity = np.std(v)
        gs_complexity.append(complexity)
        
        # Stronger coupling: threshold modulation
        threshold = base_threshold * (1.0 + 0.5 * complexity)
        heights, avs = sandpile_fast(heights, threshold)
        sp_activity.append(float(avs))
        
        # Stronger feedback: sandpile → GS
        if avs > 0 and complexity > 0.01:
            noise = np.random.randn(gs_size, gs_size) * 0.05 * np.log1p(avs)
            u = np.clip(u + noise, 0, 1)
        
        if t > 150 and complexity < 1e-8:
            u[4:8, 4:8] = 0.5
            v[4:8, 4:8] = 0.25
    
    gs_complexity = np.array(gs_complexity)
    sp_activity = np.array(sp_activity, dtype=float)
    
    if gs_complexity.std() < 1e-10 or sp_activity.std() < 1e-10:
        return {'f': float(f_val), 'C': 0.0, 'lag': 0, 'C_zero': 0.0,
                'gs_complexity_mean': float(gs_complexity.mean()), 'gs_ac50': 0.0}
    
    gs_norm = (gs_complexity - gs_complexity.mean()) / gs_complexity.std()
    sp_norm = (sp_activity - sp_activity.mean()) / sp_activity.std()
    
    n = len(gs_norm)
    corr = np.correlate(gs_norm, sp_norm, mode='full') / n
    lags = np.arange(-n+1, n)
    max_idx = np.argmax(np.abs(corr))
    max_corr = float(corr[max_idx])
    max_lag = int(lags[max_idx])
    
    def autocorr(x, lag):
        if len(x) <= lag: return 0.0
        return float(np.corrcoef(x[:-lag], x[lag:])[0,1])
    
    ac50 = autocorr(gs_complexity, 50) if len(gs_complexity) > 50 else 0.0
    
    return {
        'f': float(f_val),
        'C': max_corr,
        'lag': max_lag,
        'C_zero': float(np.corrcoef(gs_complexity, sp_activity)[0,1]),
        'gs_complexity_mean': float(gs_complexity.mean()),
        'gs_ac50': ac50,
    }

# Run scan
f_values = np.arange(0.055, 0.080, 0.002)
seeds = [42, 123]

results = []
print("Fine-grained f scan (stronger coupling, N=20, 1000 steps)...")
for f_val in f_values:
    seed_results = [run_coupled(f_val, seed=s) for s in seeds]
    
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
    print(f"  f={f_val:.3f}: |C|={avg_C:.3f}, C_signed={avg_C_signed:.3f}, {sign}, "
          f"comp={avg_complexity:.4f}, ac50={avg_ac50:.3f}")

with open('r19z_fine_fscan_data.json', 'w') as f:
    json.dump(results, f, indent=2)

# Plot
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

ax = axes[0,0]
ax.plot(fs, Cs_signed, 'b-o', label='Signed C (max-lag)', markersize=8)
ax.plot(fs, C_zeros, 'r--s', label='C (zero-lag)', markersize=6)
ax.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax.axvspan(0.064, 0.070, alpha=0.15, color='green', label='Previous island')
ax.set_xlabel('Feed rate f'); ax.set_ylabel('Cross-correlation')
ax.set_title('A) Resonance Island: Fine-Grained f Scan'); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[0,1]
colors = ['green' if r['sign']=='+' else 'red' for r in results]
ax.bar(fs, Cs, width=0.0015, color=colors, alpha=0.7)
ax.set_xlabel('Feed rate f'); ax.set_ylabel('|C|')
ax.set_title('B) |C| (green=resonance, red=anti-resonance)'); ax.grid(True, alpha=0.3)

ax = axes[1,0]
ax2 = ax.twinx()
ax.plot(fs, complexities, 'b-o', markersize=8, label='GS complexity')
ax2.plot(fs, ac50s, 'r-s', markersize=8, label='GS ac(50)')
ax.axhline(y=0, color='r', linestyle=':', alpha=0.5)
ax.set_xlabel('Feed rate f'); ax.set_ylabel('GS complexity', color='b')
ax2.set_ylabel('ac(50)', color='r')
ax.set_title('C) GS Internal Dynamics'); ax.grid(True, alpha=0.3)

ax = axes[1,1]
ax.plot(fs, Cs_signed, 'b-o', markersize=8, label='C signed')
ax3 = ax.twinx()
ax3.plot(fs, ac50s, 'r-s', markersize=8, label='ac(50)')
ax.axhline(y=0, color='k', linestyle=':', alpha=0.3)
ax3.axhline(y=0, color='r', linestyle=':', alpha=0.5)
ax.axvspan(0.064, 0.070, alpha=0.15, color='green')
ax.set_xlabel('Feed rate f'); ax.set_ylabel('Signed C', color='b')
ax3.set_ylabel('ac(50)', color='r')
ax.set_title('D) Correlation Sign vs Internal Oscillation'); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('r19z_fine_fscan.png', dpi=150, bbox_inches='tight')
print("\nSaved r19z_fine_fscan.png")

positive_fs = [r['f'] for r in results if r['sign'] == '+']
if positive_fs:
    print(f"\nResonance island: f = {min(positive_fs):.3f} to {max(positive_fs):.3f}")
ac_neg = [r['f'] for r in results if r['gs_ac50'] < 0]
if ac_neg:
    print(f"GS oscillation (ac50<0): f = {min(ac_neg):.3f} to {max(ac_neg):.3f}")
