"""R19Z Phase 9a: Dense coupled scan only (optimized for speed)."""
import numpy as np, json, time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_coupled(f_val, k=0.062, Du=0.16, Dv=0.08, size=8,
               n_steps=1200, N_gap=10, burn_in=300,
               gs_to_sp=0.3, sp_to_gs=0.005, seed=42):
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-1:size//2+1, size//2-1:size//2+1] = 0.25
    v[size//2-1:size//2+1, size//2-1:size//2+1] = 0.75
    grid = np.zeros((size, size))
    threshold_base = 4.0
    gs_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_act = np.zeros(n_steps)
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        f_eff = f_val
        if t > 0 and t % N_gap == 0 and ti > 0:
            f_eff = f_val + sp_to_gs * sp_act[ti - 1]
        u = u + Du * u_lap - uv2 + f_eff * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_eff + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        gs_complexity = np.std(v)
        if t % N_gap == 0:
            threshold = threshold_base + gs_to_sp * (gs_complexity - 0.1) * 10
            threshold = max(threshold, 1.0)
            i2, j2 = rng.randint(0, size, 2)
            grid[i2, j2] += 1
            avalanche = 0
            toppling = True
            while toppling:
                toppling = False
                for ii in range(size):
                    for jj in range(size):
                        if grid[ii, jj] >= threshold:
                            toppling = True
                            avalanche += 1
                            grid[ii, jj] -= 4
                            if ii > 0: grid[ii-1, jj] += 1
                            if ii < size-1: grid[ii+1, jj] += 1
                            if jj > 0: grid[ii, jj-1] += 1
                            if jj < size-1: grid[ii, jj+1] += 1
        else:
            avalanche = 0
        if ti >= 0:
            gs_signal[ti] = gs_complexity
            sp_signal[ti] = np.mean(grid)
            sp_act[ti] = avalanche
    max_lag = 100
    best_corr = 0
    best_lag = 0
    for lag in range(-max_lag, max_lag+1, 5):
        if lag < 0:
            a, b = gs_signal[:lag], sp_signal[-lag:]
        elif lag > 0:
            a, b = gs_signal[lag:], sp_signal[:-lag]
        else:
            a, b = gs_signal, sp_signal
        if np.std(a) > 1e-10 and np.std(b) > 1e-10:
            c = np.corrcoef(a, b)[0, 1]
            if abs(c) > abs(best_corr):
                best_corr = c
                best_lag = lag
    zero_lag = 0.0
    if np.std(gs_signal) > 1e-10 and np.std(sp_signal) > 1e-10:
        zero_lag = np.corrcoef(gs_signal, sp_signal)[0, 1]
    return {
        'f': float(f_val),
        'best_corr': float(best_corr),
        'best_lag': int(best_lag),
        'zero_lag': float(zero_lag),
        'sign': '+' if best_corr > 0 else '-',
        'gs_mean': float(np.mean(gs_signal)),
        'gs_std': float(np.std(gs_signal)),
        'sp_mean': float(np.mean(sp_signal)),
        'sp_std': float(np.std(sp_signal)),
    }

f_values = np.arange(0.058, 0.092, 0.002)
print('Dense coupled scan: %d f-values' % len(f_values))

results = []
t0 = time.time()
for i, f in enumerate(f_values):
    r = run_coupled(f, seed=42)
    results.append(r)
    print('  f=%.3f: C=%+.4f sign=%s  gs_std=%.6f  [%d/%d] (%.1fs)' % (
        f, r['best_corr'], r['sign'], r['gs_std'], i+1, len(f_values), time.time()-t0))

with open('r19z_dense_scan_coupled.json', 'w') as fp:
    json.dump({'f_values': [float(f) for f in f_values], 'results': results}, fp, indent=2)
print('Saved r19z_dense_scan_coupled.json')
