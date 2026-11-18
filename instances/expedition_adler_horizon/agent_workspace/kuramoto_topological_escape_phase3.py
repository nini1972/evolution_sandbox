#!/usr/bin/env python3
"""Phase III+ — Physics-aligned sweep (K ∈ [8.0, 12.0], t_max=300.0)."""
import json, numpy as np, os, time
from colony_lib.dynamics import simulate_kuramoto
from colony_lib.network_topology import generate_topology

# Parameters
configs = []
for topo in ['all_to_all', 'watts_strogatz', 'barabasi_albert']:
    for N in [64, 128, 256, 512]:
        for K in np.linspace(8.0, 12.0, 17):  # Escape region for r_ss ≥ 0.9
            for sigma in [1.0]:
                for R0_nominal in [0.06]:
                    configs.append({
                        'topo': topo,
                        'N': N,
                        'K': float(K),
                        'sigma': sigma,
                        'R0_nominal': R0_nominal,
                        't_max': 300.0,
                        'dt': 0.01,
                        'n_runs': 6
                    })

# Checkpointing
out_file = 'kuramoto_topological_escape_phase3.json'
if os.path.exists(out_file):
    with open(out_file, 'r') as f:
        results = json.load(f)
else:
    results = []

# Sweep
start_time = time.time()
for i, cfg in enumerate(configs):
    if i % 10 == 0:
        print(f"Config {i}/{len(configs)} | Elapsed: {time.time() - start_time:.1f}s")
        with open(out_file, 'w') as f:
            json.dump(results, f, indent=1)
    
    # Skip if already computed
    if any(r['topo'] == cfg['topo'] and r['N'] == cfg['N'] and 
           r['K'] == cfg['K'] and r['sigma'] == cfg['sigma'] and 
           r['R0_nominal'] == cfg['R0_nominal'] for r in results):
        continue
    
    # Simulate
    A = generate_topology(cfg['topo'], cfg['N'])
    lam_max_W = np.max(np.linalg.eigvals(A))
    U_pred = 1.0
    
    t_esc_all = []
    for run in range(cfg['n_runs']):
        result = simulate_kuramoto(
            n_oscillators=cfg['N'], K=cfg['K'], t_max=cfg['t_max'], dt=cfg['dt'],
            coupling_matrix=A, freq_scale=cfg['sigma'], seed=run
        )
        R = result['r_series']
        t_esc = cfg['t_max'] if np.max(R) < 0.9 else np.min(np.where(R >= 0.9)[0]) * cfg['dt']
        t_esc_all.append(t_esc)
    
    # Numerical stability
    K_ratio = min(cfg['K'] / lam_max_W, 0.99)
    delta_z = np.log(cfg['R0_nominal']) - np.log(1 - K_ratio)
    
    # Always append (preserve grid structure)
    U_meas = np.median(t_esc_all) * lam_max_W / cfg['R0_nominal'] if np.median(t_esc_all) < cfg['t_max'] else np.nan
    
    results.append({
        'topo': cfg['topo'],
        'N': cfg['N'],
        'K': cfg['K'],
        'sigma': cfg['sigma'],
        'R0_nominal': cfg['R0_nominal'],
        'lam_max_W': lam_max_W,
        'U_pred': U_pred,
        'U_meas': U_meas,
        't_esc_med': np.median(t_esc_all),
        'delta_z': delta_z,
        't_esc_all': t_esc_all,
        'valid': not np.isnan(U_meas)
    })

# Final save
with open(out_file, 'w') as f:
    json.dump(results, f, indent=1)
print(f"Sweep complete. Results saved to {out_file}.")