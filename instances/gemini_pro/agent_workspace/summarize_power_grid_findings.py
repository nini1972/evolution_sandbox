import json

summary = {
    "system": "IEEE 14-Bus Second-Order Kuramoto Network",
    "dataset": "power_grid_ieee",
    "perturbation_window_s": [0.2, 15.6],
    "baseline_order_parameter_r0": 0.993725,
    "minimum_order_parameter_rmin": 0.988998,
    "time_of_maximum_coherence_loss_s": 1.90,
    "damping_coefficient_gamma_s_inv": 0.3153,
    "relaxation_timescale_tau_s": 3.17,
    "inter_area_swing_frequency_hz": 0.2331,
    "steady_state_rqa": {
        "embedding_dimension": 3,
        "tau_steps": 4,
        "epsilon": 0.25,
        "determinism_DET": 0.9956,
        "laminarity_LAM": 0.9959,
        "recurrence_rate_RR": 0.3835,
        "shannon_entropy_ENT": 6.0581
    }
}

with open("power_grid_invariants.json", "w") as f:
    json.dump(summary, f, indent=2)

print("Saved power_grid_invariants.json")
