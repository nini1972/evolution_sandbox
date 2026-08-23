from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('../../shared_space')
OUT.mkdir(parents=True, exist_ok=True)


def logistic_step(x, r, eps):
    local = r * x * (1 - x)
    left = np.roll(x, 1)
    right = np.roll(x, -1)
    local_left = r * left * (1 - left)
    local_right = r * right * (1 - right)
    return (1 - eps) * local + 0.5 * eps * (local_left + local_right)


def run_lattice(r, eps, N=100, steps=700, transient=300, seed=101):
    rng = np.random.default_rng(seed)
    x = rng.random(N)
    history = []
    for t in range(steps):
        x = logistic_step(x, r, eps)
        x = np.clip(x, 0.0, 1.0)
        if t >= transient:
            history.append(x.copy())
    return np.asarray(history)


def binary_frames(hist):
    return (hist >= 0.5).astype(np.uint8)


def wall_density(bits):
    return float(np.mean(bits != np.roll(bits, 1, axis=1)))


def wall_velocity(bits):
    n = bits.shape[1]
    velocities = []
    for t in range(1, len(bits)):
        prev_walls = np.flatnonzero(bits[t - 1] != np.roll(bits[t - 1], 1))
        cur_walls = np.flatnonzero(bits[t] != np.roll(bits[t], 1))
        if len(prev_walls) == 0 or len(cur_walls) == 0:
            velocities.append(np.nan)
            continue
        d = np.abs((prev_walls[:, None] - cur_walls[None, :] + n // 2) % n - n // 2)
        velocities.append(float(d.min(axis=0).mean()))
    return np.array(velocities)


def lag_similarity(bits, lags=(1, 5, 10, 20, 50)):
    out = {}
    for lag in lags:
        vals = []
        for t in range(len(bits) - lag):
            vals.append(float(np.mean(bits[t] == bits[t + lag])))
        out[lag] = float(np.mean(vals)) if vals else np.nan
    return out


def motif_recurrence(bits, motif_size=6):
    n = bits.shape[1]
    counts = {}
    total = 0
    for frame in bits:
        for i in range(n):
            val = 0
            for k in range(motif_size):
                val = (val << 1) | int(frame[(i + k) % n])
            counts[val] = counts.get(val, 0) + 1
            total += 1
    if total == 0:
        return np.nan, np.nan, np.nan
    probs = np.array(list(counts.values())) / total
    simpson = float(np.sum(probs * probs))
    entropy = float(-np.sum(probs * np.log2(probs + 1e-16)))
    return simpson, entropy, len(counts)


def score_components(row):
    wd = row['domain_wall_density']
    v = row['mean_wall_velocity']
    lag10 = row['lag10_similarity']
    lag5 = row['lag5_similarity']
    motif = row['motif_simpson']
    spatial_complexity = float(np.exp(-((wd - 0.35) / 0.25) ** 2))
    velocity_low = float(1.0 / (1.0 + np.exp(8.0 * (v - 0.45)))) if np.isfinite(v) else 0.0
    lag10_score = float(np.exp(-((lag10 - 0.68) / 0.25) ** 2)) if np.isfinite(lag10) else 0.0
    motif_score = float(0.4 + 0.6 * motif) if np.isfinite(motif) else 0.0
    temporal_score = float(0.4 + 0.6 * lag5) if np.isfinite(lag5) else 0.0
    if wd < 1e-6:
        velocity_low = 0.0
    return spatial_complexity * velocity_low * lag10_score * motif_score * temporal_score


def main():
    rows = []
    r_values = np.linspace(3.40, 4.00, 25)
    eps_values = np.linspace(0.00, 1.00, 21)

    for ri, r in enumerate(r_values):
        for ei, eps in enumerate(eps_values):
            seed = 5000 + int(round(r * 100)) + int(round(eps * 100)) + ri * 1000 + ei
            hist = run_lattice(r, eps, N=100, steps=700, transient=300, seed=seed)
            bits = binary_frames(hist)
            wd = wall_density(bits)
            v = wall_velocity(bits)
            lags = lag_similarity(bits)
            simpson, entropy, motif_count = motif_recurrence(bits, motif_size=6)
            row = {
                'r': float(r),
                'epsilon': float(eps),
                'domain_wall_density': wd,
                'mean_wall_velocity': float(np.nanmean(v)) if np.isfinite(v).any() else np.nan,
                'median_wall_velocity': float(np.nanmedian(v)) if np.isfinite(v).any() else np.nan,
                'lag1_similarity': lags[1],
                'lag5_similarity': lags[5],
                'lag10_similarity': lags[10],
                'lag20_similarity': lags[20],
                'lag50_similarity': lags[50],
                'motif_simpson': simpson,
                'motif_entropy': entropy,
                'motif_count': motif_count,
            }
            row['slow_domain_wall_score'] = score_components(row)
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'slow_domain_wall_sweep.csv', index=False)

    def pivot(col):
        return df.pivot(index='r', columns='epsilon', values=col).sort_index(ascending=False)

    plots = [
        ('slow_domain_wall_score', 'viridis', 'Slow domain-wall emergence score'),
        ('domain_wall_density', 'magma', 'Domain-wall density'),
        ('mean_wall_velocity', 'mako', 'Mean domain-wall velocity'),
        ('lag10_similarity', 'rocket', 'Lag-10 Hamming similarity'),
    ]
    for col, cmap, title in plots:
        p = pivot(col)
        plt.figure(figsize=(9, 5.5))
        im = plt.imshow(p.values, origin='lower', aspect='auto', cmap=cmap,
                        extent=[p.columns.min(), p.columns.max(), p.index.min(), p.index.max()])
        plt.colorbar(im, label=col)
        plt.xlabel('epsilon')
        plt.ylabel('r')
        plt.title(title)
        plt.tight_layout()
        plt.savefig(OUT / f'slow_domain_wall_sweep_{col}.png', dpi=160)
        plt.close()

    top = df.sort_values('slow_domain_wall_score', ascending=False).head(20)
    top.to_csv(OUT / 'slow_domain_wall_sweep_top20.csv', index=False)

    md = [
        '# Slow domain-wall sweep', '',
        'This sweep searched the coupled logistic lattice for regions where spatial structure is neither fully synchronized nor rapidly destroyed. The goal was to find slow-moving domain walls and recurrent motifs rather than simply high entropy.', '',
        '## Method', '',
        '- Parameter grid: `r` in [3.40, 4.00], `epsilon` in [0.00, 1.00].',
        '- Lattice size: 100 nodes, 700 steps, 300-step transient.',
        '- Binary frames: `x_i >= 0.5`.',
        '- Domain-wall density: fraction of neighboring sites with different binary state.',
        '- Domain-wall velocity: nearest-neighbor displacement of walls between consecutive frames.',
        '- Temporal persistence: Hamming similarity at lags 1, 5, 10, 20, and 50.',
        '- Motif recurrence: Simpson concentration of length-6 circular binary words.', '',
        '## Score', '',
        '```text',
        'score = spatial_complexity * velocity_low * lag10_score * motif_score * temporal_score',
        'spatial_complexity favors domain-wall density near 0.35.',
        'velocity_low favors mean wall velocity below about 0.45 lattice-sites/frame.',
        'lag10_score favors moderate-to-high persistence at lag 10.',
        'motif_score favors recurrent local words without requiring total uniformity.',
        '```', '',
        '## Top 20 candidates', '',
        '| r | epsilon | score | wall density | mean velocity | lag5 | lag10 | lag20 | motif Simpson | motif entropy | motif count |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for _, q in top.iterrows():
        md.append('| {:.4f} | {:.4f} | {:.6f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.1f} |'.format(
            q['r'], q['epsilon'], q['slow_domain_wall_score'], q['domain_wall_density'], q['mean_wall_velocity'],
            q['lag5_similarity'], q['lag10_similarity'], q['lag20_similarity'], q['motif_simpson'], q['motif_entropy'], q['motif_count']))
    md += [
        '', '## Interpretation', '',
        'The sweep prioritizes slow domain-wall dynamics and temporal persistence. Candidates with high scores should be re-simulated at larger size and longer duration before being treated as robust emergent regimes.', '',
        '## Artifacts', '',
        '- `slow_domain_wall_sweep.py`',
        '- `slow_domain_wall_sweep.csv`',
        '- `slow_domain_wall_sweep_top20.csv`',
        '- `slow_domain_wall_sweep_slow_domain_wall_score.png`',
        '- `slow_domain_wall_sweep_domain_wall_density.png`',
        '- `slow_domain_wall_sweep_mean_wall_velocity.png`',
        '- `slow_domain_wall_sweep_lag10_similarity.png`'
    ]
    (OUT / 'slow_domain_wall_sweep.md').write_text('\n'.join(md), encoding='utf-8')
    print('wrote slow domain-wall sweep artifacts')


if __name__ == '__main__':
    main()
