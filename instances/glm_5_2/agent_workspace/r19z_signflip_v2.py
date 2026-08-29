"""R19Z Phase 5v2: The Sign-Flip Experiment — FIXED

The original sign-flip failed because the SP→GS coupling used zero-mean noise
(coup*an*randn()), whose sign is statistically irrelevant.

FIX: Make the SP→GS coupling DETERMINISTIC — avalanche activity directly
adds/subtracts from the u-field uniformly. Now flipping coup truly inverts
both arms of the feedback loop:
  Arm 1 (GS→SP): complexity → threshold modulation (sign flips)  
  Arm 2 (SP→GS): avalanche activity → u-field perturbation (sign flips)

Prediction (Duality Principle):
  coup > 0: negative feedback → anti-resonance (anti-phase)
  coup < 0: positive feedback → resonance (in-phase)
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.set_printoptions(precision=3)

class GS:
    def __init__(s,sz=6):
        s.size=sz; s.u=np.ones((sz,sz)); s.v=np.zeros((sz,sz))
        r=max(1,sz//4); c=sz//2; s.u[c-r:c+r,c-r:c+r]=0.5; s.v[c-r:c+r,c-r:c+r]=0.25
    def lap(s,f): return np.roll(f,1,0)+np.roll(f,-1,0)+np.roll(f,1,1)+np.roll(f,-1,1)-4*f
    def step(s,dt=1.0,p=None):
        du=0.16*s.lap(s.u)-s.u*s.v**2+0.035*(1-s.u)
        dv=0.08*s.lap(s.v)+s.u*s.v**2-0.1*s.v
        if p is not None: du+=p
        s.u=np.clip(s.u+du*dt,0,1); s.v=np.clip(s.v+dv*dt,0,1)
    def mv(s): return float(np.mean(s.v))
    def cx(s): return float(np.var(s.v))

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

def run(N,coup,ns,fa):
    gs=GS(6); sp=SP(4); gv,sh=[],[]
    for t in range(ns):
        f=fa*np.sin(2*np.pi*0.1*t)
        for _ in range(N):
            cx=gs.cx(); sp.thr*=0.99; sp.thr+=0.01*(1+coup*cx*0.5); sp.step()
            if abs(f)>0.1:
                for _ in range(int(abs(f)*3)):
                    x,y=np.random.randint(0,sp.size,2); sp.h[x,y]+=1
                sp.step()
        av=sp.av_log[-1] if sp.av_log else 0
        an=av/(sp.size*sp.size+1)
        # DETERMINISTIC perturbation: uniform across all cells
        # Positive coup: avalanches ADD to u (excitation)
        # Negative coup: avalanches SUBTRACT from u (inhibition)
        gp = coup * an * 0.05 * np.ones((gs.size, gs.size)) + f * 0.01
        gs.step(p=gp)
        gv.append(gs.mv()); sh.append(sp.mh())
    return np.array(gv),np.array(sh)

coups = [+0.5, -0.5]
As = [0.0, 2.0]
Ns = [1, 10, 50]

results = {}

for coup in coups:
    results[coup] = {}
    for A in As:
        results[coup][A] = {}
        for N in Ns:
            np.random.seed(42)
            gv, sh = run(N, coup, 25, A)
            l, c = xc(gv[5:], sh[5:], ml=6)
            cmx = float(np.max(c)); cmn = float(np.min(c))
            absC = max(abs(cmx), abs(cmn))
            sgn = "+" if abs(cmx) > abs(cmn) else "-"
            results[coup][A][N] = (absC, cmx, cmn, sgn)
            print(f"coup={coup:+.1f} A={A:.1f} N={N:2d}: |C|={absC:.3f} C+={cmx:.3f} C-={cmn:.3f} [{sgn}]")

# Plot comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for idx, coup in enumerate(coups):
    ax = axes[idx]
    data_abs = np.zeros((len(As), len(Ns)))
    data_signs = []
    for i, A in enumerate(As):
        for j, N in enumerate(Ns):
            data_abs[i,j] = results[coup][A][N][0]
            data_signs.append(results[coup][A][N][3])

    width = 0.15
    x = np.arange(len(Ns))
    colors = ['#4ecdc4', '#ff6b6b']
    for i, A in enumerate(As):
        bars = ax.bar(x + i*width, data_abs[i,:], width, label=f'A={A:.1f}', color=colors[i], alpha=0.8)
        for j, bar in enumerate(bars):
            h = bar.get_height()
            sgn = results[coup][A][Ns[j]][3]
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.02,
                    sgn, ha='center', va='bottom', fontsize=14, fontweight='bold',
                    color='#2d8659' if sgn=='+' else '#c0392b')

    label = "Positive (+0.5)\nPredicted: Anti-Resonance [-]" if coup > 0 else "Negative (-0.5)\nPredicted: Resonance [+]"
    ax.set_xlabel('Gap N', fontsize=13)
    ax.set_ylabel('|C| Cross-Correlation Magnitude', fontsize=13)
    ax.set_title(f'Coupling Sign = {label}', fontsize=13, fontweight='bold')
    ax.set_xticks(x + width/2)
    ax.set_xticklabels([str(n) for n in Ns])
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

plt.suptitle('R19Z Phase 5: The Sign-Flip Experiment (Deterministic Coupling)\nDoes Inverting Coupling Sign Convert Anti-Resonance → Resonance?',
             fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig('r19z_signflip_experiment.png', dpi=150, bbox_inches='tight')
plt.close()

# Save data
data_out = {}
for coup in coups:
    data_out[str(coup)] = {}
    for A in As:
        data_out[str(coup)][str(A)] = {}
        for N in Ns:
            data_out[str(coup)][str(A)][str(N)] = list(results[coup][A][N])

with open('r19z_signflip_data.json', 'w') as f:
    json.dump(data_out, f, indent=2)

# Summary
print("\n=== SIGN-FLIP EXPERIMENT SUMMARY (DETERMINISTIC) ===")
for coup in coups:
    signs = []
    for A in As:
        for N in Ns:
            signs.append(results[coup][A][N][3])
    pos = signs.count('+')
    neg = signs.count('-')
    label = "Anti-Resonance?" if coup > 0 else "Resonance?"
    print(f"coup={coup:+.1f} ({label}): {pos} positive [resonance], {neg} negative [anti-resonance]")

# Final verdict
coup_pos_all_neg = all(results[0.5][A][N][3] == '-' for A in As for N in Ns)
coup_neg_all_pos = all(results[-0.5][A][N][3] == '+' for A in As for N in Ns)

print(f"\n=== FALSIFICATION TEST RESULT ===")
print(f"Positive coup → all anti-resonance: {coup_pos_all_neg}")
print(f"Negative coup → all resonance:      {coup_neg_all_pos}")
if coup_pos_all_neg and coup_neg_all_pos:
    print("DUALITY PRINCIPLE CONFIRMED! ✓")
elif coup_pos_all_neg and not coup_neg_all_pos:
    print("DUALITY PRINCIPLE PARTIALLY CONFIRMED (positive→anti-res holds, sign-flip→resonance needs investigation)")
else:
    print("DUALITY PRINCIPLE NEEDS REVISION")
print("\nDone.")
