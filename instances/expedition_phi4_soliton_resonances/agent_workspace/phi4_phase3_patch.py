#!/usr/bin/env python3
# phi4_phase3_patch.py -- Phase III hotfix (GLM 4.7 Flash + Tencent HY3)
#
# Recomputes module_D from the SAVED sweep (phi4_phase3_results.json), with no
# re-simulation, applying two corrections:
#
#   Fix A (v_c definition): old code took idx of first v with esc>0.5, which
#     froze v_c at the grid edge (0.16) for every lambda and made the
#     corr(v_c, omega1)/corr(v_c, M) diagnostics meaningless (corr against a
#     constant). Correct estimator: v_c(lambda) := midpoint of
#     [max captured v, min escaped v above it]  (bracket on the capture/escape
#     boundary of the first-resonance band).
#
#   Fix B (phase clock): the resonance condition for phi^4 kink-antikink
#     multi-bounce escapes is tested against BOTH families
#        odd:  Phi = omega1*<dt> = (2k+1)*pi   ->  Phi mod 2pi = pi
#        even: Phi = omega1*<dt> = 2k*pi       ->  Phi mod 2pi = 0
#     using the circular metric, and the verdict reports which family the
#     multi-bounce (nb>=2) escapes cluster near.
#
# Then regenerates phi4_perturbed_resonances_phase3.png with corrected
# v_c overlays and writes the corrected diagnostics back into the JSON.
import json
import math
import importlib.util

import numpy as np
import matplotlib
matplotlib.use('Agg')

SRC = 'phi4_perturbed_resonances_phase3.py'
spec = importlib.util.spec_from_file_location('p3mod', SRC)
p3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p3)

res = json.load(open('phi4_phase3_results.json'))
spec_A = res['module_A']
sweep = res['module_C']
lambdas = list(sweep['lambdas'])


def circ_dist(a, b):
    """Circular distance |a-b| on the 2*pi circle (radians)."""
    d = np.mod(a - b, 2.0 * np.pi)
    return np.where(d > np.pi, 2.0 * np.pi - d, d)


# ---------------------------------------------------------------- Fix A: v_c
rows = []
omega1s, Ms, vcs = [], [], []
for lam in lambdas:
    key = f"lam{lam:.3f}"
    g = sweep['v_grids'][key]
    v = np.asarray(g['v'], float)
    esc = np.asarray(g['esc'], float)
    o1 = float(g['omega1'])
    # M is not stored in v_grids (saved sweep lacks it); take from spec_A
    M = float(spec_A['M'][spec_A['lambdas'].index(lam)])
    g['M'] = M

    cap = v[esc < 0.5]
    esp = v[esc >= 0.5]
    vc_lo = float(cap.max()) if len(cap) else float('nan')
    vc_hi = float('nan')
    if len(esp):
        above = esp[esp > (vc_lo if not math.isnan(vc_lo) else -np.inf)]
        if len(above):
            vc_hi = float(above.min())
    vc = 0.5 * (vc_lo + vc_hi) if (not math.isnan(vc_lo)
                                   and not math.isnan(vc_hi)) else vc_lo
    g['vc'] = vc
    g['vc_lo'] = vc_lo
    g['vc_hi'] = vc_hi
    omega1s.append(o1)
    Ms.append(M)
    vcs.append(vc)
    rows.append((lam, vc_lo, vc_hi, vc, o1, M))

omega1s = np.asarray(omega1s, float)
Ms = np.asarray(Ms, float)
vcs = np.asarray(vcs, float)
m = ~np.isnan(vcs)
corr_o1 = float(np.corrcoef(vcs[m], omega1s[m])[0, 1]) if m.sum() > 2 else None
corr_M = float(np.corrcoef(vcs[m], Ms[m])[0, 1]) if m.sum() > 2 else None

# ------------------------------------------------- Fix B: phase-clock verdict
key0 = f"lam{lambdas[0]:.3f}"
o1_0 = float(sweep['v_grids'][key0]['omega1'])
ph = []
for rk, run in sweep['runs'].items():
    if (abs(run['lam'] - lambdas[0]) < 1e-9 and run['escaped']
            and not np.isnan(run.get('mean_dt', np.nan))
            and int(run.get('nb', 0)) >= 2):
        Phi = o1_0 * float(run['mean_dt'])          # absolute clock phase
        n_odd = 2 * round((Phi / np.pi - 1.0) / 2.0) + 1   # nearest (2k+1)*pi
        n_even = 2 * round(Phi / (2.0 * np.pi))            # nearest 2k*pi
        ph.append(dict(v=float(run['v']), nb=int(run['nb']),
                       mean_dt=float(run['mean_dt']),
                       Phi_mod=float(Phi % (2.0 * np.pi)),
                       n_odd=int(n_odd),
                       d_odd=float(circ_dist(Phi, n_odd * np.pi)),
                       d_even=float(circ_dist(Phi, n_even * np.pi))))

if ph:
    d_o = np.array([p['d_odd'] for p in ph])
    d_e = np.array([p['d_even'] for p in ph])
    verdict = ('odd-multiples-of-pi: Phi=(2k+1)pi'
               if d_o.mean() < d_e.mean() else 'even-multiples: Phi=2k*pi')
    phase_stat = dict(
        n_multi_bounce_escapes=len(ph),
        mean_dev_odd=float(d_o.mean()),
        mean_dev_even=float(d_e.mean()),
        max_dev_odd=float(d_o.max()),
        frac_within_pi_over_8_odd=float(np.mean(d_o < np.pi / 8.0)),
        frac_within_pi_over_8_even=float(np.mean(d_e < np.pi / 8.0)),
        verdict=verdict)
else:
    phase_stat = dict(n_multi_bounce_escapes=0,
                      verdict='no multi-bounce escapes in lambda=0 grid')

diag_new = dict(
    lambdas=lambdas,
    vc=vcs.tolist(),
    vc_lo=[float(sweep['v_grids'][f"lam{l:.3f}"]['vc_lo']) for l in lambdas],
    vc_hi=[float(sweep['v_grids'][f"lam{l:.3f}"]['vc_hi']) for l in lambdas],
    omega1=omega1s.tolist(),
    M=Ms.tolist(),
    corr_vc_omega1=corr_o1,
    corr_vc_M=corr_M,
    phase_clock=phase_stat,
    phase_points=ph)

# ---------------------------------------------------------------- report
print("=" * 78)
print("PHASE III PATCH -- corrected v_c(lambda)  [bracket: capture .. escape]")
print("=" * 78)
for lam, vc_lo, vc_hi, vc, o1, M in rows:
    print(f"lam={lam:5.3f}  capture<={vc_lo:6.3f}  escape>={vc_hi:6.3f}  "
          f"vc={vc:6.4f}   omega1={o1:.4f}  M={M:.4f}")
print("-" * 78)
if corr_o1 is not None:
    print(f"corr(vc, omega1) = {corr_o1:+.3f}    corr(vc, M) = {corr_M:+.3f}")
print(f"phase-clock: {phase_stat.get('verdict')}")
if ph:
    print(f"  n={phase_stat['n_multi_bounce_escapes']}  "
          f"dev_odd={phase_stat['mean_dev_odd']:.3f} rad  "
          f"dev_even={phase_stat['mean_dev_even']:.3f} rad  "
          f"frac<pi/8 odd={phase_stat['frac_within_pi_over_8_odd']:.2f}")

# ------------------------------------------- persist corrected results + fig
res['module_D'] = diag_new
res.setdefault('meta', {})['patched'] = {
    'vc_definition': 'midpoint(max captured v, min escaped v above)',
    'phase_test': 'odd (2k+1)pi vs even 2k*pi circular-distance families'}
with open('phi4_phase3_results.json', 'w') as f:
    json.dump(res, f, default=lambda o: (o.tolist() if isinstance(o, np.ndarray) else o))
print("[save] phi4_phase3_results.json (module_D patched)", flush=True)

p3.make_figure(spec_A, sweep, diag_new, 'phi4_perturbed_resonances_phase3.png')
print("[done] patched diagnostics + figure", flush=True)
