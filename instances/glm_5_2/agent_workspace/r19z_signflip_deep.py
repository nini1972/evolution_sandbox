"""R19Z Phase 5v3: Sign-Flip Deep Investigation

The simple Duality Principle was FALSIFIED: both coupling signs produce anti-resonance.
This means the internal dynamics of the GS system invert the effective loop sign.

We now investigate WHY by:
1. Plotting time series for both signs side-by-side
2. Tracing the causal chain through intermediate variables
3. Testing a DIRECT sign flip: invert only ONE arm of the feedback loop
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
    def mu(s): return float(np.mean(s.u))
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

def run_full(N,coup,ns,fa,arm2_sign=None):
    """Run with full tracing. arm2_sign: if set, use different sign for SP→GS arm."""
    if arm2_sign is None: arm2_sign = coup
    gs=GS(6); sp=SP(4)
    gv,sh,gu,gx,av=[[],[],[],[],[]]
    for t in range(ns):
        f=fa*np.sin(2*np.pi*0.1*t)
        for _ in range(N):
            cx=gs.cx(); sp.thr*=0.99; sp.thr+=0.01*(1+coup*cx*0.5); sp.step()
            if abs(f)>0.1:
                for _ in range(int(abs(f)*3)):
                    x,y=np.random.randint(0,sp.size,2); sp.h[x,y]+=1
                sp.step()
        a=sp.av_log[-1] if sp.av_log else 0
        an=a/(sp.size*sp.size+1)
        gp = arm2_sign * an * 0.05 * np.ones((gs.size, gs.size)) + f * 0.01
        gs.step(p=gp)
        gv.append(gs.mv()); sh.append(sp.mh()); gu.append(gs.mu())
        gx.append(gs.cx()); av.append(a)
    return np.array(gv),np.array(sh),np.array(gu),np.array(gx),np.array(av)

# Experiment: 4 configurations
# 1. coup=+0.5, arm2=+0.5 (original positive)
# 2. coup=-0.5, arm2=-0.5 (full sign flip)
# 3. coup=+0.5, arm2=-0.5 (flip only SP→GS arm)
# 4. coup=-0.5, arm2=+0.5 (flip only GS→SP arm)

configs = [
    ("(+,+)\nBoth positive", +0.5, +0.5),
    ("(-,-)\nBoth negative", -0.5, -0.5),
    ("(+,-)\nGS→SP+, SP→GS-", +0.5, -0.5),
    ("(-,+)\nGS→SP-, SP→GS+", -0.5, +0.5),
]

fig, axes = plt.subplots(4, 3, figsize=(18, 16))

summary = []
for idx, (label, coup, arm2) in enumerate(configs):
    np.random.seed(42)
    N, A, ns = 10, 2.0, 25
    gv, sh, gu, gx, av = run_full(N, coup, ns, A, arm2)

    l, c = xc(gv[5:], sh[5:], ml=6)
    cmx = float(np.max(c)); cmn = float(np.min(c))
    absC = max(abs(cmx), abs(cmn))
    sgn = "+" if abs(cmx) > abs(cmn) else "-"

    summary.append((label, absC, cmx, cmn, sgn))
    print(f"{label.replace(chr(10),' ')}: |C|={absC:.3f} C+={cmx:.3f} C-={cmn:.3f} [{sgn}]")

    # Time series
    ax = axes[idx, 0]
    t = np.arange(len(gv))
    ax.plot(t, gv/np.max(gv+1e-10), 'b-', linewidth=1.5, label='GS v_mean', alpha=0.8)
    ax.plot(t, sh/np.max(sh+1e-10), 'r-', linewidth=1.5, label='SP height', alpha=0.8)
    ax.set_title(f'{label}\nTime Series (|C|={absC:.3f} [{sgn}])', fontsize=11, fontweight='bold')
    ax.set_xlabel('Time'); ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # Cross-correlation
    ax = axes[idx, 1]
    ax.bar(l, c, color=['#2d8659' if ci > 0 else '#c0392b' for ci in c], alpha=0.8)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_title(f'Cross-Correlation', fontsize=11)
    ax.set_xlabel('Lag'); ax.set_ylabel('C(lag)'); ax.grid(alpha=0.3)

    # Intermediate variables
    ax = axes[idx, 2]
    ax.plot(t, gv/np.max(gv+1e-10), 'b-', linewidth=1, label='v_mean', alpha=0.6)
    ax.plot(t, gu/np.max(gu+1e-10), 'g-', linewidth=1, label='u_mean', alpha=0.6)
    ax.plot(t, np.array(av)/np.max(np.array(av)+1e-10), 'm-', linewidth=1, label='avalanche', alpha=0.6)
    ax.set_title(f'Intermediate Variables', fontsize=11)
    ax.set_xlabel('Time'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.suptitle('R19Z Phase 5: Sign-Flip Deep Investigation\nWhy Does Both Signs Produce Anti-Resonance?',
             fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig('r19z_signflip_deep.png', dpi=150, bbox_inches='tight')
plt.close()

# Save summary
with open('r19z_signflip_summary.json', 'w') as f:
    json.dump([{'config': s[0], 'absC': s[1], 'Cpos': s[2], 'Cneg': s[3], 'sign': s[4]} for s in summary], f, indent=2)

print("\n=== DEEP INVESTIGATION SUMMARY ===")
for s in summary:
    print(f"  {s[0].replace(chr(10),' '):30s} |C|={s[1]:.3f} sign={s[4]}")

print("\n=== KEY FINDING ===")
# The loop gain = sign(GS→SP) * sign(SP→GS) * sign(GS internal response)
# If GS internal response is always negative (u↑→v↑ but complexity relationship is complex)
# then the overall loop sign depends on the product of both arm signs
both_pos = summary[0]
both_neg = summary[1]
flip_arm2 = summary[2]
flip_arm1 = summary[3]

print(f"Both positive (+,+): {both_pos[4]}")
print(f"Both negative (-,-): {both_neg[4]}")
print(f"Flip arm2 only (+,-): {flip_arm2[4]}")
print(f"Flip arm1 only (-,+): {flip_arm1[4]}")

if both_pos[4] == '-' and both_neg[4] == '-' and flip_arm2[4] == '+' and flip_arm1[4] == '+':
    print("\nREVISED DUALITY PRINCIPLE CONFIRMED!")
    print("The effective loop sign = sign(arm1) × sign(arm2)")
    print("Same signs → negative feedback → anti-resonance")
    print("Opposite signs → positive feedback → resonance")
elif both_pos[4] == '-' and both_neg[4] == '-':
    print("\nBoth same-sign configs → anti-resonance. Checking mixed-sign configs...")
    if flip_arm2[4] == '+' or flip_arm1[4] == '+':
        print("At least one mixed-sign config → resonance. Partial confirmation of revised principle.")
    else:
        print("Mixed-sign configs also → anti-resonance. The internal GS dynamics dominate.")
else:
    print("\nComplex behavior — need further analysis.")

print("\nDone.")
