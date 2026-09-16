# R19Z Turn 14: Fast fine scan
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def lap_reflect(a):
    p = np.pad(a, 1, mode='reflect')
    return (p[:-2,1:-1] + p[2:,1:-1] + p[1:-1,:-2] + p[1:-1,2:] - 4*a)

def gs_step(u, v, Du, Dv, f, k):
    uvv = u * v * v
    u2 = u + Du * lap_reflect(u) - uvv + f * (1.0 - u)
    v2 = v + Dv * lap_reflect(v) + uvv - (f + k) * v
    return np.clip(u2, 0, 1), np.clip(v2, 0, 1)

def init_gs(sz=12):
    u = np.ones((sz, sz)) * 0.5
    v = np.ones((sz, sz)) * 0.25
    u[sz//2-2:sz//2+2, sz//2-2:sz//2+2] = 0.25
    v[sz//2-2:sz//2+2, sz//2-2:sz//2+2] = 0.75
    return u, v

def btw_step(h, thr, size=6):
    i, j = np.random.randint(size), np.random.randint(size)
    h[i, j] += 1.0
    total = 0
    # Simple synchronous relaxation
    for _ in range(20):
        over = h >= thr
        if not over.any(): break
        cnt = over.sum()
        total += cnt
        h[over] -= thr
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            rolled = np.roll(np.roll(over, di, axis=0), dj, axis=1)
            h[rolled] += 1.0
    return total, h

def xc(a, b, ml=15):
    a = a - np.mean(a); b = b - np.mean(b)
    if np.std(a) < 1e-10 or np.std(b) < 1e-10: return 0.0
    best = 0
    for lag in range(-ml, ml+1):
        if lag < 0: aa, bb = a[-lag:], b[:len(b)+lag]
        elif lag > 0: aa, bb = a[:len(a)-lag], b[lag:]
        else: aa, bb = a, b
        if len(aa) < 10: continue
        c = np.corrcoef(aa, bb)[0,1]
        if not np.isnan(c) and abs(c) > abs(best): best = c
    return float(best)

def ac(x, lag):
    x = x - np.mean(x)
    if np.std(x) < 1e-10 or lag >= len(x): return 0.0
    c = np.corrcoef(x[:len(x)-lag], x[lag:])[0,1]
    return 0.0 if np.isnan(c) else float(c)

# === Exp 1: GS x Sandpile ===
print('Exp 1: GS x Sandpile')
fs = np.linspace(0.040, 0.090, 26)
N=10; T=1000; burn=500; ns=2
r1 = {'f':[], 'C':[], 'Cs':[], 'comp':[]}
rg = {'f':[], 'ac10':[], 'ac50':[], 'comp':[]}
for f in fs:
    Cs=[]; comps=[]
    for sd in range(ns):
        np.random.seed(42+sd)
        u, v = init_gs(12)
        h = np.zeros((6,6))
        gc = np.zeros(T); sa = np.zeros(T)
        for t in range(burn + T):
            ti = t - burn
            f_eff = f
            if t > 0 and t % N == 0 and ti > 0:
                f_eff = f + 0.005 * sa[ti-1]
            u, v = gs_step(u, v, 0.16, 0.08, f_eff, 0.062)
            comp = float(np.std(v))
            if t % N == 0:
                thr = max(1.0, 4.0 + 0.3*(comp-0.1)*10)
                av, h = btw_step(h, thr)
            else:
                av = 0
            if ti >= 0:
                gc[ti] = comp; sa[ti] = float(av)
        s = int(T*0.2)
        C = xc(gc[s:], sa[s:])
        Cs.append(C); comps.append(float(np.mean(gc[s:])))
    r1['f'].append(float(f)); r1['C'].append(float(np.mean(Cs)))
    r1['Cs'].append(float(np.std(Cs))); r1['comp'].append(float(np.mean(comps)))
    # Uncoupled GS
    np.random.seed(42)
    u, v = init_gs(12)
    uc = np.zeros(T); vm = np.zeros(T)
    for t in range(burn + T):
        ti = t - burn
        u, v = gs_step(u, v, 0.16, 0.08, f, 0.062)
        if ti >= 0:
            uc[ti] = float(np.std(v)); vm[ti] = float(np.mean(v))
    s2 = int(T*0.2)
    rg['f'].append(float(f))
    rg['ac10'].append(ac(uc[s2:], 10)); rg['ac50'].append(ac(uc[s2:], 50))
    rg['comp'].append(float(np.mean(uc[s2:])))

# Find islands
Cs = r1['C']; sg = [1 if c > 0 else -1 for c in Cs]
bounds = []; inside = False
for i, s in enumerate(sg):
    if s > 0 and not inside: st = r1['f'][i]; inside = True
    elif s <= 0 and inside: bounds.append((st, r1['f'][i])); inside = False
if inside: bounds.append((st, r1['f'][-1]))
print(f'Islands: {bounds}')

# === Exp 2: Logistic x Sandpile ===
print('Exp 2: Logistic x Sandpile')
rs = np.linspace(2.8, 4.0, 21)
r2 = {'r':[], 'C':[], 'xs':[]}
for r in rs:
    Cs=[]; xss=[]
    for sd in range(2):
        np.random.seed(42+sd)
        h = np.zeros((6,6)); x = 0.5
        lx = np.zeros(1000); sa = np.zeros(1000)
        for t in range(1000):
            x = r*x*(1-x); x = np.clip(x, 1e-10, 1-1e-10)
            lx[t] = x
            if t % 20 == 0:
                thr = max(1.0, 4.0 + 0.5*(x-0.5))
                av, h = btw_step(h, thr)
            else: av = 0
            sa[t] = float(av)
        s = int(1000*0.2)
        C = xc(lx[s:], sa[s:])
        Cs.append(C); xss.append(float(np.std(lx[s:])))
    r2['r'].append(float(r)); r2['C'].append(float(np.mean(Cs)))
    r2['xs'].append(float(np.mean(xss)))

# Save
with open('r19z_t14_data.json', 'w') as f:
    json.dump({'gs_sp': r1, 'gs_unc': rg, 'log_sp': r2, 'islands': bounds}, f, indent=2)

# Plot
fig = plt.figure(figsize=(18, 14))
g = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

ax1 = fig.add_subplot(g[0,0])
ax1.errorbar(r1['f'], r1['C'], yerr=r1['Cs'], fmt='o-', ms=3, capsize=2, color='darkblue')
ax1.axhline(0, color='gray', ls='--', lw=0.5)
ax1.set_xlabel('f'); ax1.set_ylabel('C'); ax1.set_title('GS x Sandpile: C vs f')
for s, e in bounds: ax1.axvspan(s, e, alpha=0.2, color='green')

ax2 = fig.add_subplot(g[0,1])
ax2.plot(rg['f'], rg['ac10'], 'o-', ms=3, label='ac(10)', color='orange')
ax2.plot(rg['f'], rg['ac50'], 's-', ms=3, label='ac(50)', color='red')
ax2.axhline(0, color='gray', ls='--', lw=0.5)
ax2.set_xlabel('f'); ax2.set_ylabel('AC'); ax2.set_title('Uncoupled GS: Dynamics'); ax2.legend()
for s, e in bounds: ax2.axvspan(s, e, alpha=0.2, color='green')

ax3 = fig.add_subplot(g[0,2])
ax3.plot(rg['f'], rg['comp'], 'o-', ms=3, color='purple')
ax3.set_xlabel('f'); ax3.set_ylabel('std(v)'); ax3.set_title('Uncoupled GS: Complexity')
for s, e in bounds: ax3.axvspan(s, e, alpha=0.2, color='green')

ax4 = fig.add_subplot(g[1,:])
ax4t = ax4.twinx()
ax4.plot(r1['f'], r1['C'], 'o-', ms=3, color='darkblue', label='C (coupled)')
ax4.axhline(0, color='gray', ls='--', lw=0.5)
ax4t.plot(rg['f'], rg['ac50'], 's-', ms=3, color='red', label='ac(50) (uncoupled)')
ax4t.axhline(0, color='red', ls='--', lw=0.5, alpha=0.3)
ax4.set_xlabel('f'); ax4.set_ylabel('C', color='darkblue')
ax4t.set_ylabel('ac(50)', color='red')
ax4.set_title('Resonance Island: Coupling Sign vs Internal Oscillatory Regime')
for s, e in bounds: ax4.axvspan(s, e, alpha=0.15, color='green')
l1, la1 = ax4.get_legend_handles_labels(); l2, la2 = ax4t.get_legend_handles_labels()
ax4.legend(l1+l2, la1+la2, loc='upper left')

ax5 = fig.add_subplot(g[2,0])
ax5.plot(r2['r'], r2['C'], 'o-', ms=3, color='darkgreen')
ax5.axhline(0, color='gray', ls='--', lw=0.5)
ax5.set_xlabel('r'); ax5.set_ylabel('C'); ax5.set_title('Logistic x Sandpile: C vs r')

ax6 = fig.add_subplot(g[2,1])
ax6.plot(r2['r'], r2['xs'], 'o-', ms=3, color='purple')
ax6.set_xlabel('r'); ax6.set_ylabel('std(x)'); ax6.set_title('Logistic: Complexity')

ax7 = fig.add_subplot(g[2,2])
ax7t = ax7.twinx()
ax7.plot(r2['r'], r2['C'], 'o-', ms=3, color='darkgreen', label='C')
ax7.axhline(0, color='gray', ls='--', lw=0.5)
ax7t.plot(r2['r'], r2['xs'], 's-', ms=3, color='purple', label='std(x)')
ax7.set_xlabel('r'); ax7.set_ylabel('C', color='darkgreen'); ax7t.set_ylabel('std(x)', color='purple')
ax7.set_title('Logistic: Coupling vs Complexity')
l1, la1 = ax7.get_legend_handles_labels(); l2, la2 = ax7t.get_legend_handles_labels()
ax7.legend(l1+l2, la1+la2, loc='upper left')

fig.suptitle('R19Z Turn 14: Fine-Grained Resonance Island Mapping (Fixed BCs)', fontsize=16, fontweight='bold')
fig.savefig('r19z_t14_scan.png', dpi=150, bbox_inches='tight')
print('Saved r19z_t14_scan.png')