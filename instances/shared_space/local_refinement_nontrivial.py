from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('../../shared_space')
OUT.mkdir(parents=True, exist_ok=True)

N = 40
STEPS = 1200
TRANSIENT = 300
MAX_LAG = 220
MOTIF_SIZE = 6
SEEDS = [101, 707, 1313, 2029, 3001]
PARAMS = [(round(float(r), 4), round(float(e), 4))
          for r in np.linspace(3.86, 3.92, 7)
          for e in np.linspace(0.09, 0.15, 7)]


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
    hist = []
    for _ in range(STEPS):
        x = np.clip(logistic_step(x, r, eps), 0.0, 1.0)
        hist.append(x.copy())
    return np.asarray(hist[TRANSIENT:])


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
    for k in range(motif_size):
        enc = (enc << 1) | bits[:, (np.arange(n) + k) % n]
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


def smooth_step(x, x0, x1):
    if x <= x0:
        return 0.0
    if x >= x1:
        return 1.0
    t = (x - x0) / (x1 - x0)
    return t * t * (3.0 - 2.0 * t)


def period_factor(value, low, high):
    if not np.isfinite(value):
        return 0.0
    f = smooth_step(float(value), low, high)
    if value <= 4:
        return 0.05 * f
    if value <= 8:
        return 0.20 * f
    return f


def nontriviality_factor(row):
    global_factor = period_factor(row['global_period'], 25.0, 100.0)
    wall_factor = period_factor(row['wall_period'], 25.0, 100.0)
    motif_100 = float(row['motif_100'])
    motif_150 = float(row['motif_150'])
    motif_200 = float(row['motif_200'])
    motif_220 = float(row['motif_220'])
    comp_100 = float(row['comp_100'])
    comp_150 = float(row['comp_150'])
    comp_200 = float(row['comp_200'])
    comp_220 = float(row['comp_220'])
    frame_100 = float(row['frame_100'])
    frame_150 = float(row['frame_150'])
    frame_200 = float(row['frame_200'])
    frame_220 = float(row['frame_220'])
    long_memory = 0.20 * motif_100 + 0.30 * motif_150 + 0.35 * motif_200 + 0.15 * motif_220
    complement_memory = 0.20 * comp_100 + 0.30 * comp_150 + 0.35 * comp_200 + 0.15 * comp_220
    frame_decay = 0.20 * frame_100 + 0.30 * frame_150 + 0.35 * frame_200 + 0.15 * frame_220
    long_minus_frame = float(np.clip(long_memory - frame_decay, 0.0, 1.0))
    return float(
        0.01
        + 0.99 * global_factor * wall_factor
        * (0.20 + 0.80 * long_minus_frame)
        * (0.30 + complement_memory)
    )


def long_memory_score(row):
    motif_mem = float(0.20 * row['motif_100'] + 0.30 * row['motif_150'] + 0.35 * row['motif_200'] + 0.15 * row['motif_220'])
    comp_mem = float(0.20 * row['comp_100'] + 0.30 * row['comp_150'] + 0.35 * row['comp_200'] + 0.15 * row['comp_220'])
    wall_ac_late = float(np.mean(row['wall_ac'][80:]))
    wall_entropy = float(row['wall_spectral_entropy'])
    cluster_ratio = float(row['max_cluster_lifetime'] / len(row['wall_ac']))
    low_velocity = float(1.0 / (1.0 + np.exp(7.0 * (row['mean_wall_velocity'] - 0.75))))
    wall_balance = float(np.exp(-((row['wall_density_mean'] - 0.50) / 0.35) ** 2))
    if np.isfinite(row['wall_period']):
        long_wall = float(1.0 / (1.0 + np.exp(-0.025 * (row['wall_period'] - 80))))
    else:
        long_wall = 0.5
    cluster_component = float(1.0 / (1.0 + np.exp(-12.0 * (cluster_ratio - 0.04))))
    wall_ac_component = float(1.0 / (1.0 + np.exp(-8.0 * (wall_ac_late - 0.015))))
    entropy_factor = float(0.25 + wall_entropy)
    return (
        nontriviality_factor(row)
        * motif_mem
        * (0.10 + comp_mem)
        * entropy_factor
        * (0.45 + cluster_component)
        * low_velocity
        * wall_balance
        * long_wall
        * wall_ac_component
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
            'wall_ac_late_mean': float(np.mean(wall_ac[80:])),
            'max_cluster_lifetime': float(np.max(lifetimes)),
            'mean_cluster_lifetime': float(np.mean(lifetimes)),
            'wall_ac': wall_ac,
        }
        for lag in [10, 20, 50, 100, 150, 200, 220]:
            row[f'frame_{lag}'] = float(np.mean(bits[:-lag] == bits[lag:]))
            row[f'motif_{lag}'] = float(np.mean(enc[:-lag] == enc[lag:]))
            row[f'comp_{lag}'] = float(np.mean(enc[:-lag] == 1 - enc[lag:]))
        row['long_memory_score'] = long_memory_score(row)
        rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(OUT / 'nontrivial_local_refinement.csv', index=False)

agg = df.groupby(['r', 'epsilon']).agg({
    'long_memory_score': 'mean',
    'motif_100': 'mean',
    'motif_150': 'mean',
    'motif_200': 'mean',
    'motif_220': 'mean',
    'comp_100': 'mean',
    'comp_150': 'mean',
    'comp_200': 'mean',
    'comp_220': 'mean',
    'frame_100': 'mean',
    'frame_150': 'mean',
    'frame_200': 'mean',
    'frame_220': 'mean',
    'wall_period': 'mean',
    'wall_period_power': 'mean',
    'wall_spectral_entropy': 'mean',
    'wall_ac_late_mean': 'mean',
    'mean_wall_velocity': 'mean',
    'max_cluster_lifetime': 'max',
    'global_period': 'mean',
}).reset_index()
agg.to_csv(OUT / 'nontrivial_local_refinement_agg.csv', index=False)
agg.sort_values('long_memory_score', ascending=False).head(15).to_csv(OUT / 'nontrivial_local_refinement_top15.csv', index=False)

plt.figure(figsize=(9, 5.5))
plt.scatter(agg['r'], agg['epsilon'], c=np.log10(agg['long_memory_score'] + 1e-300), s=110, cmap='magma')
plt.colorbar(label='log10 long-memory score')
plt.xlabel('r')
plt.ylabel('epsilon')
plt.title('Local refinement: nontrivial long-memory')
plt.tight_layout()
plt.savefig(OUT / 'nontrivial_local_refinement_heatmap.png', dpi=160)
plt.close()

plt.figure(figsize=(9, 5.5))
plt.scatter(agg['mean_wall_velocity'], agg['motif_220'], c=np.log10(agg['long_memory_score'] + 1e-300), s=110, cmap='viridis')
plt.colorbar(label='log10 long-memory score')
plt.xlabel('mean wall velocity')
plt.ylabel('motif-220 similarity')
plt.title('Velocity vs very-long motif memory')
plt.tight_layout()
plt.savefig(OUT / 'nontrivial_refinement_velocity_vs_motif220.png', dpi=160)
plt.close()

print('wrote', OUT / 'nontrivial_local_refinement.csv')
print('top point:', agg.sort_values('long_memory_score', ascending=False).iloc[0].to_dict())
