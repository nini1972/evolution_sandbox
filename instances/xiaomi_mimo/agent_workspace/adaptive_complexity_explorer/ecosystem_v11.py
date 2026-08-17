"""
Ecosystem V11 - Strong Predator-Prey Oscillations
Key: Hunters must crash FAST when prey is scarce
"""
import numpy as np
import json
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

random.seed(42)
np.random.seed(42)

NGEN = 600

def new_forager():
    return [60.0, 0, random.uniform(0.5, 0.9), random.uniform(0.2, 0.5), 
            random.uniform(0.2, 0.6), random.uniform(0.15, 0.35)]

def new_hunter():
    return [70.0, 0, random.uniform(0.3, 0.6), random.uniform(0.2, 0.5),
            random.uniform(0.3, 0.7), random.uniform(0.04, 0.12)]

def mutate_trait(v, sigma=0.015):
    return max(0.01, min(0.99, v + random.gauss(0, sigma)))

# Initialize
foragers = [new_forager() for _ in range(20)]
hunters = [new_hunter() for _ in range(2)]
resources = 200.0

history = []

for gen in range(NGEN):
    # Resource growth
    K = 300.0
    r = 0.35
    growth = r * resources * (1.0 - resources/K)
    resources += max(growth, 1.0)
    resources = min(K, max(1.0, resources))
    
    nf_start = len(foragers)
    nh_start = len(hunters)
    
    # === FORAGER PHASE ===
    new_foragers = []
    
    for f in foragers:
        f[1] += 1
        f[0] -= 0.25 + f[3] * 0.08
        
        if f[0] <= 0:
            continue
        
        per_capita = resources / max(1.0, nf_start + nh_start * 0.2)
        gain = f[2] * per_capita * 0.18
        gain = min(gain, 10)
        f[0] += gain
        resources -= gain * 0.4
        resources = max(0.1, resources)
        
        # Foragers reproduce quickly when population is low
        if f[0] > 45 and f[1] > 2 and nf_start + len(new_foragers) < 100:
            # Density-dependent reproduction: faster when fewer foragers
            density_factor = max(0.5, 1.5 - nf_start / 60.0)
            prob = f[5] * min(1.5, f[0]/55) * density_factor
            if random.random() < prob:
                child = [f[0]*0.45, 0] + [mutate_trait(f[j]) for j in range(2, 6)]
                new_foragers.append(child)
                f[0] *= 0.55
        
        if f[0] > 0:
            new_foragers.append(f)
    
    foragers = new_foragers
    
    # === HUNTER PHASE ===
    new_hunters = []
    killed_this_gen = 0
    
    for h in hunters:
        h[1] += 1
        h[0] -= 0.9 + h[3] * 0.2  # VERY high metabolism - crash fast without food
        
        if h[0] <= 0:
            continue
        
        # Hunt
        if foragers:
            density = min(1.0, len(foragers) / 15.0)
            avg_def = np.mean([f[4] for f in foragers])
            prob = h[2] * 0.25 * density * (1.0 - avg_def * 0.2)
            
            if random.random() < prob:
                prey_idx = random.randint(0, len(foragers)-1)
                h[0] += 15 + h[4] * 8
                foragers.pop(prey_idx)
                killed_this_gen += 1
            else:
                # Failed hunt costs extra energy
                h[0] -= 0.2
        
        # Reproduce only when plentiful
        if h[0] > 85 and h[1] > 10 and len(hunters) + len(new_hunters) < 10:
            prey_factor = min(1.0, len(foragers) / 12.0)
            prob = h[5] * prey_factor * min(1.0, h[0]/100)
            if random.random() < prob:
                child = [h[0]*0.35, 0] + [mutate_trait(h[j]) for j in range(2, 6)]
                new_hunters.append(child)
                h[0] *= 0.65
        
        if h[0] > 0:
            new_hunters.append(h)
    
    hunters = new_hunters
    
    # Record
    nf, nh = len(foragers), len(hunters)
    avg_fe = round(float(np.mean([f[0] for f in foragers])), 2) if foragers else 0
    avg_he = round(float(np.mean([h[0] for h in hunters])), 2) if hunters else 0
    
    ft = {}
    for idx, name in enumerate(['eff', 'spd', 'def', 'repro']):
        vals = [f[idx+2] for f in foragers]
        ft[name] = round(float(np.mean(vals)), 4) if vals else 0
    
    ht = {}
    for idx, name in enumerate(['skill', 'spd', 'eff', 'repro']):
        vals = [h[idx+2] for h in hunters]
        ht[name] = round(float(np.mean(vals)), 4) if vals else 0
    
    history.append({
        'gen': gen+1, 'nf': nf, 'nh': nh,
        'fe': avg_fe, 'he': avg_he,
        'res': round(resources, 1),
        'ft': ft, 'ht': ht,
        'killed': killed_this_gen,
    })
    
    if (gen+1) % 100 == 0:
        print(f"Gen {gen+1:3d}: F={nf:3d} H={nh:2d} Res={resources:.0f} K={killed_this_gen}")

with open('history_v11_predator_prey.json', 'w') as f:
    json.dump(history, f)

# === ANALYSIS & PLOTTING ===
gens = np.array([h['gen'] for h in history])
nfs = np.array([h['nf'] for h in history])
nhs = np.array([h['nh'] for h in history])
res = np.array([h['res'] for h in history])
killed = np.array([h['killed'] for h in history])

print(f"\n=== ANALYSIS ===")
print(f"Forager range: {min(nfs)}-{max(nfs)}, mean={np.mean(nfs):.1f}")
print(f"Hunter range: {min(nhs)}-{max(nhs)}, mean={np.mean(nhs):.1f}")
print(f"Total kills: {sum(killed)}")

# === MAIN DYNAMICS PLOT ===
fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)

ax1 = axes[0]
ax1.plot(gens, nfs, 'g-', linewidth=2, label='Foragers')
ax1.plot(gens, nhs * 5, 'r-', linewidth=2, label='Hunters (×5)', alpha=0.8)
ax1.set_ylabel('Population')
ax1.legend(loc='upper right', fontsize=12)
ax1.set_title('Predator-Prey Population Dynamics', fontsize=14)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(gens, res, 'b-', linewidth=2)
ax2.set_ylabel('Resources')
ax2.grid(True, alpha=0.3)

ax3 = axes[2]
window = 10
killed_smooth = np.convolve(killed, np.ones(window)/window, mode='valid')
ax3.plot(gens[window-1:], killed_smooth, 'r-', linewidth=2)
ax3.set_ylabel('Kills/gen (smoothed)')
ax3.set_xlabel('Generation')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('predator_prey_dynamics.png', dpi=150, bbox_inches='tight')
print("Saved: predator_prey_dynamics.png")

# === PHASE PORTRAIT ===
fig2, ax2 = plt.subplots(figsize=(8, 8))
skip = 50
sc = ax2.scatter(nfs[skip:], nhs[skip:], c=gens[skip:], cmap='viridis', alpha=0.6, s=15)
ax2.set_xlabel('Forager Population', fontsize=12)
ax2.set_ylabel('Hunter Population', fontsize=12)
ax2.set_title('Phase Portrait (Color = Time)', fontsize=14)
plt.colorbar(sc, label='Generation')
ax2.grid(True, alpha=0.3)
plt.savefig('phase_portrait.png', dpi=150, bbox_inches='tight')
print("Saved: phase_portrait.png")

# === TRAIT EVOLUTION ===
fig3, axes3 = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

ax = axes3[0]
for trait, color in [('eff', '#2ecc71'), ('spd', '#3498db'), ('def', '#e74c3c'), ('repro', '#9b59b6')]:
    vals = np.array([h['ft'][trait] for h in history])
    ax.plot(gens, vals, linewidth=2, label=trait, color=color)
ax.set_ylabel('Trait Value', fontsize=12)
ax.legend(fontsize=11)
ax.set_title('Forager Trait Evolution', fontsize=14)
ax.grid(True, alpha=0.3)

ax = axes3[1]
for trait, color in [('skill', '#e74c3c'), ('spd', '#3498db'), ('eff', '#2ecc71'), ('repro', '#9b59b6')]:
    vals = np.array([h['ht'][trait] for h in history])
    ax.plot(gens, vals, linewidth=2, label=trait, color=color)
ax.set_ylabel('Trait Value', fontsize=12)
ax.set_xlabel('Generation', fontsize=12)
ax.legend(fontsize=11)
ax.set_title('Hunter Trait Evolution', fontsize=14)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trait_evolution_predator_prey.png', dpi=150, bbox_inches='tight')
print("Saved: trait_evolution_predator_prey.png")

# === CROSS-CORRELATION ===
# Proper normalized cross-correlation for period detection
nfs_detrend = nfs[50:] - np.mean(nfs[50:])
nhs_detrend = nhs[50:] - np.mean(nhs[50:])

fig4, (ax4a, ax4b) = plt.subplots(2, 1, figsize=(12, 8))

# Cross-correlation
max_lag = 80
cc = np.correlate(nfs_detrend, nhs_detrend, mode='full')
mid = len(cc) // 2
lags = np.arange(-max_lag, max_lag+1)
cc_segment = cc[mid-max_lag:mid+max_lag+1]
norm = np.std(nfs_detrend) * np.std(nhs_detrend) * len(nfs_detrend)
if norm > 0:
    cc_segment /= norm

ax4a.plot(lags, cc_segment, 'b-', linewidth=2)
ax4a.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
peak_lag = lags[np.argmax(cc_segment)]
ax4a.axvline(x=peak_lag, color='red', linestyle='--', alpha=0.7, label=f'Peak at lag={peak_lag}')
ax4a.set_xlabel('Lag (generations)', fontsize=12)
ax4a.set_ylabel('Cross-correlation', fontsize=12)
ax4a.set_title('Forager-Hunter Cross-correlation\n(positive lag = forager peak leads)', fontsize=14)
ax4a.legend(fontsize=11)
ax4a.grid(True, alpha=0.3)

# Autocorrelation of forager population
ac = np.correlate(nfs_detrend, nfs_detrend, mode='full')
ac = ac[len(ac)//2:]
ac /= ac[0]
max_lag_ac = 100
ax4b.plot(range(max_lag_ac+1), ac[:max_lag_ac+1], 'g-', linewidth=2)
ax4b.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# Find period (first time autocorrelation crosses zero going negative, then comes back to zero)
zero_crossings = np.where(np.diff(np.sign(ac[:max_lag_ac])))[0]
if len(zero_crossings) > 1:
    half_period = zero_crossings[0]  # first zero crossing
    period = 2 * half_period
    ax4b.axvline(x=half_period, color='red', linestyle='--', alpha=0.5, label=f'Half-period={half_period}')
    print(f"Forager autocorrelation half-period: {half_period}, full period: ~{period}")
ax4b.set_xlabel('Lag (generations)', fontsize=12)
ax4b.set_ylabel('Autocorrelation', fontsize=12)
ax4b.set_title('Forager Population Autocorrelation', fontsize=14)
ax4b.legend(fontsize=11)
ax4b.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('correlation_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: correlation_analysis.png")

print(f"\nPeak cross-correlation at lag: {peak_lag}")
print(f"Interpretation: {'Forager peak leads hunter peak' if peak_lag > 0 else 'Hunter peak leads forager peak'}")
final = history[-1]
print(f"\nFinal: F={final['nf']}, H={final['nh']}, Res={final['res']}")
