import json

# σ=200 results from the run
results = {
    "10": {"r_mean": 0.193, "r_std": 0.100, "osc_strength": 0.000, "osc_period": 0},
    "12": {"r_mean": 0.190, "r_std": 0.103, "osc_strength": 0.000, "osc_period": 0},
    "14": {"r_mean": 0.222, "r_std": 0.119, "osc_strength": 0.000, "osc_period": 0},
    "16": {"r_mean": 0.223, "r_std": 0.118, "osc_strength": 0.000, "osc_period": 0},
    "18": {"r_mean": 0.238, "r_std": 0.129, "osc_strength": 0.000, "osc_period": 0},
    "20": {"r_mean": 0.270, "r_std": 0.146, "osc_strength": 0.000, "osc_period": 0},
    "25": {"r_mean": 0.324, "r_std": 0.176, "osc_strength": 0.172, "osc_period": 16},
    "30": {"r_mean": 0.389, "r_std": 0.204, "osc_strength": 0.169, "osc_period": 11},
    "35": {"r_mean": 0.473, "r_std": 0.230, "osc_strength": 0.261, "osc_period": 11},
    "40": {"r_mean": 0.544, "r_std": 0.232, "osc_strength": 0.000, "osc_period": 0}
}

# Load existing data and add
try:
    data = json.load(open('r19z_sigma_scan.json'))
except:
    data = {}
data["sigma_200"] = results
with open('r19z_sigma_scan.json', 'w') as f:
    json.dump(data, f, indent=2)

# Summary
for sigma_key in sorted(data.keys()):
    sigma = int(sigma_key.split('_')[1])
    osc_ks = [int(k) for k, d in data[sigma_key].items() if d["osc_strength"] > 0.15]
    if osc_ks:
        center = sum(osc_ks) / len(osc_ks)
        print(f"σ={sigma:4d}: oscillation at K={osc_ks}, center≈{center:.1f}")
    else:
        print(f"σ={sigma:4d}: no oscillation detected")
