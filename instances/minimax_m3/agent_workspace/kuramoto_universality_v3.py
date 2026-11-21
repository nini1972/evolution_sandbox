"""
Kuramoto Universal Coordinates — v3
====================================

Going beyond Lorentzian: do the Adler exponents (sigma = 1/2,
universal collapse) survive on NON-LORENTZIAN substrates?

Hypothesis (from DOSSIER-UK-L3, Sakaguchi 1988, Crawford 1995):
  - For ANY symmetric unimodal g(omega), K_c = 2/(pi g(0))
  - Critical exponent sigma = 1/2 (mean-field, independent of g shape)
  - Universal coordinate: u = (K-K_c)/(K_c)   (NOT divided by Delta)

Substrates tested:
  1. Lorentzian  g(0) = 1/(pi*Delta)            → K_c = 2 Delta
  2. Gaussian    g(0) = 1/(sqrt(2pi)*sigma_w)   → K_c = 2 sigma_w * sqrt(2/pi)
  3. Uniform     g(omega) = 1/(2 gamma)         → K_c = gamma/pi ... wait: K_c = 4/(pi*g(0)) hmm

Actually: K_c = 2/(pi*g(0)) for any symmetric g.
  Lorentzian: g(0) = Delta/pi → K_c = 2/Delta  NO WAIT
  g_L(omega) = (Delta/pi)/(omega^2 + Delta^2) → g_L(0) = 1/(pi*Delta)
  K_c = 2/(pi * g_L(0)) = 2/(pi * 1/(pi*Delta)) = 2 Delta ✓

  Gaussian: g_G(0) = 1/(sqrt(2 pi) sigma_w) → K_c = 2 sqrt(2 pi) sigma_w ≈ 5.013 sigma_w

Output: kuramoto_v3_universality_test.png + .json
"""

import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad

# --- Densities ---------------------------------------------------------
def g_lor(omega, Delta):
    return (1/np.pi) * Delta / (omega**2 + Delta**2)

def g_gauss(omega, sigma):
    return np.exp(-omega**2 / (2*sigma**2)) / (sigma * np.sqrt(2*np.pi))

def g_uniform(omega, gamma):
    return np.where(np.abs(omega) <= gamma, 1/(2*gamma), 0.0)

# --- Self-consistency (parameterized by g(omega)) ----------------------
def S_integral_general(x, g_func, **g_kwargs):
    def integrand(theta):
        s = np.sin(theta)
        c2 = np.cos(theta)**2
        return c2 * g_func(-x * s, **g_kwargs) * x
    val, _ = quad(integrand, -np.pi/2, np.pi/2, limit=300)
    return val

def fixed_point_r(K, g_func, g0, tol=1e-13, max_iter=400, **g_kwargs):
    """Iterate r_{n+1} = S(K r_n) where K_c = 2/(pi*g(0))."""
    K_c = 2 / (np.pi * g0)
    if K <= K_c:
        return 0.0
    x = 1.0  # warm start above threshold
    for _ in range(max_iter):
        Sx = S_integral_general(x, g_func, **g_kwargs)
        new_x = K * Sx
        if new_x <= 0:
            new_x = 1e-15
        if abs(new_x - x) < tol:
            x = new_x
            break
        x = 0.5*x + 0.5*new_x
    return x / K

def scan_curve(g_func, g0, K_c, scale=3.0, npts=50, **g_kwargs):
    # Dense near threshold for critical-exponent extraction,
    # sparser far above for universal Adler collapse.
    Ks_near = np.linspace(K_c*1.002, K_c*1.30, 30)
    Ks_far  = np.linspace(K_c*1.30, scale*K_c, npts)
    Ks = np.concatenate(([K_c*0.3, K_c*0.7], Ks_near, Ks_far))
    Ks = np.unique(Ks)
    rs = np.array([fixed_point_r(K, g_func, g0, **g_kwargs) for K in Ks])
    return Ks, rs

def extract_sigma(Ks, rs, K_c, window_frac=0.15):
    mask = (Ks > K_c * 1.001) & (Ks < K_c*(1+window_frac)) & (rs > 1e-4)
    if mask.sum() < 4:
        mask = (Ks > K_c * 1.001) & (Ks < K_c*1.3) & (rs > 1e-4)
    if mask.sum() < 4:
        return np.nan, np.nan
    x = Ks[mask] - K_c
    y = rs[mask]
    slope, intercept = np.polyfit(np.log(x), np.log(y), 1)
    return slope, intercept

# --- Simulation --------------------------------------------------------
def simulate_kuramoto(theta0, omega, K, dt=0.05, T=120, transient=80):
    theta = np.array(theta0, dtype=np.float64)
    N = len(theta)
    steps = int(T/dt); skip = int(transient/dt)
    rs = np.zeros(steps - skip)
    for s in range(steps):
        z = np.mean(np.exp(1j*theta)); r = np.abs(z); psi = np.angle(z)
        dtheta = omega + K*r*np.sin(psi - theta)
        if s >= skip:
            rs[s - skip] = r
        th2 = theta + 0.5*dt*dtheta
        z2 = np.mean(np.exp(1j*th2)); r2 = np.abs(z2); psi2 = np.angle(z2)
        k2 = omega + K*r2*np.sin(psi2 - th2)
        th3 = theta + 0.5*dt*k2
        z3 = np.mean(np.exp(1j*th3)); r3 = np.abs(z3); psi3 = np.angle(z3)
        k3 = omega + K*r3*np.sin(psi3 - th3)
        th4 = theta + dt*k3
        z4 = np.mean(np.exp(1j*th4)); r4 = np.abs(z4); psi4 = np.angle(z4)
        k4 = omega + K*r4*np.sin(psi4 - th4)
        theta = theta + (dt/6)*(dtheta + 2*k2 + 2*k3 + k4)
    return rs

# --- Main --------------------------------------------------------------
if __name__ == "__main__":
    print("="*68)
    print("KURAMOTO v3 — UNIVERSALITY OF ADLER EXPONENT ACROSS g(omega)")
    print("="*68)

    # Substrate specifications
    substrates = [
        {"name": "Lorentzian (Δ=1)",  "func": g_lor,    "g0": 1/np.pi,
         "kwargs": {"Delta": 1.0},     "label": "Lorentzian"},
        {"name": "Gaussian (σ=1)",    "func": g_gauss,  "g0": 1/np.sqrt(2*np.pi),
         "kwargs": {"sigma": 1.0},     "label": "Gaussian"},
        {"name": "Uniform (γ=2)",     "func": g_uniform,"g0": 1/4,
         "kwargs": {"gamma": 2.0},     "label": "Uniform"},
        {"name": "Lorentzian (Δ=2)",  "func": g_lor,    "g0": 1/(2*np.pi),
         "kwargs": {"Delta": 2.0},     "label": "Lorentzian Δ=2"},
    ]

    results = []
    for s in substrates:
        K_c = 2 / (np.pi * s["g0"])
        Ks, rs = scan_curve(s["func"], s["g0"], K_c, **s["kwargs"])
        sigma, _ = extract_sigma(Ks, rs, K_c)
        results.append({"name": s["name"], "K_c": K_c, "K": Ks.tolist(),
                        "r": rs.tolist(), "sigma": sigma,
                        "label": s["label"]})
        print(f"  {s['name']:22s}  K_c={K_c:.4f}   σ(fit)={sigma:.4f}  (theory: 0.500)")

    # Empirical validation on Gaussian substrate
    print("\n[B] Empirical validation: Gaussian σ_ω=1 (N=4000)")
    rng = np.random.default_rng(11)
    omega_g = rng.standard_normal(4000)
    theta0  = rng.uniform(-np.pi, np.pi, 4000)
    K_g_c_th = 2*np.sqrt(2*np.pi)  # ≈ 5.013
    emp = []
    for K in (5.5, 6.0, 7.0, 8.0, 10.0):
        rs = simulate_kuramoto(theta0, omega_g, K, dt=0.04, T=100, transient=70)
        r_sim = float(np.mean(rs[-300:]))
        r_th  = fixed_point_r(K, g_gauss, 1/np.sqrt(2*np.pi), sigma=1.0)
        emp.append({"K": K, "r_sim": r_sim, "r_th": r_th, "err": abs(r_sim-r_th)})
        print(f"  K={K:.2f}  K/K_c={K/K_g_c_th:.3f}  r_sim={r_sim:.4f}  r_th={r_th:.4f}")

    # Universal coordinate collapse
    print("\n[C] Universal coordinate collapse test:")
    print("    u = (K-K_c)/K_c  →  r* = (2/pi) sqrt(u)  (Adler universal)")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))

    # Panel A: r*(K) per substrate
    ax = axes[0]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for c, d in zip(colors, results):
        ax.plot(d["K"], d["r"], 'o-', color=c, label=d["label"], ms=3)
        ax.axvline(d["K_c"], color=c, ls=':', alpha=0.4)
    ax.set_xlabel("K"); ax.set_ylabel("r*")
    ax.set_title("(A) Fixed-point r*(K): K_c depends on g(0)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Panel B: Adler universal collapse — all substrates should fall on r*=(2/pi)*sqrt(u)
    ax = axes[1]
    for c, d in zip(colors, results):
        u = (np.array(d["K"]) - d["K_c"]) / d["K_c"]
        r = np.array(d["r"])
        mask = u > 0
        ax.plot(u[mask], r[mask], 'o', color=c, label=d["label"], ms=3)
    u_t = np.linspace(0, 1.5, 300)
    r_adler = (2/np.pi) * np.sqrt(u_t)
    ax.plot(u_t, r_adler, 'k--', lw=2, label="Adler: r=(2/π)√u")
    ax.set_xlabel("universal u = (K-K_c)/K_c")
    ax.set_ylabel("r*")
    ax.set_title("(B) Adler UNIVERSAL collapse (all g)?")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_xlim(0, 1.0)

    # Panel C: sim vs theory (Gaussian)
    ax = axes[2]
    Ks = [d["K"] for d in emp]
    ax.plot(Ks, [d["r_sim"] for d in emp], 'bo-', label="RK4 sim (N=4000)")
    ax.plot(Ks, [d["r_th"] for d in emp], 'r^--', label="Fixed-point theory")
    ax.axvline(K_g_c_th, color='gray', ls=':', label=f"K_c={K_g_c_th:.3f} (Gaussian)")
    ax.set_xlabel("K"); ax.set_ylabel("r")
    ax.set_title("(C) Gaussian substrate: sim vs theory")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.suptitle("Kuramoto Universality v3: σ = 1/2 should be invariant across g(ω)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("kuramoto_v3_universality_test.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("\nSaved kuramoto_v3_universality_test.png")

    with open("kuramoto_v3_metrics.json", "w") as f:
        json.dump({"substrates": results, "empirical_gaussian": emp,
                   "claim": "sigma=1/2 universal across g; K_c = 2/(pi*g(0))",
                   "universal_coord": "u = (K-K_c)/K_c"}, f, indent=2)
    print("Saved kuramoto_v3_metrics.json")
