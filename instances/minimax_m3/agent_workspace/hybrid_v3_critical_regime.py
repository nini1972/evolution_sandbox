"""
Hybrid v3: CRITICAL REGIME — both phenomena near their onset.
=============================================================
v1, v2 failed because either K was far above K_c (saturated sync)
or F modulation killed patterns. Here we work in the critical
regime of BOTH transitions:
  - K_base near K_c(Δ_eff) so synchronization is partial
  - Use only GRADIENT coupling (v→K), not direct F modulation
  - σ_v std kept as the order parameter for pattern onset

If the unification hypothesis is right, we should see:
  (a) A chimera-like state: spatial regions where sync coexists
      with pattern, and others where pattern dominates
  (b) A NEGATIVE correlation between local r(x) and |∇v(x)|
      (sync suppresses pattern locally)
"""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L = 24
m = 4  # fewer oscillators per cell → K_c is reachable

def laplacian_2d(f):
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4*f)

def kuramoto_r(theta):
    return np.abs(np.mean(np.exp(1j*theta), axis=2))

def step(theta, u, v, omega, K_base, K_grad_strength,
         K_net, Du, Dv, F, k, dt):
    """K_local(x) = K_base * (1 + alpha*(v - v_mean)). Pure gradient."""
    r_cell = kuramoto_r(theta)
    R_cell = r_cell * np.exp(1j*np.angle(np.mean(np.exp(1j*theta), axis=2)))
    R_nb = (
        np.roll(R_cell, 1, 0) + np.roll(R_cell, -1, 0) +
        np.roll(R_cell, 1, 1) + np.roll(R_cell, -1, 1)
    ) / 4.0
    psi_nb = np.angle(R_nb)
    psi_self = np.angle(np.mean(np.exp(1j*theta), axis=2))

    # Spatially-varying local coupling (gradient only)
    v_centered = v - v.mean()
    K_local_field = K_base * (1 + K_grad_strength * v_centered)
    K_local_field = np.clip(K_local_field, 0.0, 10.0)
    K_local_b = K_local_field[:, :, None]

    dtheta = (omega +
              K_local_b * r_cell[:, :, None] *
              np.sin(psi_self[:, :, None] - theta) +
              K_net * np.sin(psi_nb[:, :, None] - theta))
    theta_new = theta + dt * dtheta

    uvv = u * v * v
    Lu = laplacian_2d(u); Lv = laplacian_2d(v)
    u_new = u + dt * (Du * Lu - uvv + F * (1 - u))
    v_new = v + dt * (Dv * Lv + uvv - (F + k) * v)
    return theta_new, u_new, v_new

def run(K_base, K_grad, K_net, T=200, dt=0.05, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, (L, L, m))
    # Narrower ω distribution → lower K_c → easier to reach critical
    omega = rng.standard_normal((L, L, m)) * 0.3
    u = np.ones((L, L))
    v = np.zeros((L, L))
    v[L//2-3:L//2+3, L//2-3:L//2+3] = 0.7

    steps = int(T/dt)
    r_series = np.zeros(steps)
    sigma_v_series = np.zeros(steps)
    for s in range(steps):
        theta, u, v = step(theta, u, v, omega, K_base, K_grad,
                           K_net, 0.16, 0.08, 0.04, 0.06, dt)
        r_series[s] = kuramoto_r(theta).mean()
        sigma_v_series[s] = v.std()

    r_field = kuramoto_r(theta)
    # Spatial correlation between local sync and local v
    r_flat = r_field.flatten()
    v_flat = v.flatten()
    corr = float(np.corrcoef(r_flat, v_flat)[0, 1])
    # Chimera index: spatial variance of r (large = chimera)
    chimera_idx = float(r_field.std())

    return {
        "r_final": float(r_series[-50:].mean()),
        "sigma_v_final": float(sigma_v_series[-50:].mean()),
        "r_max": float(r_series.max()),
        "corr_r_v": corr,
        "chimera_idx": chimera_idx,
        "r_field": r_field.tolist(),
        "v_field": v.tolist(),
        "r_series": r_series[::20].tolist(),
        "sigma_v_series": sigma_v_series[::20].tolist(),
    }

if __name__ == "__main__":
    print("="*64)
    print("HYBRID v3 — Critical regime (K_base near K_c, gradient coupling)")
    print("="*64)
    # m=4 oscillators/cell, σ_ω=0.3 → K_c(m=4) should be much smaller
    # K_c(small swarm, all-to-all) ≈ 2 * σ_ω * sqrt(2/(π*m)) for m>1
    # = 2*0.3*sqrt(0.159) ≈ 0.24 ... so we sweep K_base in [0.1, 1.0]
    K_base_grid = [0.1, 0.3, 0.5, 0.8, 1.2]
    K_grad_grid = [0.0, 0.5, 1.0, 2.0]
    K_net_fix = 0.2
    results = {}
    for Kb in K_base_grid:
        for Kg in K_grad_grid:
            res = run(Kb, Kg, K_net_fix, T=200, dt=0.05, seed=hash((Kb,Kg))&0xFFFF)
            key = f"Kb={Kb:.2f}_Kg={Kg:.1f}"
            results[key] = res
            print(f"  Kb={Kb:.2f}  Kg={Kg:.1f}  "
                  f"r̄={res['r_final']:.3f}  σ_v={res['sigma_v_final']:.4f}  "
                  f"corr(r,v)={res['corr_r_v']:+.3f}  "
                  f"chimera={res['chimera_idx']:.3f}")

    # Plot tradeoff + chimera maps
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # (A) sync vs K_grad for each K_base
    markers = ['o','s','^','D','v']
    cmap = plt.cm.plasma
    for i, Kb in enumerate(K_base_grid):
        rs = [results[f"Kb={Kb:.2f}_Kg={Kg:.1f}"]["r_final"]
              for Kg in K_grad_grid]
        axes[0,0].plot(K_grad_grid, rs, f'{markers[i]}-',
                       color=cmap(i/len(K_base_grid)), label=f"Kb={Kb:.2f}")
    axes[0,0].set_xlabel("K_grad"); axes[0,0].set_ylabel("r̄")
    axes[0,0].set_title("(A) Synchronization r̄ vs coupling gradient")
    axes[0,0].grid(alpha=0.3); axes[0,0].legend()

    # (B) sigma_v vs K_grad for each K_base
    for i, Kb in enumerate(K_base_grid):
        svs = [results[f"Kb={Kb:.2f}_Kg={Kg:.1f}"]["sigma_v_final"]
               for Kg in K_grad_grid]
        axes[0,1].plot(K_grad_grid, svs, f'{markers[i]}-',
                       color=cmap(i/len(K_base_grid)), label=f"Kb={Kb:.2f}")
    axes[0,1].set_xlabel("K_grad"); axes[0,1].set_ylabel("σ_v")
    axes[0,1].set_title("(B) Pattern formation σ_v vs coupling gradient")
    axes[0,1].grid(alpha=0.3); axes[0,1].legend()

    # (C) Chimera index heatmap
    chim_grid = np.array([[results[f"Kb={Kb:.2f}_Kg={Kg:.1f}"]["chimera_idx"]
                           for Kg in K_grad_grid] for Kb in K_base_grid])
    im = axes[1,0].imshow(chim_grid, origin="lower", aspect="auto",
                          cmap="inferno",
                          extent=[min(K_grad_grid), max(K_grad_grid),
                                  min(K_base_grid), max(K_base_grid)])
    axes[1,0].set_xlabel("K_grad"); axes[1,0].set_ylabel("K_base")
    axes[1,0].set_title("(C) Chimera index σ[r(x)]")
    plt.colorbar(im, ax=axes[1,0])

    # (D) Correlation heatmap
    corr_grid = np.array([[results[f"Kb={Kb:.2f}_Kg={Kg:.1f}"]["corr_r_v"]
                           for Kg in K_grad_grid] for Kb in K_base_grid])
    im = axes[1,1].imshow(corr_grid, origin="lower", aspect="auto",
                          cmap="RdBu_r", vmin=-1, vmax=1,
                          extent=[min(K_grad_grid), max(K_grad_grid),
                                  min(K_base_grid), max(K_base_grid)])
    axes[1,1].set_xlabel("K_grad"); axes[1,1].set_ylabel("K_base")
    axes[1,1].set_title("(D) Spatial corr(r(x), v(x))")
    plt.colorbar(im, ax=axes[1,1])

    plt.suptitle("Hybrid v3 — Critical regime analysis (m=4 osc/cell, σ_ω=0.3)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("hybrid_v3_critical_regime.png", dpi=130, bbox_inches="tight")
    plt.close()

    # Spatial field visualization: pick the most chimera-like case
    best_key = max(results, key=lambda k: results[k]["chimera_idx"])
    res_best = results[best_key]
    fig2, axes2 = plt.subplots(1, 3, figsize=(15, 4))
    im0 = axes2[0].imshow(np.array(res_best["r_field"]), cmap="viridis")
    axes2[0].set_title(f"r(x) field — {best_key}")
    plt.colorbar(im0, ax=axes2[0])
    im1 = axes2[1].imshow(np.array(res_best["v_field"]), cmap="magma")
    axes2[1].set_title(f"v(x) field — {best_key}")
    plt.colorbar(im1, ax=axes2[1])
    # Overlay: r thresholded + v contours
    r_f = np.array(res_best["r_field"]); v_f = np.array(res_best["v_field"])
    axes2[2].imshow(r_f > 0.5, cmap="Blues", alpha=0.6)
    axes2[2].contour(v_f, levels=5, colors="red", linewidths=1)
    axes2[2].set_title(f"Sync regions (blue) + v contours (red)\n"
                       f"corr(r,v)={res_best['corr_r_v']:+.3f}")
    plt.suptitle(f"Best chimera case: {best_key}", fontweight="bold")
    plt.tight_layout()
    plt.savefig("hybrid_v3_best_chimera.png", dpi=130, bbox_inches="tight")
    plt.close()

    with open("hybrid_v3_results.json","w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBest chimera case: {best_key} (chimera_idx={res_best['chimera_idx']:.3f})")
    print("Saved hybrid_v3_critical_regime.png + best chimera overlay + .json")
