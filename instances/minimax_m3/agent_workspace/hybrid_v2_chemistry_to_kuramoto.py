"""
Hybrid v2: INVERSE coupling — chemistry → Kuramoto.
=====================================================
In v1, Kuramoto sync killed Gray-Scott patterns (negative result).
Here we flip the arrow: the local morphogen field v(x,t) modulates
the local Kuramoto coupling strength K_local(v).

Hypothesis: spatial gradients in v create spatial gradients in K,
which can FRAGMENT synchronization (chimera-like states) or
SELECTIVELY synchronize only v-rich regions.
"""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L = 24
m = 8

def laplacian_2d(f):
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4*f)

def kuramoto_r(theta):
    return np.abs(np.mean(np.exp(1j*theta), axis=2))

def step(theta, u, v, omega, K_base, K_grad_strength,
         K_net, Du, Dv, F, k, dt):
    """v modulates K_local: K(x) = K_base * (1 + alpha*(v - v_mean))."""
    r_cell = kuramoto_r(theta)
    R_cell = r_cell * np.exp(1j*np.angle(np.mean(np.exp(1j*theta), axis=2)))
    R_nb = (
        np.roll(R_cell, 1, 0) + np.roll(R_cell, -1, 0) +
        np.roll(R_cell, 1, 1) + np.roll(R_cell, -1, 1)
    ) / 4.0
    psi_nb = np.angle(R_nb)
    psi_self = np.angle(np.mean(np.exp(1j*theta), axis=2))

    # Spatially-varying local coupling
    K_local_field = K_base * (1 + K_grad_strength * (v - v.mean()))
    K_local_b = K_local_field[:, :, None]

    dtheta = (omega +
              K_local_b * r_cell[:, :, None] * np.sin(psi_self[:, :, None] - theta) +
              K_net * np.sin(psi_nb[:, :, None] - theta))
    theta_new = theta + dt * dtheta

    # Gray-Scott (unmodulated by r)
    uvv = u * v * v
    Lu = laplacian_2d(u); Lv = laplacian_2d(v)
    u_new = u + dt * (Du * Lu - uvv + F * (1 - u))
    v_new = v + dt * (Dv * Lv + uvv - (F + k) * v)
    return theta_new, u_new, v_new

def run(K_base, K_grad, K_net, T=120, dt=0.05, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, (L, L, m))
    omega = rng.standard_normal((L, L, m)) * 0.5
    u = np.ones((L, L))
    v = np.zeros((L, L))
    # Larger perturbation to ensure pattern formation
    v[L//2-3:L//2+3, L//2-3:L//2+3] = 0.7

    steps = int(T/dt)
    r_series = np.zeros(steps)
    sigma_v_series = np.zeros(steps)
    for s in range(steps):
        theta, u, v = step(theta, u, v, omega, K_base, K_grad,
                           K_net, 0.16, 0.08, 0.04, 0.06, dt)
        r_series[s] = kuramoto_r(theta).mean()
        sigma_v_series[s] = v.std()
    return {
        "r_final": float(r_series[-50:].mean()),
        "sigma_v_final": float(sigma_v_series[-50:].mean()),
        "r_max": float(r_series.max()),
        "r_field_final": kuramoto_r(theta).tolist(),
        "v_final": v.tolist(),
        "r_series": r_series[::20].tolist(),
        "sigma_v_series": sigma_v_series[::20].tolist(),
    }

if __name__ == "__main__":
    print("="*64)
    print("HYBRID v2 — Chemistry → Kuramoto coupling")
    print("="*64)
    # Sweep (K_base × K_grad)
    K_base_grid = [1.0, 2.0, 4.0]
    K_grad_grid = [-2.0, -1.0, 0.0, 1.0, 2.0]
    K_net_fix = 1.0
    results = {}
    for Kb in K_base_grid:
        for Kg in K_grad_grid:
            res = run(Kb, Kg, K_net_fix, T=120, dt=0.05, seed=hash((Kb,Kg))&0xFFFF)
            key = f"Kb={Kb:.1f}_Kg={Kg:+.1f}"
            results[key] = res
            print(f"  Kb={Kb:.1f}  Kg={Kg:+.1f}  "
                  f"r̄={res['r_final']:.3f}  r_max={res['r_max']:.3f}  "
                  f"σ_v={res['sigma_v_final']:.4f}")

    # Plot the tradeoff
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    cmap = plt.cm.viridis
    markers = ['o','s','^']
    for i, Kb in enumerate(K_base_grid):
        rs = [results[f"Kb={Kb:.1f}_Kg={Kg:+.1f}"]["r_final"]
              for Kg in K_grad_grid]
        svs = [results[f"Kb={Kb:.1f}_Kg={Kg:+.1f}"]["sigma_v_final"]
               for Kg in K_grad_grid]
        axes[0].plot(K_grad_grid, rs, f'{markers[i]}-',
                     color=cmap(i/len(K_base_grid)), label=f"Kb={Kb:.1f}")
        axes[1].plot(K_grad_grid, svs, f'{markers[i]}-',
                     color=cmap(i/len(K_base_grid)), label=f"Kb={Kb:.1f}")
    axes[0].set_xlabel("K_grad (coupling strength)"); axes[0].set_ylabel("r̄")
    axes[0].set_title("(A) Synchronization vs coupling gradient"); axes[0].grid(alpha=0.3); axes[0].legend()
    axes[1].set_xlabel("K_grad"); axes[1].set_ylabel("σ_v (pattern strength)")
    axes[1].set_title("(B) Pattern formation vs coupling gradient"); axes[1].grid(alpha=0.3); axes[1].legend()
    plt.suptitle("Hybrid v2: chemistry→Kuramoto coupling",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("hybrid_v2_chemistry_to_kuramoto.png", dpi=130, bbox_inches="tight")
    plt.close()
    with open("hybrid_v2_results.json","w") as f:
        json.dump(results, f, indent=2)
    print("Saved hybrid_v2_chemistry_to_kuramoto.png + .json")
