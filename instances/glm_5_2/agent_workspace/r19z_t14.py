# R19Z Turn 14: Fixed fine scan - compact version
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

class BTW:
    def __init__(self, size=6):
        self.size = size
        self.h = np.zeros((size, size), dtype=float)
        self.thr = 4.0
    def step(self, mod=0.0):
        self.thr = max(1.0, 4.0 + mod)
        si = (np.random.randint(self.size), np.random.randint(self.size))
        self.h[si] += 1.0
        total = 0; q = [si]; vis = set()
        while q:
            s = q.pop(0)
            if s in vis: continue
            vis.add(s)
            if self.h[s] >= self.thr:
                self.h[s] -= self.thr; total += 1
                for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ni, nj = s[0]+di, s[1]+dj
                    if 0 <= ni < self.size and 0 <= nj < self.size:
                        self.h[ni, nj] += 1.0; q.append((ni, nj))
                    elif di or dj: total += 1
        return total

def lap(a):
    return np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)-4*a

def gs_step(u, v, Du, Dv, f, k, dt=1.0):
    uvv = u*v*v
    u2 = u + dt*(Du*lap(u) - uvv + f*(1.0-u))
    v2 = v + dt*(Dv*lap(v) + uvv - (f+k)*v)
    return np.clip(u2,0,1), np.clip(v2,0,1)

def xc(a, b, ml=20):
    a = a - np.mean(a); b = b - np.mean(b)
    if np.std(a) < 1e-10 or np.std(b) < 1e-10: return 0.0, 0
    cs = []
    for lag in range(-ml, ml+1):
        if lag < 0: c = np.corrcoef(a[-lag:], b[:len(b)+lag])[0,1]
        elif lag > 0: c = np.corrcoef(a[:len(a)-lag], b[lag:])[0,1]
        else: c = np.corrcoef(a, b)[0,1]
        cs.append(0.0 if np.isnan(c) else c)
    cs = np.array(cs); i = np.argmax(np.abs(cs))
    return float(cs[i]), list(range(-ml,ml+1))[i]

def ac(x, lag):
    x = x - np.mean(x)
    if np.std(x) < 1e-10 or lag >= len(x): return 0.0
    c = np.corrcoef(x[:len(x)-lag], x[lag:])[0,1]
    return 0.0 if np.isnan(c) else float(c)

def run_gs_sp(f, k=0.062, N=10, T=1000, seed=42):
    np.random.seed(seed); sz = 12
    u = np.ones((sz, sz)); v = np.zeros((sz, sz))
    u[4:8, 4:8] = 0.5; v[4:8, 4:8] = 0.25
    sp = BTW(6); gc = []; sa = []; sc = 0
    for t in range(T):
        u, v = gs_step(u, v, 0.16, 0.08, f, k)
        if sc > 0 and sa:
            u = np.clip(u + sa[-1]*0.001*(np.random.rand(sz,sz)-0.5), 0, 1)
        gc.append(float(np.var(v)))
        sc += 1
        if sc >= N:
            sc = 0
            av = sp.step(mod=-0.5*(gc[-1]-0.01))
            sa.append(float(av))
        else:
            sa.append(sa[-1]*0.9 if sa else 0.0)
    return np.array(gc), np.array(sa)

def run_gs(f, k=0.062, T=1000, seed=42):
    np.random.seed(seed); sz = 12
    u = np.ones((sz, sz)); v = np.zeros((sz, sz))
    u[4:8, 4:8] = 0.5; v[4:8, 4:8] = 0.25
    c = []; vm = []
    for t in range(T):
        u, v = gs_step(u, v, 0.16, 0.08, f, k)
        c.append(float(np.var(v))); vm.append(float(np.mean(v)))
    return np.array(c), np.array(vm)

def run_log_sp(r, N=20, T=1000, seed=42):
    np.random.seed(seed)
    sp = BTW(6); x = 0.5; lx = []; sa = []; sc = 0
    for t in range(T):
        x = r*x*(1-x); x = np.clip(x, 1e-10, 1-1e-10)
        lx.append(x); sc += 1
        if sc >= N:
            sc = 0
            av = sp.step(mod=0.5*(x-0.5)); sa.append(float(av))
        else:
            sa.append(sa[-1]*0.9 if sa else 0.0)
    return np.array(lx), np.array(sa)

# === Exp 1: GS x Sandpile ===
print('Exp 1: GS x Sandpile fine f scan')
fs = np.linspace(0.055, 0.085, 31)
N=10; T=1000; ns=2
r1 = {'f':[], 'C':[], 'Cs':[], 'comp':[], 'sign':[]}
rg = {'f':[], 'ac10':[], 'ac50':[], 'comp':[], 'vm':[]}
for i, f in enumerate(fs):
    Cs=[]; comps=[]
    for sd in range(42, 42+ns):
        gc, sa = run_gs_sp(f, N=N, T=T, seed=sd)
        s = int(T*0.2)
        C, lag = xc(gc[s:], sa[s:], ml=20)
        Cs.append(C); comps.append(float(np.mean(gc[s:])))
    cm = float(np.mean(Cs))
    r1['f'].append(float(f)); r1['C'].append(cm)
    r1['Cs'].append(float(np.std(Cs))); r1['comp'].append(float(np.mean(comps)))
    r1['sign'].append(1 if cm > 0 else -1)
    uc, vm = run_gs(f, T=T)
    s2 = int(T*0.2)
    rg['f'].append(float(f))
    rg['ac10'].append(ac(uc[s2:], 10)); rg['ac50'].append(ac(uc[s2:], 50))
    rg['comp'].append(float(np.mean(uc[s2:]))); rg['vm'].append(float(np.mean(vm[s2:])))
    if i % 6 == 0:
        print(f'  f={f:.4f}: C={cm:.4f}, ac50={rg["ac50"][-1]:.4f}, comp={rg["comp"][-1]:.6f}')

# Islands
sg = r1['sign']; bounds = []; inside = False
for i, s in enumerate(sg):
    if s > 0 and not inside: st = r1['f'][i]; inside = True
    elif s < 0 and inside: bounds.append((st, r1['f'][i-1])); inside = False
if inside: bounds.append((st, r1['f'][-1]))
print(f'Islands: {bounds}')

# === Exp 2: Logistic x Sandpile ===
print('Exp 2: Logistic x Sandpile fine r scan')
rs = np.linspace(2.8, 4.0, 41)
r2 = {'r':[], 'C':[], 'Cs':[], 'xs':[], 'sign':[]}
for i, r in enumerate(rs):
    Cs=[]; xss=[]
    for sd in range(42, 44):
        lx, sa = run_log_sp(r, T=1000, seed=sd)
        s = int(1000*0.2)
        C, lag = xc(lx[s:], sa[s:], ml=20)
        Cs.append(C); xss.append(float(np.std(lx[s:])))
    cm = float(np.mean(Cs))
    r2['r'].append(float(r)); r2['C'].append(cm)
    r2['Cs'].append(float(np.std(Cs))); r2['xs'].append(float(np.mean(xss)))
    r2['sign'].append(1 if cm > 0 else -1)
    if i % 8 == 0:
        print(f'  r={r:.4f}: C={cm:.4f}, xs={r2["xs"][-1]:.4f}')

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
ax3.set_xlabel('f'); ax3.set_ylabel('Var(v)'); ax3.set_title('Uncoupled GS: Complexity')
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
ax5.errorbar(r2['r'], r2['C'], yerr=r2['Cs'], fmt='o-', ms=3, capsize=2, color='darkgreen')
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

fig.suptitle('R19Z Turn 14: Fine-Grained Resonance Island Mapping', fontsize=16, fontweight='bold')
fig.savefig('r19z_t14_scan.png', dpi=150, bbox_inches='tight')
print('Saved r19z_t14_scan.png')
