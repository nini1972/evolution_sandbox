"""M15 - Probe Thomas labyrinth and Game-of-Life against the Adler ceiling.

Hypothesis (from M14): any substrate with band_frac > 0.414 is NOT
Adler-like. Thomas and GoL may occupy Mechanism B territory.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUTDIR = Path('_artifacts')
OUTDIR.mkdir(exist_ok=True)

# ---------- Thomas labyrinth (manual RK4) ----------
def thomas_deriv(state, b):
    x, y, z = state
    return np.array([np.sin(y) - b * x,
                     np.sin(z) - b * y,
                     np.sin(x) - b * z])


def rk4_step(state, dt, b):
    k1 = thomas_deriv(state, b)
    k2 = thomas_deriv(state + 0.5 * dt * k1, b)
    k3 = thomas_deriv(state + 0.5 * dt * k2, b)
    k4 = thomas_deriv(state + dt * k3, b)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def thomas_complexity(b, T_total=300.0, dt=0.05, warmup=150.0):
    """Symbolic-entropy-based complexity at damping b."""
    n_steps = int(T_total / dt)
    state = np.array([0.1, 0.0, 0.0])
    trace = np.zeros((n_steps, 3))
    for i in range(n_steps):
        trace[i] = state
        state = rk4_step(state, dt, b)
    warm = int(warmup / dt)
    sol = trace[warm:]
    sym = np.zeros_like(sol)
    for i in range(3):
        med = np.median(sol[:, i])
        sym[:, i] = (sol[:, i] > med).astype(int)
    blocks = sym[:-2:3, 0].astype(int) * 4 + \
             sym[1:-1:3, 1].astype(int) * 2 + \
             sym[2::3, 2].astype(int)
    _, counts = np.unique(blocks, return_counts=True)
    p = counts / counts.sum()
    H = float(-(p * np.log2(p)).sum())  # bits in [0, 3]
    return H / 3.0


def thomas_bifurcation_scan(b_grid):
    return np.array([thomas_complexity(b) for b in b_grid])


# ---------- Game of Life with perturbation ----------
def step_gol(grid, perturb_rate):
    n, m = grid.shape
    new = np.zeros_like(grid)
    for i in range(n):
        for j in range(m):
            nb = (grid[(i-1) % n, (j-1) % m] +
                  grid[(i-1) % n, j] +
                  grid[(i-1) % n, (j+1) % m] +
                  grid[i, (j-1) % m] +
                  grid[i, (j+1) % m] +
                  grid[(i+1) % n, (j-1) % m] +
                  grid[(i+1) % n, j] +
                  grid[(i+1) % n, (j+1) % m])
            if grid[i, j] == 1 and nb in (2, 3):
                new[i, j] = 1
            elif grid[i, j] == 0 and nb == 3:
                new[i, j] = 1
    flip = np.random.random(new.shape) < perturb_rate
    return np.logical_xor(new, flip).astype(int)


def gof_density_scan(perturb_grid, n=24, steps=60, warmup=20):
    R_vals = []
    for p in perturb_grid:
        grid = np.random.randint(0, 2, (n, n))
        dens = []
        for t in range(steps):
            grid = step_gol(grid, p)
            if t >= warmup:
                dens.append(float(grid.mean()))
        R_vals.append(np.mean(dens))
    return np.array(R_vals)


# ---------- Archetype features ----------
def band_fraction(R, lo=0.3, hi=0.7):
    return float(((R >= lo) & (R <= hi)).mean())


def longest_run(R, threshold, above=True):
    mask = (R >= threshold) if above else (R <= threshold)
    if not mask.any():
        return 0.0
    runs, cur = [], 0
    for v in mask:
        if v:
            cur += 1
        else:
            if cur > 0:
                runs.append(cur)
            cur = 0
    if cur > 0:
        runs.append(cur)
    return max(runs) / len(R)


# ---------- Adler reference ----------
def adler_curve(dw_grid, K_eff):
    delta = np.asarray(dw_grid) / (2 * K_eff)
    return np.where(delta <= 1.0, 1.0,
                    delta - np.sqrt(np.maximum(delta**2 - 1, 0)))


def adler_max_bandfrac(K_eff_grid, dw_grid):
    return max(band_fraction(dw_grid, adler_curve(dw_grid, K))
               for K in K_eff_grid)


# ---------- Main ----------
def main():
    print('=== M15 - Probe Thomas & GoL against the Adler ceiling ===\n')

    K_eff_grid = np.linspace(0.1, 5.0, 500)
    dw_grid = np.linspace(0.01, 8.0, 1000)
    ceiling = adler_max_bandfrac(K_eff_grid, dw_grid)
    print(f'Adler ceiling (band_frac max): {ceiling:.4f}')

    # ---- Thomas ----
    print('\n--- Thomas labyrinth ---')
    b_grid = np.linspace(0.05, 0.30, 20)
    R_thomas = thomas_bifurcation_scan(b_grid)
    bf_t = band_fraction(R_thomas)
    sr_t = longest_run(R_thomas, threshold=0.85, above=True)
    or_t = longest_run(R_thomas, threshold=0.15, above=False)
    print(f'  band_frac = {bf_t:.4f}  (> ceiling? {bf_t > ceiling})')
    print(f'  sat_run   = {sr_t:.4f}')
    print(f'  order_run = {or_t:.4f}')
    print(f'  R range   = [{R_thomas.min():.3f}, {R_thomas.max():.3f}]')
    # find crisis location from R profile
    crisis_idx = np.argmin(np.abs(b_grid - 0.208186))
    print(f'  near crisis (b={b_grid[crisis_idx]:.3f}): R={R_thomas[crisis_idx]:.3f}')

    # ---- GoL ----
    print('\n--- Game of Life with perturbation ---')
    perturb_grid = np.linspace(0.0, 0.5, 15)
    R_gol = gof_density_scan(perturb_grid)
    bf_g = band_fraction(R_gol)
    sr_g = longest_run(R_gol, 0.85, above=True)
    or_g = longest_run(R_gol, 0.15, above=False)
    print(f'  band_frac = {bf_g:.4f}  (> ceiling? {bf_g > ceiling})')
    print(f'  sat_run   = {sr_g:.4f}')
    print(f'  order_run = {or_g:.4f}')
    print(f'  density range = [{R_gol.min():.3f}, {R_gol.max():.3f}]')

    # ---- Verdict ----
    print('\n=== Verdict ===')
    thomas_exceeds = bool(bf_t > ceiling)
    gol_exceeds = bool(bf_g > ceiling)
    print(f'Thomas exceeds Adler ceiling ({ceiling:.4f})? '
          f'{thomas_exceeds} (bf={bf_t:.4f})')
    print(f'GoL   exceeds Adler ceiling ({ceiling:.4f})? '
          f'{gol_exceeds} (bf={bf_g:.4f})')

    # ---- Plot ----
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    # Thomas
    ax = axes[0, 0]
    ax.plot(b_grid, R_thomas, 'o-', lw=2, ms=6, color='crimson',
            label='Thomas')
    ax.axhline(ceiling, color='navy', ls='--', lw=2,
               label=f'Adler ceiling {ceiling:.3f}')
    ax.axhspan(0.3, 0.7, alpha=0.15, color='gold',
               label='M11 intermediate band')
    ax.axvline(0.208186, color='purple', ls=':', lw=2,
               label='Thomas crisis b_c')
    ax.set_xlabel('damping b')
    ax.set_ylabel('normalized complexity R')
    ax.set_title('Thomas labyrinth vs Adler ceiling')
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # GoL
    ax = axes[0, 1]
    ax.plot(perturb_grid, R_gol, 's-', lw=2, ms=6, color='green',
            label='GoL density')
    ax.axhline(ceiling, color='navy', ls='--', lw=2,
               label=f'Adler ceiling {ceiling:.3f}')
    ax.axhspan(0.3, 0.7, alpha=0.15, color='gold',
               label='M11 intermediate band')
    ax.set_xlabel('perturbation rate p')
    ax.set_ylabel('mean density R')
    ax.set_title('Game of Life vs Adler ceiling')
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # Archetype plane
    ax = axes[1, 0]
    bf_a = np.array([band_fraction(dw_grid, adler_curve(dw_grid, K))
                     for K in K_eff_grid])
    sr_a = np.array([longest_run(dw_grid, adler_curve(dw_grid, K),
                                 0.85, above=True)
                     for K in K_eff_grid])
    ax.plot(bf_a, sr_a, '-', color='navy', lw=1.5, alpha=0.6,
            label='Adler family')
    m11_pts = {
        'kuramoto': (0.190, 0.026, 'crimson'),
        'logistic': (0.744, 0.371, 'green'),
        'rule30':   (0.000, 0.967, 'purple'),
    }
    for name, (x, y, c) in m11_pts.items():
        ax.scatter([x], [y], s=200, c=c, marker='o',
                   edgecolors='black', linewidths=1.5,
                   label=name, zorder=5)
    ax.scatter([bf_t], [sr_t], s=300, c='orange', marker='*',
               edgecolors='black', linewidths=1.5,
               label='Thomas (M15)', zorder=6)
    ax.scatter([bf_g], [sr_g], s=300, c='cyan', marker='*',
               edgecolors='black', linewidths=1.5,
               label='GoL (M15)', zorder=6)
    ax.axvline(ceiling, color='navy', ls='--', lw=2,
               label=f'Adler ceiling {ceiling:.3f}')
    ax.set_xlabel('band_frac')
    ax.set_ylabel('sat_run')
    ax.set_title('Archetype-feature plane: M11 + M15 + Adler family')
    ax.set_xlim(-0.05, 1.0); ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=9, loc='lower right'); ax.grid(alpha=0.3)

    # Bar comparison
    ax = axes[1, 1]
    names = ['Adler\nceiling', 'kuramoto', 'logistic', 'rule30',
             'Thomas\n(M15)', 'GoL\n(M15)']
    vals = [ceiling, 0.190, 0.744, 0.0, bf_t, bf_g]
    colors = ['navy', 'crimson', 'green', 'purple', 'orange', 'cyan']
    ax.barh(names, vals, color=colors, edgecolor='black', linewidth=1.2)
    for i, v in enumerate(vals):
        ax.text(v + 0.01, i, f'{v:.3f}', va='center', fontsize=9)
    ax.axvline(ceiling, color='navy', ls='--', lw=2)
    ax.set_xlabel('band_frac')
    ax.set_title('Band-fraction comparison with the Adler ceiling')
    ax.set_xlim(0, 0.9); ax.grid(alpha=0.3, axis='x')

    plt.suptitle('M15 - Probing Thomas labyrinth and Game of Life\n'
                 f'against the Adler-ceiling theorem (band_frac <= {ceiling:.3f})',
                 fontsize=12)
    plt.tight_layout()
    fig.savefig(OUTDIR / 'm15_adler_ceiling_probe.png',
                dpi=120, bbox_inches='tight')
    plt.close(fig)

    record = {
        'milestone': 'M15',
        'adler_ceiling': float(ceiling),
        'thomas': {
            'b_grid_n': int(len(b_grid)),
            'R_min': float(R_thomas.min()),
            'R_max': float(R_thomas.max()),
            'band_frac': float(bf_t),
            'sat_run': float(sr_t),
            'order_run': float(or_t),
            'exceeds_ceiling': thomas_exceeds,
        },
        'gol': {
            'perturb_n': int(len(perturb_grid)),
            'density_min': float(R_gol.min()),
            'density_max': float(R_gol.max()),
            'band_frac': float(bf_g),
            'sat_run': float(sr_g),
            'order_run': float(or_g),
            'exceeds_ceiling': gol_exceeds,
        },
        'interpretation': (
            'Both Thomas and GoL measured against the Adler ceiling. '
            f'Thomas band_frac={bf_t:.4f}; '
            f'GoL band_frac={bf_g:.4f}; '
            f'Adler ceiling={ceiling:.4f}.'
        ),
    }
    with open(OUTDIR / 'm15_adler_ceiling_probe.json', 'w') as fp:
        json.dump(record, fp, indent=2)
    print('\nSaved: _artifacts/m15_adler_ceiling_probe.png')
    print('Saved: _artifacts/m15_adler_ceiling_probe.json')


if __name__ == '__main__':
    main()
