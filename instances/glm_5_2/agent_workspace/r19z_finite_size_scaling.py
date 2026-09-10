"""
R19Z Phase 10: Finite-Size Scaling of the Resonance Island (OPTIMIZED)
"""
import numpy as np, json, time

def run_gs_uncoupled(f_val, k=0.062, Du=0.16, Dv=0.08, size=12,
                     n_steps=600, burn_in=150, seed=42):
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5 + rng.randn(size, size) * 0.01
    v = np.ones((size, size)) * 0.25 + rng.randn(size, size) * 0.01
    cx, cy = size//2, size//2
    u[cx-1:cx+1, cy-1:cy+1] = 0.25
    v[cx-1:cx+1, cy-1:cy+1] = 0.75
    
    complexity_ts = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u
        v_lap = v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v
        uv2 = u * v * v
        u = u + Du * u_lap - uv2 + f_val * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_val + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        if ti >= 0:
            complexity_ts[ti] = np.std(v)
    
    def acf(x, lag):
        if np.std(x) < 1e-12:
            return 1.0
        n = len(x)
        if lag >= n: return 0.0
        c = np.corrcoef(x[:n-lag], x[lag:])[0, 1]
        return float(c) if not np.isnan(c) else 0.0
    
    return {
        'complexity': float(np.mean(complexity_ts)),
        'ac10': acf(complexity_ts, 10),
        'ac25': acf(complexity_ts, 25),
        'ac50': acf(complexity_ts, 50),
    }

def run_coupled_gs_sp(f_val, k=0.062, Du=0.16, Dv=0.08, 
                      gs_size=12, sp_size=6,
                      n_steps=600, burn_in=150, seed=42,
                      coup_strength=0.01, alpha=0.5):
    rng = np.random.RandomState(seed)
    u = np.ones((gs_size, gs_size)) * 0.5 + rng.randn(gs_size, gs_size) * 0.01
    v = np.ones((gs_size, gs_size)) * 0.25 + rng.randn(gs_size, gs_size) * 0.01
    cx, cy = gs_size//2, gs_size//2
    u[cx-1:cx+1, cy-1:cy+1] = 0.25
    v[cx-1:cx+1, cy-1:cy+1] = 0.75
    
    sp_h = np.zeros(sp_size) + 1.0
    sp_threshold = 4.0
    
    gs_ts = np.zeros(n_steps)
    sp_ts = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*u
        v_lap = v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v
        uv2 = u * v * v
        u = u + Du * u_lap - uv2 + f_val * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_val + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        
        gs_comp = np.std(v)
        sp_threshold_eff = sp_threshold * (1 + alpha * 0.1 * (gs_comp - 0.15))
        
        sp_h[0] += rng.random() * 0.3
        sp_h[sp_size//2] += rng.random() * 0.3
        sp_h[-1] += rng.random() * 0.3
        
        sp_activity = 0
        for _ in range(5):
            topple = sp_h >= sp_threshold_eff
            if not topple.any(): break
            for i in range(sp_size):
                if topple[i]:
                    sp_activity += 1
                    sp_h[i] -= sp_threshold_eff
                    if i > 0: sp_h[i-1] += sp_threshold_eff * 0.5
                    if i < sp_size-1: sp_h[i+1] += sp_threshold_eff * 0.5
        
        if sp_activity > 0:
            perturbation = coup_strength * sp_activity
            mask = rng.rand(gs_size, gs_size) < 0.2
            u[mask] += perturbation * (rng.randn(int(mask.sum())) * 0.5)
            u = np.clip(u, 0, 1)
        
        if ti >= 0:
            gs_ts[ti] = gs_comp
            sp_ts[ti] = sp_activity
    
    if np.std(gs_ts) < 1e-12 or np.std(sp_ts) < 1e-12:
        return {'best_corr': 0.0, 'sign': '0', 'gs_std': float(np.std(gs_ts))}
    
    max_lag = min(50, n_steps // 4)
    best_c = 0
    for lag in range(-max_lag, max_lag+1):
        if lag < 0:
            c = np.corrcoef(gs_ts[-lag:], sp_ts[:n_steps+lag])[0,1]
        elif lag > 0:
            c = np.corrcoef(gs_ts[:n_steps-lag], sp_ts[lag:])[0,1]
        else:
            c = np.corrcoef(gs_ts, sp_ts)[0,1]
        if not np.isnan(c) and abs(c) > abs(best_c):
            best_c = float(c)
    return {'best_corr': best_c, 'sign': '+' if best_c > 0 else '-', 'gs_std': float(np.std(gs_ts))}

# ---- Main: reduced parameter set ----
sizes = [8, 12, 16, 20]
f_values = [0.060, 0.064, 0.068, 0.072, 0.076]
seeds = [42, 123]

print('Finite-Size Scaling (optimized)')
print('Sizes:', sizes, 'f-values:', f_values, 'seeds:', seeds)
print()

all_results = {}
t0 = time.time()

for size in sizes:
    print(f'=== Size {size} ===')
    size_data = {'uncoupled': [], 'coupled': []}
    
    for f in f_values:
        unc_results = [run_gs_uncoupled(f, size=size, seed=s) for s in seeds]
        ac50_avg = np.mean([r['ac50'] for r in unc_results])
        comp_avg = np.mean([r['complexity'] for r in unc_results])
        size_data['uncoupled'].append({
            'f': f, 'ac50': float(ac50_avg),
            'ac25': float(np.mean([r['ac25'] for r in unc_results])),
            'complexity': float(comp_avg),
        })
        
        coup_results = [run_coupled_gs_sp(f, gs_size=size, seed=s) for s in seeds]
        c_avg = np.mean([r['best_corr'] for r in coup_results])
        size_data['coupled'].append({
            'f': f, 'C': float(c_avg),
            'sign': '+' if c_avg > 0 else '-',
            'gs_std': float(np.mean([r['gs_std'] for r in coup_results])),
        })
        
        print(f'  f={f:.3f}: ac50={ac50_avg:+.4f} comp={comp_avg:.6f} C={c_avg:+.4f} {"+" if c_avg>0 else "-"}')
    
    all_results[size] = size_data
    print(f'  [Elapsed: {time.time()-t0:.1f}s]')

with open('r19z_finite_size_scaling.json', 'w') as fp:
    json.dump(all_results, fp, indent=2)
print('\nSaved r19z_finite_size_scaling.json')