# R19Z Turn 13: Fine-Grained Resonance Island Mapping
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

class BTWSandpile:
    def __init__(self, size=8):
        self.size = size
        self.heights = np.zeros((size, size), dtype=float)
        self.threshold = 4.0
    def add_grain(self, site=None):
        if site is None:
            site = (np.random.randint(self.size), np.random.randint(self.size))
        self.heights[site] += 1.0
        return self.topple(site)
    def topple(self, site):
        total = 0
        queue = [site]
        visited = set()
        while queue:
            s = queue.pop(0)
            if s in visited:
                continue
            visited.add(s)
            if self.heights[s] >= self.threshold:
                self.heights[s] -= self.threshold
                total += 1
                for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ni, nj = s[0]+di, s[1]+dj
                    if 0 <= ni < self.size and 0 <= nj < self.size:
                        self.heights[ni, nj] += 1.0
                        queue.append((ni, nj))
                    elif di != 0 or dj != 0:
                        total += 1
        return total
    def step(self, threshold_mod=0.0):
        self.threshold = max(1.0, 4.0 + threshold_mod)
        return self.add_grain()
    def mean_height(self):
        return float(np.mean(self.heights))

def laplacian(arr):
    return (np.roll(arr, 1, 0) + np.roll(arr, -1, 0) +
            np.roll(arr, 1, 1) + np.roll(arr, -1, 1) - 4*arr)

def gray_scott_step(u, v, Du, Dv, f, k, dt=1.0):
    uvv = u * v * v
    u_new = u + dt * (Du * laplacian(u) - uvv + f * (1.0 - u))
    v_new = v + dt * (Dv * laplacian(v) + uvv - (f + k) * v)
    return np.clip(u_new, 0, 1), np.clip(v_new, 0, 1)

def xcorr(a, b, max_lag=50):
    a = a - np.mean(a)
    b = b - np.mean(b)
    if np.std(a) < 1e-10 or np.std(b) < 1e-10:
        return 0.0, 0
    lags = range(-max_lag, max_lag+1)
    corrs = []
    for lag in lags:
        if lag < 0:
            c = np.corrcoef(a[-lag:], b[:len(b)+lag])[0, 1]
        elif lag > 0:
            c = np.corrcoef(a[:len(a)-lag], b[lag:])[0, 1]
        else:
            c = np.corrcoef(a, b)[0, 1]
        corrs.append(0.0 if np.isnan(c) else c)
    corrs = np.array(corrs)
    best_idx = np.argmax(np.abs(corrs))
    return float(corrs[best_idx]), list(lags)[best_idx]

def autocorr(x, lag):
    x = x - np.mean(x)
    if np.std(x) < 1e-10:
        return 0.0
    if lag >= len(x):
        return 0.0
    return float(np.corrcoef(x[:len(x)-lag], x[lag:])[0, 1])

def run_gs_sandpile(f, k=0.062, Du=0.16, Dv=0.08, N=10, T=1500, seed=42):
    np.random.seed(seed)
    sz = 12
    u = np.ones((sz, sz))
    v = np.zeros((sz, sz))
    u[sz//2-2:sz//2+2, sz//2-2:sz//2+2] = 0.5
    v[sz//2-2:sz//2+2, sz//2-2:sz//2+2] = 0.25
    sp = BTWSandpile(size=6)
    gs_c = []
    sp_a = []
    sp_h = []
    sp_counter = 0
    for t in range(T):
        u, v = gray_scott_step(u, v, Du, Dv, f, k, dt=1.0)
        if sp_counter > 0 and len(sp_a) > 0:
            noise = sp_a[-1] * 0.001 * (np.random.rand(sz, sz) - 0.5)
            u = np.clip(u + noise, 0, 1)
        gs_c.append(float(np.var(v)))
        sp_counter += 1
        if sp_counter >= N:
            sp_counter = 0
            thresh_mod = -0.5 * (gs_c[-1] - 0.01)
            av = sp.step(threshold_mod=thresh_mod)
            sp_a.append(float(av))
            sp_h.append(sp.mean_height())
        else:
            if len(sp_a) > 0:
                sp_a.append(sp_a[-1] * 0.9)
                sp_h.append(sp_h[-1] if sp_h else 0.0)
            else:
                sp_a.append(0.0)
                sp_h.append(0.0)
    return np.array(gs_c), np.array(sp_a), np.array(sp_h)

def run_gs_uncoupled(f, k=0.062, Du=0.16, Dv=0.08, T=1500, seed=42):
    np.random.seed(seed)
    sz = 12
    u = np.ones((sz, sz))
    v = np.zeros((sz, sz))
    u[sz//2-2:sz//2+2, sz//2-2:sz//2+2] = 0.5
    v[sz//2-2:sz//2+2, sz//2-2:sz//2+2] = 0.25
    complexity = []
    v_mean = []
    for t in range(T):
        u, v = gray_scott_step(u, v, Du, Dv, f, k, dt=1.0)
        complexity.append(float(np.var(v)))
        v_mean.append(float(np.mean(v)))
    return np.array(complexity), np.array(v_mean)

def run_log_sp(r, N=20, T=2000, seed=42):
    np.random.seed(seed)
    sp = BTWSandpile(size=8)
    x = 0.5
    log_x = []
    sp_a = []
    sp_h = []
    sp_counter = 0
    for t in range(T):
        x = r * x * (1.0 - x)
        x = np.clip(x, 0, 1)
        log_x.append(x)
        sp_counter += 1
        if sp_counter >= N:
            sp_counter = 0
            thresh_mod = 0.5 * (x - 0.5)
            av = sp.step(threshold_mod=thresh_mod)
            sp_a.append(float(av))
            sp_h.append(sp.mean_height())
        else:
            if len(sp_a) > 0:
                sp_a.append(sp_a[-1] * 0.9)
                sp_h.append(sp_h[-1] if sp_h else 0.0)
            else:
                sp_a.append(0.0)
                sp_h.append(0.0)
    return np.array(log_x), np.array(sp_a), np.array(sp_h)

# === MAIN ===
print('=== Experiment 1: Fine f scan (GS x Sandpile) ===')
f_values = np.linspace(0.040, 0.090, 51)
N = 20
T = 1500
n_seeds = 3

res1 = {'f': [], 'C_mean': [], 'C_std': [], 'lag': [], 'complexity': [], 'sign': []}
res_gs = {'f': [], 'ac10': [], 'ac50': [], 'complexity': [], 'v_mean': []}

for i, f in enumerate(f_values):
    Cs = []
    lags = []
    comps = []
    for seed in range(42, 42 + n_seeds):
        gs_c, sp_a, sp_h = run_gs_sandpile(f, N=N, T=T, seed=seed)
        s = int(T * 0.2)
        C, lag = xcorr(gs_c[s:], sp_a[s:], max_lag=30)
        Cs.append(C)
        lags.append(lag)
        comps.append(float(np.mean(gs_c[s:])))
    cm = float(np.mean(Cs))
    res1['f'].append(float(f))
    res1['C_mean'].append(cm)
    res1['C_std'].append(float(np.std(Cs)))
    res1['lag'].append(float(np.mean(lags)))
    res1['complexity'].append(float(np.mean(comps)))
    res1['sign'].append(1 if cm > 0 else -1)
    uc, vm = run_gs_uncoupled(f, T=T, seed=42)
    s2 = int(T * 0.2)
    res_gs['f'].append(float(f))
    res_gs['ac10'].append(autocorr(uc[s2:], 10))
    res_gs['ac50'].append(autocorr(uc[s2:], 50))
    res_gs['complexity'].append(float(np.mean(uc[s2:])))
    res_gs['v_mean'].append(float(np.mean(vm[s2:])))
    if i % 10 == 0:
        print(f'  f={f:.4f}: C={cm:.4f}, ac50={res_gs["ac50"][-1]:.4f}')

print('  Done!')

# Find resonance island boundaries
signs = res1['sign']
island_bounds = []
in_island = False
for i, sg in enumerate(signs):
    if sg > 0 and not in_island:
        start_f = res1['f'][i]
        in_island = True
    elif sg < 0 and in_island:
        end_f = res1['f'][i-1]
        island_bounds.append((start_f, end_f))
        in_island = False
if in_island:
    island_bounds.append((start_f, res1['f'][-1]))

print(f'\nResonance island boundaries: {island_bounds}')

# === Experiment 2: Logistic x Sandpile fine r scan ===
print('\n=== Experiment 2: Fine r scan (Logistic x Sandpile) ===')
r_values = np.linspace(2.8, 4.0, 61)
N_log = 20
T_log = 2000
n_seeds_log = 3

res2 = {'r': [], 'C_mean': [], 'C_std': [], 'lag': [], 'x_mean': [], 'x_std': [], 'sign': []}

for i, r in enumerate(r_values):
    Cs = []
    lags = []
    xms = []
    xss = []
    for seed in range(42, 42 + n_seeds_log):
        lx, sa, sh = run_log_sp(r, N=N_log, T=T_log, seed=seed)
        s = int(T_log * 0.2)
        C, lag = xcorr(lx[s:], sa[s:], max_lag=30)
        Cs.append(C)
        lags.append(lag)
        xms.append(float(np.mean(lx[s:])))
        xss.append(float(np.std(lx[s:])))
    cm = float(np.mean(Cs))
    res2['r'].append(float(r))
    res2['C_mean'].append(cm)
    res2['C_std'].append(float(np.std(Cs)))
    res2['lag'].append(float(np.mean(lags)))
    res2['x_mean'].append(float(np.mean(xms)))
    res2['x_std'].append(float(np.mean(xss)))
    res2['sign'].append(1 if cm > 0 else -1)
    if i % 10 == 0:
        print(f'  r={r:.4f}: C={cm:.4f}')

print('  Done!')

# Count sign changes in logistic
log_signs = res2['sign']
log_sign_changes = []
for i in range(1, len(log_signs)):
    if log_signs[i] != log_signs[i-1]:
        log_sign_changes.append((res2['r'][i-1], res2['r'][i], log_signs[i-1], log_signs[i]))

print(f'\nLogistic sign changes: {log_sign_changes}')

# === Save data ===
with open('r19z_fine_scan_data.json', 'w') as fout:
    json.dump({'gs_sandpile': res1, 'gs_uncoupled': res_gs,
               'logistic_sandpile': res2, 'island_bounds': island_bounds,
               'log_sign_changes': log_sign_changes}, fout, indent=2)

# === Plot ===
fig = plt.figure(figsize=(18, 14))
gs_grid = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: C vs f (coupled)
ax1 = fig.add_subplot(gs_grid[0, 0])
ax1.errorbar(res1['f'], res1['C_mean'], yerr=res1['C_std'], fmt='o-', ms=3, capsize=2, color='darkblue')
ax1.axhline(0, color='gray', ls='--', lw=0.5)
ax1.set_xlabel('f (feed rate)')
ax1.set_ylabel('Cross-correlation C')
ax1.set_title('GS x Sandpile: C vs f (fine scan)')
for (s, e) in island_bounds:
    ax1.axvspan(s, e, alpha=0.2, color='green')

# Panel 2: GS uncoupled autocorrelation
ax2 = fig.add_subplot(gs_grid[0, 1])
ax2.plot(res_gs['f'], res_gs['ac10'], 'o-', ms=3, label='ac(10)', color='orange')
ax2.plot(res_gs['f'], res_gs['ac50'], 's-', ms=3, label='ac(50)', color='red')
ax2.axhline(0, color='gray', ls='--', lw=0.5)
ax2.set_xlabel('f (feed rate)')
ax2.set_ylabel('Autocorrelation')
ax2.set_title('Uncoupled GS: Internal Dynamics')
ax2.legend()
for (s, e) in island_bounds:
    ax2.axvspan(s, e, alpha=0.2, color='green')

# Panel 3: GS complexity
ax3 = fig.add_subplot(gs_grid[0, 2])
ax3.plot(res_gs['f'], res_gs['complexity'], 'o-', ms=3, color='purple')
ax3.set_xlabel('f (feed rate)')
ax3.set_ylabel('Variance of v')
ax3.set_title('Uncoupled GS: Pattern Complexity')
for (s, e) in island_bounds:
    ax3.axvspan(s, e, alpha=0.2, color='green')

# Panel 4: Combined view - C and ac50 overlaid
ax4 = fig.add_subplot(gs_grid[1, :])
ax4_twin = ax4.twinx()
ax4.plot(res1['f'], res1['C_mean'], 'o-', ms=3, color='darkblue', label='C (coupled)')
ax4.axhline(0, color='gray', ls='--', lw=0.5)
ax4_twin.plot(res_gs['f'], res_gs['ac50'], 's-', ms=3, color='red', label='ac(50) (uncoupled)')
ax4_twin.axhline(0, color='red', ls='--', lw=0.5, alpha=0.3)
ax4.set_xlabel('f (feed rate)')
ax4.set_ylabel('Cross-correlation C', color='darkblue')
ax4_twin.set_ylabel('Autocorrelation ac(50)', color='red')
ax4.set_title('The Resonance Island: Coupling Sign Maps to Internal Oscillatory Regime')
for (s, e) in island_bounds:
    ax4.axvspan(s, e, alpha=0.15, color='green')
lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4_twin.get_legend_handles_labels()
ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# Panel 5: Logistic C vs r
ax5 = fig.add_subplot(gs_grid[2, 0])
ax5.errorbar(res2['r'], res2['C_mean'], yerr=res2['C_std'], fmt='o-', ms=3, capsize=2, color='darkgreen')
ax5.axhline(0, color='gray', ls='--', lw=0.5)
ax5.set_xlabel('r (logistic growth rate)')
ax5.set_ylabel('Cross-correlation C')
ax5.set_title('Logistic x Sandpile: C vs r')

# Panel 6: Logistic x_std (complexity proxy)
ax6 = fig.add_subplot(gs_grid[2, 1])
ax6.plot(res2['r'], res2['x_std'], 'o-', ms=3, color='purple')
ax6.set_xlabel('r')
ax6.set_ylabel('std(x)')
ax6.set_title('Logistic: Internal Complexity (std)')

# Panel 7: Logistic C and std overlaid
ax7 = fig.add_subplot(gs_grid[2, 2])
ax7_twin = ax7.twinx()
ax7.plot(res2['r'], res2['C_mean'], 'o-', ms=3, color='darkgreen', label='C (coupled)')
ax7.axhline(0, color='gray', ls='--', lw=0.5)
ax7_twin.plot(res2['r'], res2['x_std'], 's-', ms=3, color='purple', label='std(x)')
ax7.set_xlabel('r')
ax7.set_ylabel('Cross-correlation C', color='darkgreen')
ax7_twin.set_ylabel('std(x)', color='purple')
ax7.set_title('Logistic: Coupling vs Internal Complexity')
lines1, labels1 = ax7.get_legend_handles_labels()
lines2, labels2 = ax7_twin.get_legend_handles_labels()
ax7.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

fig.suptitle('R19Z Turn 13: Fine-Grained Resonance Island Mapping', fontsize=16, fontweight='bold')
fig.savefig('r19z_fine_scan.png', dpi=150, bbox_inches='tight')
print('\nSaved r19z_fine_scan.png')
print('Done!')
