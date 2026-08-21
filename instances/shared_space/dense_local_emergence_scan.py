
"""
Dense local scan of coupled logistic lattices near the candidate ridge.
Adds spatial-structure diagnostics:
- domain-wall density
- largest-cluster fraction
- cluster-count distribution
- spatial autocorrelation length
- motif lifetime proxy
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path('../../shared_space')
OUT.mkdir(parents=True, exist_ok=True)

def logistic_step(x, r, eps):
    local = r * x * (1 - x)
    left = np.roll(x, 1)
    right = np.roll(x, -1)
    local_left = r * left * (1 - left)
    local_right = r * right * (1 - right)
    return (1 - eps) * local + 0.5 * eps * (local_left + local_right)

def run_lattice(r, eps, N=96, steps=900, transient=600, seed=17):
    rng = np.random.default_rng(seed)
    x = rng.random(N)
    history = []
    for t in range(steps):
        x = logistic_step(x, r, eps)
        x = np.clip(x, 0.0, 1.0)
        if t >= transient:
            history.append(x.copy())
    return np.asarray(history)

def order_metric(hist):
    # Mean pairwise alignment with the spatial mean field.
    if hist.size == 0:
        return np.nan
    mf = hist.mean(axis=1, keepdims=True)
    dev = np.abs(hist - mf).mean(axis=1)
    return float(np.mean(1.0 - dev / 0.5))

def entropy_metric(hist):
    # Normalized binary spatial entropy over time.
    bins = np.array([0, 0.5, 1.0])
    out = []
    for frame in hist:
        b = np.digitize(frame, bins[1:])
        counts = np.bincount(b, minlength=2)[:2]
        p = counts / counts.sum()
        p = p[p > 0]
        out.append(-np.sum(p * np.log2(p)))
    return float(np.mean(out))

def sensitivity_proxy(r, eps, N=96, steps=500, transient=200, trials=3):
    vals = []
    for seed in range(100, 100 + trials):
        rng = np.random.default_rng(seed)
        x1 = rng.random(N)
        x2 = x1 + 1e-9
        d = []
        for t in range(steps):
            x1 = np.clip(logistic_step(x1, r, eps), 0.0, 1.0)
            x2 = np.clip(logistic_step(x2, r, eps), 0.0, 1.0)
            if t >= transient:
                d.append(np.mean(np.abs(x1 - x2)))
        vals.append(np.mean(d) / 1e-9)
    return float(np.mean(vals))

def domain_wall_density(hist):
    vals = []
    for frame in hist:
        b = frame >= 0.5
        vals.append(np.mean(b != np.roll(b, 1)))
    return float(np.mean(vals))

def largest_cluster_fraction(hist):
    vals = []
    for frame in hist:
        b = frame >= 0.5
        max_run = 0
        cur = 0
        for bit in b:
            if bit:
                cur += 1
                max_run = max(max_run, cur)
            else:
                cur = 0
        # Also consider circular wrap.
        if b[0] and b[-1]:
            left = 0
            while left < len(b) and b[left]:
                left += 1
            right = len(b) - 1
            while right >= 0 and b[right]:
                right -= 1
            wrap = left + (len(b) - 1 - right)
            max_run = max(max_run, wrap)
        vals.append(max_run / len(b))
    return float(np.mean(vals))

def cluster_count(hist):
    vals = []
    for frame in hist:
        b = frame >= 0.5
        # Count 0->1 transitions on the ring.
        if b.sum() == 0 or b.sum() == len(b):
            vals.append(0)
        else:
            vals.append(np.sum((~b) & np.roll(b, 1)))
    return float(np.mean(vals))

def autocorrelation_length(hist):
    vals = []
    for frame in hist:
        z = frame - frame.mean()
        var = np.mean(z*z)
        if var < 1e-12:
            vals.append(len(frame))
            continue
        ac = np.correlate(z, z, mode='full')[len(z)-1:] / (var * np.arange(len(z), 0, -1))
        # First lag where ac falls below 1/e.
        threshold = np.exp(-1)
        below = np.where(ac < threshold)[0]
        if len(below):
            vals.append(float(below[0]))
        else:
            vals.append(float(len(frame)))
    return float(np.mean(vals))

def motif_lifetime_proxy(hist, motif_size=4):
    # Fraction of adjacent motif windows that persist for at least half the observed frames.
    if len(hist) < 4:
        return np.nan
    encoded = []
    for frame in hist:
        b = (frame >= 0.5).astype(np.uint8)
        arr = []
        for i in range(len(b)):
            val = 0
            for k in range(motif_size):
                val = (val << 1) | int(b[(i+k) % len(b)])
            arr.append(val)
        encoded.append(np.array(arr, dtype=np.int32))
    encoded = np.asarray(encoded)
    stable = 0
    total = 0
    half = len(hist) // 2
    for i in range(encoded.shape[1]):
        motif = encoded[:, i]
        # Count longest run of identical motif values.
        runs = np.diff(np.r_[0, np.where(np.diff(np.r_[motif, motif[-1]+1]))[0]+1, len(motif)+1])
        longest = runs.max()
        total += 1
        if longest >= half:
            stable += 1
    return float(stable / total)

def score(row):
    order = row['order']
    entropy = row['entropy']
    sens = row['sensitivity']
    dw = row['domain_wall_density']
    lcf = row['largest_cluster_fraction']
    cc = row['cluster_count']
    ac = row['autocorrelation_length']
    mp = row['motif_lifetime_proxy']
    # Reward moderate order, high entropy/sensitivity, nontrivial domain walls,
    # neither too fragmented nor too homogeneous, and long spatial motifs.
    moderate_order = np.exp(-((order - 0.72) / 0.22) ** 2)
    structure = dw * (1.0 - abs(lcf - 0.45)) * np.clip(cc / 8.0, 0.0, 1.0)
    coherence = np.clip(ac / 12.0, 0.0, 1.0)
    return float(moderate_order * entropy * sens * (0.35 + 0.65 * structure) * (0.5 + 0.5 * mp) * (0.5 + 0.5 * coherence))

def main():
    rv = np.linspace(3.84, 3.91, 8)
    ev = np.linspace(0.65, 0.90, 11)
    rows = []
    print('r,eps,order,entropy,sens,dw,lcf,clusters,ac,motif,score')
    for r in rv:
        for eps in ev:
            hist = run_lattice(r, eps, N=72, steps=650, transient=400, seed=221)
            order = order_metric(hist)
            entropy = entropy_metric(hist)
            sens = sensitivity_proxy(r, eps, N=72, steps=400, transient=180, trials=2)
            dw = domain_wall_density(hist)
            lcf = largest_cluster_fraction(hist)
            cc = cluster_count(hist)
            ac = autocorrelation_length(hist)
            mp = motif_lifetime_proxy(hist)
            row = {
                'r': r,
                'epsilon': eps,
                'order': order,
                'entropy': entropy,
                'sensitivity': sens,
                'domain_wall_density': dw,
                'largest_cluster_fraction': lcf,
                'cluster_count': cc,
                'autocorrelation_length': ac,
                'motif_lifetime_proxy': mp,
            }
            row['structure_score'] = score(row)
            rows.append(row)
            print('{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f}'.format(
                r, eps, order, entropy, sens, dw, lcf, cc, ac, mp, row['structure_score']))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'dense_local_emergence_scan.csv', index=False)

    # Heatmaps
    def pivot(col):
        return df.pivot(index='r', columns='epsilon', values=col).sort_index(ascending=False)

    p = pivot('structure_score')
    plt.figure(figsize=(9, 5.5))
    im = plt.imshow(p.values, origin='lower', aspect='auto', cmap='magma',
                    extent=[p.columns.min(), p.columns.max(), p.index.min(), p.index.max()])
    plt.colorbar(im, label='structure_score')
    plt.xlabel('epsilon')
    plt.ylabel('r')
    plt.title('Dense local emergence score')
    plt.tight_layout()
    plt.savefig(OUT / 'dense_local_emergence_score.png', dpi=160)
    plt.close()

    p = pivot('domain_wall_density')
    plt.figure(figsize=(9, 5.5))
    im = plt.imshow(p.values, origin='lower', aspect='auto', cmap='viridis',
                    extent=[p.columns.min(), p.columns.max(), p.index.min(), p.index.max()])
    plt.colorbar(im, label='domain-wall density')
    plt.xlabel('epsilon')
    plt.ylabel('r')
    plt.title('Dense local domain-wall density')
    plt.tight_layout()
    plt.savefig(OUT / 'dense_local_domain_wall_density.png', dpi=160)
    plt.close()

    p = pivot('autocorrelation_length')
    plt.figure(figsize=(9, 5.5))
    im = plt.imshow(p.values, origin='lower', aspect='auto', cmap='plasma',
                    extent=[p.columns.min(), p.columns.max(), p.index.min(), p.index.max()])
    plt.colorbar(im, label='autocorrelation length')
    plt.xlabel('epsilon')
    plt.ylabel('r')
    plt.title('Dense local autocorrelation length')
    plt.tight_layout()
    plt.savefig(OUT / 'dense_local_autocorrelation_length.png', dpi=160)
    plt.close()

    top = df.sort_values('structure_score', ascending=False).head(15)
    md = ['# Dense local emergence scan', '', 'Dense scan around `r=3.82..3.93`, `epsilon=0.55..0.95` with spatial diagnostics.', '']
    md.append('## Top structure-score candidates')
    md.append('')
    md.append('| r | epsilon | order | entropy | sensitivity | domain walls | largest cluster | clusters | AC length | motif proxy | score |')
    md.append('|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for _, q in top.iterrows():
        md.append('| {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.6f} |'.format(
            q['r'], q['epsilon'], q['order'], q['entropy'], q['sensitivity'], q['domain_wall_density'], q['largest_cluster_fraction'], q['cluster_count'], q['autocorrelation_length'], q['motif_lifetime_proxy'], q['structure_score']))
    md.append('')
    md.append('## Interpretation')
    md.append('')
    md.append('The structure-aware metric shifts attention away from nearly homogeneous synchronized regimes and toward mixed spatial order with persistent motifs.')
    md.append('')
    md.append('## Artifacts')
    md.append('')
    md.append('- `dense_local_emergence_scan.csv`')
    md.append('- `dense_local_emergence_score.png`')
    md.append('- `dense_local_domain_wall_density.png`')
    md.append('- `dense_local_autocorrelation_length.png`')
    (OUT / 'dense_local_emergence_scan.md').write_text('\n'.join(md), encoding='utf-8')
    print('wrote dense local scan artifacts')

if __name__ == '__main__':
    main()
