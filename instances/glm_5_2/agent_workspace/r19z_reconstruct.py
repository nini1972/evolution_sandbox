import json

# From the first run (r19z_sigma_scan2.py output):
# σ=50: oscillation at K=[8]
# σ=100: oscillation at K=[10, 12, 14, 16, 18]

# From the detailed σ=50 run output (r19z_sigma_scan.py first run):
sigma_50 = {
    "8": {"r_mean": 0.862, "r_std": 0.077, "osc_strength": 0.197, "osc_period": 22},
    "10": {"r_mean": 0.902, "r_std": 0.060, "osc_strength": 0.000, "osc_period": 0},
    "12": {"r_mean": 0.917, "r_std": 0.054, "osc_strength": 0.000, "osc_period": 0},
    "14": {"r_mean": 0.927, "r_std": 0.051, "osc_strength": 0.000, "osc_period": 0},
    "16": {"r_mean": 0.939, "r_std": 0.047, "osc_strength": 0.000, "osc_period": 0},
    "18": {"r_mean": 0.949, "r_std": 0.043, "osc_strength": 0.000, "osc_period": 0},
    "20": {"r_mean": 0.950, "r_std": 0.047, "osc_strength": 0.000, "osc_period": 0},
    "25": {"r_mean": 0.961, "r_std": 0.039, "osc_strength": 0.000, "osc_period": 0},
    "30": {"r_mean": 0.969, "r_std": 0.033, "osc_strength": 0.000, "osc_period": 0}
}

# From the σ=100 detailed output:
sigma_100 = {
    "8": {"r_mean": 0.278, "r_std": 0.136, "osc_strength": 0.000, "osc_period": 0},
    "10": {"r_mean": 0.354, "r_std": 0.162, "osc_strength": 0.251, "osc_period": 25},
    "12": {"r_mean": 0.491, "r_std": 0.175, "osc_strength": 0.189, "osc_period": 28},
    "14": {"r_mean": 0.630, "r_std": 0.176, "osc_strength": 0.237, "osc_period": 30},
    "16": {"r_mean": 0.656, "r_std": 0.183, "osc_strength": 0.231, "osc_period": 15},
    "18": {"r_mean": 0.730, "r_std": 0.158, "osc_strength": 0.150, "osc_period": 16},
    "20": {"r_mean": 0.766, "r_std": 0.156, "osc_strength": 0.206, "osc_period": 14},
    "25": {"r_mean": 0.814, "r_std": 0.151, "osc_strength": 0.000, "osc_period": 0}
}

data = json.load(open('r19z_sigma_scan.json'))
data["sigma_50"] = sigma_50
data["sigma_100"] = sigma_100
with open('r19z_sigma_scan.json', 'w') as f:
    json.dump(data, f, indent=2)

# Print summary
for sigma_key in sorted(data.keys()):
    sigma = int(sigma_key.split('_')[1])
    osc_ks = [int(k) for k, d in data[sigma_key].items() if d["osc_strength"] > 0.15]
    if osc_ks:
        center = sum(osc_ks) / len(osc_ks)
        print(f"σ={sigma:4d}: oscillation at K={osc_ks}, center≈{center:.1f}")
    else:
        print(f"σ={sigma:4d}: no oscillation detected")
