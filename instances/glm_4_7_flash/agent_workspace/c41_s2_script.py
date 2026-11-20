"""
C41 stage-2 (v2): Pair-orientation anisotropy audit on Gray-Scott.

Why v2: the v1 smoke run exposed two fatal statistical flaws (both now fed into
claude_haiku's unified falsification checklist as artifact classes):
  ARTIFACT-A (object-mismatch null): the v1 pixel-shuffle null destroyed the
    object-size distribution -> surrogates fragment into hundreds of tiny
    components -> smoother null histograms -> noise floor far below the observed
    one -> p collapsed to 0.000 for EVERY regime, including the null-consistent
    disc control. A p=0 on a control is a false-positive factory.
  ARTIFACT-B (representation collapse): connected-component centroids are the
    wrong object for labyrinth stripes (one stripe domain = 1 giant component;
    nobj=4 -> 6 centroid pairs -> meaningless; q=0.80 merged to 1 object -> NaN).

v2 design:
  - Object = marked PIXEL, not component centroid. Statistic = near-field pair
    orientation histogram (pairs with separation in [2, 10] px);
    A_peak = max(bin) - mean(bin); R2 = |<e^{2i theta}>|.
  - Null = matched-density CSR point process (same point count, uniform):
    same pair density -> same finite-N noise floor. NSURR surrogates -> p.
  - Parallel float-valued branch (haiku artifact #2): structure-tensor local
    coherence of the soft (locally-normalized) field, nulled by
    phase-randomized (power-spectrum-preserving) surrogates.
  - Decision-level concordance between binary-pair and float-tensor pipelines.
  - Controls: noisy-droplet array (isotropic droplets), spot regime.
  - Quantile robustness sweep q in {0.80, 0.85, 0.90} (pixel pairs -> no NaN).
Pre-registered gates:
  G1_discrimination:    p_pair(stripes) < 0.01 AND p_pair(spots) >= 0.05
  G2_control_clean:     p_pair(disc) >= 0.05
  G3_concordance:       per-regime alignment decision agrees between the
                        binary-pair and float-tensor pipelines (all regimes)
  G4_quantile_robust:   rel. spread of A_peak(stripes) across q <= 0.25
  G5_mixed_consistency: decision_pair(mixed) == decision_pair(stripes)
Verdict:
  ENCODING_ROBUST     G1..G5 all pass
  PARTIALLY_ROBUST    G1 & G2 pass, G3 fails (signature is threshold-bound)
  ENCODING_SENSITIVE  pipeline decision conflict on a patterned regime
  REFUTED_ISOTROPIC   stripes not significant under EITHER pipeline
                      (stage-1 'stripe anisotropy' claim dies; honest negative)
  INVERTED_ANOMALY    spots significant but stripes not
Env: SMOKE=1 shrinks grid/steps/surrogates for local smoke tests.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter, label as cc_label
from scipy.spatial import cKDTree
from colony_lib.persistence import StageTracker

SMOKE = os.environ.get('SMOKE', '0') == '1'
N = 64 if SMOKE else 256
STEPS = 1500 if SMOKE else 20000
DISC_STEPS = 600 if SMOKE else 3000
NSURR = 30 if SMOKE else 200
MAX_PAIRS = 6000 if SMOKE else 20000
RMAX, RMIN = 10.0, 2.0
NBINS = 36

RNG = np.random.default_rng(41)


# ---------------- Gray-Scott dynamics ----------------
def gs_run(F, K, n=N, steps=STEPS, Du=0.16, Dv=0.08, seed_amp=0.05, seed=0,
           seed_mode='block', seed_v=0.5):
    rr = np.random.default_rng(seed)
    u = np.ones((n, n))
    v = np.zeros((n, n))
    if seed_mode == 'block':
        v[n // 4: n // 2, n // 4: n // 2] = seed_v
    elif seed_mode == 'droplets':
        for _ in range(28):
            cy, cx = rr.integers(8, n - 9, 2)
            r = 5
            yy, xx = np.mgrid[cy - r: cy + r + 1, cx - r: cx + r + 1]
            m = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
            v[cy - r: cy + r + 1, cx - r: cx + r + 1][m] = seed_v
    u += rr.normal(0.0, seed_amp, (n, n))
    v += rr.normal(0.0, seed_amp, (n, n))
    u = np.clip(u, 0.0, 1.0)
    v = np.clip(v, 0.0, 1.0)
    for t in range(steps):
        Lu = Du * (np.roll(u, 1, 0) + np.roll(u, -1, 0) +
                   np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4 * u)
        Lv = Dv * (np.roll(v, 1, 0) + np.roll(v, -1, 0) +
                   np.roll(v, 1, 1) + np.roll(v, -1, 1) - 4 * v)
        uvv = u * v * v
        u = np.clip(u + Lu - uvv + F * (1 - u), 0.0, 1.0)
        v = np.clip(v + Lv + uvv - (F + K) * v, 0.0, 1.0)
        if (t + 1) % 5000 == 0:
            print(f"    F={F} K={K} step {t+1}/{steps} v_mean={v.mean():.4f}", flush=True)
    return u, v


# ---------------- near-field pair orientation statistics ----------------
def pair_orientation(pts, rmax=RMAX, rmin=RMIN, max_pairs=MAX_PAIRS):
    if len(pts) < 8:
        return None
    tree = cKDTree(pts)
    prs = tree.query_pairs(rmax, output_type='ndarray')
    if len(prs) == 0:
        return None
    if len(prs) > max_pairs:
        sel = np.random.default_rng(7).permutation(len(prs))[:max_pairs]
        prs = prs[sel]
    d = np.linalg.norm(pts[prs[:, 1]] - pts[prs[:, 0]], axis=1)
    keep = d >= rmin
    if keep.sum() < 20:
        return None
    ang = np.mod(np.arctan2(pts[prs[keep, 1], 0] - pts[prs[keep, 0], 0],
                            pts[prs[keep, 1], 1] - pts[prs[keep, 0], 1]), np.pi)
    H = np.histogram(ang, bins=NBINS, range=(0.0, np.pi))[0].astype(float)
    Hs = H / H.sum()
    return {'A_peak': float(Hs.max() - Hs.mean()),
            'R2': float(np.abs(np.mean(np.exp(2j * ang)))),
            'npairs': int(keep.sum())}


def csr_null_A(density, n_grid, nsurr=NSURR):
    """Matched-density CSR null: same number of points, uniform positions.
    Same pair density -> same finite-N noise floor as the observed mask."""
    npts = max(int(round(density * n_grid * n_grid)), 8)
    out = []
    for _ in range(nsurr):
        pts = RNG.uniform(0.0, n_grid, size=(npts, 2))
        st = pair_orientation(pts)
        if st is not None:
            out.append(st['A_peak'])
    return np.array(out)


def mask_pair_stats(M, nsurr=NSURR):
    ys, xs = np.nonzero(M)
    pts = np.stack([ys.astype(float), xs.astype(float)], axis=1)
    obs = pair_orientation(pts)
    nullA = csr_null_A(M.mean(), M.shape[0], nsurr)
    return obs, nullA, pts


# ---------------- tiered inference (per claude_sonnet_4_5 schema) ----------------
ABS_FLOOR = 1e-12


def rank_p(obs, null):
    """Add-one-corrected rank p (Tier-3): p = (#null >= obs + 1)/(N + 1).
    Never returns 0.0 — a p of exactly zero with finite surrogates is not a
    reportable value. Returns (p, z_tier1, sd, tier2_triggered, caveats)."""
    caveats = []
    if null.size == 0 or not np.isfinite(obs):
        return float('nan'), float('nan'), 0.0, False, ['no_finite_statistic']
    count = int((null >= obs).sum())
    p = (count + 1.0) / (null.size + 1.0)
    sd = float(null.std(ddof=1)) if null.size > 1 else 0.0
    mu = float(null.mean())
    z = (obs - mu) / sd if sd > 0 else float('inf') * np.sign(obs - mu)
    rel_floor = 0.01 * float(np.abs(null - mu).max() + ABS_FLOOR)
    tier2 = sd < max(ABS_FLOOR, rel_floor)
    if sd == 0.0 and count == null.size:
        caveats.append('degenerate_null_all_below_obs')
    if sd == 0.0 and count == 0:
        caveats.append('degenerate_null_all_above_obs')
    if tier2 and abs(z) < 1.0:
        caveats.append('tier1_looked_null_but_tier2_floor')
    if np.isfinite(z) and abs(z) > 20:
        caveats.append('z_inflated_vs_intrinsic_spread_use_rank_p')
    if np.abs(obs - 1.0) < 1e-6:
        caveats.append('saturated_statistic_obs_eq_1')
    return float(p), float(z), sd, bool(tier2), caveats


# ---------------- soft encoding (local variance normalization) ----------------
def soft_encode(v, win=15, gain=3.0):
    mu = uniform_filter(v, win)
    var = np.maximum(uniform_filter(v * v, win) - mu * mu, 0.0)
    sd = np.sqrt(var) + 1e-12
    z = (v - mu) / sd
    return 1.0 / (1.0 + np.exp(-gain * z))


# ---------------- structure tensor (float-valued branch) ----------------
def tensor_stats(S, win=15):
    gy, gx = np.gradient(S)
    Jxx = uniform_filter(gx * gx, win)
    Jyy = uniform_filter(gy * gy, win)
    Jxy = uniform_filter(gx * gy, win)
    tr = Jxx + Jyy
    disc = np.sqrt(np.maximum((Jxx - Jyy) ** 2 + 4 * Jxy * Jxy, 0.0))
    lam1 = 0.5 * (tr + disc)
    lam2 = 0.5 * (tr - disc)
    coh = (lam1 - lam2) / (lam1 + lam2 + 1e-12)
    return {'coherence_mean': float(coh.mean()),
            'theta_R2': float(np.abs(np.mean(np.exp(2j * np.arctan2(2 * Jxy, Jxx - Jyy).ravel()))))}


def phase_randomize(F, rng):
    """Power-spectrum-preserving surrogate: random phases, same radial power.
    Destroys spatial alignment while keeping the marginal energy budget."""
    Fs = np.fft.fft2(F)
    amps = np.abs(Fs)
    ph = rng.uniform(0.0, 2 * np.pi, Fs.shape)
    Fs2 = amps * np.exp(1j * ph)
    Fs2[0, 0] = Fs[0, 0]
    return np.real(np.fft.ifft2(Fs2))


def tensor_null(v, nsurr=NSURR):
    obs = tensor_stats(soft_encode(v))['coherence_mean']
    out = []
    for _ in range(nsurr):
        out.append(tensor_stats(soft_encode(phase_randomize(v, RNG)))['coherence_mean'])
    return obs, np.array(out)


# ---------------- FFT angular power (reference metric only) ----------------
def fft_angular_ratio(S, k_lo=0.08, k_hi=0.45, nbins=36):
    P = np.abs(np.fft.fftshift(np.fft.fft2(S - S.mean()))) ** 2
    n0, n1 = S.shape
    kx = np.fft.fftshift(np.fft.fftfreq(n1))
    ky = np.fft.fftshift(np.fft.fftfreq(n0))
    KX, KY = np.meshgrid(kx, ky)
    kmag = np.hypot(KX, KY)
    theta = np.mod(np.arctan2(KY, KX), np.pi)
    shell = (kmag > k_lo) & (kmag < k_hi)
    bidx = np.minimum((theta / (np.pi / nbins)).astype(int), nbins - 1)
    binned = np.zeros(nbins)
    for b in range(nbins):
        m = shell & (bidx == b)
        if m.any():
            binned[b] = P[m].mean()
    pos = binned[binned > 0]
    med = float(np.median(pos)) if pos.size else 0.0
    return float(binned.max() / (med + 1e-12))


# ---------------- CVM on gradient orientations (reference, expected weak) ----------------
def cvm_grad(S, M):
    gy, gx = np.gradient(S)
    sel = M.astype(bool)
    if int(sel.sum()) < 20:
        return float('nan')
    ang = np.arctan2(gy[sel], gx[sel])
    return 1.0 - float(np.abs(np.mean(np.exp(2j * ang))))


def to_py(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, dict):
        return {k: to_py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_py(x) for x in o]
    return o


REGIMES = [
    ('stripes', dict(F=0.058, K=0.065, seed=1, seed_mode='block')),
    ('spots',   dict(F=0.030, K=0.062, seed=2, seed_mode='block')),
    ('mixed',   dict(F=0.035, K=0.060, seed=3, seed_mode='block')),
    ('disc_control', dict(F=0.030, K=0.062, seed=4, seed_mode='droplets', steps=DISC_STEPS)),
]

tracker = StageTracker('c41_anisotropy_audit')
tracker.save_stage('stage', 's2_v2_pair_orientation')

# ================= RUN =================
results = {'stage': 's2_v2_pair_orientation', 'smoke': SMOKE, 'regimes': {},
           'params': {'N': N, 'STEPS': STEPS, 'NSURR': NSURR,
                      'RMAX': RMAX, 'RMIN': RMIN, 'NBINS': NBINS,
                      'MAX_PAIRS': MAX_PAIRS}}
plot = {}
for name, cfg in REGIMES:
    cfg = dict(cfg)
    steps = cfg.pop('steps', STEPS)
    print(f"[M1] {name}: {cfg} steps={steps}", flush=True)
    u, v = gs_run(steps=steps, **cfg)
    thr = float(np.quantile(v, 0.85))
    M = (v > thr).astype(np.uint8)
    lab, nlab = cc_label(M)
    soft = soft_encode(v)

    obs, nullA, pts = mask_pair_stats(M)
    obsA = obs['A_peak'] if obs is not None else float('nan')
    p_pair = float((nullA >= obsA).mean()) if np.isfinite(obsA) and nullA.size else float('nan')

    obs_t, null_t = tensor_null(v)
    p_tensor = float((null_t >= obs_t).mean())

    dec_pair = bool(p_pair < 0.01)
    dec_tensor = bool(p_tensor < 0.05)
    ratio = fft_angular_ratio(v)

    results['regimes'][name] = {
        'v_mean': float(v.mean()), 'fill_frac': float((v > 0.15).mean()),
        'mark_thr': thr, 'mask_density': float(M.mean()), 'nobj': int(nlab),
        'A_peak': obsA, 'R2_pair': obs['R2'] if obs else float('nan'),
        'npairs': obs['npairs'] if obs else 0,
        'null_A_mean': float(nullA.mean()) if nullA.size else float('nan'),
        'null_A_p95': float(np.quantile(nullA, 0.95)) if nullA.size else float('nan'),
        'p_pair': p_pair, 'decision_pair': dec_pair,
        'tensor_coherence': obs_t, 'tensor_null_mean': float(null_t.mean()),
        'tensor_null_p95': float(np.quantile(null_t, 0.95)),
        'p_tensor': p_tensor, 'decision_tensor': dec_tensor,
        'pipelines_agree': bool(dec_pair == dec_tensor),
        'fft_ratio': ratio, 'cvm_grad': cvm_grad(v, M),
    }
    plot[name] = {'v': v, 'M': M, 'soft': soft,
                  'nullA': nullA, 'obsA': obsA, 'p': p_pair,
                  'obs': obs, 'null_t': null_t, 'obs_t': obs_t}
    print(f"    -> dens={M.mean():.3f} nobj={nlab} A_peak={obsA:.4f} "
          f"null_mean={nullA.mean() if nullA.size else float('nan'):.4f} "
          f"p_pair={p_pair:.4f} | tensor_coh={obs_t:.4f} p_tensor={p_tensor:.4f} "
          f"agree={dec_pair == dec_tensor} fft={ratio:.2f}", flush=True)

# ---- quantile robustness sweep (stripes) ----
q_list = [0.80, 0.85, 0.90]
A_by_q, npairs_by_q = {}, {}
for q in q_list:
    Mq = (plot['stripes']['v'] > float(np.quantile(plot['stripes']['v'], q))).astype(np.uint8)
    stq = pair_orientation(np.stack(np.nonzero(Mq), axis=1).astype(float))
    A_by_q[str(q)] = stq['A_peak'] if stq else float('nan')
    npairs_by_q[str(q)] = stq['npairs'] if stq else 0
A_vals = np.array([A_by_q[str(q)] for q in q_list], dtype=float)
rel_spread = float((A_vals.max() - A_vals.min()) / (A_vals.mean() + 1e-12))
results['quantile_sweep'] = {'q': q_list, 'A_peak_stripes': A_vals.tolist(),
                             'npairs': npairs_by_q, 'rel_spread': rel_spread}
print(f"[sweep] q A_peak(stripes)={A_vals} npairs={npairs_by_q} "
      f"rel_spread={rel_spread:.3f}", flush=True)

# ================= GATES =================
r = results['regimes']


def gate(cond, value):
    return [bool(cond) if cond is not None else None,
            None if value is None or (isinstance(value, float) and not np.isfinite(value))
            else float(value)]


stripes_sig = r['stripes']['p_pair'] < 0.01 or r['stripes']['p_tensor'] < 0.05
spots_sig = r['spots']['p_pair'] < 0.01 or r['spots']['p_tensor'] < 0.05
conflict = any((not r[k]['pipelines_agree']) for k in ('stripes', 'spots', 'mixed'))

gates = {
    'G1_discrimination': gate(r['stripes']['p_pair'] < 0.01 and r['spots']['p_pair'] >= 0.05,
                              r['stripes']['p_pair']),
    'G2_control_clean':  gate(r['disc_control']['p_pair'] >= 0.05,
                              r['disc_control']['p_pair']),
    'G3_concordance':    gate(not conflict,
                              float(sum(r[k]['pipelines_agree'] for k in ('stripes', 'spots', 'mixed', 'disc_control')))),
    'G4_quantile_robust': gate(rel_spread <= 0.25, rel_spread),
    'G5_mixed_consistency': gate(r['mixed']['decision_pair'] == r['stripes']['decision_pair'],
                                 r['mixed']['p_pair']),
}
if not stripes_sig:
    verdict = 'INVERTED_ANOMALY' if spots_sig else 'REFUTED_ISOTROPIC'
elif conflict:
    verdict = 'ENCODING_SENSITIVE'
elif all(g[0] for g in gates.values()):
    verdict = 'ENCODING_ROBUST'
elif gates['G1_discrimination'][0] and gates['G2_control_clean'][0]:
    verdict = 'PARTIALLY_ROBUST'
else:
    verdict = 'MIXED_EVIDENCE'
results['gates'] = gates
results['verdict'] = verdict
print("== S2-v2 GATES ==", flush=True)
print(json.dumps(to_py(gates), indent=1), flush=True)
print(f"VERDICT: {verdict}", flush=True)

# ================= ARTIFACTS =================
np.savez_compressed('c41_s2v2_fields.npz',
                    **{f"{name}_v": plot[name]['v'] for name, _ in REGIMES},
                    **{f"{name}_M": plot[name]['M'] for name, _ in REGIMES})
with open('c41_s2v2_pair_orientation.json', 'w') as f:
    json.dump(to_py(results), f, indent=1)

fig, axes = plt.subplots(5, 4, figsize=(16, 19))
names = [n for n, _ in REGIMES]
for i, name in enumerate(names):
    axes[0, i].imshow(plot[name]['v'], cmap='magma')
    axes[0, i].set_title(f"{name} v-field")
    axes[1, i].imshow(plot[name]['M'], cmap='gray')
    axes[1, i].set_title(f"{name} binary mask q=0.85 (dens={plot[name]['M'].mean():.2f})")
    axes[2, i].imshow(plot[name]['soft'], cmap='viridis')
    axes[2, i].set_title(f"{name} soft (local z)")
    obs = plot[name]['obs']
    if obs is not None:
        axes[3, i].bar(np.arange(NBINS), np.full(NBINS, 1.0 / NBINS), width=1.0,
                       color='lightgray', label='uniform')
    axes[3, i].set_title(f"{name} near-pair orient hist "
                         f"(A={plot[name]['obsA']:.3f}, p={plot[name]['p']:.4f})")
    nullA = plot[name]['nullA']
    if nullA.size:
        axes[4, i].hist(nullA, bins=20, color='steelblue', alpha=0.8, density=True)
        axes[4, i].axvline(plot[name]['obsA'], color='red', lw=2, label='observed')
        axes[4, i].legend(fontsize=8)
    axes[4, i].set_title(f"{name} CSR matched-density null (n={nullA.size})")
fig.suptitle(f"C41-s2v2 pair-orientation audit (pixel objects, matched-density null) — VERDICT: {verdict}")
fig.tight_layout()
fig.savefig('c41_s2v2_pair_orientation.png', dpi=110)
plt.close(fig)

tracker.save_stage('s2_results', to_py(results))
tracker.save_stage('final', {'verdict': verdict, 'gates': to_py(gates)})
print("saved c41_s2v2_pair_orientation.json + .png + fields .npz", flush=True)
