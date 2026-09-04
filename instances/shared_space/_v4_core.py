# Coupled Logistic Lattice - v4: clean multi-timescale model (resonance gap law test)
# All sites do r*x*(1-x) every step (intrinsic chaos). Spatial diffusion (coupling to
# neighbors) is applied at a per-site period -> a slowly-varying spatial scaffold coexists
# with fast chaotic mixing. This is the condition under which cross-timescale structure
# (the "bridge") should rise with the timescale gap.
import math, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')

def logistic_step(x, r):
    return np.clip(r * x * (1.0 - x), 0.0, 1.0)

def diffusion_step(x, eps, x_prev=None):
    # nonlocal coupling to left/right neighbors (uses x_prev optionally; here neighbor values)
    src = x if x_prev is None else x_prev
    return np.clip((1.0 - eps) * x + 0.5 * eps * (np.roll(src, 1) + np.roll(src, -1)), 0.0, 1.0)

def make_periods(N, f_fast, N_fast, rng):
    n_fast = max(0, min(N, int(round(f_fast * N))))
    period = np.full(N, N_fast, dtype=int)
    if n_fast > 0:
        period[rng.choice(N, size=n_fast, replace=False)] = 1
    return period

def evolve(N, steps, transient, r, eps, seed=0, method='uniform', N_fast=1, f_fast=0.5):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.05, 0.95, size=N).astype(np.float64)
    period = make_periods(N, f_fast, N_fast, np.random.default_rng(seed + 7)) if method == 'hetero' else None
    def apply(xa, t):
        xa = logistic_step(xa, r)
        if method == 'uniform':
            xa = diffusion_step(xa, eps)
        else:
            m = (t % period == 0)
            xa = xa.copy()
            xa[m] = diffusion_step(x, eps)[m]
        return xa
    for t in range(transient):
        x = apply(x, t)
    h = np.empty((steps, N), dtype=np.float64)
    for t in range(steps):
        x = apply(x, t)
        h[t] = x
    return h, period

def entropy_hist(vals, bins=32):
    hist, _ = np.histogram(vals, bins=bins, range=(0.0, 1.0))
    p = hist / max(int(hist.sum()), 1)
    p = p[p > 0]
    return float(-(p * np.log(p + 1e-15)).sum() / np.log(bins))

def sync_order(h):
    v = h.var(axis=1)
    obs = max(float(h.max() - h.min()), 1e-12)
    return float(np.clip(1.0 - np.mean(v / (obs * obs)), 0.0, 1.0))

def spatial_entropy(h, bins=32):
    return entropy_hist(h.ravel(), bins=bins)

def temporal_entropy(h, bins=32, sites=32):
    n = h.shape[1]
    js = np.linspace(0, n - 1, min(sites, n)).astype(int)
    return float(np.mean([entropy_hist(h[:, j], bins=bins) for j in js]))

def edge_density(h, thr=0.5, bins=40):
    s = (h >= thr).astype(np.float64)
    d = np.abs(np.roll(s, -1, axis=1) - s)
    return float(np.mean(d > 0.5))

def phase_var(h):
    th = np.arctan2(2.0 * h[-1] - 1.0, np.ones_like(h[-1]))
    R = math.hypot(float(np.mean(np.cos(th))), float(np.mean(np.sin(th))))
    return float(1.0 - R)

def cluster_count(h, thr=0.5):
    s = h[-1] >= thr
    return int((np.diff(s.astype(int)) != 0).sum() + 1)

def motif_persistence(h, window=10):
    if h.shape[0] <= window:
        return 0.0
    a = 2.0 * (h[window:] >= 0.5).astype(np.float64) - 1.0
    b = 2.0 * (h[:-window] >= 0.5).astype(np.float64) - 1.0
    return float(np.mean(a * b))

def sensitivity_proxy(N, r, eps, seed=0, trials=1, transient=80, method='uniform', N_fast=1, f_fast=0.5):
    rng = np.random.default_rng(seed + 999)
    best = 0.0
    for k in range(trials):
        h1, _ = evolve(N, 60, transient, r, eps, seed=seed, method=method, N_fast=N_fast, f_fast=f_fast)
        h2, _ = evolve(N, 60, max(0, transient - 30), r, eps, seed=seed + 1 + k, method=method, N_fast=N_fast, f_fast=f_fast)
        if h1.shape[0] != h2.shape[0]:
            n = min(h1.shape[0], h2.shape[0])
            h1 = h1[:n]; h2 = h2[:n]
        d = np.mean(np.abs(h1 - h2), axis=1)
        # late-time divergence
        if d.size > 20:
            best = max(best, float(d[-20:].mean() - d[:20].mean()))
    return float(best)

def metrics_from_history(h, N, r, eps, method, N_fast, f_fast):
    order = sync_order(h)
    sp_ent = spatial_entropy(h)
    tm_ent = temporal_entropy(h)
    edge = edge_density(h)
    pv = phase_var(h)
    cc = cluster_count(h)
    mp = motif_persistence(h)
    sens = sensitivity_proxy(N, r, eps, seed=424242, method=method, N_fast=N_fast, f_fast=f_fast)
    # Bridge score: a late-time, cross-timescale spatial motif that persists while
    # fast chaos mixes point values. We quantify as motif_persistence weighted by
    # how much edge structure survives (edge_density) on the slow scaffold.
    bridge = mp * edge * (1.0 - sens)
    return {
        'order': order,
        'entropy': 0.5 * (sp_ent + tm_ent),
        'sensitivity': sens,
        'boundary_complexity': edge,
        'phase_var': pv,
        'cluster_count': cc,
        'motif_persistence': mp,
        'bridge_score': bridge,
    }

def gap_law(N_fast):
    # r19z resonance gap law placeholder: monotonic saturating in timescale gap
    return float(0.793 * (1.0 - math.exp(-N_fast / 11.2)))
