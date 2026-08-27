from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('../../shared_space')
OUT.mkdir(parents=True, exist_ok=True)

N = 80
STEPS = 1600
TRANSIENT = 400
MAX_LAG = 300
MOTIF_SIZE = 6
SEEDS = [101, 707, 1313, 2029, 3001, 4099, 5003]
PARAMS = [
    (3.55, 1/12),
    (3.60, 1/12),
    (3.65, 1/12),
    (3.70, 1/12),
    (3.85, 1/6),
    (3.90, 1/6),
    (3.95, 1/6),
    (4.00, 1/6),
    (4.00, 0.14),
    (4.00, 0.18),
]


def logistic_step(x, r, eps):
    local = r * x * (1 - x)
    left = np.roll(x, 1)
    right = np.roll(x, -1)
    return (1 - eps) * local + 0.5 * eps * (
        r * left * (1 - left) + r * right * (1 - right)
    )


def run_lattice(r, eps, seed):
    rng = np.random.default_rng(seed)
    x = rng.random(N)
    history = []
    for _ in range(STEPS):
        x = np.clip(logistic_step(x, r, eps), 0.0, 1.0)
        history.append(x.copy())
    return np.asarray(history[TRANSIENT:])


def binary_frames(hist):
    return (hist >= 0.5).astype(np.uint8)


def autocorr(x, max_lag=MAX_LAG):
    x = x - x.mean()
    den = float(np.dot(x, x))
    if den == 0:
        return np.ones(max_lag + 1)
    out = np.empty(max_lag + 1)
    out[0] = 1.0
    for lag in range(1, max_lag + 1):
        out[lag] = float(np.dot(x[:-lag], x[lag:]) / den)
    return out


def spectral_profile(x):
    x = x - x.mean()
    if np.allclose(x, 0):
        return np.nan, 0.0, 0.0, 0.0
    y = np.fft.rfft(x)
    power = np.abs(y) ** 2
    power[0] = 0.0
    total = float(np.sum(power))
    if total == 0:
        return np.nan, 0.0, 0.0, 0.0
    p = power / total
    freqs = np.fft.rfftfreq(len(x), d=1.0)
    idx = int(np.argmax(p))
    f = float(freqs[idx])
    period = 1.0 / f if f > 0 else np.nan
    nz = p[p > 0]
    entropy = float(-np.sum(nz * np.log2(nz)) / np.log2(len(nz))) if len(nz) > 1 else 0.0
    return period, float(p[idx]), entropy, float(np.sum(p[:20]))


def encode_motifs(bits, motif_size=MOTIF_SIZE):
    frames, n = bits.shape
    enc = np.zeros((frames, n), dtype=np.int16)
    mask = (1 << motif_size) - 1
    for i in range(n):
        val = np.zeros(frames, dtype=np.int16)
        for k in range(motif_size):
            val = ((val << 1) | bits[:, (i + k) % n]) & mask
        enc[:, i] = val
    return enc


def ring_intervals(bits):
    n = len(bits)
    s = int(bits.sum())
    if s == 0 or s == n:
        return []
    start = int(np.argmax(bits == 0))
    rot = np.roll(bits, -start)
    intervals = []
    i = 0
    while i < n:
        if rot[i] == 1:
            j = i
            while j < n and rot[j] == 1:
                j += 1
            intervals.append(((i + start) % n, (j - 1 + start) % n, j - i))
            i = j
        else:
            i += 1
    return intervals


def interval_set(interval, n):
    a, b, _ = interval
    if a <= b:
        return set(range(a, b + 1))
    return set(range(a, n)) | set(range(0, b + 1))


def cluster_lifetimes(bits_history, threshold=0.35):
    n = len(bits_history[0])
    active = {}
    next_id = 0
    lifetimes = []
    births = {}
    for frame_idx, bits in enumerate(bits_history):
        sets = [interval_set(iv, n) for iv in ring_intervals(bits)]
        assigned = set()
        matched = set()
        if active:
            pairs = []
            for cid, old_set in active.items():
                for si, new_set in enumerate(sets):
                    if si in assigned:
                        continue
                    union = len(old_set | new_set)
                    iou = len(old_set & new_set) / union if union else 0.0
                    if iou >= threshold:
                        pairs.append((iou, cid, si))
            pairs.sort(reverse=True)
            for _, cid, si in pairs:
                if cid in matched or si in assigned:
                    continue
                active[cid] = active[cid] | sets[si]
                matched.add(cid)
                assigned.add(si)
        for cid in list(active):
            if cid not in matched:
                lifetimes.append(frame_idx - births[cid])
                del births[cid]
                del active[cid]
        for si in range(len(sets)):
            if si not in assigned:
                active[next_id] = set(sets[si])
                births[next_id] = frame_idx
                next_id += 1
    for birth in births.values():
        lifetimes.append(len(bits_history) - birth)
    return np.array(lifetimes, dtype=float) if lifetimes else np.array([0.0])


def wall_density_series(bits):
    return np.mean(bits != np.roll(bits, 1, axis=1), axis=1)


def wall_velocity(bits):
    n = bits.shape[1]
    velocities = []
    for t in range(1, len(bits)):
        prev = np.flatnonzero(bits[t - 1] != np.roll(bits[t - 1], 1))
        cur = np.flatnonzero(bits[t] != np.roll(bits[t], 1))
        if len(prev) == 0 or len(cur) == 0:
            velocities.append(np.nan)
            continue
        d = np.abs((cur[:, None] - prev[None, :] + n // 2) % n - n // 2)
        velocities.append(float(d.min(axis=1).mean()))
    return np.array(velocities)


def long_memory_score(row):
    motif_mem = float(np.nanmean([
        row['motif_100'], row['motif_200'], row['motif_300'],
        row['motif_500']
    ]))
    comp_mem = float(np.nanmean([
        row['comp_100'], row['comp_200'], row['comp_300'],
        row['comp_500']
    ]))
    wall_ac_late = float(np.mean(row['wall_ac'][40:]))
    wall_entropy = float(row['wall_spectral_entropy'])
    cluster_ratio = float(row['max_cluster_lifetime'] / len(row['wall_ac']))
    low_velocity = float(1.0 / (1.0 + np.exp(7.0 * (row['mean_wall_velocity'] - 0.35))))
    wall_balance = float(np.exp(-((row['wall_density_mean'] - 0.50) / 0.35) ** 2))

    global_period = row['global_period']
    wall_period = row['wall_period']
    if np.isfinite(global_period) and global_period <= 8:
        short_cycle_penalty = 0.08
    elif np.isfinite(global_period) and global_period <= 20:
        short_cycle_penalty = 0.40
    else:
        short_cycle_penalty = 1.0
    if np.isfinite(wall_period):
        long_wall = float(1.0 / (1.0 + np.exp(-0.006 * (wall_period - 80))))
    else:
        long_wall = 0.5
    cluster_component = float(1.0 / (1.0 + np.exp(-16.0 * (cluster_ratio - 0.05))))
    wall_ac_component = float(1.0 / (1.0 + np.exp(-9.0 * (wall_ac_late - 0.010))))
    return (
        short_cycle_penalty * long_wall * motif_mem * comp_mem *
        (0.45 + wall_entropy) * (0.45 + cluster_component) *
        low_velocity * wall_balance * wall_ac_component
    )

rows = []
for r, eps in PARAMS:
    for seed in SEEDS:
        hist = run_lattice(r, eps, seed)
        bits = binary_frames(hist)
        wall_density = wall_density_series(bits)
        global_activity = np.mean(bits, axis=1)
        velocities = wall_velocity(bits)
        global_ac = autocorr(global_activity, MAX_LAG)
        wall_ac = autocorr(wall_density, MAX_LAG)
        global_period, global_power, global_entropy, global_lowfreq = spectral_profile(global_activity)
        wall_period, wall_power, wall_entropy, wall_lowfreq = spectral_profile(wall_density)
        enc = encode_motifs(bits, MOTIF_SIZE)
        lifetimes = cluster_lifetimes(bits, threshold=0.35)

        row = {
            'r': r,
            'epsilon': eps,
            'seed': seed,
            'global_activity_mean': float(global_activity.mean()),
            'global_activity_std': float(global_activity.std()),
            'wall_density_mean': float(wall_density.mean()),
            'wall_density_std': float(wall_density.std()),
            'mean_wall_velocity': float(np.nanmean(velocities)) if np.isfinite(velocities).any() else np.nan,
            'global_period': global_period,
            'global_period_power': global_power,
            'global_spectral_entropy': global_entropy,
            'global_lowfreq_power': global_lowfreq,
            'wall_period': wall_period,
            'wall_period_power': wall_power,
            'wall_spectral_entropy': wall_entropy,
            'wall_lowfreq_power': wall_lowfreq,
            'global_ac_peak_lag': int(np.argmax(global_ac[1:]) + 1),
            'global_ac_peak_value': float(global_ac[np.argmax(global_ac[1:]) + 1]),
            'wall_ac_peak_lag': int(np.argmax(wall_ac[1:]) + 1),
            'wall_ac_peak_value': float(wall_ac[np.argmax(wall_ac[1:]) + 1]),
            'wall_ac_late_mean': float(np.mean(wall_ac[40:])),
            'max_cluster_lifetime': float(np.max(lifetimes)),
            'mean_cluster_lifetime': float(np.mean(lifetimes)),
            'wall_ac': wall_ac,
        }
        for lag in [10, 20, 50, 100, 200, 300]:
            if lag < len(bits):
                row[f'frame_{lag}'] = float(np.mean(bits[:-lag] == bits[lag:]))
                row[f'motif_{lag}'] = float(np.mean(enc[:-lag] == enc[lag:]))
                row[f'comp_{lag}'] = float(np.mean(enc[:-lag] == 1 - enc[lag:]))
            else:
                row[f'frame_{lag}'] = np.nan
                row[f'motif_{lag}'] = np.nan
                row[f'comp_{lag}'] = np.nan
        row['long_memory_score'] = long_memory_score(row)
        rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUT / 'two_regime_long_memory.csv', index=False)

agg = df.groupby(['r', 'epsilon']).agg({
    'long_memory_score': 'mean',
    'motif_500': 'mean',
    'motif_700': 'mean',
    'comp_500': 'mean',
    'comp_700': 'mean',
    'wall_period': 'mean',
    'wall_period_power': 'mean',
    'wall_spectral_entropy': 'mean',
    'wall_ac_late_mean': 'mean',
    'mean_wall_velocity': 'mean',
    'max_cluster_lifetime': 'max',
    'global_period': 'mean',
}).reset_index()
agg.to_csv(OUT / 'two_regime_long_memory_agg.csv', index=False)

plt.figure(figsize=(8.5, 5))
plt.scatter(agg['r'], agg['epsilon'], c=agg['long_memory_score'], s=90, cmap='magma')
plt.colorbar(label='long-memory score')
plt.xlabel('r')
plt.ylabel('epsilon')
plt.title('Two-regime long-memory comparison')
plt.tight_layout()
plt.savefig(OUT / 'two_regime_long_memory_heatmap.png', dpi=160)
plt.close()

plt.figure(figsize=(8.5, 5))
plt.scatter(agg['mean_wall_velocity'], agg['motif_700'], c=agg['long_memory_score'], s=90, cmap='viridis')
plt.colorbar(label='long-memory score')
plt.xlabel('mean wall velocity')
plt.ylabel('motif-700 similarity')
plt.title('Velocity vs long motif memory')
plt.tight_layout()
plt.savefig(OUT / 'two_regime_velocity_vs_motif700.png', dpi=160)
plt.close()

top = agg.sort_values('long_memory_score', ascending=False).head(12)
top.to_csv(OUT / 'two_regime_long_memory_top12.csv', index=False)

md = [
    '# Two-regime long-memory comparison',
    '',
    'This run compares the lower-coupling slow-wall region with the higher-coupling motif-persistence region.',
    '',
    '## Simulation settings',
    '',
    f'- lattice size: `{N}`',
    f'- total steps: `{STEPS}`',
    f'- transient discarded: `{TRANSIENT}`',
    f'- post-transient frames: `{len(df) // (len(PARAMS) * len(SEEDS))}`',
    f'- maximum lag: `{MAX_LAG}`',
    f'- motif size: `{MOTIF_SIZE}`',
    f'- seeds per parameter: `{len(SEEDS)}`',
    '',
    '## Score',
    '',
    'The score combines long-lag motif memory, complement-invariant memory, late wall-density autocorrelation, spectral entropy, low wall velocity, balanced wall density, cluster lifetime, and a penalty for obvious short global cycles.',
    '',
    '## Top aggregate candidates',
    '',
    '| r | epsilon | score | motif500 | comp500 | wall period | wall power | wall entropy | wall AC late | velocity | max cluster lifetime | global period |',
    '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|'
]
for _, q in top.iterrows():
    md.append(
        '| {:.4f} | {:.4f} | {:.6f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.3f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.3f} | {:.4f} |'.format(
            q['r'], q['epsilon'], q['long_memory_score'], q['motif_500'], q['comp_500'],
            q['wall_period'], q['wall_period_power'], q['wall_spectral_entropy'], q['wall_ac_late_mean'],
            q['mean_wall_velocity'], q['max_cluster_lifetime'], q['global_period']
        )
    )
md += [
    '',
    '## Interpretation',
    '',
    'The lower-coupling region tests whether slow domain-wall motion can produce long memory without high motif recurrence. The higher-coupling region tests whether motif persistence survives longer simulations and multiple seeds.',
    '',
    '## Artifacts',
    '',
    '- `two_regime_long_memory.csv`',
    '- `two_regime_long_memory_agg.csv`',
    '- `two_regime_long_memory_top12.csv`',
    '- `two_regime_long_memory_heatmap.png`',
    '- `two_regime_velocity_vs_motif700.png`'
]
(OUT / 'two_regime_long_memory.md').write_text('\n'.join(md), encoding='utf-8')
print('wrote two-regime long-memory artifacts')
print(top[['r', 'epsilon', 'long_memory_score', 'motif_700', 'comp_700', 'mean_wall_velocity', 'max_cluster_lifetime']].to_string(index=False))
