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

# ---------- Bandt-Pompe ----------
def bandt_pompe(x, d, tau=1):
    x = np.asarray(x, float)
    n = len(x) - (d - 1) * tau
    if n < 20: return np.nan, np.nan
    idx = np.arange(d) * tau
    Xi = np.array([x[i + idx] for i in range(n)])
    order = np.argsort(Xi, axis=1, kind="stable")
    codes = np.zeros(n, dtype=np.int64)
    for j in range(d): codes = codes * d + order[:, j]
    pcodes, cnts = np.unique(codes, return_counts=True)
    full = np.zeros(math.factorial(d)); full[pcodes] = cnts; full /= full.sum()
    m = len(full)
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -np.sum(full[full > 0] * np.log(full[full > 0]))
    Hn = H / math.log(math.factorial(d))
    u = np.ones(m) / m; mid = 0.5 * (full + u)
    kl = lambda a, b: np.sum(a[a > 0] * np.log(a[a > 0] / b[a > 0]))
    JS = 0.5 * kl(full, mid) + 0.5 * kl(u, mid)
    peaked = np.zeros(m); peaked[0] = 1.0; midp = 0.5 * (peaked + u)
    JSmax = 0.5 * kl(peaked, midp) + 0.5 * kl(u, midp)
    C = Hn * (JS / JSmax) if JSmax > 0 else 0.0
    return float(Hn), float(C)

# ---------- surrogates ----------
def surr_shuffle(x):
    y = x.copy(); np.random.shuffle(y); return y

def surr_iaaft(x, n_iter=20):
    """Correct IAAFT: start from shuffle, iterate."""
    x = np.asarray(x, float)
    n = len(x)
    Xf = np.fft.rfft(x)
    target_mag = np.abs(Xf)
    sorted_x = np.sort(x)
    y = np.random.permutation(x)          # <-- must start from a shuffle
    for _ in range(n_iter):
        Yf = np.fft.rfft(y)
        ph = np.angle(Yf)                  # keep current phases
        z = np.fft.irfft(target_mag * np.exp(1j * ph), n=n)
        ranks = np.argsort(np.argsort(z))
        y = sorted_x[ranks]
    return y

def surr_iaaft_buggy(x, n_iter=2):
    """The OLD buggy version: start from x, only 2 iters."""
    x = np.asarray(x, float); y = x.copy()
    for _ in range(n_iter):
        F = np.fft.rfft(y); mag = np.abs(F)
        ph = np.exp(1j * 2 * np.pi * np.random.rand(len(F))); ph[0] = 0.0
        z = np.fft.irfft(mag * ph, n=len(y))
        ranks = np.argsort(np.argsort(z))
        y = np.sort(x)[ranks]
    return y

# ---------- ground-truth systems ----------
def sys_white(n=4000): return np.random.randn(n)
def sys_ar1(n=4000, a=0.9):
    e = np.random.randn(n); y = np.zeros(n)
    for i in range(1, n): y[i] = a * y[i-1] + e[i]
    return y
def sys_sine(n=4000):
    t = np.arange(n); return np.sin(2*np.pi*t/500) + 0.3*np.random.randn(n)
def sys_logistic(n=4000, r=3.99):
    y = np.zeros(n); y[0] = 0.4
    for i in range(1, n): y[i] = r*y[i-1]*(1-y[i-1])
    return y
def sys_henon(n=4000):
    x, y = 0.1, 0.1; xs = np.zeros(n)
    for i in range(n):
        xn = 1 - 1.4*x*x + y; y = 0.3*x; x = xn; xs[i] = x
    return xs

systems = {
    "white_noise":  sys_white,
    "AR1(linear)":  sys_ar1,
    "sine+noise":   sys_sine,
    "logistic":     sys_logistic,
    "henon":        sys_henon,
}
N_SUR = 50
d = 4

print(f"{'system':16s} {'H_real':>7s} {'IAAFT_mean':>10s} {'IAAFT_std':>9s} "
      f"{'zH_new':>8s} {'zH_buggy':>9s}  verdict")
rows = []
for name, fn in systems.items():
    x = fn(); x = (x - x.mean()) / (x.std() + 1e-12)
    Hr, Cr = bandt_pompe(x, d)
    Hs_new = np.array([bandt_pompe(surr_iaaft(x, 20), d)[0] for _ in range(N_SUR)])
    Hs_old = np.array([bandt_pompe(surr_iaaft_buggy(x, 2), d)[0] for _ in range(N_SUR)])
    z_new = (Hr - Hs_new.mean()) / (Hs_new.std() + 1e-12)
    z_old = (Hr - Hs_old.mean()) / (Hs_old.std() + 1e-12)
    # honest expectation:
    #   linear (white, AR1) -> |z| small ; nonlinear/periodic -> |z| large
    rows.append(dict(system=name, H_real=Hr, iaaft_new_mean=float(Hs_new.mean()),
                     iaaft_new_std=float(Hs_new.std()), z_new=float(z_new),
                     iaaft_old_std=float(Hs_old.std()), z_old=float(z_old)))
    print(f"{name:16s} {Hr:7.4f} {Hs_new.mean():10.4f} {Hs_new.std():9.4f} "
          f"{z_new:+8.2f} {z_old:+9.2f}")

with open(os.path.join(OUT, "diag_iaaft.json"), "w") as f:
    json.dump(rows, f, indent=2)

# sanity: show IAAFT preserves spectrum for AR1
x = sys_ar1(); x = (x-x.mean())/x.std()
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
