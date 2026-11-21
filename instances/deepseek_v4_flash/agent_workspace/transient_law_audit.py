"""
TRANSIENT-LAW AUDIT  (deepseek_v4_flash)
=========================================
My claimed "Kramers->power crossover" law  ln(rate) = c0 - c1*N - b*ln N
with b ~ 0.86 has been shown to be an ARTIFACT: on exact zero-noise data the
quadratic curvature b2 -> 0 and the sliding-window b collapses toward 0.

This script does NOT re-argue that. It asks the constructive question:

    If the crossover is a finite-N TRANSIENT, what is its decay law?
    i.e.  b_app(N) = -d ln(rate)/d ln N - c1_analytic*N  ~  A * N^{-p}  ?
    and where does the 6-point MC fit land on that curve?

If b_app(N) decays as a clean power of N, the "crossover exponent" is not a
universal physical constant but a finite-size correction with a measurable
scaling. That is a falsifiable, positive statement replacing a false one.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('exact_model_comparison.json'))
Ns = np.asarray(d['Ns'], float)
lnrate = np.asarray(d['lnrate'], float)
c1 = float(d['c1_analytic'])          # asymptotic Kramers slope  (= -2B(Rc)/S2)
print(f"asymptotic Kramers slope c1_analytic = {c1:.8f}")

# ---------------------------------------------------------------------------
# 1. Remove the pure-Kramers line. r(N) = ln(rate) + c1*N  is the transient.
# ---------------------------------------------------------------------------
r = lnrate + c1 * Ns

# asymptote of r: take the mean of the top 10% of N as c0 estimate
top = Ns >= np.quantile(Ns, 0.90)
c0 = float(np.mean(r[top]))
g = r - c0                       # transient, -> 0 as N -> inf
print(f"c0 (asymptote of r) = {c0:.6f}")
print(f"transient g(N) range: {g[0]:.4f} (N={Ns[0]:.0f}) -> {g[-1]:.6f} (N={Ns[-1]:.0f})")

# ---------------------------------------------------------------------------
# 2. Apparent crossover exponent from the exact curve:
#    b_app(N) = -d ln(rate)/d ln N - c1*N   (equals -d g / d ln N)
# ---------------------------------------------------------------------------
lnN = np.log(Ns)
b_app = -np.gradient(lnrate, lnN) - c1 * Ns
# guard: only trust where |b_app| is not swamped by numerical noise
good = np.abs(b_app) > 1e-6
print(f"\n{'N':>9} {'b_app':>12} {'g(N)':>12}")
for i in range(0, len(Ns), max(1, len(Ns)//14)):
    print(f"{Ns[i]:>9.0f} {b_app[i]:>12.5f} {g[i]:>12.5f}")

# ---------------------------------------------------------------------------
# 3. Fit the decay law of the transient:  |g(N)| ~ A * N^{-q}
#    and the decay of the apparent exponent:  b_app(N) ~ B * N^{-p}
#    (if g ~ A N^{-q} then b_app = -dg/dlnN ~ q A N^{-q}, so p should equal q)
# ---------------------------------------------------------------------------
def loglog_fit(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0)
    x, y = x[m], y[m]
    A = np.vstack([np.ones_like(x), np.log(x)]).T
    coef, *_ = np.linalg.lstsq(A, np.log(y), rcond=None)
    resid = np.log(y) - A @ coef
    return coef[0], coef[1], float(np.sqrt(np.mean(resid**2)))   # intercept, slope, rms

# window where transient is well-resolved and positive (small/medium N)
sel = (Ns >= 40) & (Ns <= 1200) & (g > 1e-4)
q_int, q_slope, q_rms = loglog_fit(Ns[sel], g[sel])
print(f"\n[g decay]  g(N) ~ A N^-q  :  A={math.exp(q_int):.4f}  q={-q_slope:.4f}  rms(log)={q_rms:.4f}")

selb = (Ns >= 40) & (Ns <= 1200) & (b_app > 1e-4)
p_int, p_slope, p_rms = loglog_fit(Ns[selb], b_app[selb])
print(f"[b decay]  b_app(N) ~ B N^-p :  B={math.exp(p_int):.4f}  p={-p_slope:.4f}  rms(log)={p_rms:.4f}")

# ---------------------------------------------------------------------------
# 4. Where does the 6-point MC fit land?  The claimed b~0.86 came from 6 points
#    in N in [~15, ~200].  Evaluate b_app at those N (interpolated).
# ---------------------------------------------------------------------------
mc_N = np.array([15, 30, 60, 100, 150, 200], float)
b_at_mc = np.interp(mc_N, Ns, b_app)
print(f"\n[6-point MC region] b_app at N = {mc_N.tolist()}")
print(f"                    b_app = {np.round(b_at_mc,4).tolist()}")
print(f"                    mean b_app over MC region = {np.mean(b_at_mc):.4f}   (claimed 0.86)")

# transient half-life: N where b_app falls to half its N=40 value
b40 = np.interp(40.0, Ns, b_app)
half_idx = np.where((Ns > 40) & (b_app < 0.5 * b40))[0]
N_half = float(Ns[half_idx[0]]) if len(half_idx) else float('nan')
print(f"\nN_half (b_app drops to 50% of b(40)={b40:.4f}) = {N_half:.0f}")

# ---------------------------------------------------------------------------
# 5. Verdict
# ---------------------------------------------------------------------------
verdict = dict(
    asymptotic_slope_c1 = c1,
    transient_c0 = c0,
    g_decay = dict(A=math.exp(q_int), q=-q_slope, rms=q_rms, fit_window=[40,1200]),
    b_decay = dict(B=math.exp(p_int), p=-p_slope, rms=p_rms, fit_window=[40,1200]),
    b_app_at_mc_N = dict(N=mc_N.tolist(), b=b_at_mc.tolist(), mean=float(np.mean(b_at_mc))),
    N_half = N_half,
    conclusion = ("crossover exponent is a finite-N transient; b_app(N) decays as a "
                  "power law in N, so the 'crossover law' is not asymptotically valid"),
)
json.dump(verdict, open('transient_law_audit.json','w'), indent=2)

# ---------------------------------------------------------------------------
# 6. Figure
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))

ax[0].plot(Ns, lnrate, 'o-', ms=2.5, lw=1, color='crimson', label='exact ln(rate)')
ax[0].plot(Ns, c0 - c1*Ns, '--', lw=1.2, color='navy', label=f'asymptote  c0-c1N  (c1={c1:.4f})')
ax[0].set_xscale('log'); ax[0].set_xlabel('N'); ax[0].set_ylabel('ln(rate)')
ax[0].set_title('Exact escape law: asymptotically linear'); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3)

ax[1].loglog(Ns[sel], g[sel], 'o', ms=3, color='darkgreen', label='transient g(N)')
NN = np.geomspace(Ns[sel].min(), Ns[sel].max(), 200)
ax[1].loglog(NN, math.exp(q_int)*NN**q_slope, '--', color='k', lw=1.2,
             label=f'fit: A N^-q, q={-q_slope:.3f}')
ax[1].set_xlabel('N'); ax[1].set_ylabel('g(N) = ln(rate)+c1*N-c0')
ax[1].set_title('Transient decays as a power law'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3, which='both')

ax[2].loglog(Ns[selb], b_app[selb], 'o', ms=3, color='darkorange', label='b_app(N)')
ax[2].loglog(NN, math.exp(p_int)*NN**p_slope, '--', color='k', lw=1.2,
             label=f'fit: B N^-p, p={-p_slope:.3f}')
ax[2].axhline(0.86, color='red', ls=':', lw=1.2, label='claimed b=0.86')
for x, y in zip(mc_N, b_at_mc):
    ax[2].plot(x, y, 'x', color='red', ms=9, mew=2)
ax[2].set_xlabel('N'); ax[2].set_ylabel('apparent exponent b_app')
ax[2].set_title('"Exponent" is a decaying transient'); ax[2].legend(fontsize=7); ax[2].grid(alpha=.3, which='both')

plt.tight_layout()
plt.savefig('transient_law_audit.png', dpi=130)
print("\nSaved transient_law_audit.json + .png")
