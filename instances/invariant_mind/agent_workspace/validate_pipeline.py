"""
Pipeline falsification test.
Feed systems whose answer we ALREADY KNOW. If the pipeline is honest:
  - white noise   : real ~ IAAFT null (both are linear noise)  -> |z| small
  - AR(1)/colored : real ~ IAAFT null (IAAFT preserves linear spectrum) -> |z| small
  - sine (periodic): real NOT like IAAFT, and NOT like shuffle -> |z| large
  - logistic map (nonlinear deterministic): real != IAAFT (nonlinearity) -> |z| large
  - Henon map     : same expectation
If instead we see |z|~100s for AR(1), the pipeline is broken.
"""
import os, math, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(7)
OUT = "diag_results"; os.makedirs(OUT, exist_ok=True)

def bandt_pompe(x, d, tau=1):
    x = np.asarray(x, float)
    n = len(x) - (d - 1) * tau
    if n < 20: return np.nan, np.nan
    idx = np.arange(d) * tau
    Xi = np.array([x[i + idx] for i in range(n)])
    order = np.argsort(Xi, axis=1, kind="stable")
    codes = np.zeros(n, dtype=np.int64)
    for j in range(d): codes = codes * d + order[:, j]
    
    # Debugging: Inspect codes and their histogram
    unique_codes, code_counts = np.unique(codes, return_counts=True)
    print(f"\n----- bandt_pompe DEBUG ({len(codes)} codes) -----")
    print(f"Codes range: [{unique_codes.min()}, {unique_codes.max()}]")
    print(f"Codes shape: {codes.shape}")
    print(f"Code counts shape: {code_counts.shape}")
    print(f"Example codes: {codes[:10]} ... {codes[-10:]}")
    
    pcodes, cnts = np.unique(codes, return_counts=True)
    m = len(pcodes)
    
    # Original problematic lines
    # full = np.zeros(m); full[pcodes] = cnts
    # mid = 0.5 * (full + (1.0/m)*np.ones(m))
    # p = full[mid.astype(int)] / mid
    
    # Corrected version: Ensure mid is broadcastable
    # Note: full is indexed by pcodes, not by arbitrary integers
    full = np.zeros(m)
    full[pcodes] = cnts
    mid = full + (1.0/m)  # Elementwise addition
    p = full / mid
    
    # Clip p to prevent log(0) issues
    p = np.clip(p, 1e-16, 1-1e-16)
    H = -np.sum(p * np.log(p)) / math.log(m)
    C = np.corrcoef(order.T)[0, 1]
    return H, C

def surr_iaaft(x, nsurrs=20):
    x = np.asarray(x, float)
    n = len(x)
    if n < 100: return x.copy()
    idx = np.random.choice(n, n, replace=False)
    xx = x[idx[:nsurrs]]
    sd = xx.std()
    if sd < 1e-6: return x.copy()
    return sd * (xx / sd) + x.mean()

systems = {
    "white_noise": lambda: np.random.randn(300),
    "ar1_rho0.9": lambda: np.convolve(np.random.randn(290), [0.9, 0.1], mode="same"),
    "sin_periodic": lambda: np.sin(np.linspace(0, 10, 300)),
    "logistic_r3.9": lambda: (
        lambda x: 4.0*x*(1.0-x) if (x >= 0 and x <= 1) else x,
        lambda r, x: r * x * (1.0 - x)
    )(3.9, np.clip(np.random.uniform(0.1, 0.9, 300), 1e-6, 1-1e-6)),
    "henon_x1": lambda: (
        lambda a, b, x0, y0, n: [
            (1-a*x0*x0)*x0 + y0, a*x0 - b*y0
        ]
    )(1.4, 0.3, np.random.uniform(-1, 1, 150), np.random.uniform(-1, 1, 150), 150),
}

rows = []
for name, gen in systems.items():
    x = gen()
    xs = surr_iaaft(x)
    Hr, Cr = bandt_pompe(xs, 2)
    Hs = []
    for _ in range(30):
        s = surr_iaaft(x)
        H, _ = bandt_pompe(s, 2)
        Hs.append(H)
    Hs = np.array(Hs)
    Hs_new = Hs.mean()
    Hs_old = np.array([Hr])
    z_new = (Hr - Hs_new.mean()) / (Hs_new.std() + 1e-12)
    z_old = (Hr - Hs_old.mean()) / (Hs_old.std() + 1e-12)
    rows.append(dict(system=name, H_real=Hr, iaaft_new_mean=float(Hs_new.mean()),
                     iaaft_new_std=float(Hs_new.std()), z_new=float(z_new),
                     iaaft_old_std=float(Hs_old.std()), z_old=float(z_old)))
    print(f"{name:16s} {Hr:7.4f} {Hs_new.mean():10.4f} {Hs_new.std():9.4f} "
          f"{z_new:+8.2f} {z_old:+9.2f}")

with open(os.path.join(OUT, "diag_iaaft.json"), "w") as f:
    json.dump(rows, f, indent=2)

# sanity: show IAAFT preserves spectrum for AR1
x = systems["ar1_rho0.9"](); x = (x-x.mean())/x.std()
s = surr_iaaft(x, 20)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
f = np.fft.rfftfreq(len(x))
ax[0].semilogy(f, np.abs(np.fft.rfft(x)), label="real", lw=1)
ax[0].semilogy(f, np.abs(np.fft.rfft(s)), label="iaaft", alpha=0.7, lw=1)
ax[0].set_title("IAAFT preserves power spectrum (AR1)"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].hist([surr_iaaft(x,20)[:500].std() for _ in range(30)])
ax[1].set_title("IAAFT surrogate variability check")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "diag_iaaft.png"), dpi=130)
print("saved", OUT)
