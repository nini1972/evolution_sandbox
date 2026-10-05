import numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
N = 2000; dt = 0.02; T = 40.0; nsteps = int(T/dt)
gammas = [0.5, 1.0, 2.0]

def closed_I(B, g):
    # exact integral of lorentzian * sin contribution:  g * (1 - 1/sqrt(1+B^2)) ... normalize
    return (np.sqrt(1+B*B) - 1.0)/B  # = B/(sqrt(1+B^2)+1), times g? define per-unit gamma below

def flow(a, K, R, g):
    """theta-dot-mean-field on R using Ott-Antonsen: dR = (g/2)( (1-a)R - K R^{1+a} (R^2-1)/2 ... )"""
    # OA: dR/dt = -g R + (g/2) * (1 - R^2) * K R^a   (Lorentzian, Pieter's form)  -> times?
    # Standard OA with K R^a:  dR = -g R + (g/2)(1 - R^2) K R^a
    return -g*R + 0.5*g*(1-R*R)*K*(R**a)

def equilibrium_R(a, K, g, Rgrid):
    """roots of dR=0; returns array of (R, stability)"""
    dR = flow(a, K, Rgrid, g)
    roots = []
    for i in range(len(Rgrid)-1):
        if dR[i]*dR[i+1] < 0:
            R0 = Rgrid[i] - dR[i]*(Rgrid[i+1]-Rgrid[i])/(dR[i+1]-dR[i])
            # stability: derivative of flow wrt R
            eps=1e-5; f0 = flow(a,K,R0,g)
            fp = (flow(a,K,R0+eps,g)-flow(a,K,R0-eps,g))/(2*eps)
            roots.append((R0, fp<0))
    # also check R=0 fixed point: stable if f'(0)<0 => -g + g K /2 (1) * (0^a)... for a>0 f'(0)=-g stable; a<0 singular
    return roots

# --- theory vs simulation, supercritical a=-1 ---
print("=== Theory branch check (g=1) ===")
for a in [-1.0, -0.5, 0.0, 0.5, 1.0]:
    Kc = (1.0-a)  # from dR=0 at R->0: -g + g/2*(1-R^2) K R^a ~ -1 + K R^a/2 ... a<0 diverges-like; Kc ~ (1-a)/... 
    print(f"a={a:+.1f} Kc_theory={(1-a)/2:.3f}")

# --- sim: escape time tau for supercritical a=-1, K slightly above/below Kc ---
def sim_escape(a, K, g, seeds=8):
    taus = []
    for s in range(seeds):
        r = rng.normal(0,1,N); th = rng.uniform(-np.pi, np.pi, N)
        R = abs(np.mean(np.exp(1j*th)))
        tau = None
        for i in range(nsteps):
            z = np.mean(np.exp(1j*th))
            R = abs(z)
            w = rng.standard_cauchy(N)*g
            th = th + dt*(w + K*(R**a)*np.imag(np.exp(-1j*th)*z))
            th = (th+np.pi)%(2*np.pi)-np.pi
            if R > 0.8 and tau is None: tau = i*dt; break
        taus.append(tau if tau else np.inf)
    return np.array(taus)

results = {}
for g in gammas:
    for a in [-0.5, 0.0, 0.5]:
        Kc = (1-a)/2
        for eps in [0.05, 0.2]:
            K = Kc*(1+eps)
            taus = sim_escape(a, K, g, seeds=12)
            med = np.median(taus[taus<np.inf])
            frac = np.mean(np.isfinite(taus))
            results[f"a={a},g={g},eps={eps}"] = {"K":K,"Kc":Kc,"median_tau":med,"frac_escaped":frac}
            print(f"a={a:+.1f} g={g} eps={eps:+.2f} K/Kc={K/Kc:.3f} med_tau={med:7.2f} frac={frac:.2f}")

with open("reflexive_sanity.json","w") as f: json.dump(results,f,indent=1)

# --- figure: OA flow curves for a=0.5 (barrier case) ---
fig, ax = plt.subplots(1,2,figsize=(13,5))
Rg = np.linspace(0.001,1,600)
for a,Kcut in [(-0.5,0.9),(0.5,0.95)]:
    ax0 = ax[0 if a<0 else 1]
    for K in [0.3,0.6,0.9,1.2,2.0]:
        dR = flow(a,K,Rg,1.0)
        ax0.plot(Rg,dR,label=f"K={K}")
    ax0.axhline(0,color='k',lw=0.6); ax0.set_title(f"OA flow dR/dt, a={a:+.1f}"); ax0.legend(fontsize=7)
    ax0.set_xlabel("R"); ax0.set_ylabel("dR/dt")
fig.tight_layout(); fig.savefig("reflexive_OA_flow.png",dpi=110)
print("saved figure, done")