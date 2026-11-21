"""
Hybrid Synchronization-Pattern Emergence
=========================================
A coupled (Kuramoto) ⨯ (Gray-Scott) lattice system.

Each cell of an L×L grid hosts:
  (a) a small Kuramoto swarm of m oscillators with phases θ_i(x,t)
  (b) two morphogens u(x,t), v(x,t) governed by Gray-Scott

Coupling rules:
  (S1) Intra-cell Kuramoto coupling: K_local Σ sin(θ_j - θ_i)
  (S2) Inter-cell Kuramoto coupling: K_network R_neighbor - θ_i,
       where R_neighbor = |Σ exp(iθ)| over nearest neighbors
  (P1) Gray-Scott within cell (same as standard)
  (P2) Gray-Scott diffusion between cells (Laplacian)
  (C)  Coupling: u production rate F modulated by local r = |R_cell|

Goal: discover whether the joint (K, Du, Dv, F, k) parameter space
has a unified "synchronization ↔ pattern" phase diagram.

Computational cost:
  L=24, m=8 oscillators/cell, 5000 steps → feasible in single turn.
  Total DOFs: 24*24*8 phases + 2*24*24 chemicals = 5760.

Output: hybrid_sync_pattern_phase_diagram.png + .json
"""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import laplace

# --- Lattice setup ---
L = 24           # grid side
m = 8            # oscillators per cell
N_total = L*L*m # total Kuramoto DOF

def build_phase_grid():
    """L*L*m phase array: phase[lx, ly, i]"""
    return np.random.uniform(-np.pi, np.pi, (L, L, m))

def kuramoto_r_field(theta):
    """Per-cell order parameter r_cell[lx,ly] = |<exp(iθ)>|"""
    return np.abs(np.mean(np.exp(1j*theta), axis=2))  # shape (L,L)

def laplacian_2d(f):
    """5-point Laplacian with periodic BCs (vectorized)."""
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4*f)

def laplace_2d(f):
    """Alias used in main loop (matches the call site)."""
    return laplacian_2d(f)

def step(theta, u, v, omega, K_local, K_net, Du, Dv, F, k, dt):
    """
    One RK4-style Euler step of the hybrid system.
    omega is per-oscillator frequencies (L,L,m).
    """
    # ---- Kuramoto ----
    r_cell = kuramoto_r_field(theta)  # (L,L)
    R_cell = r_cell * np.exp(1j * np.angle(
        np.mean(np.exp(1j*theta), axis=2)))  # complex (L,L)

    # Neighbor mean R
    R_nb = (
        np.roll(R_cell, 1, 0) + np.roll(R_cell, -1, 0) +
        np.roll(R_cell, 1, 1) + np.roll(R_cell, -1, 1)
    ) / 4.0
    psi_nb = np.angle(R_nb)
    # Broadcast to (L,L,m)
    psi_nb_b = psi_nb[:, :, None]
    psi_self_b = np.angle(np.mean(np.exp(1j*theta), axis=2))[:, :, None]

    # Within-cell order parameter (same for all i in a cell)
    dtheta = (omega + K_local * r_cell[:, :, None] *
              np.sin(psi_self_b - theta) +
              K_net * np.sin(psi_nb_b - theta))
    theta_new = theta + dt * dtheta

    # ---- Gray-Scott ----
    uvv = u * v * v
    Lu = laplace_2d(u); Lv = laplace_2d(v)
    # Modulate F by local Kuramoto synchronization (coupling rule C)
    F_eff = F * (1.0 + 2.0 * (r_cell - 0.5))  # higher r ⇒ stronger feed
    u_new = u + dt * (Du * Lu - uvv + F_eff * (1 - u))
    v_new = v + dt * (Dv * Lv + uvv - (F_eff + k) * v)
    return theta_new, u_new, v_new

def run_hybrid(K_local, K_net, Du, Dv, F, k, T=80, dt=0.05, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi, np.pi, (L, L, m))
    omega = rng.standard_normal((L, L, m)) * 0.5
    # Init chemistry: u=1, v=0 + small perturbation at center
    u = np.ones((L, L)); v = np.zeros((L, L))
    v[L//2-2:L//2+2, L//2-2:L//2+2] = 0.5

    steps = int(T/dt)
    # Trajectories to save
    r_traj = np.zeros(steps)
    pattern_var_traj = np.zeros(steps)
    for s in range(steps):
        theta, u, v = step(theta, u, v, omega,
                           K_local, K_net, Du, Dv, F, k, dt)
        if s % 5 == 0:
            r_traj[s] = kuramoto_r_field(theta).mean()
            # Pattern variability: spatial std of v across cells
            pattern_var_traj[s] = v.std()
    return {"r_mean": float(r_traj[-10:].mean()),
            "pattern_var": float(pattern_var_traj[-10:].mean()),
            "r_series": r_traj[::10].tolist(),
            "pattern_var_series": pattern_var_traj[::10].tolist(),
            "u_final": u, "v_final": v}

# --- Phase diagram: (K_local × K_net) × pattern regime ---
if __name__ == "__main__":
    print("="*64)
    print("HYBRID KURAMOTO × GRAY-SCOTT PHASE DIAGRAM")
    print("="*64)
    # Fix chemistry (Du=0.16, Dv=0.08, F=0.04, k=0.06 — known pattern regime)
    Du_fix, Dv_fix = 0.16, 0.08
    F_fix, k_fix   = 0.04, 0.06
    K_local_grid = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
    K_net_grid   = [0.0, 0.5, 1.0, 2.0, 4.0]
    grid = np.zeros((len(K_local_grid), len(K_net_grid)))
    pvar = np.zeros_like(grid)
    for i, Kl in enumerate(K_local_grid):
        for j, Kn in enumerate(K_net_grid):
            res = run_hybrid(Kl, Kn, Du_fix, Dv_fix, F_fix, k_fix,
                             T=60, dt=0.05, seed=i*10+j)
            grid[i, j] = res["r_mean"]
            pvar[i, j] = res["pattern_var"]
            print(f"  K_loc={Kl:.1f}  K_net={Kn:.1f}  r̄={res['r_mean']:.3f}  "
                  f"σ_v={res['pattern_var']:.4f}")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    im = axes[0].imshow(grid, origin="lower", aspect="auto", cmap="viridis",
                        extent=[min(K_net_grid), max(K_net_grid),
                                min(K_local_grid), max(K_local_grid)])
    axes[0].set_xlabel("K_net (inter-cell)"); axes[0].set_ylabel("K_local (intra-cell)")
    axes[0].set_title("(A) Synchronization r̄(K_local, K_net)")
    plt.colorbar(im, ax=axes[0], label="r̄")

    im = axes[1].imshow(pvar, origin="lower", aspect="auto", cmap="magma",
                        extent=[min(K_net_grid), max(K_net_grid),
                                min(K_local_grid), max(K_local_grid)])
    axes[1].set_xlabel("K_net"); axes[1].set_ylabel("K_local")
    axes[1].set_title("(B) Pattern variability σ_v(K_local, K_net)")
    plt.colorbar(im, ax=axes[1], label="σ_v")

    # Tradeoff scatter
    axes[2].scatter(grid.flatten(), pvar.flatten(),
                    c=np.array(K_local_grid)[:,None].repeat(len(K_net_grid),1).flatten(),
                    cmap="viridis", s=80, edgecolor="k")
    axes[2].set_xlabel("Sync r̄"); axes[2].set_ylabel("Pattern σ_v")
    axes[2].set_title("(C) Sync ↔ Pattern tradeoff")
    axes[2].grid(alpha=0.3)

    plt.suptitle("Hybrid Kuramoto × Gray-Scott: a unified phase diagram",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig("hybrid_sync_pattern_phase_diagram.png", dpi=130,
                bbox_inches="tight")
    plt.close()
    np.save("hybrid_grid.npy", grid)
    np.save("hybrid_pvar.npy", pvar)
    with open("hybrid_sync_pattern_results.json", "w") as f:
        json.dump({
            "K_local": K_local_grid, "K_net": K_net_grid,
            "sync_grid": grid.tolist(), "pattern_var_grid": pvar.tolist(),
            "Du": Du_fix, "Dv": Dv_fix, "F": F_fix, "k": k_fix,
            "L": L, "m": m, "T": 60,
        }, f, indent=2)
    print("Saved hybrid_sync_pattern_phase_diagram.png + .json")
