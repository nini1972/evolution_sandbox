"""
Hybrid v4 — Random K_local field control (falsification test).
==============================================================
v3 found POSITIVE corr(r(x), v(x)) = +0.348 at Kb=1.2, Kg=2.0.
Question: is this specific to the v→K gradient coupling, or
is any spatially heterogeneous K field sufficient?

Compare THREE coupling architectures at Kb=1.2, K_net=0.2:
  (A) HOMOGENEOUS: K_local = Kb everywhere
  (B) GRADIENT:    K_local(x) = Kb*(1 + Kg*(v(x) - v̄))
  (C) RANDOM:      K_local(x) = Kb*(1 + Kg*ξ(x))  where ξ ∼ U[-1,1] fixed

If (A) gives similar corr(r,v) → spatial coupling heterogeneity is generic.
If (B) ≫ (C) in corr → the v→K coupling specifically co-aligns them.
If (C) ≫ (B) → random heterogeneity is more disruptive.
"""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L = 24
m = 4

def laplacian_2d(f):
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4*f)

def kuramoto_r(theta):
    return np.abs(np.mean(np.exp(1j*theta), axis=2))

def step(theta, u, v, omega, K_local_field, K_net,
         Du, Dv, F, k, dt):
    r_cell = kuramoto_r(theta)
    R_cell = r_cell * np.exp(1j*np.angle(np.mean(np.exp(1j*theta), axis=2)))
    R_nb = (
        np.roll(R_cell, 1, 0) + np.roll(R_cell, -1, 0) +
        np.roll(R_cell, 1, 1) + np.roll(R_cell, -1, 1)
    ) / 4.0
    psi_nb = np.angle(R_nb)
    psi_self = np.angle(np.mean(np.exp(1j*theta), axis=2))

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

def run(K_base, K_grad, K_net, T=200, dt=0.05, seed=0,
        coupling="gradient", K_local_static=None):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, (L, L, m))
    omega = rng.standard_normal((L, L, m)) * 0.3
    u = np.ones((L, L))
    v = np.zeros((L, L))
    v[L//2-3:L//2+3, L//2-3:L//2+3] = 0.7

    # Pre-build the K_local field if random
    if coupling == "random":
        if K_local_static is None:
            xi = rng.uniform(-1.0, 1.0, (L, L))
            K_local_static = K_base * (1 + K_grad * xi)

    steps = int(T/dt)
    r_series = np.zeros(steps)
    sigma_v_series = np.zeros(steps)
    for s in range(steps):
        # Determine K_local field this step
        if coupling == "homogeneous":
            K_local_field = np.full((L, L), K_base)
        elif coupling == "gradient":
            K_local_field = K_base * (1 + K_grad * (v - v.mean()))
            K_local_field = np.clip(K_local_field, 0.0, 10.0)
        elif coupling == "random":
            K_local_field = K_local_static
        else:
            raise ValueError(coupling)

        theta, u, v = step(theta, u, v, omega, K_local_field, K_net,
                           0.16, 0.08, 0.04, 0.06, dt)
        r_series[s] = kuramoto_r(theta).mean()
        sigma_v_series[s] = v.std()

    r_field = kuramoto_r(theta)
    r_flat = r_field.flatten()
    v_flat = v.flatten()
    corr = float(np.corrcoef(r_flat, v_flat)[0, 1])
    chimera_idx = float(r_field.std())

    return {
        "r_final": float(r_series[-50:].mean()),
        "sigma_v_final": float(sigma_v_series[-50:].mean()),
        "corr_r_v": corr,
        "chimera_idx": chimera_idx,
        "r_field": r_field.tolist(),
        "v_field": v.tolist(),
    }

if __name__ == "__main__":
    print("="*64)
    print("HYBRID v4 — Random K_local field control (falsification test)")
    print("="*64)

    K_base = 1.2
    K_net = 0.2
    K_grad = 2.0
    n_seeds = 8

    results = {"homogeneous": [], "gradient": [], "random": []}

    for seed in range(n_seeds):
        # 1. Homogeneous
        res_h = run(K_base, K_grad, K_net, T=200, dt=0.05,
                    seed=seed, coupling="homogeneous")
        results["homogeneous"].append(res_h)
        # 2. Gradient
        res_g = run(K_base, K_grad, K_net, T=200, dt=0.05,
                    seed=seed, coupling="gradient")
        results["gradient"].append(res_g)
        # 3. Random (build K field from independent seed for reproducibility)
        rng_xi = np.random.default_rng(seed * 1000)
        xi = rng_xi.uniform(-1.0, 1.0, (L, L))
        K_field = K_base * (1 + K_grad * xi)
        res_r = run(K_base, K_grad, K_net, T=200, dt=0.05,
                    seed=seed, coupling="random",
                    K_local_static=K_field)
        results["random"].append(res_r)

        print(f"  seed={seed}  "
              f"HOMO: r̄={res_h['r_final']:.3f} corr={res_h['corr_r_v']:+.3f} | "
              f"GRAD: r̄={res_g['r_final']:.3f} corr={res_g['corr_r_v']:+.3f} | "
              f"RAND: r̄={res_r['r_final']:.3f} corr={res_r['corr_r_v']:+.3f}")

    # Aggregate
    print("\n--- Aggregated over", n_seeds, "seeds ---")
    summary = {}
    for arch in ["homogeneous", "gradient", "random"]:
        corrs = [r["corr_r_v"] for r in results[arch]]
        rs = [r["r_final"] for r in results[arch]]
        chims = [r["chimera_idx"] for r in results[arch]]
        summary[arch] = {
            "corr_mean": float(np.mean(corrs)),
            "corr_std": float(np.std(corrs)),
            "r_mean": float(np.mean(rs)),
            "chimera_mean": float(np.mean(chims)),
        }
        print(f"  {arch:12s}: corr(r,v)={np.mean(corrs):+.3f}±{np.std(corrs):.3f}  "
              f"r̄={np.mean(rs):.3f}±{np.std(rs):.3f}  "
              f"chimera={np.mean(chims):.3f}±{np.std(chims):.3f}")

    # Plot comparison
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    archs = ["homogeneous", "gradient", "random"]
    colors = ["#2c7bb6", "#d7191c", "#fdae61"]
    x_pos = np.arange(len(archs))

    corr_means = [summary[a]["corr_mean"] for a in archs]
    corr_stds = [summary[a]["corr_std"] for a in archs]
    axes[0].bar(x_pos, corr_means, yerr=corr_stds, color=colors,
                alpha=0.8, capsize=6)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels([a.capitalize() for a in archs])
    axes[0].set_ylabel("corr(r(x), v(x))")
    axes[0].set_title("(A) Spatial correlation: r vs v")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].grid(alpha=0.3, axis="y")

    r_means = [summary[a]["r_mean"] for a in archs]
    axes[1].bar(x_pos, r_means, color=colors, alpha=0.8)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels([a.capitalize() for a in archs])
    axes[1].set_ylabel("r̄ (mean sync)")
    axes[1].set_title("(B) Mean synchronization")
    axes[1].grid(alpha=0.3, axis="y")

    chim_means = [summary[a]["chimera_mean"] for a in archs]
    axes[2].bar(x_pos, chim_means, color=colors, alpha=0.8)
    axes[2].set_xticks(x_pos)
    axes[2].set_xticklabels([a.capitalize() for a in archs])
    axes[2].set_ylabel("σ[r(x)] (chimera index)")
    axes[2].set_title("(C) Chimera index")
    axes[2].grid(alpha=0.3, axis="y")

    plt.suptitle("Hybrid v4: Falsification test — gradient vs random vs homogeneous K_local",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("hybrid_v4_falsification_test.png", dpi=130, bbox_inches="tight")
    plt.close()

    # Sample spatial fields side by side (last seed)
    fig2, axes2 = plt.subplots(2, 3, figsize=(14, 9))
    for col, arch in enumerate(archs):
        last = results[arch][-1]
        r_field = np.array(last["r_field"])
        v_field = np.array(last["v_field"])
        axes2[0, col].imshow(r_field, cmap="viridis", vmin=0, vmax=1)
        axes2[0, col].set_title(f"r(x) — {arch}")
        axes2[0, col].axis("off")
        axes2[1, col].imshow(v_field, cmap="magma")
        axes2[1, col].set_title(f"v(x) — {arch}")
        axes2[1, col].axis("off")
    plt.suptitle(f"Spatial fields (seed={n_seeds-1}): do sync and pattern co-localize?",
                 fontweight="bold")
    plt.tight_layout()
    plt.savefig("hybrid_v4_spatial_fields.png", dpi=130, bbox_inches="tight")
    plt.close()

    with open("hybrid_v4_falsification_results.json", "w") as f:
        json.dump({"per_seed": results, "summary": summary}, f, indent=2)
    print("\nSaved hybrid_v4_falsification_test.png + spatial_fields + .json")
