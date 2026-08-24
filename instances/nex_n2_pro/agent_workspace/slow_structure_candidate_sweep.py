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
    return (1 - eps) * local + 0.5 * eps * (
        r * left * (1 - left) + r * right * (1 - right)
    )


def run_lattice(r, eps, N=100, steps=700, transient=200, seed=101):
    rng = np.random.default_rng(seed)
    x = rng.random(N)
    history = []
    for t in range(steps):
        x = np.clip(logistic_step(x, r, eps), 0.0, 1.0)
        if t >= transient:
            history.append(x.copy())
    return np.asarray(history)


def binary_frames(hist):
    return (hist >= 0.5).astype(np.uint8)


def hamming_lags(bits, max_lag=200):
    out = []
    comp = []
    for lag in range(max_lag + 1):
        vals = [float(np.mean(bits[t] == bits[t + lag])) for t in range(len(bits) - lag)]
        s = float(np.mean(vals)) if vals else np.nan
        out.append(s)
        comp.append(float(max(s, 1.0 - s)) if np.isfinite(s) else np.nan)
    return np.array(out), np.array(comp)


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


def autocorr(x, max_lag=200):
    x = x - x.mean()
    den = float(np.dot(x, x))
    if den == 0:
        return np.ones(max_lag + 1)
    out = np.empty(max_lag + 1)
    out[0] = 1.0
    for lag in range(1, max_lag + 1):
        out[lag] = float(np.dot(x[:-lag], x[lag:]) / den)
    return out


def dominant_period(x):
    x = x - x.mean()
    if np.allclose(x, 0):
        return np.nan, 0.0
    y = np.fft.rfft(x)
    power = np.abs(y) ** 2
    power[0] = 0.0
    total = np.sum(power)
    if total == 0:
        return np.nan, 0.0
    power = power / total
    freqs = np.fft.rfftfreq(len(x), d=1.0)
    idx = np.argmax(power)
    f = float(freqs[idx])
    return (1.0 / f) if f > 0 else np.nan, float(power[idx])


def encode_motifs(bits, motif_size=6):
    frames, n = bits.shape
    enc = np.zeros((frames, n), dtype=np.int16)
    for i in range(n):
        val = np.zeros(frames, dtype=np.int16)
        for k in range(motif_size):
            val = (val << 1) | bits[:, (i + k) % n]
        enc[:, i] = val
    return enc


def motif_stats(bits, motif_size=6):
    enc = encode_motifs(bits, motif_size)
    flat = enc.ravel()
    counts = np.bincount(flat, minlength=2 ** motif_size)
    probs = counts / counts.sum()
    simpson = float(np.sum(probs * probs))
    entropy = float(-np.sum(probs[probs > 0] * np.log2(probs[probs > 0])))

    a = enc[:-1].ravel()
    b = enc[1:].ravel()
    pair_counts = np.bincount(a * (2 ** motif_size) + b, minlength=(2 ** motif_size) ** 2)
    pair_counts = pair_counts[pair_counts > 0]
    trans_probs = pair_counts / pair_counts.sum()
    trans_entropy = float(-np.sum(trans_probs * np.log2(trans_probs)))
    max_trans_entropy = np.log2(len(trans_probs)) if len(trans_probs) > 1 else 0.0
    trans_norm = trans_entropy / max_trans_entropy if max_trans_entropy > 0 else np.nan

    persistence = {}
    for lag in [1, 2, 5, 10, 20, 50, 100, 150, 200]:
        if lag >= len(enc):
            persistence[lag] = np.nan
            continue
        persistence[lag] = float(np.mean(enc[:-lag] == enc[lag:]))

    return {
        'motif_simpson': simpson,
        'motif_entropy': entropy,
        'motif_count': int(np.sum(counts > 0)),
        'motif_transition_entropy': trans_entropy,
        'motif_transition_entropy_norm': trans_norm,
        'motif_p1': persistence[1],
        'motif_p2': persistence[2],
        'motif_p5': persistence[5],
        'motif_p10': persistence[10],
        'motif_p20': persistence[20],
        'motif_p50': persistence[50],
        'motif_p100': persistence[100],
        'motif_p150': persistence[150],
        'motif_p200': persistence[200],
    }


def ring_intervals(bits):
    n = len(bits)
    if bits.sum() == 0:
        return []
    if bits.sum() == n:
        return [(0, n)]
    start = int(np.argmax(bits == 0))
    rot = np.roll(bits, -start)
    intervals = []
    i = 0
    while i < n:
        if rot[i] == 1:
            j = i
            while j < n and rot[j] == 1:
                j += 1
            a = (i + start) % n
            b = (j - 1 + start) % n
            intervals.append((a, b, j - i))
            i = j
        else:
            i += 1
    return intervals


def interval_set(interval, n):
    a, b, length = interval
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
        intervals = ring_intervals(bits)
        sets = [interval_set(iv, n) for iv in intervals]
        assigned = set()
        matched_clusters = set()
        if active:
            pairs = []
            for cid, old_set in active.items():
                for si, new_set in enumerate(sets):
                    if si in assigned:
                        continue
                    inter = len(old_set & new_set)
                    union = len(old_set | new_set)
                    iou = inter / union if union else 0.0
                    if iou >= threshold:
                        pairs.append((iou, cid, si))
            pairs.sort(reverse=True)
            for iou, cid, si in pairs:
                if cid in matched_clusters or si in assigned:
                    continue
                active[cid] = active[cid] | sets[si]
                matched_clusters.add(cid)
                assigned.add(si)
        for cid in list(active):
            if cid not in matched_clusters:
                lifetimes.append(frame_idx - births[cid])
                del births[cid]
                del active[cid]
        for si in range(len(sets)):
            if si not in assigned:
                cid = next_id
                next_id += 1
                active[cid] = set(sets[si])
                births[cid] = frame_idx
    final_frame = len(bits_history)
    for cid, birth in births.items():
        lifetimes.append(final_frame - birth)
    return lifetimes


def score(row):
    wall_period = row['wall_density_period']
    global_period = row['global_activity_period']
    comp_lag200 = row['lag200_complement_similarity']
    motif_p100 = row['motif_p100']
    motif_p200 = row['motif_p200']
    wall_ac_peak = row['wall_ac_peak_value']
    wall_ac_lag = row['wall_ac_peak_lag']

    long_wall = float(1.0 / (1.0 + np.exp(-0.006 * (wall_period - 80)))) if np.isfinite(wall_period) else 0.0
    not_short_wall = 1.0 if (not np.isfinite(wall_period) or wall_period > 12) else 0.0
    high_lag = float(np.exp(-((comp_lag200 - 0.88) / 0.10) ** 2)) if np.isfinite(comp_lag200) else 0.0
    motif_mem = float(np.nanmean([motif_p100, motif_p200])) if np.isfinite(motif_p100) or np.isfinite(motif_p200) else 0.0
    moderate_ac = float(np.exp(-((wall_ac_peak - 0.60) / 0.25) ** 2)) if np.isfinite(wall_ac_peak) else 0.0
    late_ac = 1.0 if wall_ac_lag > 20 else 0.0
    periodic_penalty = 1.0 if global_period > 6 else 0.35

    return periodic_penalty * long_wall * not_short_wall * high_lag * motif_mem * moderate_ac * late_ac


params = []
for eps in np.linspace(0.10, 0.24, 8):
    params.append((4.00, float(eps)))
for r in [3.85, 3.90, 3.95, 4.00]:
    params.append((float(r), 0.1666667))

rows = []
for r, eps in params:
    seed = 30000 + int(round(r * 1000)) + int(round(eps * 1000))
    hist = run_lattice(r, eps, N=100, steps=700, transient=200, seed=seed)
    bits = binary_frames(hist)
    lags, comp_lags = hamming_lags(bits, max_lag=200)
    wall_density = wall_density_series(bits)
    global_activity = np.mean(bits, axis=1)
    velocities = wall_velocity(bits)
    ac_global = autocorr(global_activity, max_lag=200)
    ac_wall = autocorr(wall_density, max_lag=200)
    global_period, global_power = dominant_period(global_activity)
    wall_period, wall_power = dominant_period(wall_density)
    peak_global_lag = int(np.argmax(ac_global[1:]) + 1)
    peak_wall_lag = int(np.argmax(ac_wall[1:]) + 1)
    lifetimes = cluster_lifetimes(bits, threshold=0.35)
    mstats = motif_stats(bits, motif_size=6)

    row = {
        'r': r,
        'epsilon': eps,
        'global_activity_mean': float(global_activity.mean()),
        'global_activity_std': float(global_activity.std()),
        'wall_density_mean': float(wall_density.mean()),
        'wall_density_std': float(wall_density.std()),
        'mean_wall_velocity': float(np.nanmean(velocities)) if np.isfinite(velocities).any() else np.nan,
        'lag10_similarity': float(lags[10]),
        'lag20_similarity': float(lags[20]),
        'lag50_similarity': float(lags[50]),
        'lag100_similarity': float(lags[100]),
        'lag200_similarity': float(lags[200]),
        'lag200_complement_similarity': float(comp_lags[200]),
        'global_activity_period': global_period,
        'global_activity_power': global_power,
        'wall_density_period': wall_period,
        'wall_density_power': wall_power,
        'global_ac_peak_lag': peak_global_lag,
        'global_ac_peak_value': float(ac_global[peak_global_lag]),
        'wall_ac_peak_lag': peak_wall_lag,
        'wall_ac_peak_value': float(ac_wall[peak_wall_lag]),
        'mean_cluster_lifetime': float(np.mean(lifetimes)) if lifetimes else np.nan,
        'max_cluster_lifetime': float(np.max(lifetimes)) if lifetimes else np.nan,
    }
    row.update(mstats)
    row['slow_structure_score'] = score(row)
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUT / 'slow_structure_candidate_sweep.csv', index=False)

plt.figure(figsize=(9, 5))
plt.scatter(df['wall_density_period'], df['slow_structure_score'], s=80, c=df['wall_density_power'], cmap='viridis')
plt.colorbar(label='wall density periodogram power')
plt.xlabel('dominant wall-density period')
plt.ylabel('slow structure score')
plt.title('Candidate sweep: long wall-density timescales')
plt.tight_layout()
plt.savefig(OUT / 'slow_structure_candidate_sweep.png', dpi=160)
plt.close()

top = df.sort_values('slow_structure_score', ascending=False).head(10)
top.to_csv(OUT / 'slow_structure_candidate_sweep_top10.csv', index=False)

md = ['# Slow structure candidate sweep', '',
      'This sweep revisits the promising region around `r=4.00`, `epsilon≈0.167` with a score designed to avoid being fooled by simple period-2 cycling.', '',
      '## Score components', '',
      '```text',
      'slow_structure_score = periodic_penalty * long_wall * not_short_wall * high_lag * motif_mem * moderate_ac * late_ac',
      '```', '',
      'The score rewards long wall-density timescales, high complement-invariant lag-200 similarity, motif persistence, and late autocorrelation peaks, while penalizing obvious short global cycles.', '',
      '## Top candidates', '',
      '| r | epsilon | score | wall period | wall power | lag200 | complement lag200 | motif p100 | motif p200 | wall AC lag | wall AC peak | mean cluster lifetime | max cluster lifetime |',
      '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for _, q in top.iterrows():
    md.append('| {:.4f} | {:.4f} | {:.6f} | {:.3f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.1f} | {:.4f} | {:.3f} | {:.3f} |'.format(
        q['r'], q['epsilon'], q['slow_structure_score'], q['wall_density_period'], q['wall_density_power'],
        q['lag200_similarity'], q['lag200_complement_similarity'], q['motif_p100'], q['motif_p200'],
        q['wall_ac_peak_lag'], q['wall_ac_peak_value'], q['mean_cluster_lifetime'], q['max_cluster_lifetime']))
md += ['', '## Artifacts', '',
       '- `slow_structure_candidate_sweep.csv`',
       '- `slow_structure_candidate_sweep_top10.csv`',
       '- `slow_structure_candidate_sweep.png`']
(OUT / 'slow_structure_candidate_sweep.md').write_text('\n'.join(md), encoding='utf-8')
print('wrote slow structure candidate sweep artifacts')
print(top[['r', 'epsilon', 'slow_structure_score', 'wall_density_period', 'wall_density_power', 'lag200_similarity', 'lag200_complement_similarity', 'motif_p100', 'motif_p200', 'wall_ac_peak_lag', 'wall_ac_peak_value']].to_string(index=False))
