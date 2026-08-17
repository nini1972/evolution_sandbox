import json

# All alpha values' oscillation results from the three runs
# From run 1: α=0.0, 0.2, 0.4 (partial - got cut off)
# From run 2: α=0.5, 0.6, 0.7
# From run 3: α=0.8, 0.9, 0.95

# But I only have osc K values, not full data. I need the full data.
# Let me just note what we know and build the heatmap from the osc detection results
# I'll need to re-run but more efficiently.

# Actually, the printed outputs tell us which K values had oscillation for each alpha.
# Let me compile this.

phase_data = {
    "alpha_0.0": {"osc_ks": [10, 20]},
    "alpha_0.2": {"osc_ks": [8, 20]},
    "alpha_0.4": {"osc_ks": [8, 10, 12, 25]},
    "alpha_0.5": {"osc_ks": [6, 12, 16, 18, 20]},
    "alpha_0.6": {"osc_ks": [10, 12, 14, 16, 20]},
    "alpha_0.7": {"osc_ks": [12, 14, 16, 20]},
    "alpha_0.8": {"osc_ks": [6, 10, 12, 14, 16, 18]},
    "alpha_0.9": {"osc_ks": [6, 8, 10, 12, 14, 16, 20, 30]},
    "alpha_0.95": {"osc_ks": [8, 10, 14, 16, 18, 20, 30]},
}

with open('r19z_phase_diagram_summary.json', 'w') as f:
    json.dump(phase_data, f, indent=2)
print("Saved summary")

# Print phase diagram as ASCII
alpha_list = [0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
K_list = [4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30]
header = "α\\K | " + " ".join(f"{k:3d}" for k in K_list)
print(header)
print("-" * len(header))
for alpha in alpha_list:
    key = f"alpha_{alpha}"
    osc = set(phase_data[key]["osc_ks"])
    row = " ".join("  * " if k in osc else "   ." for k in K_list)
    print(f"{alpha:.2f} | {row}")
