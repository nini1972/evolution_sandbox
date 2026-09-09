"""R19Z Phase 9b: Uncoupled GS scan - characterize internal dynamics."""
import numpy as np, json, time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_uncoupled_gs(f_val, k=0.062, Du=0.16, Dv=0.08, size=8,
                     n_steps=1200, burn_in=300, seed=42):
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-1:size//2+1, size//2-1:size//2+1] = 0.25
    v[size//2-1:size//2+1, size//2-1:size//2+1] = 0.75
    complexity_ts = np.zeros(n_steps)
    v_mean_ts = np.zeros(n_steps)
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
            complexity_ts[ti] = np.std(v)
            v_mean_ts[ti] = np.mean(v)
    def acf(x, lag):
        if np.std(x) < 1e-12:
            return 1.0
        n = len(x)
        if lag >= n:
            return 0.0
        c = np.corrcoef(x[:n-lag], x[lag:])[0, 1]
        return float(c) if not np.isnan(c) else 0.0
    return {
        'f': float(f_val),
        'complexity_mean': float(np.mean(complexity_ts)),
        'complexity_std': float(np.std(complexity_ts)),
        'v_mean': float(np.mean(v_mean_ts)),
        'ac10': acf(complexity_ts, 10),
        'ac20': acf(complexity_ts, 20),
        'ac50': acf(complexity_ts, 50),
        'ac100': acf(complexity_ts, 100),
    }

f_values = np.arange(0.058, 0.092, 0.002)
print('Uncoupled GS scan: %d f-values' % len(f_values))

results = []
t0 = time.time()
for i, f in enumerate(f_values):
    r = run_uncoupled_gs(f, seed=42)
    results.append(r)
    print('  f=%.3f: comp=%.6f ac50=%+.4f ac20=%+.4f  [%d/%d] (%.1fs)' % (
        f, r['complexity_mean'], r['ac50'], r['ac20'], i+1, len(f_values), time.time()-t0))

with open('r19z_dense_scan_uncoupled.json', 'w') as fp:
    json.dump({'f_values': [float(f) for f in f_values], 'results': results}, fp, indent=2)
print('Saved r19z_dense_scan_uncoupled.json')
