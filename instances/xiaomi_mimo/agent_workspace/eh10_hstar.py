"""
Echo-Horizon v10 — corrected dense H-sweep of the convergence exponent alpha(H)
of the correlation-onset estimator p_rho, and the critical Hurst index H*
(alpha(H*)=0) with robustness check across floor multipliers k in {5,10,20,40}.

Chain: eh6 (onset window) -> eh8 (floor gate + truth convention p->2H)
       -> eh9 (n-convergence: alpha(0.55)=0.37, alpha(0.75)=0.15,
               alpha(0.95)=-0.09 -> H* bracketed in (0.75, 0.95])
       -> eh10 resolves H* on a dense grid with a VALID generator.

Corrections vs the broken job-9390 attempt:
  * generator = the SAME eh9_valid fgn_fine (spectral fractional Gaussian
    noise, delta=1e-3), whose beta_10 within ~0.12 of 2H at n>=1e4
    (measured gate below), NOT the integer-lattice covariance-embedding hack.
  * estimator = the SAME eh9 code path: rho -> floor gate k/sqrt(n)
    -> onset window (one_max=0.30) -> log-log fit of 1-rho.
  * alpha fit requires >=4 valid n-points (eh9 used >=3), frac>=0.5.

Validity gates (all reported):
  G1 generator: |mean beta_10(n=1e5..1e6) - 2H| <= 0.15 per H condition.
  G2 truth convention: p -> 2H (eh8/eh9), NOT 1+H.
  G3 alpha fit: >=4 n-points with frac>=0.5.
  G4 split-half: alpha from odd vs even reps -> error bar.

Controls (estimator pathology anchors, same code): AR(1) phi=0.9 (p->1.448
plateau observed in eh9, truth 1.0), iid (p->2), periodic (p->0).
"""
import numpy as np, json, time, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

T0 = time.time()
RNG = np.random.default_rng(9101)

# ---------------- verbatim copies from eh9_nconv.py (chain integrity) ----------
def rho_fgn(h, H):
    h = np.abs(np.asarray(h, dtype=float))
    return 0.5 * ((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

def onset_from_rho(h, rho, one_max=0.30, floor=0.0):
    h = np.asarray(h, dtype=float); one = 1.0 - np.asarray(rho, dtype=float)
    ok = (np.isfinite(h) & np.isfinite(one) & (h > 0) &
          (one > floor) & (one < one_max))
    if ok.sum() < 3:
        return float('nan'), 0
    lr = np.log(h[ok]); lo = np.log(one[ok])
    if lo.var() <= 0:
        return float('nan'), int(ok.sum())
    p, _ = np.polyfit(lr, lo, 1)
    resid = lo - np.polyval(np.polyfit(lr, lo, 1), lr)
    r2 = 1 - resid.var()/lo.var()
    return float(p), int(ok.sum())

def fgn_fine(n, H, delta=1e-3, rng=RNG):
    """Spectral fGn (valid): power spectrum of the exact fractional
    covariance sampled on a delta-fine grid, embedded in a circulant."""
    m = 1 << int(np.ceil(np.log2(max(4*n, 64))))
    k = np.arange(m//2 + 1)
    c = rho_fgn(k*delta, H); c[0] = 1.0
    circ = np.concatenate([c, c[-2:0:-1]])
    lam = np.fft.rfft(circ).real
    lam[lam < 1e-12] = 1e-12
    z = (rng.normal(size=len(lam)) + 1j*rng.normal(size=len(lam))) * np.sqrt(lam/2)
    x = np.fft.irfft(z, m)[:n]
    return (x - x.mean())/x.std()

def ar1(n, phi, rng=RNG):
    e = rng.normal(size=n); y = np.empty(n); y[0] = e[0]
    s = np.sqrt(1 - phi*phi)
    for i in range(1, n):
        y[i] = phi*y[i-1] + s*e[i]
    return y

def autocorr_rho(x):
    """Exactly the eh9 measure(): FFT autocorrelation, normalized rho."""
    n = len(x)
    x = np.asarray(x, dtype=float)
    x = x - x.mean(); sd = x.std()
    if sd <= 0:
        return np.zeros(1)
    x = x/sd
    F = np.fft.rfft(x, n=2*n); pw = (F*np.conj(F)).real
    rho = np.fft.irfft(pw)[:n]
    rho /= np.arange(n, 0, -1)
    rho /= rho[0]
    return rho

def p_from_rho(rho, n, k, one_max=0.30):
    """Exactly the eh9 measure() gate + fit path, parameterized by k.
    Returns (p, nfit, floor, gate_open)."""
    floor = k/np.sqrt(n)
    ad_max = min(20000, n//4)
    one_all = 1.0 - rho[:ad_max+1]
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max))
    else:
        lmax = ad_max
    lmax = max(lmax, 40)
    lags = np.arange(1, lmax+1)
    p, nfit = onset_from_rho(lags, rho[lags-1], one_max, floor)
    return p, nfit, floor, bool(len(k_over) > 0)

def beta10(x, w=10):
    """eh9 structure function beta over window w (slope of log V vs log h)."""
    x = np.asarray(x, dtype=float)
    if w >= len(x)//4:
        return float('nan')
    hh = np.arange(1, w+1)
    V = np.array([np.mean((x[h:] - x[:-h])**2) for h in hh])
    ok = V > 1e-13
    if ok.sum() < 3:
        return float('nan')
    return float(np.polyfit(np.log(hh[ok]), np.log(V[ok]), 1)[0])

# ---------------- experiment design ----------------
H_GRID = [0.55, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
KGRID = [5, 10, 20, 40]
NS = [1000, 3000, 10000, 30000, 100000, 300000, 1000000]
REPS = {1000: 10, 3000: 8, 10000: 6, 30000: 5, 100000: 4, 300000: 3, 1000000: 3}
CTRLS = [('ar1_09', 1.0), ('iid', 2.0), ('periodic', 0.0)]
CTRL_NS = [10000, 100000, 1000000]
CTRL_REPS = 4
truth = {('fgn', H): 2*H for H in H_GRID}
for name, t in CTRLS:
    truth[(name, None)] = t

rows = []   # per (cond, H, n, k, rep): p, nfit, gate, beta10
n_series = 0

# ---- main sweep ----
for H in H_GRID:
    for n in NS:
        for rep in range(REPS[n]):
            x = fgn_fine(n, H, rng=RNG)
            rho = autocorr_rho(x)
            b10 = beta10(x, 10)
            n_series += 1
            for k in KGRID:
                p, nfit, floor, gate = p_from_rho(rho, n, k)
                rows.append(dict(cond='fgn', H=H, n=n, k=k, rep=rep,
                                 p=p, nfit=nfit, gate=int(gate), b10=b10))

# ---- controls ----
for name, t in CTRLS:
    for n in CTRL_NS:
        for rep in range(CTRL_REPS):
            if name == 'ar1_09':
                x = ar1(n, 0.9, rng=RNG)
            elif name == 'iid':
                x = RNG.normal(size=n)
            else:
                ph = np.linspace(0, 2*np.pi, n, endpoint=False)
                x = np.cos(ph) + 0.1*RNG.normal(size=n)
            rho = autocorr_rho(x)
            b10 = beta10(x, 10)
            n_series += 1
            for k in KGRID:
                p, nfit, floor, gate = p_from_rho(rho, n, k)
                rows.append(dict(cond=name, H=float('nan'), n=n, k=k, rep=rep,
                                 p=p, nfit=nfit, gate=int(gate), b10=b10))

print(f"[t={time.time()-T0:.0f}s] generated {n_series} series, {len(rows)} rows")

# ---------------- aggregation: alpha(H,k) ----------------
def alpha_fit(pts):
    """pts: list of (n, |bias|); eh9 formula: alpha = -slope(log|bias| vs log n)."""
    if len(pts) < 4:
        return float('nan'), len(pts)
    a = np.log([q[0] for q in pts]); b = np.log([q[1] for q in pts])
    return float(-np.polyfit(a, b, 1)[0]), len(pts)

def cond_bias(cond, H, k, repsel=None):
    """returns {n: mean p over reps (frac>=0.5 gate)} for alpha fitting"""
    out = {}
    for n in NS:
        sel = [r for r in rows if r['cond'] == cond and r['k'] == k and r['n'] == n
               and (H is None or (np.isfinite(r['H']) and abs(r['H'] - H) < 1e-9))
               and np.isfinite(r['p'])]
        if repsel is not None:
            sel = [r for r in sel if repsel(r['rep'])]
        reps_total = REPS[n] if cond == 'fgn' else CTRL_REPS
        frac = len(sel)/reps_total if reps_total else 0
        if len(sel) == 0 or frac < 0.5:
            continue
        out[n] = (float(np.mean([r['p'] for r in sel])), frac, len(sel))
    return out

results = {}
for k in KGRID:
    for H in H_GRID:
        cb = cond_bias('fgn', H, k)
        t = 2*H
        pts = [(n, abs(mp - t)) for n, (mp, fr, cnt) in sorted(cb.items())
               if abs(mp - t) > 0]
        alpha, npts = alpha_fit(pts)
        # split-half
        cb_e = cond_bias('fgn', H, k, repsel=lambda r: r % 2 == 0)
        cb_o = cond_bias('fgn', H, k, repsel=lambda r: r % 2 == 1)
        def fit(cb_):
            pts_ = [(n, abs(mp - t)) for n, (mp, fr, cnt) in sorted(cb_.items())
                    if abs(mp - t) > 0]
            return alpha_fit(pts_)[0]
        a_e, a_o = fit(cb_e), fit(cb_o)
        alpha_sd = 0.5*abs(a_e - a_o) if np.isfinite(a_e) and np.isfinite(a_o) else float('nan')
        # generator gate beta10 at large n
        bl = [r['b10'] for r in rows if r['cond'] == 'fgn'
              and abs(r['H'] - H) < 1e-9 and r['n'] >= 100000 and r['k'] == KGRID[0]]
        beta10_mean = float(np.nanmean(bl)) if len(bl) else float('nan')
        # per-n biases for reporting
        bias_tbl = {n: round(mp - t, 4) for n, (mp, fr, cnt) in sorted(cb.items())}
        results[(k, H)] = dict(k=k, H=H, truth=t, alpha=alpha, npts=npts,
                               alpha_sd=alpha_sd, beta10=beta10_mean,
                               gate_dev=beta10_mean - t, bias=bias_tbl)
        print(f"[t={time.time()-T0:.0f}s] k={k} H={H} alpha={alpha:.3f}"
              f"±{alpha_sd if np.isfinite(alpha_sd) else float('nan'):.3f} "
              f"(npts={npts}, b10={beta10_mean:.3f}, dev={beta10_mean-t:+.3f})")

# H* per k: linear interpolation of alpha(H)=0 crossing
hstar = {}
for k in KGRID:
    pairs = [(results[(k, H)]['alpha'], H) for H in H_GRID
             if np.isfinite(results[(k, H)]['alpha'])]
    pairs.sort(key=lambda q: q[1])
    cross = None
    bracket = None
    for (a1, h1), (a2, h2) in zip(pairs, pairs[1:]):
        if a1 > 0 >= a2 or a1 >= 0 > a2:
            cross = float(h1 + (h2-h1)*a1/(a1-a2)) if a1 != a2 else float(h1)
            bracket = [h1, h2]
            break
    hstar[k] = dict(H_star=cross, bracket=bracket)
    print(f"H*(k={k}) = {cross} bracket={bracket}")

# controls
ctrl_out = {}
for name, t in CTRLS:
    for k in KGRID:
        cb = cond_bias(name, None, k)
        ctrl_out[(name, k)] = {n: round(mp - t, 4) for n, (mp, fr, cnt) in sorted(cb.items())}

# ---------------- outputs ----------------
with open('eh10_hstar.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

serial = {str(k): {str(H): {kk: vv for kk, vv in v.items() if kk != 'bias'}
                   | {'bias': {str(n): b for n, b in v['bias'].items()}}
                   for (kk2, H), v in [(key, results[key]) for key in results]}
          for k in KGRID for kk2, H in [(k, H) for H in H_GRID]}
out = dict(
    design=dict(H_GRID=H_GRID, KGRID=KGRID, NS=NS, REPS=REPS, n_series=n_series,
                seed=9101, generator='fgn_fine(delta=1e-3) [valid, eh9-chain]',
                truth_convention='p -> 2H', one_max=0.30, alpha_fit_pts_min=4),
    gates=dict(
        G1_generator={str(H): dict(beta10=results[(KGRID[0], H)]['beta10'],
                                   dev=results[(KGRID[0], H)]['gate_dev'],
                                   pass_=abs(results[(KGRID[0], H)]['gate_dev']) <= 0.15)
                      for H in H_GRID},
        G3_min_npts=min(results[key]['npts'] for key in results),
    ),
    alpha={f"k={k}|H={H}": results[(k, H)] for k in KGRID for H in H_GRID},
    hstar={str(k): hstar[k] for k in KGRID},
    controls={f"{name}|k={k}": {str(n): d for n, d in ctrl_out[(name, k)].items()}
              for name, _ in CTRLS for k in KGRID},
    elapsed_s=round(time.time()-T0, 1),
)
json.dump(out, open('eh10_hstar.json', 'w'), indent=1, default=str)

# ---------------- figure ----------------
fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
ax = axes[0]
for H in H_GRID:
    for k in [KGRID[1]]:
        cb = cond_bias('fgn', H, k)
        if cb:
            ns = sorted(cb)
            bias = [abs(cb[n][0] - 2*H) for n in ns]
            ax.loglog(ns, bias, 'o-', label=f"H={H:.2f}")
ax.set_xlabel('n'); ax.set_ylabel('|p̄ − 2H|')
ax.set_title('bias decay (k=20)'); ax.legend(fontsize=7, ncol=2); ax.grid(alpha=.3)

ax = axes[1]
cmap = plt.get_cmap('coolwarm')
for i, k in enumerate(KGRID):
    al = [results[(k, H)]['alpha'] for H in H_GRID]
    sd = [results[(k, H)]['alpha_sd'] for H in H_GRID]
    ax.errorbar(H_GRID, al, yerr=sd, marker='s', label=f"k={k}", alpha=.85)
ax.axhline(0, color='k', ls='--')
for k in KGRID:
    if hstar[k]['H_star']:
        ax.axvline(hstar[k]['H_star'], color='gray', ls=':', alpha=.5)
ax.set_xlabel('H'); ax.set_ylabel('alpha (convergence exponent)')
ax.set_title('alpha(H): >0 convergent, <=0 inconsistent\n(dotted = H*)')
ax.legend(fontsize=8); ax.grid(alpha=.3)

ax = axes[2]
names = [n for n, _ in CTRLS]
xpos = np.arange(len(names))
for i, k in enumerate(KGRID):
    vals = []
    for name in names:
        d = ctrl_out[(name, k)]
        vals.append(d.get(1000000, float('nan')))
    ax.bar(xpos + (i-1.5)*0.2, vals, width=0.18, label=f"k={k}")
truths = [t for _, t in CTRLS]
for xi, t in zip(xpos, truths):
    ax.plot([xi-0.45, xi+0.45], [t, t], 'k--', lw=1.5)
ax.set_xticks(xpos); ax.set_xticklabels(names)
ax.set_ylabel('p̄(n=1e6) − truth'); ax.set_title('controls (dashed = truth)')
ax.legend(fontsize=8); ax.grid(alpha=.3, axis='y')
fig.suptitle('EH10 — convergence exponent alpha(H) and critical H* of p_rho', y=1.02)
fig.tight_layout()
fig.savefig('eh10_hstar.png', dpi=140, bbox_inches='tight')

# ---------------- report ----------------
lines = ["# EH10 — H* : critical Hurst index where p_rho loses n-convergence",
         "", f"Elapsed {out['elapsed_s']}s; {n_series} series; seed 9101.",
         "", "Chain: eh6 -> eh8 (truth p->2H) -> eh9 (alpha 0.37/0.15/-0.09 at "
         "H=0.55/0.75/0.95) -> eh10 dense sweep.", "",
         "## G1 generator gate (beta10 vs 2H, n>=1e5)", "",
         "| H | beta10 | dev | pass<=0.15 |", "|---|---|---|---|"]
for H in H_GRID:
    g = out['gates']['G1_generator'][str(H)]
    lines.append(f"| {H} | {g['beta10']:.3f} | {g['dev']:+.3f} | {'YES' if g['pass_'] else 'NO'} |")
lines += ["", "## alpha(H,k)  (alpha>0 = bias decays = consistent asymptotically; "
          "<=0 = plateau/growth = structurally inconsistent)", "",
          "| H | " + " | ".join(f"k={k} (±sd)" for k in KGRID) + " |", "|---|" + "---|"*len(KGRID)]
for H in H_GRID:
    cells = []
    for k in KGRID:
        r = results[(k, H)]
        if np.isfinite(r['alpha']):
            cells.append(f"{r['alpha']:+.3f} (±{r['alpha_sd']:.3f}, n={r['npts']})")
        else:
            cells.append("---")
    lines.append(f"| {H} | " + " | ".join(cells) + " |")
lines += ["", "## H* (alpha=0 crossing)", "",
          "| k | H* | bracket |", "|---|---|---|"]
for k in KGRID:
    hs = hstar[k]
    lines.append(f"| {k} | {hs['H_star'] if hs['H_star'] else '>max' or 'none'} | {hs['bracket']} |")
lines += ["", "## per-n bias p̄−2H (k=20)", "",
          "| H | " + " | ".join(f"n={n}" for n in NS) + " |",
          "|---|" + "---|"*len(NS)]
for H in H_GRID:
    b = results[(20, H)]['bias']
    lines.append(f"| {H} | " + " | ".join(str(b.get(n, '---')) for n in NS) + " |")
lines += ["", "## controls (p̄ − truth)", "",
          "| cond | " + " | ".join(f"n={n} k={k}" for n in CTRL_NS for k in KGRID) + " |",
          "|---|" + "---|"*(len(CTRL_NS)*len(KGRID))]
for name, t in CTRLS:
    cells = []
    for n in CTRL_NS:
        for k in KGRID:
            d = ctrl_out[(name, k)]
            cells.append(str(d.get(n, '---')))
    lines.append(f"| {name} | " + " | ".join(cells) + " |")
lines += ["", "## gates", "",
          f"- G2 truth convention: p -> 2H (eh8/eh9).",
          f"- G3 min npts across fits: {out['gates']['G3_min_npts']} (>=4 required).",
          "- G4 split-half alpha sd shown per cell.", "",
          "## validity verdict", ""]
allg = all(v['pass_'] for v in out['gates']['G1_generator'].values())
hs_vals = [hstar[k]['H_star'] for k in KGRID if hstar[k]['H_star']]
if allg and hs_vals:
    spread = max(hs_vals) - min(hs_vals)
    lines.append(f"ALL GATES PASS. H* = {np.mean(hs_vals):.3f} ± {spread/2:.3f} "
                 f"(spread across k: {spread:.3f}, n={n_series} series).")
    lines.append(f"Chain to eh9: H* must lie in (0.75, 0.95].")
else:
    lines.append(f"Gate status G1={allg}, H* found for k={hs_vals}. REVIEW REQUIRED.")
open('eh10_hstar_REPORT.md', 'w').write("\n".join(lines))
print("DONE", out['elapsed_s'], "s")
print("\n".join(lines[-14:]))
