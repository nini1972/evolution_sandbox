#!/usr/bin/env python3
"""
Simulation script to systematically scan parameter space and investigate
synchronization transitions in various oscillator models.
"""
import json
import os
target_dir = "../simulation_results"
os.makedirs(target_dir, exist_ok=True)

import numpy as np
np.random.seed(42)

# -----------------------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------------------
def simulate_standard_kuramoto(theta, omega, K0, alpha=1.0, dt=0.05,
                                T_total=100.0, n_steps=None, rng=None):
    """Standard Kuramoto model with constant coupling K0."""
    if rng is None:
        rng = np.random.default_rng()
    n_phases = len(theta)
    t_arr = np.arange(n_steps) * dt if n_steps else None
    # Order parameter tracking
    R_history = []
    theta_history = []
    # Main integration loop
    for step in range(int(T_total / dt)):
        z = np.exp(1j * theta)
        R_mag = abs(np.mean(z)) / n_phases
        R_phase = np.angle(np.mean(z)) % (2 * np.pi)
        R_history.append((R_mag, R_phase))
        theta_new = theta + dt * (omega + K0 * R_mag * np.sin(R_phase - theta))
        theta_new = (theta_new + 2 * np.pi) % (2 * np.pi)
        theta_history.append(theta_new.tolist())
        theta = theta_new
    return np.array(R_history), np.array(theta_history), t_arr

# -----------------------------------------------------------------------------------------
# Load configurations from JSON
# -----------------------------------------------------------------------------------------
configurations = {
    "kuramoto_fixed_K": {
        "model": "kuramoto",
        "K0_list": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
        "N": 100,
        "alpha": 1.0,
        "dt": 0.05,
        "T_total": 100.0,
        "seed": 42,
        "description": "Standard Kuramoto model with fixed coupling K0. Tests phase locking
        and synchronization transitions as K0 varies."
    },
    "kuramoto_adaptive_K": {
        "model": "kuramoto",
        "K0_min": 0.5,
        "K0_max": 4.0,
        "K0_n": 15,
        "K_eff_alpha": 1.0,
        "N": 100,
        "alpha": 1.0,
        "dt": 0.05,
        "T_total": 100.0,
        "seed": 42,
        "description": "Adaptive Kuramoto model where effective coupling K_eff = K0 * R^alpha,
        with R being the order parameter. Tests how heterogeneity shapes synchronization
        transitions."
    },
    "heterogeneous_NaturalFreqs": {
        "model": "kuramoto",
        "K0": 2.0,
        "N_low": 50,
        "N_high": 50,
        "sigma_low": 0.1,
        "sigma_high": 0.5,
        "alpha": 1.0,
        "dt": 0.05,
        "T_total": 100.0,
        "seed": 42,
        "description": "Tests how heterogeneous natural frequencies distribute around bimodal
        distributions influence synchronization threshold."
    }
}

# -----------------------------------------------------------------------------------------
# Execute simulations for each configuration
# -----------------------------------------------------------------------------------------
results = {}
for config_name, config in configurations.items():
    print(f"\
--- BEGIN SIMULATION: {config_name} ---\
")
    N = config.get("N", 100)
    alpha = config.get("alpha", 1.0)
    dt = config.get("dt", 0.05)
    T_total = config.get("T_total", 100.0)
    seed = config.get("seed", 42)
    rng = np.random.default_rng(seed)
    
    if config_name == "kuramoto_fixed_K":
        K0_list = config.get("K0_list")
        R_mean_list = []
        R_std_list = []
        for K0 in K0_list:
            theta = rng.uniform(0, 2 * np.pi, size=N)
            omega = rng.normal(0, 1.0, size=N)
            R_hist, _, _ = simulate_standard_kuramoto(
                theta, omega, K0, alpha, dt, T_total=T_total, rng=rng
            )
            R_mean_list.append(float(np.mean([r[0] for r in R_hist])))
            R_std_list.append(float(np.std([r[0] for r in R_hist])))
        results[config_name] = {
            "K0_values": K0_list,
            "mean_R": R_mean_list,
            "std_R": R_std_list,
            "description": config.get("description")
        }
    elif config_name == "kuramoto_adaptive_K":
        K0_min = config.get("K0_min")
        K0_max = config.get("K0_max")
        K0_n = config.get("K0_n")
        K_eff_alpha = config.get("K_eff_alpha")
        N_low = config.get("N_low")
        N_high = config.get("N_high")
        
        K0_list = np.linspace(K0_min, K0_max, K0_n).tolist()
        R_mean_list = []
        R_std_list = []
        for K0 in K0_list:
            omega_low = rng.normal(-1, config.get("sigma_low"), size=N_low)
            omega_high = rng.normal(1, config.get("sigma_high"), size=N_high)
            omega = np.concatenate([omega_low, omega_high])
            theta = rng.uniform(0, 2 * np.pi, size=len(omega))
            R_hist, _, _ = simulate_standard_kuramoto(
                theta, omega, K0, K_eff_alpha, dt, T_total=T_total, rng=rng
            )
            R_mean_list.append(float(np.mean([r[0] for r in R_hist])))
            R_std_list.append(float(np.std([r[0] for r in R_hist])))
        results[config_name] = {
            "K0_values": K0_list,
            "mean_R": R_mean_list,
            "std_R": R_std_list,
            "description": config.get("description")
        }
    elif config_name == "heterogeneous_NaturalFreqs":
        N_low = config.get("N_low")
        N_high = config.get("N_high")
        sigma_low = config.get("sigma_low")
        sigma_high = config.get("sigma_high")
        
        omega_low = rng.normal(-1, sigma_low, size=N_low)
        omega_high = rng.normal(1, sigma_high, size=N_high)
        omega = np.concatenate([omega_low, omega_high])
        theta = rng.uniform(0, 2 * np.pi, size=len(omega))
        K0 = config.get("K0")
        alpha = config.get("alpha")
        dt = config.get("dt")
        T_total = config.get("T_total")
        R_hist, _, _ = simulate_standard_kuramoto(
            theta, omega, K0, alpha, dt, T_total=T_total, rng=rng
        )
        R_final = float(R_hist[-1][0])
        results[config_name] = {
            "K0": K0,
            "N_low": N_low,
            "N_high": N_high,
            "sigma_low": sigma_low,
            "sigma_high": sigma_high,
            "final_R": R_final,
            "description": config.get("description")
        }
    print(f" "--- END SIMULATION: {config_name} ---\
")

# -----------------------------------------------------------------------------------------
# Save results to JSON file
# -----------------------------------------------------------------------------------------
output_json = {
    "simulations": {
        name: res for name, res in results.items()
    }
}
with open(os.path.join(target_dir, "simulation_results.json"), "w") as f:
    json.dump(output_json, f, indent=4)
print(f"Simulation results saved to {os.path.join(target_dir, "simulation_results.json")}")