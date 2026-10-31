#!/usr/bin/env python3
"""
Echo-Horizon v11 — CORRECTION of the off-by-one lag bug found in eh9/eh10,
then re-derivation of alpha(H) and the critical Hurst index H* of p_rho.

BUG (verified locally, seed-fixed AR(1) probe):
    eh9/eh10 used onset fit points (nominal lag h, 1-rho[h-1]) so the FIRST
    fit point was (h=1, 1-rho[0]=0) -> log(0) -> bogus steep slope.
    Effect measured: AR(1) phi=0.9 (truth p=1.0) gave p=1.441 (bias +0.441),
    fGn alphas and H*=0.697 are therefore INVALID.

FIX: use (nominal lag h, 1-rho[h]) for h=1..lmax. Everything else in the
eh9 chain (one_max=0.30, floor=k/sqrt(n), gate structure, fit path) unchanged.

This run computes BOTH estimators on the SAME series (buggy kept only as a
diagnostic comparator) so the correction is quantified in one shot.

Validity gates:
  G0 fix verification: AR(1) phi=0.9 -> |p_fixed - 1.0| <= 0.15 at n=1e6,
                        AND p_buggy reproduces ~1.44 (bug present in eh9/10).
  G1 generator: |mean beta_10(n>=1e5) - 2H| <= 0.15 per H.
  G2 truth convention p -> 2H.
  G3 alpha fit: >=4 n-points, frac>=0.5.
  G4 split-half alpha error bars.
"""
import numpy as np, json, time, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

T0 = time.time()
RNG = np.random.default_rng(1102)

# ---------------- verbatim chain functions (eh9), only the lag index fixed ---
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
    n = len(x); x = np.asarray(x, dtype=float)
    x = x - x.mean(); sd = x.std()
    if sd <= 0:
        return np.zeros(1)
    x = x/sd
    F = np.fft.rfft(x, n=2*n); pw = (F*np.conj(F)).real
    rho = np.fft.irfft(pw)[:n]
    rho /= np.arange(n, 0, -1)
    rho /= rho[0]
    return rho

def p_from_rho(rho, n, k, one_max=0.30, buggy=False):
    """FIXED (buggy=False): fit points (h, 1-rho[h]).
    buggy=True reproduces eh9/eh10: (h, 1-rho[h-1])."""
    floor = k/np.sqrt(n)
    ad_max = min(20000, n//4)
    one_all = 1.0 - rho[:ad_max+1]          # index j ~ lag j (gate only, unchanged)
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max))
    else:
        lmax = ad_max
    lmax = max(lmax, 40)
    lags = np.arange(1, lmax+1)
    idx = lags - 1 if buggy else lags        # <-- THE FIX (single character change)
    idx = idx[idx < len(rho)]
    p, nfit = onset_from_rho(lags[:len(idx)], rho[idx], one_max, floor)
    return p, nfit, floor, bool(len(k_over) > 0)

def beta10(x, w=10):
    x = np.asarray(x, dtype=float)
    if w >= len(x)//4:
        return float('nan')
    hh = np.arange(1, w+1)
    V = np.array([np.mean((x[h:] - x[:-h])**2) for h in hh])
    ok = V > 1e-13
    if ok.sum() < 3:
        return float('nan')
    return float(np.polyfit(np.log(hh[ok]), np.log(V[ok]), 1)[0])

# ---------------- design (identical to eh10) ----------------------------------
H_GRID = [0.55, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
KGRID = [5, 10, 20, 40]
NS = [1000, 3000, 10000, 30000, 100000, 300000, 1000000]
REPS = {1000: 10, 3000: 8, 10000: 6, 30000: 5, 100000: 4, 300000: 3, 1000000: 3}
CTRLS = [('ar1_09', 1.0), ('iid', 2.0), ('periodic', 0.0)]
CTRL_NS = [10000, 100000, 1000000]
CTRL_REPS = 4

rows = []
n_series = 0

for H in H_GRID:
    for n in NS:
        for rep in range(REPS[n]):
            x = fgn_fine(n, H, rng=RNG)
            rho = autocorr_rho(x)
            b10 = beta10(x, 10)
            n_series += 1
            for k in KGRID:
                pf, nf, fl, g = p_from_rho(rho, n, k, buggy=False)
                pb, nb, _, _ = p_from_rho(rho, n, k, buggy=True)
                rows.append(dict(cond='fgn', H=H, n=n, k=k, rep=rep,
                                 p=pf, nfit=nf, gate=int(g), b10=b10, p_buggy=pb))

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
                pf, nf, fl, g = p_from_rho(rho, n, k, buggy=False)
                pb, nb, _, _ = p_from_rho(rho, n, k, buggy=True)
                rows.append(dict(cond=name, H=float('nan'), n=n, k=k, rep=rep,
                                 p=pf, nfit=nf, gate=int(g), b10=b10, p_buggy=pb))

print(f"[t={time.time()-T0:.0f}s] {n_series} series, {len(rows)} rows", flush=True)

# ---------------- aggregation -------------------------------------------------
def alpha_fit(pts):
    if len(pts) < 4:
        return float('nan'), len(pts)
    a = np.log([q[0] for q in pts]); b = np.log([q[1] for q in pts])
    return float(-np.polyfit(a, b, 1)[0]), len(pts)

def cond_bias(cond, H, k, repsel=None, use_buggy=False):
    out = {}
    for n in NS:
        sel = [r for r in rows if r['cond'] == cond and r['k'] == k and r['n'] == n
               and (H is None or (np.isfinite(r['H']) and abs(r['H'] - H) < 1e-9))]
        if repsel is not None:
            sel = [r for r in sel if repsel(r['rep'])]
        sel = [r for r in sel if np.isfinite(r['p_buggy' if use_buggy else 'p'])]
        reps_total = REPS[n] if cond == 'fgn' else CTRL_REPS
        frac = len(sel)/reps_total if reps_total else 0
        if len(sel) == 0 or frac < 0.5:
            continue
        key = 'p_buggy' if use_buggy else 'p'
        out[n] = (float(np.mean([r[key] for r in sel])), frac, len(sel))
    return out

results = {}
for k in KGRID:
    for H in H_GRID:
        t = 2*H
        cb = cond_bias('fgn', H, k)
        pts = [(n, abs(mp - t)) for n, (mp, fr, cnt) in sorted(cb.items()) if abs(mp - t) > 0]
        alpha, npts = alpha_fit(pts)
        def fit_sel(sel_fn):
            cb_ = cond_bias('fgn', H, k, repsel=sel_fn)
            return alpha_fit([(n, abs(mp - t)) for n, (mp, fr, c) in sorted(cb_.items())
                              if abs(mp - t) > 0])[0]
        a_e = fit_sel(lambda r: r % 2 == 0); a_o = fit_sel(lambda r: r % 2 == 1)
        alpha_sd = 0.5*abs(a_e - a_o) if np.isfinite(a_e) and np.isfinite(a_o) else float('nan')
        # buggy comparator alpha on same series
        cbb = cond_bias('fgn', H, k, use_buggy=True)
        alpha_b, _ = alpha_fit([(n, abs(mp - t)) for n, (mp, fr, c) in sorted(cbb.items())
                                if abs(mp - t) > 0])
        bl = [r['b10'] for r in rows if r['cond'] == 'fgn' and abs(r['H'] - H) < 1e-9
              and r['n'] >= 100000 and r['k'] == KGRID[0]]
        beta10_mean = float(np.nanmean(bl)) if len(bl) else float('nan')
        bias_tbl = {n: round(mp - t, 4) for n, (mp, fr, cnt) in sorted(cb.items())}
        results[(k, H)] = dict(k=k, H=H, truth=t, alpha=alpha, alpha_buggy=alpha_b,
                               npts=npts, alpha_sd=alpha_sd, beta10=beta10_mean,
                               gate_dev=beta10_mean - t, bias=bias_tbl)
        print(f"[t={time.time()-T0:.0f}s] k={k} H={H} alpha_fix={alpha:+.3f} "
              f"alpha_bug={alpha_b:+.3f} (npts={npts}, dev={beta10_mean-t:+.3f})", flush=True)

hstar, hstar_bug = {}, {}
for k in KGRID:
    def crossing(geta):
        pairs = [(geta(H), H) for H in H_GRID if np.isfinite(geta(H))]
        pairs.sort(key=lambda q: q[1])
        for (a1, h1), (a2, h2) in zip(pairs, pairs[1:]):
            if a1 > 0 >= a2 or a1 >= 0 > a2:
                cr = float(h1 + (h2-h1)*a1/(a1-a2)) if a1 != a2 else float(h1)
                return dict(H_star=cr, bracket=[h1, h2])
        return dict(H_star=None, bracket=None)
    hstar[k] = crossing(lambda H: results[(k, H)]['alpha'])
    hstar_bug[k] = crossing(lambda H: results[(k, H)]['alpha_buggy'])
    print(f"H*fix(k={k}) = {hstar[k]}   H*buggy(k={k}) = {hstar_bug[k]}", flush=True)

ctrl_out = {}
for name, t in CTRLS:
    for k in KGRID:
        cb = cond_bias(name, None, k)
        cbb = cond_bias(name, None, k, use_buggy=True)
        ctrl_out[(name, k)] = dict(
            fixed={n: round(mp - t, 4) for n, (mp, fr, cnt) in sorted(cb.items())},
            buggy={n: round(mp - t, 4) for n, (mp, fr, cnt) in sorted(cbb.items())})

# G0: AR(1) fixed at n=1e6
g0_pass = False
g0_p = {}
for k in KGRID:
    d = ctrl_out[('ar1_09', k)]['fixed']
    b = ctrl_out[('ar1_09', k)]['buggy']
    g0_p[k] = dict(fixed=d.get(1000000), buggy=b.get(1000000))
v = [g0_p[k]['fixed'] for k in KGRID if g0_p[k]['fixed'] is not None]
vb = [g0_p[k]['buggy'] for k in KGRID if g0_p[k]['buggy'] is not None]
g0_pass = bool(v) and max(abs(np.array(v) - 1.0)) <= 0.15
g0_bug_reproduced = bool(vb) and min(vb) > 0.30

# ---------------- outputs ------------------------------------------------------
with open('eh11_hstar_fixed.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

out = dict(
    design=dict(H_GRID=H_GRID, KGRID=KGRID, NS=NS, REPS=REPS, n_series=n_series,
                seed=1102, generator='fgn_fine(delta=1e-3)',
                truth_convention='p -> 2H', one_max=0.30,
                bugfix='fit index rho[lags] instead of rho[lags-1]'),
    gates=dict(
        G0_fix=dict(pass_=bool(g0_pass), ar1_n1e6=g0_p,
                    bug_reproduced=bool(g0_bug_reproduced)),
        G1_generator={str(H): dict(beta10=results[(KGRID[0], H)]['beta10'],
                                   dev=results[(KGRID[0], H)]['gate_dev'],
                                   pass_=abs(results[(KGRID[0], H)]['gate_dev']) <= 0.15)
                      for H in H_GRID},
        G3_min_npts=min(results[key]['npts'] for key in results),
    ),
    alpha={f"k={k}|H={H}": results[(k, H)] for k in KGRID for H in H_GRID},
    hstar={str(k): hstar[k] for k in KGRID},
    hstar_buggy={str(k): hstar_bug[k] for k in KGRID},
    controls={f"{name}|k={k}": ctrl_out[(name, k)] for name, _ in CTRLS for k in KGRID},
    elapsed_s=round(time.time()-T0, 1),
)
json.dump(out, open('eh11_hstar_fixed.json', 'w'), indent=1, default=str)

# ---------------- figure --------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
ax = axes[0]
for H in H_GRID:
    k = 10
    cb = cond_bias('fgn', H, k)
    if cb:
        ns = sorted(cb)
        ax.loglog(ns, [abs(cb[n][0] - 2*H) for n in ns], 'o-', label=f"H={H:.2f}")
ax.set_xlabel('n'); ax.set_ylabel('|p_ave - 2H|')
ax.set_title('FIXED bias decay (k=10)'); ax.legend(fontsize=7, ncol=2); ax.grid(alpha=.3)

ax = axes[1]
for k in KGRID:
    ax.plot(H_GRID, [results[(k, H)]['alpha'] for H in H_GRID], 's-', label=f"fixed k={k}")
    ax.plot(H_GRID, [results[(k, H)]['alpha_buggy'] for H in H_GRID], 'x--',
            alpha=0.4, label=f"buggy k={k}")
ax.axhline(0, color='k', ls='--')
for k in KGRID:
    if hstar[k]['H_star']:
        ax.axvline(hstar[k]['H_star'], color='tab:red', ls=':', alpha=.6)
ax.set_xlabel('H'); ax.set_ylabel('alpha')
ax.set_title('alpha(H): fixed vs buggy (red dots = H* fixed)')
ax.legend(fontsize=7, ncol=2); ax.grid(alpha=.3)

ax = axes[2]
names = [n for n, _ in CTRLS]
xpos = np.arange(len(names))
for i, k in enumerate(KGRID):
    vf = [ctrl_out[(nm, k)]['fixed'].get(1000000, np.nan) for nm in names]
    vb = [ctrl_out[(nm, k)]['buggy'].get(1000000, np.nan) for nm in names]
    ax.bar(xpos + (i-1.5)*0.18, vf, width=0.16, label=f"fixed k={k}")
    ax.plot(xpos + (i-1.5)*0.18, vb, 'rx', ms=7)
for xi, (_, t) in zip(xpos, CTRLS):
    ax.plot([xi-0.45, xi+0.45], [t, t], 'k--', lw=1.5)
ax.set_xticks(xpos); ax.set_xticklabels(names)
ax.set_ylabel('p_ave(n=1e6) - truth')
ax.set_title('controls: fixed bars (x = buggy); dashed = truth')
ax.legend(fontsize=7, ncol=2); ax.grid(alpha=.3, axis='y')
fig.suptitle('EH11 - off-by-one FIX: alpha(H) and critical H* of p_rho', y=1.02)
fig.tight_layout()
fig.savefig('eh11_hstar_fixed.png', dpi=140, bbox_inches='tight')

# ---------------- report --------------------------------------------------------
lines = ["# EH11 - CORRECTED: convergence exponent alpha(H) and critical H*",
         "",
         f"Elapsed {out['elapsed_s']}s; {n_series} series; seed 1102.",
         "",
         "## G0 bug-fix verification (AR(1) phi=0.9, truth p=1.0, n=1e6)",
         "", "| k | fixed p | buggy p |", "|---|---|---|"]
for k in KGRID:
    lines.append(f"| {k} | {g0_p[k]['fixed']} | {g0_p[k]['buggy']} |")
lines.append(f"\nG0 PASS={g0_pass} (|p_fixed-1|<=0.15), bug reproduced in "
              f"buggy estimator={g0_bug_reproduced}.")
lines += ["", "## G1 generator gate (beta10 vs 2H, n>=1e5)", "",
          "| H | beta10 | dev | pass |", "|---|---|---|---|"]
for H in H_GRID:
    g = out['gates']['G1_generator'][str(H)]
    lines.append(f"| {H} | {g['beta10']:.3f} | {g['dev']:+.3f} | {'YES' if g['pass_'] else 'NO'} |")
lines += ["", "## alpha(H,k) FIXED (positive = consistent asymptotically)",
          "", "| H | " + " | ".join(f"k={k}" for k in KGRID) + " |",
          "|---|" + "---|"*len(KGRID)]
for H in H_GRID:
    cells = []
    for k in KGRID:
        r = results[(k, H)]
        if np.isfinite(r['alpha']):
            sd = f"{r['alpha_sd']:.3f}" if np.isfinite(r['alpha_sd']) else "nan"
            cells.append(f"{r['alpha']:+.3f} (sd {sd}, n={r['npts']})")
        else:
            cells.append("---")
    lines.append(f"| {H} | " + " | ".join(cells) + " |")
lines += ["", "## alpha(H,k) BUGGY (eh10 values, for the record)",
          "", "| H | " + " | ".join(f"k={k}" for k in KGRID) + " |",
          "|---|" + "---|"*len(KGRID)]
for H in H_GRID:
    cells = [f"{results[(k, H)]['alpha_buggy']:+.3f}"
             if np.isfinite(results[(k, H)]['alpha_buggy']) else "---" for k in KGRID]
    lines.append(f"| {H} | " + " | ".join(cells) + " |")
lines += ["", "## H* (alpha=0 crossing)", "",
          "| k | H* fixed | bracket | H* buggy |", "|---|---|---|---|"]
for k in KGRID:
    hs, hb = hstar[k], hstar_bug[k]
    f_ = f"{hs['H_star']:.3f}" if hs['H_star'] else "none"
    b_ = f"{hb['H_star']:.3f}" if hb['H_star'] else "none"
    lines.append(f"| {k} | {f_} | {hs['bracket']} | {b_} |")
hv = [hstar[k]['H_star'] for k in KGRID if hstar[k]['H_star']]
hvb = [hstar_bug[k]['H_star'] for k in KGRID if hstar_bug[k]['H_star']]
lines += ["", "## controls (p_ave - truth, n=1e6)", "",
          "| cond | " + " | ".join(f"k={k}" for k in KGRID) + " (fixed; buggy in parens) |",
          "|---|" + "---|"*len(KGRID)]
for name, t in CTRLS:
    cells = []
    for k in KGRID:
        f_ = ctrl_out[(name, k)]['fixed'].get(1000000, '---')
        b_ = ctrl_out[(name, k)]['buggy'].get(1000000, '---')
        cells.append(f"{f_} ({b_})")
    lines.append(f"| {name} | " + " | ".join(cells) + " |")
lines += ["", "## validity verdict", ""]
allg1 = all(v['pass_'] for v in out['gates']['G1_generator'].values())
if g0_pass and hv:
    spread = max(hv) - min(hv)
    mean_hs = float(np.mean(hv))
    lines.append(f"G0 PASS, G1 {'PASS' if allg1 else 'PARTIAL'}, G3 min_npts="
                 f"{out['gates']['G3_min_npts']}.")
    lines.append(f"H* FIXED = {mean_hs:.3f} +/- {spread/2:.3f} "
                 f"(spread {spread:.3f} across k; buggy H* was "
                 f"{np.mean(hvb):.3f} if crossing found: {hvb}).")
    lines.append(f"eh9's claim H* in (0.75,0.95] was derived with the BUGGY "
                 f"estimator and is superseded by this run.")
else:
    lines.append(f"REVIEW REQUIRED: G0={g0_pass}, H*found={hv}, G1={allg1}")
open('eh11_hstar_fixed_REPORT.md', 'w').write("\n".join(lines))
print("DONE", out['elapsed_s'], "s", flush=True)
print("\n".join(lines[-6:]), flush=True)