"""Stratified tongue scan: classify P1/P2/P4/P8/CHAOS across the CML chaos
region and extract tongue boundaries. Produces a class-map PNG + JSON data.
Follow-up to the P8 discovery at (r=3.925, eps=0.148)."""
import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import p4_cml_period_gate_module as M

N = 120
N_TRANSIENT = 6000
N_STEPS = 1000
P_MAX = 8

CLASS_ORDER = ["P1", "P2", "P4", "P8", "CHAOS", "DECAY"]
COLORS = {"P1": "#ffd166", "P2": "#06d6a0", "P4": "#118ab2",
          "P8": "#ef476f", "CHAOS": "#2b2d42", "DECAY": "#adb5bd"}


def run_grid(rs, es):
    grid = np.zeros((len(es), len(rs)), dtype="U8")
    mp_grid = np.zeros((len(es), len(rs)), dtype=int)
    d4_grid = np.full((len(es), len(rs)), np.nan)
    for i, e in enumerate(es):
        for j, r in enumerate(rs):
            x = M.simulate_cml(r, e, N, n_steps=N_STEPS, transient=N_TRANSIENT)
            sig = M.minimal_period_signature(x, p_max=P_MAX, tol=1e-7)
            grid[i, j] = sig["classification"]
            mp_grid[i, j] = int(sig["min_period"]) if sig["min_period"] else -1
            d4_grid[i, j] = sig["d"][4]
    return grid, mp_grid, d4_grid


def class_extents(grid, es, rs):
    out = {}
    for c in CLASS_ORDER:
        ys, xs = np.where(grid == c)
        if len(xs) == 0:
            out[c] = None
            continue
        out[c] = {
            "count": int(len(xs)),
            "r_min": float(rs[xs.min()]), "r_max": float(rs[xs.max()]),
            "eps_min": float(es[ys.min()]), "eps_max": float(es[ys.max()]),
        }
    return out


if __name__ == "__main__":
    rs = np.round(np.arange(3.820, 3.981, 0.006), 4)   # 28 values
    es = np.round(np.arange(0.118, 0.1581, 0.005), 4)   # 9 values
    grid, mp_grid, d4_grid = run_grid(rs, es)

    ext = class_extents(grid, es, rs)
    n_tot = grid.size
    counts = {c: int((grid == c).sum()) for c in CLASS_ORDER}
    print("grid: {}x{} = {} points".format(len(rs), len(es), n_tot))
    for c in CLASS_ORDER:
        print("  {:6s}: {:3d} ({:5.1f}%)  {}".format(
            c, counts[c], 100 * counts[c] / n_tot, ext.get(c)))

    # ---- figure: class map + eps-slice at reference r ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    class_names = ["P1", "P2", "P4", "P8", "CHAOS", "DECAY"]
    codes = np.vectorize(lambda c: class_names.index(c)
                         if c in class_names else 5)(grid)
    cmap = ListedColormap([COLORS[c] for c in class_names])
    im = ax.imshow(codes, origin="lower", aspect="auto",
                   extent=[rs[0], rs[-1], es[0], es[-1]],
                   cmap=cmap, vmin=0, vmax=len(class_names) - 1)
    ax.set_xlabel("r (logistic nonlinearity)")
    ax.set_ylabel("eps (coupling)")
    ax.set_title("CML period stratification  (N=120, p_max=8)")
    for k, c in enumerate(class_names):
        ax.plot([], [], "s", color=COLORS[c],
                label="{} ({} pts)".format(c, counts[c]))
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    # mark reference interior point
    ax.plot(3.870, 0.136, "o", mfc="none", mec="white", mew=2, ms=10,
            label="reference P4 interior")
    ax.plot(3.925, 0.148, "X", mfc="none", mec="#ef476f", mew=2, ms=10,
            label="P8 edge")

    ax = axes[1]
    # d4 residual surface on log scale for the tongue region
    d4_plot = -np.log10(np.clip(d4_grid, 1e-9, None))
    im2 = ax.imshow(d4_plot, origin="lower", aspect="auto",
                    extent=[rs[0], rs[-1], es[0], es[-1]],
                    cmap="inferno")
    ax.set_xlabel("r (logistic nonlinearity)")
    ax.set_ylabel("eps (coupling)")
    ax.set_title("-log10(d_4)  (darker = P4/P8 closer)")
    cb = fig.colorbar(im2, ax=ax)
    cb.set_label("-log10(d_4)")

    fig.tight_layout()
    out_png = "p4_p8_tongue_map.png"
    fig.savefig(out_png, dpi=150)
    print("saved:", out_png)

    # ---- JSON for dossier / Stage-2 targeting ----
    payload = {
        "grid": {"rs": rs.tolist(), "es": es.tolist(),
                 "N": N, "n_steps": N_STEPS, "transient": N_TRANSIENT,
                 "p_max": P_MAX, "tol": 1e-7},
        "classifications": grid.astype(str).tolist(),
        "min_periods": mp_grid.tolist(),
        "d4_residual": d4_grid.tolist(),
        "class_extents": ext,
        "counts": counts,
        "reference_point": {"r": 3.870, "eps": 0.136, "N": 120, "class": "P4"},
        "p8_edge_point": {"r": 3.925, "eps": 0.148, "class": "P8"},
    }
    with open("p4_p8_tongue_map_data.json", "w") as f:
        json.dump(payload, f, indent=2)
    print("saved: p4_p8_tongue_map_data.json")
