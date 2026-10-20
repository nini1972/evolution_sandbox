"""
EXP: EMP135_AUDIT — replication + surrogate discrimination + cross-coordinate

dissociation for the ratified EMP-135 hidden period-4 claim.

Treaty (r=3.865, eps=0.132, N=100, T=2000, 4-bit symbolic motif, C4=0.257).

Part A: multi-variant C4 replication on coupled logistic lattice.
Part B: FT surrogate discrimination of period-4 (C4 alone cannot prove
        nonlinear determinism — AR(4) control with period-4 pole shows that).
Part C: cross-coordinate dissociation — does LZ complexity show an n=4 feature
        on the same substrate? (my prior: no, monotone ramp)
"""
import numpy as np, json, os, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = "emp135_audit"
os.makedirs(OUT, exist_ok=True)

R, EPS, N, T_TREATY = 3.865, 0.132, 100, 2000


def logistic_lattice(r, eps, N, T, seed, bc='periodic', form='additive', burn=0):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.1, 0.9, N).astype(float)
    traj = np.empty((T, N))
    for t in range(T):
        if bc == 'periodic':
            xm, xp = np.roll(x, 1), np.roll(x, -1)
        else:
            xm = np.empty(N); xp = np.empty(N)
            xm[1:] = x[:-1]; xm[0] = x[0]
            xp[:-1] = x[1:]; xp[-1] = x[-1]
        mnb = 0.5 * (xm + xp)
        if form == 'additive':
            x = (1 - eps) * r * x * (1 - x) + eps * 0.5 * (r * xm * (1 - xm) + r * xp * (1 - xp))
        else:  # impladed
            y = (1 - eps) * x + eps * mnb
            x = r * y * (1 - y)
        x = np.where(np.isfinite(x), x, 0.0)
        x = np.clip(x, -1e6, 1e6)
        traj[t] = x
    return traj


def mean_series(traj):
    return traj.mean(axis=1)


def acf(seq, maxlag):
    seq = np.asarray(seq, dtype=float)
    seq = seq - seq.mean()
    var = np.dot(seq, seq)
    if var <= 0:
        return np.zeros(maxlag + 1)
    ac = np.array([np.dot(seq[:len(seq) - k], seq[k:]) / var for k in range(maxlag + 1)])
    return ac


def c4_residues(ac):
    """Mean ACF over lags ≡ r mod 4, excluding lag 0 (lag0 is tautologically 1)."""
    lags = np.arange(1, len(ac))
    res = {}
    for r4 in range(4):
        m = lags[lags % 4 == r4]
        res[r4] = float(np.mean(ac[m]))
    C4 = res[0] - res[2]
    return res, C4


def motif4_symbols(seq):
    """4-bit symbolic motif: median-binarize, group 4 consecutive bits -> 0..15."""
    b = (np.asarray(seq) > np.median(seq)).astype(np.int64)
    n4 = (len(b) // 4) * 4
    b = b[:n4].reshape(-1, 4)
    return (b * (1 << np.arange(3, -1, -1))).sum(axis=1)


def lz_phrasal(s):
    if len(s) == 0:
        return 0
    D = {s[0]}
    i, phrases, w = 1, 1, ""
    while i < len(s):
        w += s[i]
        i += 1
        if w not in D:
            D.add(w); phrases += 1; w = ""
    return phrases + (1 if w else 0)


def period_string(n, k=60, seed=None):
    rng = np.random.default_rng((seed or 0) + n * 17 + 3)
    word = ''.join(str(b) for b in rng.integers(0, 2, n))
    if word.count('0') == 0 or word.count('1') == 0:
        word = '0' * (n - 1) + '1'
    return word * k


def random_string(N, seed=0):
    rng = np.random.default_rng(seed)
    return ''.join(str(b) for b in rng.integers(0, 2, N))


def ft_surrogate(x, seed):
    """Fourier phase-randomized surrogate preserving exact power spectrum."""
    rng = np.random.default_rng(seed)
    n = len(x)
    F = np.fft.rfft(x - x.mean())
    ph = rng.uniform(0, 2 * np.pi, len(F))
    ph[0] = 0.0
    if n % 2 == 0:
        ph[-1] = 0.0
    Y = np.abs(F) * np.exp(1j * ph)
    return np.fft.irfft(Y, n=n)


# ---------------------------------------------------------------- Part A
results = {"partA": [], "partB": {}, "partC": {}}

print("=== Part A: multi-variant C4 replication (treaty params) ===")
for bc in ['periodic', 'fixed']:
    for form in ['additive', 'impladed']:
        for seed in [1, 2, 3]:
            traj = logistic_lattice(R, EPS, N, T_TREATY, seed, bc=bc, form=form, burn=500)
            s = mean_series(traj)
            ac_raw = acf(s, 40)
            res_raw, C4_raw = c4_residues(ac_raw)
            b = (s > np.median(s)).astype(float) * 2 - 1
            ac_bin = acf(b, 40)
            res_bin, C4_bin = c4_residues(ac_bin)
            syms = motif4_symbols(s)
            ac_sym = acf(syms.astype(float), 40)
            res_sym, C4_sym = c4_residues(ac_sym)
            diverged = bool(np.any(np.abs(s) > 1e3))
            row = dict(bc=bc, form=form, seed=seed, diverged=diverged,
                       C4_raw=C4_raw, C4_bin=C4_bin, C4_sym=C4_sym,
                       res_raw=res_raw, res_bin=res_bin, res_sym=res_sym,
                       mean_abs=float(np.mean(np.abs(s))))
            results["partA"].append(row)
            print(f"  bc={bc:8s} form={form:8s} seed={seed} div={diverged} "
                  f"C4_raw={C4_raw:+.3f} C4_bin={C4_bin:+.3f} C4_sym={C4_sym:+.3f}")

# headline replication candidate: treaty-like params, first stable config
stable = [r for r in results["partA"] if not r["diverged"]]
print(f"  treaty C4 target = 0.257 (threshold 0.1)")
print(f"  configs with any |C4|>0.1: "
      f"{sum(1 for r in stable if max(abs(r['C4_raw']), abs(r['C4_bin']), abs(r['C4_sym'])) > 0.1)}/{len(stable)}")

# ---------------------------------------------------------------- Part B
print("\n=== Part B: FT-surrogate discrimination (is period-4 nonlinear-deterministic?) ===")
traj = logistic_lattice(R, EPS, N, 4000, 7, bc='periodic', form='additive')
s = mean_series(traj)[1000:]  # burn
N_B = len(s)
ac_real = acf(s, 40)
res_real, C4_real = c4_residues(ac_real)

SUR = 60
C4_sur = []
for i in range(SUR):
    y = ft_surrogate(s, 1000 + i)
    _, c = c4_residues(acf(y, 40))
    C4_sur.append(c)
C4_sur = np.array(C4_sur)
z_c4 = (C4_real - C4_sur.mean()) / (C4_sur.std() + 1e-12)

# AR(4)-control: linear process with period-4 pole (complex-conjugate pair at |z|~0.97, omega=pi/2)
def ar4_period4(n, seed, noise_std=1.0):
    rng = np.random.default_rng(seed)
    # poles at r*e^{±i*pi/2} -> characteristic poly: 1 - 2 r cos(w) z^-1 + r^2 z^-2 with w=pi/2 -> cos=0
    # add second pair slightly detuned to make it 4-real-dim; use AR(4): y_t = a2 y_{t-2} - a4 y_{t-4} ... simpler:
    # y_t = 1.85 y_{t-2} - 0.9 y_{t-4} + eps  (period-4 resonance, stable)
    y = np.zeros(n)
    for t in range(4, n):
        y[t] = 1.85 * y[t - 2] - 0.90 * y[t - 4] + noise_std * rng.normal()
    return y[-2000:]

ar = ar4_period4(4000, 42)
_, C4_ar = c4_residues(acf(ar, 40))
C4_ar_surs = [c4_residues(acf(ft_surrogate(ar, 2000 + i), 40))[1] for i in range(40)]
z_ar = (C4_ar - np.mean(C4_ar_surs)) / (np.std(C4_ar_surs) + 1e-12)
print(f"  real logistic C4={C4_real:.3f} (FT-sur mean={C4_sur.mean():.3f}±{C4_sur.std():.3f}, z={z_c4:+.2f})")
print(f"  AR(4) control   C4={C4_ar:.3f} (z={z_ar:+.2f})  <- linear process with period-4 pole")

# prediction-error test (h=1 vs h=4) on logistic

def local_pred(series, H, tau, w, emb, k):
    """Leave-one-out local linear nearest-neighbor prediction error (normalized MSE)."""
    n = len(series)
    m = (n - 1 - (emb - 1) * tau - H)
    E = np.zeros((m, emb))
    for j in range(emb):
        E[:, j] = series[j * tau: j * tau + m]
    tgt1 = series[(emb - 1) * tau: (emb - 1) * tau + m]
    tgtH = series[(emb - 1) * tau + H: (emb - 1) * tau + H + m]
    err_loo = []
    # simple k-NN (no library split, LOO) with distance excluding temporal window
    dmat = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)
    np.fill_diagonal(dmat, np.inf)
    idx_all = np.argsort(dmat, axis=1)
    for i in range(m):
        # exclude temporally close indices (Theiler window)
        cand = [j for j in idx_all[i] if abs(j - i) > w]
        nb = cand[:k]
        wts = 1.0 / (dmat[i, nb] + 1e-12)
        wts /= wts.sum()
        p1 = np.dot(wts, tgt1[nb])
        pH = np.dot(wts, tgtH[nb])
        err_loo.append((p1 - tgt1[i], pH - tgtH[i]))
    err_loo = np.array(err_loo)
    var1 = np.var(tgt1) + 1e-12
    varH = np.var(tgtH) + 1e-12
    return float(np.mean(err_loo[:, 0] ** 2) / var1), float(np.mean(err_loo[:, 1] ** 2) / varH)

H, TAU, W, K = 4, 1, 100, 6
s_small = s[:1800]
e1, e4 = local_pred(s_small, H, TAU, W, emb=6, k=K)
e4g = (e1 - e4) / e1
print(f"  pred: h1={e1:.4f} h4={e4:.4f}  gain_4over1={e4g*100:.1f}%  (negative=h4 better)")

sur_gains = []
for i in range(16):
    y = ft_surrogate(s[:1800], 3000 + i)
    a, b_ = local_pred(y, H, TAU, W, emb=6, k=K)
    sur_gains.append((a - b_) / a)
sur_gains = np.array(sur_gains)
z_gain = (e4g - sur_gains.mean()) / (sur_gains.std() + 1e-12)
print(f"  gain FT-surrogates: mean={sur_gains.mean():+.4f}±{sur_gains.std():.4f} z={z_gain:+.2f}")

# AR control gain
a_ar, b_ar = local_pred(ar[:1800], H, TAU, W, emb=6, k=K)
g_ar = (a_ar - b_ar) / a_ar
print(f"  AR(4) control gain = {g_ar*100:.1f}% (expect ~0 -> C4 alone ≠ nonlinear determinism)")

results["partB"] = dict(
    C4_real=C4_real, C4_sur_mean=float(C4_sur.mean()), C4_sur_std=float(C4_sur.std()),
    z_c4=float(z_c4), C4_ar=float(C4_ar), z_ar=float(z_ar),
    e1=e1, e4=e4, gain=e4g, gain_sur_mean=float(sur_gains.mean()),
    gain_sur_std=float(sur_gains.std()), z_gain=float(z_gain), gain_ar=g_ar,
    res_real=res_real,
)

# ---------------------------------------------------------------- Part C
print("\n=== Part C: LZ cross-coordinate on same substrate ===")
# binary sequence of logistic mean series -> LZ phrases per length-4 window sweep
b_logic = (s > np.median(s)).astype(int)
bs = ''.join(str(v) for v in b_logic[:4096])
Ns = [256, 512, 1024, 2048, 4096]
Rn_tab = {}
for NN in Ns:
    rng = np.random.default_rng(42)
    c_rand = np.mean([lz_phrasal(''.join(str(v) for v in rng.integers(0, 2, NN))) for _ in range(10)])
    sub = bs[:NN]
    Rn_tab[NN] = dict(c_sub=lz_phrasal(sub), c_rand=c_rand,
                      R=lz_phrasal(sub) / c_rand)
    print(f"  N={NN}: c_sub={Rn_tab[NN]['c_sub']} c_rand={c_rand:.1f} R={Rn_tab[NN]['R']:.3f}")

# period-n strings LZ ratio (prior instrument, flat-ramp check)
ns_list = [2, 3, 4, 5, 6, 7, 8, 12, 16]
ramp = {}
for n in ns_list:
    sp = period_string(n, k=60)
    sr = random_string(len(sp), seed=99)
    ramp[n] = lz_phrasal(sp) / lz_phrasal(sr)
print("  R(n) period-string ramp: " + " ".join(f"n{n}:{ramp[n]:.3f}" for n in ns_list))
print(f"  argmax R(n) = n={max(ramp, key=ramp.get)}, R(4)={ramp[4]:.3f}")
results["partC"] = dict(Rn_tab={str(k): v for k, v in Rn_tab.items()}, ramp={str(k): v for k, v in ramp.items()})

# ---------------------------------------------------------------- figures
fig, axes = plt.subplots(2, 2, figsize=(13, 10))
ax = axes[0, 0]
res_ids = ["R0", "R1", "R2", "R3"]
ax.bar([f"lag%4={i}" for i in range(4)], [res_real[i] for i in range(4)], color=["#2b8cbe", "#a6bddb", "#e34a33", "#fdbb84"])
ax.set_title(f"Part A/B: ACF residues mod 4 (logistic, r={R})")
ax.set_ylabel("mean ACF")
ax = axes[0, 1]
ax.hist(C4_sur, bins=20, alpha=0.7, label=f"FT surrogates ({SUR})", color="#a6bddb")
ax.axvline(C4_real, color="red", lw=2, label=f"real C4={C4_real:.3f}")
ax.axvline(C4_ar, color="green", lw=2, ls="--", label=f"AR(4) ctrl C4={C4_ar:.3f}")
ax.axvline(0.1, color="gray", ls=":", label="treaty threshold 0.1")
ax.legend(fontsize=8); ax.set_title("Part B: C4 under FT surrogates")
ax = axes[1, 0]
ax.plot(list(ramp.keys()), [ramp[k] for k in ramp], 'o-', color="#6a3d9a")
ax.set_xscale('log'); ax.axvline(4, color='red', ls='--', label='n=4 claim')
ax.set_xlabel("period n"); ax.set_ylabel("R(n)=c_LZ(period)/c_LZ(rand)")
ax.set_title("Part C: LZ coordinate ramp (substrate-independent)")
ax.legend()
ax = axes[1, 1]
ax.bar(["h=1", "h=4"], [e1, e4], color=["#969696", "#e34a33"])
ax.set_title(f"Part B: pred. error (gain {e4g*100:.1f}%, z={z_gain:+.2f})")
ax.set_ylabel("normalized MSE")
fig.tight_layout()
fig.savefig(f"{OUT}/emp135_audit.png", dpi=110)
print(f"saved {OUT}/emp135_audit.png")

with open(f"{OUT}/emp135_audit_results.json", "w") as f:
    json.dump(results, f, indent=2, default=float)
print(f"saved {OUT}/emp135_audit_results.json")

# ---------------------------------------------------------------- summary
summary = dict(
    replication_stable_configs=sum(1 for r in results['partA'] if not r['diverged']),
    replication_total_configs=len(results['partA']),
    C4_real=C4_real, z_c4=float(z_c4), C4_ar=float(C4_ar),
    gain=e4g, z_gain=float(z_gain), gain_ar=g_ar,
    lz_R4=ramp[4], lz_argmax=max(ramp, key=ramp.get),
)
print("\nSUMMARY:", json.dumps(summary, indent=2, default=float))
with open(f"{OUT}/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=float)
