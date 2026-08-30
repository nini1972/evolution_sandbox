"""R19Z Phase 6: Verify Revised Principle — Kuramoto-Sandpile Sign Flip

If the revised principle is correct:
- Kuramoto has positive internal response sign → resonance regardless of coupling sign
- We test both coupling signs on Kuramoto-sandpile pair
- Prediction: BOTH signs produce resonance (+)
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.set_printoptions(precision=3)

class Kuramoto:
    def __init__(s, n=12):
        s.n = n
        s.theta = np.random.uniform(0, 2*np.pi, n)
        s.omega = np.random.normal(0, 0.1, n)
        s.K = 1.5
    def step(s, dt=0.5, perturb=None):
        diff = np.sin(s.theta - s.theta[:, None])
        coupling = (s.K / s.n) * np.sum(diff, axis=1)
        s.dtheta = s.omega + coupling
        if perturb is not None:
            s.dtheta += perturb
        s.theta = (s.theta + s.dtheta * dt) % (2 * np.pi)
    def order(s):
        return float(np.abs(np.mean(np.exp(1j * s.theta))))

class SP:
    def __init__(s,sz=4):
        s.size=sz; s.thr=np.maximum(np.random.normal(4,0.5,(sz,sz)),2.0)
        s.h=np.random.uniform(0,1,(sz,sz)); s.av_log=[]
    def step(s):
        x,y=np.random.randint(0,s.size,2); s.h[x,y]+=1
        total=0
        for _ in range(15):
            m=s.h>=s.thr
            if not np.any(m): break
            total+=int(np.sum(m)); s.h-=s.thr*m.astype(float)
            m2=m.astype(float)
            s.h+=np.roll(m2,1,0)+np.roll(m2,-1,0)+np.roll(m2,1,1)+np.roll(m2,-1,1)
        s.av_log.append(total); return total
    def mh(s): return float(np.mean(s.h))

def xc(x,y,ml=10):
    x=(x-np.mean(x))/(np.std(x)+1e-10); y=(y-np.mean(y))/(np.std(y)+1e-10)
    n=len(x); lags=np.arange(-ml,ml+1); c=np.zeros(len(lags))
    for i,lag in enumerate(lags):
        if lag<0: c[i]=np.mean(x[-lag:]*y[:n+lag]) if n+lag>0 else 0
        elif lag>0: c[i]=np.mean(x[:n-lag]*y[lag:]) if n-lag>0 else 0
        else: c[i]=np.mean(x*y)
    return lags,c

def run(N,coup,ns):
    km=Kuramoto(12); sp=SP(4)
    r_vals, sh_vals = [], []
    for t in range(ns):
        for _ in range(N):
            r = km.order()
            sp.thr *= 0.99; sp.thr += 0.01 * (1 + coup * r * 0.3)
            sp.step()
        av = sp.av_log[-1] if sp.av_log else 0
        an = av / (sp.size * sp.size + 1)
        # Deterministic perturbation to Kuramoto phases
        perturb = coup * an * 0.1 * np.ones(km.n)
        km.step(perturb=perturb)
        r_vals.append(km.order())
        sh_vals.append(sp.mh())
    return np.array(r_vals), np.array(sh_vals)

# Test both signs
coups = [+0.5, -0.5]
Ns = [1, 10, 50]
results = {}

for coup in coups:
    results[coup] = {}
    for N in Ns:
        np.random.seed(42)
        rv, sh = run(N, coup, 40)
        l, c = xc(rv[5:], sh[5:], ml=8)
        cmx = float(np.max(c)); cmn = float(np.min(c))
        absC = max(abs(cmx), abs(cmn))
        sgn = "+" if abs(cmx) > abs(cmn) else "-"
        results[coup][N] = (absC, cmx, cmn, sgn)
        print(f"Kuramoto-SP coup={coup:+.1f} N={N:2d}: |C|={absC:.3f} C+={cmx:.3f} C-={cmn:.3f} [{sgn}]")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for idx, coup in enumerate(coups):
    ax = axes[idx]
    absCs = [results[coup][N][0] for N in Ns]
    sgns = [results[coup][N][3] for N in Ns]
    bars = ax.bar(range(len(Ns)), absCs, color=['#4ecdc4' if s=='+' else '#ff6b6b' for s in sgns], alpha=0.8)
    for j, bar in enumerate(bars):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.02,
                sgns[j], ha='center', va='bottom', fontsize=14, fontweight='bold',
                color='#2d8659' if sgns[j]=='+' else '#c0392b')
    ax.set_xticks(range(len(Ns)))
    ax.set_xticklabels([str(n) for n in Ns])
    ax.set_xlabel('Gap N', fontsize=13)
    ax.set_ylabel('|C|', fontsize=13)
    ax.set_ylim(0, 1.15)
    pred = "Predicted: Resonance [+]" if coup > 0 else "Predicted: Resonance [+]"
    ax.set_title(f'coup={coup:+.1f}\n{pred}', fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

plt.suptitle('R19Z Phase 6: Kuramoto-Sandpile Sign Flip Verification\nRevised Principle: Positive Internal Sign → Resonance Regardless of Coupling',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('r19z_kuramoto_signflip.png', dpi=150, bbox_inches='tight')
plt.close()

# Summary
print("\n=== KURAMOTO-SANDPILE SIGN FLIP SUMMARY ===")
for coup in coups:
    signs = [results[coup][N][3] for N in Ns]
    pos = signs.count('+')
    neg = signs.count('-')
    print(f"coup={coup:+.1f}: {pos} positive, {neg} negative")

coup_pos_all = all(results[0.5][N][3] == '+' for N in Ns)
coup_neg_all = all(results[-0.5][N][3] == '+' for N in Ns)

print(f"\nPositive coup → all resonance: {coup_pos_all}")
print(f"Negative coup → all resonance: {coup_neg_all}")
if coup_pos_all and coup_neg_all:
    print("REVISED PRINCIPLE CONFIRMED FOR KURAMOTO! ✓")
    print("Kuramoto has positive internal response sign → resonance regardless of coupling sign")
else:
    print("Results are mixed — need further investigation")

with open('r19z_kuramoto_signflip_data.json', 'w') as f:
    json.dump({str(c): {str(n): list(results[c][n]) for n in Ns} for c in coups}, f, indent=2)

print("\nDone.")
