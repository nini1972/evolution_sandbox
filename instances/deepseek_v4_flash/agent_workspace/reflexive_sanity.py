import numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
dt = 0.02

# ---------- OA theory ----------
def oa_flow(a, K, R, Delta=1.0):
    return -Delta*R + 0.5*K*(1-R*R)*(R**(a+1.0))

def branch_R(a, K, Delta=1.0):
    """solutions of K R^a (1-R^2) = 2Delta  (stationary R of OA)"""
    Rg = np.linspace(1e-4, 1-1e-4, 4000)
    lhs = K*(Rg**a)*(1-Rg*Rg)
    d = lhs - 2*Delta
    roots = []
    for i in range(len(Rg)-1):
        if d[i]*d[i+1] < 0:
            r = Rg[i] - d[i]*(Rg[i+1]-Rg[i])/(d[i+1]-d[i])
            roots.append(r)
    return np.array(roots)

def K_sn(a, Delta=1.0):
    """saddle-node K for a>0: K_sn = 2Delta / M(a), M=max R^a(1-R^2)"""
    if a <= 0: return None
    Rg = np.linspace(1e-4, 1-1e-4, 8000)
    M = np.max(Rg**a*(1-Rg*Rg))
    return 2*Delta/M

print("=== OA branch structure (Delta=1) ===")
for a in [-1.0, -0.5, 0.0, 0.5, 1.0]:
    if a > 0:
        print(f"a={a:+.1f}  K_sn={K_sn(a):.4f}")
    else:
        for K in [0.5, 1.0, 2.0]:
            roots = branch_R(a, K)
            print(f"a={a:+.1f}  K={K:.1f}  R_ss={roots}")
print("a=0: K_c=2.0 (pitchfork); R=sqrt(1-2/K)")

# ---------- N-particle sim: quenched Lorentzian, reflexive coupling ----------
def sim_rss(a, K, N=4000, T=60.0, seeds=4):
    out = []
    nsteps = int(T/dt)
    for s in range(seeds):
        th = rng.uniform(-np.pi, np.pi, N)
        om = rng.standard_cauchy(N)  # Lorentzian width 1
        R = 0.0
        for i in range(nsteps):
            z = np.mean(np.exp(1j*th))
            R = abs(z)
            keff = K*(R**a)
            th = th + dt*(om + keff*np.imag(np.exp(-1j*th)*z))
            th = (th+np.pi)%(2*np.pi)-np.pi
        out.append(R)
    return np.mean(out)

print("\n=== sim R_ss vs OA branch ===")
comp = {}
for a in [-0.5, 0.0, 0.5]:
    for K in [0.5, 1.0, 2.0]:
        r_sim = sim_rss(a, K)
        r_oa = branch_R(a, K)
        comp[f"a={a},K={K}"] = {"sim_R": r_sim, "OA_R": list(r_oa)}
        print(f"a={a:+.1f} K={K:.1f}  sim R={r_sim:.3f}  OA R={r_oa}")

with open("reflexive_sanity.json","w") as f: json.dump(comp, f, indent=1)

# ---------- escape dynamics (horizon) ----------
def sim_escape(a, K, N, Rtarget=0.6, T=200.0):
    """time for R to first cross Rtarget from incoherence; inf if not by T"""
    nsteps = int(T/dt)
    th = rng.uniform(-np.pi, np.pi, N)
    om = rng.standard_cauchy(N)
    tau = np.inf
    for i in range(nsteps):
        z = np.mean(np.exp(1j*th))
        R = abs(z)
        keff = K*(R**a)
        th = th + dt*(om + keff*np.imag(np.exp(-1j*th)*z))
        th = (th+np.pi)%(2*np.pi)-np.pi
        if R > Rtarget: tau = i*dt; break
    return tau

print("\n=== horizon: median escape time (a<0 supercritical vs a>0 metastable) ===")
hor = {}
for a in [-0.5, 0.5, 1.0]:
    Kset = [0.8, 1.5, 3.0]
    if a > 0:
        ks = K_sn(a)
        Kset = [0.85*ks, 0.95*ks, ks*1.05]
    for K in Kset:
        taus = [sim_escape(a, K, 2000) for _ in range(6)]
        med = float(np.median(taus))
        frac = float(np.mean(np.isfinite(taus)))
        hor[f"a={a},K={K:.3f}"] = {"med_tau": med, "frac_fin": frac}
        print(f"a={a:+.1f} K={K:.3f}  med_tau={med:8.2f}  frac={frac:.2f}")

with open("reflexive_horizon_sanity.json","w") as f: json.dump(hor, f, indent=1)

# ---------- figure ----------
fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
Rg = np.linspace(0.001, 0.999, 500)
for j, a in enumerate([-0.5, 0.0, 0.5]):
    for K in [0.5, 1.0, 1.5, 2.0, 3.0]:
        ax[j].plot(Rg, oa_flow(a, K, Rg), lw=1.0, label=f"K={K}")
    ax[j].axhline(0, color='k', lw=0.5)
    ax[j].set_title(f"OA dR/dt, a={a:+.1f}")
    ax[j].set_xlabel("R"); ax[j].legend(fontsize=6)
fig.tight_layout(); fig.savefig("reflexive_OA_flow.png", dpi=110)
print("\nsaved figure")