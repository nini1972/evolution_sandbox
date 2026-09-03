# Coupled Logistic Lattice - Phase Scan v3 (heterogeneous timescale)
# Tests r19z prediction: timescale gap -> higher bridge scores (resonance gap law)
import json, math, csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')

def local_update(x, r, eps):
    y = r * x * (1.0 - x)
    return np.clip((1.0 - eps) * y + 0.5 * eps * (np.roll(y, 1) + np.roll(y, -1)), 0.0, 1.0)

def make_periods(N, f_fast, N_fast, rng):
    n_fast = max(0, min(N, int(round(f_fast * N))))
    period = np.full(N, N_fast, dtype=int)
    if n_fast > 0:
        period[rng.choice(N, size=n_fast, replace=False)] = 1
    return period

def evolve(N, steps, transient, r, eps, seed=0, method='uniform', N_fast=1, f_fast=0.5):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.05, 0.95, size=N).astype(np.float64)
    if method == 'hetero':
        period = make_periods(N, f_fast, N_fast, rng)
    for t in range(transient):
        if method == 'uniform':
            x = local_update(x, r, eps)
        else:
            mask = (t % period == 0)
            coupled = local_update(x, r, eps)
            x[mask] = coupled[mask]
    h = np.empty((steps, N), dtype=np.float64)
    for t in range(steps):
        if method == 'uniform':
            x = local_update(x, r, eps)
        else:
            mask = (t % period == 0)
            coupled = local_update(x, r, eps)
            x[mask] = coupled[mask]
        h[t] = x
    return h

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

def edge_density(h):
    d = np.abs(np.roll(h, -1, axis=1) - h)
    return float(np.mean(d > 0.45))

def sensitivity_proxy(N, r, eps, trials=2, transient=100, method='uniform', N_fast=1, f_fast=0.5):
    rng = np.random.default_rng(1234)
    vals = []
    for _ in range(trials):
        a = rng.uniform(0.05, 0.95, size=N)
        b = a.copy()
        b[rng.integers(0, N)] += 1e-6
        period = make_periods(N, f_fast, N_fast, np.random.default_rng(99)) if method == 'hetero' else None
        for t in range(transient):
            if method == 'uniform':
                a = local_update(a, r, eps); b = local_update(b, r, eps)
            else:
                mask = (t % period == 0)
                a[mask] = local_update(a, r, eps)[mask]
                b[mask] = local_update(b, r, eps)[mask]
        vals.append(min(1.0, max(0.0, float(np.mean(np.abs(a - b)) / 0.5))))
    return float(np.mean(vals))

def phase_var(h):
    th = np.arctan2(2.0 * h[-1] - 1.0, np.ones_like(h[-1]))
    R = math.hypot(float(np.mean(np.cos(th))), float(np.mean(np.sin(th))))
    return float(1.0 - R)

def cluster_count(h):
    s = h[-1] >= 0.5
    return int((np.diff(s.astype(int)) != 0).sum() + 1)

def motif_persistence(h, window=10):
    if h.shape[0] <= window:
        return 0.0
    a = 2.0 * (h[window:] >= 0.5).astype(np.float64) - 1.0
    b = 2.0 * (h[:-window] >= 0.5).astype(np.float64) - 1.0
    return float(np.mean(a * b))

def bridge(o, e, s, b, p):
    co = max(0.0, 1.0 - abs(o - e))
    return float(max(0.0, o * e * s * (0.65 + 0.35 * b) * (0.5 + 0.5 * max(0.0, p)) * co))

def gap_law(N):
    return 0.793 * (1.0 - math.exp(-N / 11.2))

def metrics_from_history(h, N, r, eps, method, N_fast, f_fast):
    o = sync_order(h)
    se = spatial_entropy(h); te = temporal_entropy(h)
    ent = 0.55 * se + 0.45 * te
    sens = sensitivity_proxy(N, r, eps, method=method, N_fast=N_fast, f_fast=f_fast)
    bd = edge_density(h); pv = phase_var(h); cl = cluster_count(h); mp = motif_persistence(h)
    co = max(0.0, 1.0 - abs(o - ent))
    br = bridge(o, ent, sens, bd, mp)
    return dict(order=o, spatial_entropy=se, temporal_entropy=te, entropy=ent,
                sensitivity=sens, boundary_complexity=bd, phase_variance=pv,
                cluster_count=cl, motif_persistence=mp, coexistence=co, bridge_score=br)
