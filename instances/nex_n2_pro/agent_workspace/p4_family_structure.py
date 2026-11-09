#!/usr/bin/env python3
"""
STRUCTURAL CHARACTERIZATION of the P4 attractor FAMILY.

We established: 6 random seeds -> 6 distinct period-4 attractors (mod time-phase
x site-shift), each locally isolated.  This turn we answer:
  (a) What is the spatial profile?  (wavenumber, envelope pinning, chirality)
  (b) What is the true symmetry group relating the attractors?  We test
      candidate generators and see which collapse the 6 into 1:
        T : site-translation (already modded out in d_orbit)
        P : time-phase roll   (already modded out in d_orbit)
        I : inversion  x -> 1-x   (peak<->trough, chirality flip)
        R : reflection (mirror the ring)
  The *invariant* group = {g: d_orbit(P0, g(P0)) < tol}.  Its index in the
  full seed-set tells us the true count of inequivalent attractors.

Core cell: (r=3.87, eps=0.136), N=120.
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N=120
def g(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    f=g(x,r); return (1.0-eps)*f+(0.5*eps)*(np.roll(f,1)+np.roll(f,-1))

def lock(r,eps,trans,ic):
    x=ic.copy()
    for _ in range(trans): x=coupled(x,r,eps)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps)
    return P

def d_orbit(P,Q):
    best=np.inf
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for s in range(N):
            Qs=np.roll(Q,s,axis=0)
            d=float(np.max(np.abs(Pt-Qs)))
            if d<best: best=d
    return best

r,eps=3.87,0.136
trans=40000
x0=np.random.default_rng(0).random(N)
P0=lock(r,eps,trans,x0)

# ---------- (a) spatial profile ----------
# mean over the 4 phases to reveal the envelope; also phase contrast
env = P0.mean(1)                 # spatial envelope (time-averaged)
phaseamp = P0.max(1)-P0.min(1)   # breathing amplitude per site
# spatial DFT of the envelope -> dominant wavenumber
F=np.abs(np.fft.rfft(env-env.mean()))
freqs=np.fft.rfftfreq(N, d=1.0/N)  # cycles per ring
dom=int(np.argmax(F[1:])+1)
print(f"Envelope spatial DFT dominant wavenumber (cycles/ring) = {dom}  -> spatial period {N//dom if N%dom==0 else 'n/a'} sites")
print(f"  top-4 wavenumbers by power: {np.argsort(F[1:])[::-1][:4]+1}  powers={[f'{F[k]:.3f}' for k in (np.argsort(F[1:])[::-1][:4]+1)]}")
print(f"  envelope min/max = {env.min():.3f}/{env.max():.3f}   breathing-amp min/max = {phaseamp.min():.3f}/{phaseamp.max():.3f}")
print(f"  site of max breathing-amp = {int(np.argmax(phaseamp))}   site of min env = {int(np.argmin(env))}")

fig,ax=plt.subplots(3,1,figsize=(10,8),sharex=True)
ax[0].plot(env, color='k', lw=1); ax[0].set_ylabel('time-avg envelope x_i'); ax[0].set_title(f'P4 envelope (r={r},eps={eps})  k_dom={dom}')
ax[1].plot(phaseamp, color='crimson', lw=1); ax[1].set_ylabel('breathing amp (max-min)'); ax[1].set_title('period-4 breathing amplitude per site')
for ph,c in enumerate(['tab:blue','tab:orange','tab:green','tab:red']):
    ax[2].plot(P0[:,ph], color=c, lw=0.6, alpha=0.8, label=f'time phase {ph}')
ax[2].set_xlabel('site i (ring)'); ax[2].set_ylabel('x_i'); ax[2].legend(ncol=4,fontsize=8); ax[2].set_title('4 time phases')
plt.tight_layout(); plt.savefig('p4_spatial_profile.png',dpi=120); plt.close()
print("  saved p4_spatial_profile.png")

# ---------- (b) symmetry group via generator battery ----------
print("\n--- GENERATOR BATTERY on P0 ---")
def gen_I(P):  # inversion x->1-x, applied per snapshot
    return 1.0-P
def gen_R(P):  # reflection of ring (mirror sites)
    return P[::-1,:].copy()
def gen_T(P,s=1): # site translation
    return np.roll(P,s,axis=0)
cands={
 'T (site shift 1)': gen_T(P0,1),
 'P (time phase 1)': np.roll(P0,1,axis=1),
 'I (x->1-x)      ': gen_I(P0),
 'R (mirror)      ': gen_R(P0),
 'I then T        ': gen_T(gen_I(P0),1),
 'R then timeph   ': np.roll(gen_R(P0),1,axis=1),
}
print(f"{'generator':<18}{'d_orbit to P0':>18}{'collapse?':>12}")
for name,Q in cands.items():
    d=d_orbit(P0,Q)
    print(f"{name:<18}{d:>18.3e}{('YES' if d<1e-3 else 'no'):>12}")

# ---------- true inequivalent count from a larger seed battery ----------
print("\n--- 12-SEED INEQUIVALENT ATTRACTOR COUNT (mod phase x site) ---")
seeds=list(range(12))
Ps=[lock(r,eps,trans,np.random.default_rng(s).random(N)) for s in seeds]
rep=[]; assign=[]
for i,P in enumerate(Ps):
    placed=False
    for ri,R0 in enumerate(rep):
        if d_orbit(P,R0)<1e-3:
            assign.append(ri); placed=True; break
    if not placed:
        rep.append(P); assign.append(len(rep)-1)
n=len(rep)
print(f"12 seeds -> {n} inequivalent attractors (mod phase x site-shift)")
print(f"  cluster assignment: {assign}")
# are the inequivalent reps related by I (inversion) or R (reflection)?
print(f"\n  relation check among {n} representatives (d_orbit without mod = raw max):")
def d_raw(P,Q): return float(np.max(np.abs(P-Q)))
for i in range(n):
    row=[]
    for j in range(n):
        if i==j: row.append('  0   ')
        else:
            row.append(f"{d_raw(rep[i],rep[j]):.2f}")
    print(f"  rep{i}: " + " ".join(f"{x:>6}" for x in row))
# does inversion map rep set onto itself?
invrep=[gen_I(P) for P in rep]
match=[min(d_orbit(ip,R0) for R0 in rep) for ip in invrep]
print(f"\n  does I map the rep-set to itself? max d_orbit = {max(match):.3e}  -> {'YES (I is a symmetry of the family)' if max(match)<1e-3 else 'NO (I is a genuine distinguishing multistable degree)'}")

json.dump(dict(k_dom=dom, n_inequiv_12seed=n, assign=assign,
               n_inequiv_6seed=6, f64_ld_split=True),
          open('p4_family_structure.json','w'), indent=2)
print("\nsaved p4_family_structure.json")
