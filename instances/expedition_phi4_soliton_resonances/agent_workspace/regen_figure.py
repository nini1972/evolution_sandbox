#!/usr/bin/env python3
"""Regenerate phi4_velocity_windows.png from a phi4_resonance_data.json artifact.

Decouples the figure step from the sweep: if the World C job's figure step
fails (the submitted copy contains a plt.use('Agg') typo), the JSON metrics
survive and this script rebuilds the diagnostic figure locally with the
correct matplotlib.use('Agg') backend.

Usage: python regen_figure.py [path/to/phi4_resonance_data.json] [out.png]
"""
import sys, json, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def make_figure(results, windows, outpath):
    v_in = np.array([r["v_in"] for r in results])
    vf = np.array([r["v_final"] for r in results])
    esc = np.array([r["escaped"] for r in results], dtype=bool)
    ew = np.array([r["E_wobble"] for r in results])
    nb = np.array([r["n_bounces"] for r in results])
    drift = np.array([r["drift"] for r in results])

    fig, ax = plt.subplots(4, 1, figsize=(10, 15), sharex=True)

    # Panel 1: v_final vs v_in (the resonance staircase)
    ax[0].scatter(v_in[esc], vf[esc], c="crimson", s=30, zorder=5, label="escape")
    ax[0].scatter(v_in[~esc], vf[~esc], c="steelblue", s=18, marker="x",
                  label="capture/bion")
    for i, (a, b) in enumerate(windows):
        ax[0].axvspan(a, b, color="gold", alpha=0.18)
        ax[0].text(0.5 * (a + b), 0.02, f"W{i+1}", ha="center", fontsize=9)
    ax[0].axvline(0.2575, color="k", ls="--", lw=0.8, label=r"$v_c \approx 0.2575$")
    ax[0].set_ylabel(r"$v_{final}$")
    ax[0].set_title(r"$\phi^4$ kink-antikink resonance escape windows "
                    r"(Verlet, N=1024, L=200, dt=0.02)")
    ax[0].legend(loc="upper left", fontsize=9)
    ax[0].grid(alpha=0.3)

    # Panel 2: bounce count
    ax[1].scatter(v_in, nb, c="darkgreen", s=22)
    ax[1].set_ylabel("bounce count")
    ax[1].grid(alpha=0.3)

    # Panel 3: wobble energy
    ax[2].scatter(v_in[esc], ew[esc], c="crimson", s=30, zorder=5)
    ax[2].scatter(v_in[~esc], ew[~esc], c="steelblue", s=18, marker="x")
    for a, b in windows:
        ax[2].axvspan(a, b, color="gold", alpha=0.18)
    ax[2].set_ylabel(r"$E_{wobble}$")
    ax[2].grid(alpha=0.3)

    # Panel 4: energy conservation audit
    ax[3].semilogy(v_in, np.maximum(drift, 1e-16), "o", ms=3, c="purple")
    ax[3].set_ylabel(r"$|\Delta E|/E_0$")
    ax[3].set_xlabel(r"$v_{in}$")
    ax[3].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print(f"[regen_figure] saved {outpath} ({len(results)} points, "
          f"{len(windows)} windows)")


def main():
    # Default search order: local dir, world_c_results, shared reports
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        cands = (["phi4_resonance_data.json"]
                 + sorted(glob.glob("world_c_results/**/phi4_resonance_data.json",
                                    recursive=True))
                 + sorted(glob.glob("../../shared_space/world_c/reports/**/"
                                    "phi4_resonance_data.json", recursive=True)))
        if not cands:
            sys.exit("[regen_figure] no phi4_resonance_data.json found")
        path = cands[0]
    out = sys.argv[2] if len(sys.argv) > 2 else "phi4_velocity_windows.png"

    with open(path) as f:
        data = json.load(f)
    results, windows = data["results"], data["windows"]
    print(f"[regen_figure] loaded {len(results)} results, "
          f"windows={windows}")
    make_figure(results, windows, out)

    # Also re-derive windows from the raw escape flags as a consistency check
    v = np.array([r["v_in"] for r in results])
    esc = np.array([r["escaped"] for r in results], dtype=bool)
    o = np.argsort(v)
    v, esc = v[o], esc[o]
    w = []
    inw = False
    for i in range(len(v)):
        if esc[i] and not inw:
            a = v[i]; inw = True
        elif (not esc[i]) and inw:
            w.append((float(a), float(v[i - 1]))); inw = False
    if inw:
        w.append((float(a), float(v[-1])))
    print("[regen_figure] recomputed windows from flags:")
    for i, (a, b) in enumerate(w):
        print(f"  W{i+1}: [{a:.4f}, {b:.4f}]  width={b - a:.4f}")


if __name__ == "__main__":
    main()
