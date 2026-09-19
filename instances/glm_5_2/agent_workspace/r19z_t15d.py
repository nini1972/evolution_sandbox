# R19Z Turn 15d: Fine-grained f scan - REDUCED for speed
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

k_gs = 0.062
Du, Dv = 0.16, 0.08

def lap(a):
    return np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)-4*a

def gs_step(u, v, f, k, dt=1.0):
    uvv = u*v*v
    u2 = u + dt*(Du*lap(u) - uvv + f*(1.0-u))
    v2 = v + dt*(Dv*lap(v) + uvv - (f+k)*v)
    return np.clip(u2,0,1), np.clip(v2,0,1)

def sandpile_step_fast(heights, threshold):
    h = heights.copy()
    toppled_count = 0
    for _ in range(50):
        sites = np.argwhere(h >= threshold)
        if len(sites) == 0:
            break
        toppled_count += len(sites)
        for sy, sx in sites:
            h[sy, sx] -= 4
            for dy, dx in [(1,0),(-1,0),(0,1),(0,-1)]:
                ny, nx = sy+dy, sx+dx
                if 0 <= ny < h.shape[0] and 0 <= nx < h.shape[1]:
                    h[ny, nx] += 1
    return h, toppled_count

sz_gs = 24
sz_sp = 6

f_vals = np.arange(0.050, 0.078, 0.004)
results = {'f': [], 'gs_complexity': [], 'gs_ac50': [], 'gs_ac10': [],
           'coupled_C': [], 'coupled_C_zero': []}

T_total = 600
burn = 100
measure_len = T_total - burn

print("=== Fine-grained f scan (fast) ===")
for fi, f in enumerate(f_vals):
    # --- Uncoupled GS ---
    np.random.seed(42)
    u = np.ones((sz_gs, sz_gs)); v = np.zeros((sz_gs, sz_gs))
    c = sz_gs//2; r = sz_gs//6
    u[c-r:c+r, c-r:c+r] = 0.5
    v[c-r:c+r, c-r:c+r] = 0.25
    v += np.random.rand(sz_gs, sz_gs) * 0.01
    
    var_v_unc = []
    for t in range(T_total):
        u, v = gs_step(u, v, f, k_gs)
        if t >= burn:
            var_v_unc.append(float(np.var(v)))
    var_v_unc = np.array(var_v_unc)
    
    def autocorr(x, lag):
        if len(x) < lag + 5: return 1.0
        x = x - np.mean(x)
        if np.std(x) < 1e-12: return 1.0
        return float(np.corrcoef(x[:-lag], x[lag:])[0,1])
    
    ac10 = autocorr(var_v_unc, 10)
    ac50 = autocorr(var_v_unc, 50)
    
    # --- Coupled GS-Sandpile ---
    np.random.seed(42)
    u_c = np.ones((sz_gs, sz_gs)); v_c = np.zeros((sz_gs, sz_gs))
    u_c[c-r:c+r, c-r:c+r] = 0.5
    v_c[c-r:c+r, c-r:c+r] = 0.25
    v_c += np.random.rand(sz_gs, sz_gs) * 0.01
    
    sp_h = np.full((sz_sp, sz_sp), 2.0)
    sp_threshold_base = 4.0
    coupling_alpha = 0.05
    
    var_v_coup_list = []
    sp_activity_list = []
    
    for t in range(T_total):
        u_c, v_c = gs_step(u_c, v_c, f, k_gs)
        gs_complexity = float(np.var(v_c))
        threshold = max(sp_threshold_base * (1.0 + coupling_alpha * (gs_complexity - 0.02) / 0.02), 2.0)
        
        if t % 5 == 0:
            sp_h[np.random.randint(sz_sp), np.random.randint(sz_sp)] += 1
        
        sp_h, sp_act = sandpile_step_fast(sp_h, threshold)
        
        if sp_act > 0:
            for _ in range(min(sp_act, 10)):
                u_c[np.random.randint(sz_gs), np.random.randint(sz_gs)] *= 0.99
        
        if t >= burn:
            var_v_coup_list.append(gs_complexity)
            sp_activity_list.append(float(sp_act))
    
    var_v_coup = np.array(var_v_coup_list)
    sp_act_arr = np.array(sp_activity_list)
    
    if np.std(var_v_coup) > 1e-10 and np.std(sp_act_arr) > 1e-10:
        x1 = (var_v_coup - np.mean(var_v_coup)) / np.std(var_v_coup)
        x2 = (sp_act_arr - np.mean(sp_act_arr)) / np.std(sp_act_arr)
        max_lag = min(50, measure_len // 4)
        xcorrs = []
        for lag in range(-max_lag, max_lag+1):
            if lag >= 0:
                cc = np.mean(x1[lag:] * x2[:len(x1)-lag])
            else:
                la = -lag
                cc = np.mean(x1[:len(x1)-la] * x2[la:])
            xcorrs.append(cc)
        xcorrs = np.array(xcorrs)
        best_C = float(xcorrs[np.argmax(np.abs(xcorrs))])
        zero_C = float(xcorrs[max_lag])
    else:
        best_C = 0.0; zero_C = 0.0
    
    results['f'].append(float(f))
    results['gs_complexity'].append(float(np.mean(var_v_unc)))
    results['gs_ac50'].append(ac50)
    results['gs_ac10'].append(ac10)
    results['coupled_C'].append(best_C)
    results['coupled_C_zero'].append(zero_C)
    
    print(f"  f={f:.3f}: complexity={np.mean(var_v_unc):.6f}, ac10={ac10:.4f}, ac50={ac50:.4f}, C={best_C:.4f}")

# Plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax = axes[0,0]
ax.plot(results['f'], results['gs_complexity'], 'bo-', ms=6)
ax.set_xlabel('f'); ax.set_ylabel('Mean Var(v)'); ax.set_title('GS Pattern Complexity')

ax = axes[0,1]
ax.plot(results['f'], results['gs_ac10'], 'go-', ms=5, label='ac(10)')
ax.plot(results['f'], results['gs_ac50'], 'ro-', ms=5, label='ac(50)')
ax.axhline(0, color='k', ls='--', alpha=0.5)
ax.set_xlabel('f'); ax.set_ylabel('Autocorrelation'); ax.set_title('GS Internal Dynamics')
ax.legend()

ax = axes[1,0]
ax.plot(results['f'], results['coupled_C'], 'bs-', ms=6, label='Best |C|')
ax.plot(results['f'], results['coupled_C_zero'], 'r^-', ms=6, label='Zero-lag C')
ax.axhline(0, color='k', ls='--', alpha=0.5)
ax.set_xlabel('f'); ax.set_ylabel('Cross-correlation'); ax.set_title('GS-SP Coupling')
ax.legend()

ax = axes[1,1]
ax.scatter(results['gs_ac50'], results['coupled_C'], c=results['f'], cmap='viridis', s=100)
for i, f in enumerate(results['f']):
    ax.annotate(f'{f:.3f}', (results['gs_ac50'][i], results['coupled_C'][i]), fontsize=8)
ax.axhline(0, color='k', ls='--', alpha=0.5)
ax.axvline(0, color='k', ls='--', alpha=0.5)
ax.set_xlabel('GS ac(50)'); ax.set_ylabel('Coupled C')
ax.set_title('Resonance Island: Internal Osc vs Coupling Sign')

fig.suptitle('R19Z Turn 15d: Fine-Grained Resonance Island Mapping', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_t15d_resonance_island.png', dpi=150, bbox_inches='tight')
print('\nSaved r19z_t15d_resonance_island.png')

with open('r19z_t15d_data.json', 'w') as fout:
    json.dump(results, fout, indent=2)
print('Saved r19z_t15d_data.json')