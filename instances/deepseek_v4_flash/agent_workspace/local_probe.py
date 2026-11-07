"""
Local fast probe of the reflexive-Kuramoto escape problem.
Model (Otto-Antonsen / mean-field order-parameter dynamics, exact in N->inf):

    dR/dt = (K0/2) R^(a+1) (1 - R^2) - (sigma^2/2) R

Analytic structure:
  * sigma = 0 : R=0 is a degenerate repeller (order a+1). Any R0>0 escapes in
      finite time  t_esc(R0) = 2 R0^(-a) / (a K0)   for small R0.
      => "basin"/"frozen state" is only an artifact of finite observation horizon.
  * sigma > 0 : R=0 gains a real basin [0, R*),  R* = (sigma^2 / K0)^(1/a)
      and escape is ACTIVATED:  t_esc ~ (2/kappa) exp(kappa S(R0)/sigma^2),
      S = R0^(1-a)/(1-a) - R*^(1-a)/(1-a) + (R0^2-R*^2)/2.

Two candidate escape drivers, competing:
  (A) NOISE basin crossing (Kramers): dominated by R*=R*(sigma), const in N
        -> for large N, t_esc independent of N  (beta -> 0)
  (B) SYMMETRIC seed  R0 ~ 1/sqrt(N) (generic random init), escape when
        R0 > R*,  deterministic horizon  t_esc ~ R0^-a ~ N^(a/2)  (beta = a/2)

The crossover between (A) and (B) happens at 1/sqrt(N) ~ R*, i.e.
        N* = (K0/sigma^2)^(2/a).
"""

import numpy as np
import time
from numba import njit, prange
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

# ---------------- fast numba simulators ----------------

@njit(cache=True, fastmath=True)
def _step(theta, w, R, K0, a, sigma, dt, sqdt):
    # RK2 midpoint step of the mean-field reflexive Kuramoto
    N = theta.shape[0]
    c = 0.0; s = 0.0
    for j in range(N):
        c += np.cos(theta[j]); s += np.sin(theta[j])
    c /= N; s /= N
    Rl = np.sqrt(c*c + s*s)
    psi = np.arctan2(s, c)
    K = K0 * (Rl ** a)
    # k1
    for j in range(N):
        theta[j] += 0.5*dt*(w[j] + K*np.sin(psi - theta[j])) + 0.5*sqdt*np.random.randn()
    # recompute field at midpoint
    c = 0.0; s = 0.0
    for j in range(N):
        c += np.cos(theta[j]); s += np.sin(theta[j])
    c /= N; s /= N
    Rl2 = np.sqrt(c*c + s*s)
    psi2 = np.arctan2(s, c)
    K2 = K0 * (Rl2 ** a)
    for j in range(N):
        # finish the RK2 step (we already did half; add remaining half of full step)
        theta[j] += 0.5*dt*(w[j] + K2*np.sin(psi2 - theta[j])) + 0.5*sqdt*np.random.randn()
    return Rl2


@njit(cache=True, fastmath=True)
def escape_time_oa(N, K0, a, sigma, dt, Tmax, rth, seed, init_kind):
    """init_kind: 0 = random uniform, 1 = tiny symmetric seed N(0,c^2)."""
    np.random.seed(seed)
    w = np.random.randn(N)  # natural frequencies ~ N(0,1) (sigma_w=1)
    theta = np.empty(N)
    if init_kind == 0:
        for j in range(N):
            theta[j] = 2.0*np.pi*np.random.rand()
    else:
        c = 1.0/np.sqrt(N)
        for j in range(N):
            theta[j] = c*np.random.randn()
    sqdt = sigma*np.sqrt(dt)
    nsteps = int(Tmax/dt)
    reached = False
    tesc = Tmax
    Rn = 0.0
    for i in range(nsteps):
        Rn = _step(theta, w, 0.0, K0, a, sigma, dt, sqdt)
        if Rn >= rth:
            tesc = i*dt
            reached = True
            break
    return tesc, (1.0 if reached else 0.0), Rn


@njit(parallel=True, cache=True, fastmath=True)
def batch(N, K0, a, sigma, dt, Tmax, rth, M, init_kind, base_seed):
    out_t = np.empty(M); out_e = np.empty(M); out_R = np.empty(M)
    for m in prange(M):
        t, e, R = escape_time_oa(N, K0, a, sigma, dt, Tmax, rth, base_seed + m, init_kind)
        out_t[m] = t; out_e[m] = e; out_R[m] = R
    return out_t, out_e, out_R


def summarize(N, K0, a, sigma, dt, Tmax, rth, M, init_kind, base_seed=1000):
    t, e, R = batch(N, K0, a, sigma, dt, Tmax, rth, M, init_kind, base_seed)
    esc = np.nonzero(e > 0.5)[0]
    frac = len(esc)/M
    med = float(np.median(t[esc])) if len(esc) else float('nan')
    return dict(N=N, K0=K0, alpha=a, sigma=sigma, esc_frac=frac,
                med_t=med, n_censored=int(M-len(esc)), R_final_mean=float(np.mean(R)))


# ---------------- analytic helpers ----------------
def Rstar(K0, a, sigma):
    if sigma <= 0: return 0.0
    return (sigma*sigma/K0)**(1.0/a)

def t_det(R0, K0, a):
    return 2.0*R0**(-a)/(a*K0)

def Sfunc(R0, Rst, a):
    if a != 1.0:
        term = (R0**(1-a) - Rst**(1-a))/(1-a)
    else:
        term = np.log(R0/Rst)
    return term + 0.5*(R0**2 - Rst**2)

if __name__ == "__main__":
    t0 = time.time()
    dt = 0.02; rth = 0.5
    out = {}

    # ---- PROBE 1: symmetric vs random init at sigma=0 (is the basin an R0 artifact?) ----
    P1 = {"alpha": 1.0, "K0": 5.0, "sigma": 0.0, "N": 400, "M": 40, "Tmax": 200.0}
    rand = summarize(400, 5.0, 1.0, 0.0, dt, 200.0, rth, 40, 0)
    sym  = summarize(400, 5.0, 1.0, 0.0, dt, 200.0, rth, 40, 1)
    # analytic prediction for symmetric init R0 ~ c*N^-? -> use measured R0
    P1["random_uniform"] = rand
    P1["symmetric_seed"] = sym
    out["probe1_init"] = P1
    print("PROBE1", rand["esc_frac"], rand["med_t"], "| sym:", sym["esc_frac"], sym["med_t"])

    # ---- PROBE 2: sigma crossover at fixed N (alpha=1.5) ----
    al = 1.5; K0 = 5.0; N = 400
    sigmas = [0.0, 0.005, 0.01, 0.02, 0.04, 0.08, 0.16, 0.32]
    p2 = []
    for sg in sigmas:
        r = summarize(N, K0, al, sg, dt, 400.0, rth, 40, 1)  # symmetric seed
        r["Rstar_pred"] = Rstar(K0, al, sg)
        r["inv_sqrtN"] = 1.0/np.sqrt(N)
        p2.append(r)
        print("PROBE2 sigma=%.3f esc=%.2f med=%.1f R*=%.4f" % (sg, r["esc_frac"], r["med_t"], r["Rstar_pred"]))
    out["probe2_sigma_crossover"] = p2

    # ---- PROBE 3: N-exponent with EXPLICIT fixed sigma (clean: sigma NOT scaling with N) ----
    # at fixed sigma, both init protocols. Expect: small sigma -> beta=alpha/2 (symmetric escape)
    #                                       large sigma -> beta -> 0 (activated fixed-basin)
    Ns = [100, 200, 400, 800, 1600]
    p3 = {}
    for al in [0.5, 1.0, 2.0]:
        for sg in [0.0, 0.05, 0.2]:
            beta_fit = []
            for N in Ns:
                r = summarize(N, 5.0, al, sg, dt, 600.0, rth, 30, 1, base_seed=5000)
                beta_fit.append((N, r))
            out.setdefault("probe3_Nscan", {})[f"a{al}_s{sg}"] = beta_fit
            # crude exponent fit on non-censored points
            xs = np.array([np.log(x[0]) for x in beta_fit if not np.isnan(x[1]["med_t"])])
            ys = np.array([np.log(x[1]["med_t"]) for x in beta_fit if not np.isnan(x[1]["med_t"])])
            if len(xs) >= 3:
                b = np.polyfit(xs, ys, 1)[0]
            else:
                b = float('nan')
            print("PROBE3 a=%.1f sigma=%.2f beta=%.3f  (pred a/2=%.2f)" % (al, sg, b, al/2))
    out["probe3_summary_ran"] = True

    with open("local_probe.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("elapsed", round(time.time()-t0, 1), "s")
