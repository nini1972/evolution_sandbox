"""
C41 stage-2: Pair-orientation anisotropy audit on Gray-Scott.
Fixes stage-1 (job_glm_4_7_flash_1795055650_c91b never ran; stage-1 logic flaws):
  1. Quantile marking (encoding-relative threshold) instead of absolute u<0.35.
  2. Soft encoding with LOCAL variance normalization (uniform_filter), not global sigma.
  3. Pair-orientation anisotropy on marked-object centroids (A_peak, R2) with a
     uniform pixel-shuffle permutation null (200 surrogates) -> p-values.
  4. Structure-tensor coherence + FFT angular-power ratio as structural references.
  5. CVM on gradient orientations of the marked set, reported honestly (predicted
     non-discriminative between regimes since both labyrinths and rings are
     globally isotropic in orientation).
  6. Disc control replaced by an isotropic droplet array (noisy-seeded, short run)
     so it survives AND provides >=3 objects for pair statistics.
  7. Quantile robustness sweep q in {0.80, 0.85, 0.90}.

Pre-registered gates:
  H1 concordance:          median regime Spearman(binary, soft) >= 0.90
  H2 stripe anisotropy:    p_stripe < 0.01 (A_peak above pixel-shuffle null)
  H3 spots null-consistent: p_spots >= 0.05
  H4 disc not flagged:     p_disc  >= 0.05
  H5 fft contrast:         ratio[stripes] / max(ratio[spots], ratio[disc]) >= 3
  H6 quantile robustness:  rel. spread of A_peak[stripes] across q <= 0.25
Verdict: ENCODING_ROBUST (all) / PARTIALLY_ROBUST (H1,H2 pass) /
         METRIC_INSENSITIVE (H2 fails) / ENCODING_SENSITIVE (H1 fails)
Env: SMOKE=1 shrinks grid/steps/surrogates for local smoke tests.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter, label as cc_label
from scipy.stats import spearmanr
from colony_lib.persistence import StageTracker

SMOKE = os.environ.get('SMOKE', '0') == '1'
N = 64 if SMOKE else 256
STEPS = 1200 if SMOKE else 20000
DISC_STEPS = 500 if SMOKE else 3000
NSURR = 30 if SMOKE else 200
MAX_PAIRS = 5000 if SMOKE else 20000

RNG = np.random.default_rng(41)


# ---------------- Gray-Scott dynamics (standard parameterization) ----------------
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
            mask_d = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
            v[cy - r: cy + r + 1, cx - r: cx + r + 1][mask_d] = seed_v
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


# ---------------- marking (encoding-relative quantile) ----------------
def mark_quantile(v, q=0.85):
    thr = float(np.quantile(v, q))
    M = (v > thr).astype(np.uint8)
    lab, nlab = cc_label(M)
    return M, thr, lab, int(nlab)


def centroids(lab, nlab):
    if nlab == 0:
        return np.zeros((0, 2))
    ys, xs = np.nonzero(lab)
    k = lab[ys, xs].astype(np.int64)
    cnt = np.bincount(k, minlength=nlab + 1).astype(float)
    cy = np.bincount(k, weights=ys, minlength=nlab + 1) / np.maximum(cnt, 1.0)
    cx = np.bincount(k, weights=xs, minlength=nlab + 1) / np.maximum(cnt, 1.0)
    return np.stack([cy[1:], cx[1:]], axis=1)


def pair_orientation_stats(pts, nbins=36, max_pairs=MAX_PAIRS):
    n = len(pts)
    if n < 3:
        return None
    ii, jj = np.triu_indices(n, k=1)
    if len(ii) > max_pairs:
        sel = np.random.default_rng(7).permutation(len(ii))[:max_pairs]
        ii, jj = ii[sel], jj[sel]
    dy = pts[jj, 0] - pts[ii, 0]
    dx = pts[jj, 1] - pts[ii, 1]
    ang = np.arctan2(dy, dx)          # (-pi, pi]
    dth = np.mod(ang, np.pi)          # orientation in [0, pi)
    H = np.histogram(dth, bins=nbins, range=(0.0, np.pi))[0].astype(float)
    Hs = H / max(H.sum(), 1.0)
    R2 = float(np.abs(np.mean(np.exp(2j * ang))))
    return {'A_peak': float(Hs.max() - Hs.mean()), 'R2': R2,
            'npairs': int(len(ii)), 'nobj': int(n), 'hist': Hs.tolist()}


# ---------------- soft encoding (local variance normalization) ----------------
def soft_encode(v, win=15, gain=3.0):
    mu = uniform_filter(v, win)
    var = np.maximum(uniform_filter(v * v, win) - mu * mu, 0.0)
    sd = np.sqrt(var) + 1e-12
    z = (v - mu) / sd
    return 1.0 / (1.0 + np.exp(-gain * z))


# ---------------- structure tensor ----------------
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
    theta = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy)
    return {'coherence_mean': float(coh.mean()),
            'coherence_med': float(np.median(coh)),
            'theta_global_R2': float(np.abs(np.mean(np.exp(2j * theta.ravel()))))}


# ---------------- FFT angular power ratio ----------------
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
    return float(binned.max() / (med + 1e-12)), (binned / (binned.max() + 1e-12)).tolist()


# ---------------- CVM on gradient orientations of the marked set ----------------
def cvm_grad(S, M):
    gy, gx = np.gradient(S)
    sel = M.astype(bool)
    if int(sel.sum()) < 20:
        return float('nan')
    ang = np.arctan2(gy[sel], gx[sel])
    R2 = float(np.abs(np.mean(np.exp(2j * ang))))
    return 1.0 - R2


# ---------------- uniform pixel-shuffle null for A_peak ----------------
def perm_null_A(M, nsurr=NSURR):
    n0, n1 = M.shape
    flat = M.reshape(-1)
    out = []
    for _ in range(nsurr):
        Mp = RNG.permutation(flat).reshape(n0, n1)
        lab, nl = cc_label(Mp)
        pts = centroids(lab, nl)
        st = pair_orientation_stats(pts)
        if st is not None:
            out.append(st['A_peak'])
    return np.array(out)


def spearman_union(M, soft):
    sel = (M.astype(bool)) | (soft > 0.5)
    a = M[sel].astype(float)
    b = soft[sel]
    if a.size < 50:
        return float('nan')
    rho = spearmanr(a, b)[0]
    return float(rho)


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
tracker.save_stage('stage', 's2_pair_orientation')

# ================= RUN =================
results = {'stage': 's2_pair_orientation', 'smoke': SMOKE, 'regimes': {}}
plot = {}
for name, cfg in REGIMES:
    cfg = dict(cfg)
    steps = cfg.pop('steps', STEPS)
    print(f"[M1] {name}: {cfg} steps={steps}", flush=True)
    u, v = gs_run(steps=steps, **cfg)
    M, thr, lab, nlab = mark_quantile(v, 0.85)
    soft = soft_encode(v)
    rho = spearman_union(M, soft)
    pts = centroids(lab, nlab)
    ps = pair_orientation_stats(pts)
    nullA = perm_null_A(M)
    obsA = ps['A_peak'] if ps is not None else float('nan')
    pval = float((nullA >= obsA).mean()) if np.isfinite(obsA) and nullA.size else float('nan')
    ratio, angpow = fft_angular_ratio(v)
    ts = tensor_stats(soft)
    cvm = cvm_grad(v, M)
    results['regimes'][name] = {
        'v_mean': float(v.mean()), 'fill_frac': float((v > 0.15).mean()),
        'mark_thr': thr, 'nobj': nlab,
        'A_peak': obsA, 'R2_pair': ps['R2'] if ps else float('nan'),
        'npairs': ps['npairs'] if ps else 0,
        'pair_hist': ps['hist'] if ps else None,
        'null_A_mean': float(nullA.mean()) if nullA.size else float('nan'),
        'null_A_p95': float(np.quantile(nullA, 0.95)) if nullA.size else float('nan'),
        'p_perm': pval, 'fft_ratio': ratio,
        'tensor_coherence': ts['coherence_mean'], 'tensor_R2': ts['theta_global_R2'],
        'cvm_grad': cvm, 'spearman_binary_soft': rho,
    }
    plot[name] = {'v': v, 'M': M, 'soft': soft, 'pair_hist': ps['hist'] if ps else None,
                  'nullA': nullA, 'obsA': obsA, 'p': pval}
    print(f"    -> nobj={nlab} A_peak={obsA:.3f} p={pval:.3f} fft={ratio:.2f} "
          f"tensor_coh={ts['coherence_mean']:.3f} cvm={cvm:.3f} rho={rho:.3f}", flush=True)

# ---- quantile robustness sweep (stripes regime) ----
q_list = [0.80, 0.85, 0.90]
A_by_q = {}
for q in q_list:
    Mq, _, labq, nlq = mark_quantile(plot['stripes']['v'], q)
    stq = pair_orientation_stats(centroids(labq, nlq))
    A_by_q[str(q)] = stq['A_peak'] if stq else float('nan')
A_vals = np.array([A_by_q[str(q)] for q in q_list], dtype=float)
rel_spread = float((A_vals.max() - A_vals.min()) / (A_vals.mean() + 1e-12))
results['quantile_sweep'] = {'q': q_list, 'A_peak_stripes': A_vals.tolist(),
                             'rel_spread': rel_spread}
print(f"[sweep] q sweep A_peak(stripes)={A_vals} rel_spread={rel_spread:.3f}", flush=True)

# ================= GATES =================
def gate(name, cond, value):
    return [bool(cond) if cond is not None else None,
            None if value is None or (isinstance(value, float) and not np.isfinite(value)) else float(value)]

r = results['regimes']
rhos = [r[k]['spearman_binary_soft'] for k in ('stripes', 'spots', 'mixed', 'disc_control')]
med_rho = float(np.nanmedian(rhos))
max_spots_disc_fft = max(r['spots']['fft_ratio'], r['disc_control']['fft_ratio'])

gates = {
    'H1_concordance_binary_vs_soft': gate('H1', med_rho >= 0.90, med_rho),
    'H2_stripe_aniso_real':          gate('H2', r['stripes']['p_perm'] < 0.01, r['stripes']['p_perm']),
    'H3_spots_null_consistent':      gate('H3', r['spots']['p_perm'] >= 0.05, r['spots']['p_perm']),
    'H4_disc_not_flagged':           gate('H4', r['disc_control']['p_perm'] >= 0.05, r['disc_control']['p_perm']),
    'H5_fft_contrast':               gate('H5', r['stripes']['fft_ratio'] / (max_spots_disc_fft + 1e-12) >= 3,
                                          r['stripes']['fft_ratio'] / (max_spots_disc_fft + 1e-12)),
    'H6_quantile_robust':            gate('H6', rel_spread <= 0.25, rel_spread),
}
if all(g[0] for g in gates.values()):
    verdict = 'ENCODING_ROBUST'
elif gates['H2_stripe_aniso_real'][0] and gates['H1_concordance_binary_vs_soft'][0]:
    verdict = 'PARTIALLY_ROBUST'
elif not gates['H2_stripe_aniso_real'][0]:
    verdict = 'METRIC_INSENSITIVE'
else:
    verdict = 'ENCODING_SENSITIVE'
results['gates'] = gates
results['verdict'] = verdict
print("== S2 GATES ==", flush=True)
print(json.dumps(to_py(gates), indent=1), flush=True)
print(f"VERDICT: {verdict}", flush=True)

# ================= ARTIFACTS =================
np.savez_compressed('c41_s2_fields.npz',
                    **{f"{name}_v": plot[name]['v'] for name, _ in REGIMES},
                    **{f"{name}_M": plot[name]['M'] for name, _ in REGIMES})
with open('c41_s2_pair_orientation.json', 'w') as f:
    json.dump(to_py(results), f, indent=1)

fig, axes = plt.subplots(5, 4, figsize=(16, 19))
names = [n for n, _ in REGIMES]
for i, name in enumerate(names):
    axes[0, i].imshow(plot[name]['v'], cmap='magma'); axes[0, i].set_title(f"{name} v-field")
    axes[1, i].imshow(plot[name]['M'], cmap='gray'); axes[1, i].set_title(f"{name} binary mask q=0.85")
    axes[2, i].imshow(plot[name]['soft'], cmap='viridis'); axes[2, i].set_title(f"{name} soft (local z)")
    ph = plot[name]['pair_hist']
    if ph is not None:
        axes[3, i].bar(np.arange(len(ph)), ph, width=1.0)
    axes[3, i].set_title(f"{name} pair-orient hist (A={plot[name]['obsA']:.2f}, p={plot[name]['p']:.3f})")
    nullA = plot[name]['nullA']
    axes[4, i].hist(nullA, bins=20, color='steelblue', alpha=0.8)
    axes[4, i].axvline(plot[name]['obsA'], color='red', lw=2, label='observed')
    axes[4, i].set_title(f"{name} pixel-shuffle null (n={len(nullA)})")
    axes[4, i].legend(fontsize=8)
fig.suptitle(f"C41-s2 pair-orientation anisotropy audit — VERDICT: {verdict}")
fig.tight_layout()
fig.savefig('c41_s2_pair_orientation.png', dpi=110)
plt.close(fig)

tracker.save_stage('s2_results', to_py(results))
tracker.save_stage('final', {'verdict': verdict, 'gates': to_py(gates)})
print("saved c41_s2_pair_orientation.json + .png + fields .npz", flush=True)
