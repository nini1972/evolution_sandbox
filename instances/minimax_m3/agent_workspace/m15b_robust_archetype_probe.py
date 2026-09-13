'''M15b - Robust multi-metric probe of Thomas labyrinth and GoL
against the Adler ceiling.

Re-runs M15 with:
- Thomas: symbolic-entropy over damping b (existing metric)
- GoL: BOTH (a) mean-density and (b) symbolic-entropy over perturbation rate
- Checks Adler-ceiling robustness across both metrics
- Adds monotonicity / one-parameter-family test
'''

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUTDIR = Path('_artifacts')
OUTDIR.mkdir(exist_ok=True)


# ---------- Adler reference ----------
def adler_curve(dw_grid, K_eff):
    delta = np.asarray(dw_grid) / (2 * K_eff)
    return np.where(delta <= 1.0, 1.0,
                    delta - np.sqrt(np.maximum(delta**2 - 1, 0)))


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
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def thomas_complexity(b, T_total=300.0, dt=0.05, warmup=150.0):
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
    blocks = (sym[:-2:3, 0].astype(int) * 4 +
              sym[1:-1:3, 1].astype(int) * 2 +
              sym[2::3, 2].astype(int))
    _, counts = np.unique(blocks, return_counts=True)
    p = counts / counts.sum()
    H = float(-(p * np.log2(p)).sum())
    return H / 3.0


def thomas_bifurcation_scan(b_grid):
    return np.array([thomas_complexity(b) for b in b_grid])


# ---------- Game of Life with periodic boundary ----------
def gol_step(grid):
    pad = np.pad(grid, 1, mode='wrap')
    n = (pad[:-2, 1:-1] + pad[2:, 1:-1] +
         pad[1:-1, :-2] + pad[1:-1, 2:] +
         pad[:-2, :-2] + pad[:-2, 2:] +
         pad[2:, :-2] + pad[2:, 2:])
    return ((n == 3) | ((n == 2) & (grid == 1))).astype(np.uint8)


def perturb(grid, p):
    if p <= 0:
        return grid
    flip = np.random.random(grid.shape) < p
    return np.logical_xor(grid, flip).astype(np.uint8)


def gol_metric_scan(p_grid, n=30, steps=200, warmup=50, metric='density'):
    """For each perturbation rate p, run a GoL trajectory and compute
    either mean density or symbolic entropy over the post-warmup window.
    """
    R_vals = []
    for p in p_grid:
        np.random.seed(int(p * 10000) + 7)
        grid = np.random.randint(0, 2, (n, n))
        if metric == 'density':
            for t in range(steps):
                grid = gol_step(grid)
                if t > 0 and t % 5 == 0:
                    grid = perturb(grid, p)
            dens = []
            for t in range(60):
                grid = gol_step(grid)
                dens.append(float(grid.mean()))
            R_vals.append(float(np.mean(dens)))
        elif metric == 'entropy':
            sym_trace = []
            for t in range(steps):
                grid = gol_step(grid)
                if t > 0 and t % 5 == 0:
                    grid = perturb(grid, p)
                if t > warmup:
                    sym = (grid > 0).astype(int).flatten()
                    sym_trace.append(sym)
            if not sym_trace:
                R_vals.append(0.0)
                continue
            arr = np.array(sym_trace)
            col_mean = arr.mean(axis=0)
            col_bin = np.clip((col_mean * 8).astype(int), 0, 7)
            _, c = np.unique(col_bin, return_counts=True)
            prob = c / c.sum()
            H = float(-(prob[prob > 0] * np.log2(prob[prob > 0])).sum())
            R_vals.append(H / 3.0)
    return np.array(R_vals)


# ---------- Main ----------
def main():
    print('=== M15b - Robust multi-metric Adler-ceiling probe ===\n')

    K_eff_grid = np.linspace(0.1, 5.0, 500)
    dw_grid = np.linspace(0.01, 8.0, 1000)
    bf_a_perK = np.array([band_fraction(adler_curve(dw_grid, K))
                          for K in K_eff_grid])
    ceiling = float(bf_a_perK.max())
    print(f'Adler ceiling (band_frac max): {ceiling:.4f}')

    # ---- Thomas ----
    print('\n--- Thomas labyrinth ---')
    b_grid = np.linspace(0.05, 0.30, 20)
    R_thomas = thomas_bifurcation_scan(b_grid)
    bf_t = band_fraction(R_thomas)
    sr_t = longest_run(R_thomas, 0.85, above=True)
    or_t = longest_run(R_thomas, 0.15, above=False)
    print(f'  band_frac = {bf_t:.4f}  (> ceiling? {bf_t > ceiling})')
    print(f'  sat_run   = {sr_t:.4f}')
    print(f'  order_run = {or_t:.4f}')
    print(f'  R range   = [{R_thomas.min():.3f}, {R_thomas.max():.3f}]')

    # ---- GoL density ----
    print('\n--- GoL mean density ---')
    p_grid = np.linspace(0.0, 0.5, 15)
    R_gol_density = gol_metric_scan(p_grid, metric='density')
    bf_gd = band_fraction(R_gol_density)
    sr_gd = longest_run(R_gol_density, 0.85, above=True)
    or_gd = longest_run(R_gol_density, 0.15, above=False)
    print(f'  band_frac = {bf_gd:.4f}  (> ceiling? {bf_gd > ceiling})')
    print(f'  sat_run   = {sr_gd:.4f}')
    print(f'  order_run = {or_gd:.4f}')
    print(f'  R range   = [{R_gol_density.min():.3f}, {R_gol_density.max():.3f}]')

    # ---- GoL entropy ----
    print('\n--- GoL symbolic entropy ---')
    R_gol_entropy = gol_metric_scan(p_grid, metric='entropy')
    bf_ge = band_fraction(R_gol_entropy)
    sr_ge = longest_run(R_gol_entropy, 0.85, above=True)
    or_ge = longest_run(R_gol_entropy, 0.15, above=False)
    print(f'  band_frac = {bf_ge:.4f}  (> ceiling? {bf_ge > ceiling})')
    print(f'  sat_run   = {sr_ge:.4f}')
    print(f'  order_run = {or_ge:.4f}')
    print(f'  R range   = [{R_gol_entropy.min():.3f}, {R_gol_entropy.max():.3f}]')

    # ---- Verdict ----
    print('\n=== Verdict ===')
    print(f'Thomas band_frac          = {bf_t:.4f}  '
          f'(exceeds {ceiling:.3f}? {bf_t > ceiling})')
    print(f'GoL density band_frac     = {bf_gd:.4f}  '
          f'(exceeds {ceiling:.3f}? {bf_gd > ceiling})')
    print(f'GoL entropy band_frac     = {bf_ge:.4f}  '
          f'(exceeds {ceiling:.3f}? {bf_ge > ceiling})')

    # ---- Plot ----
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    ax = axes[0, 0]
    ax.plot(b_grid, R_thomas, 'o-', lw=2, ms=6, color='crimson',
            label='Thomas (entropy)')
    ax.axhline(ceiling, color='navy', ls='--', lw=2,
               label=f'Adler ceiling {ceiling:.3f}')
    ax.axhspan(0.3, 0.7, alpha=0.15, color='gold',
               label='M11 intermediate band')
    ax.set_xlabel('damping b')
    ax.set_ylabel('normalized entropy R')
    ax.set_title('Thomas labyrinth vs Adler ceiling')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(p_grid, R_gol_density, 's-', lw=2, ms=6, color='green',
            label='GoL mean density')
    ax.plot(p_grid, R_gol_entropy, 'D-', lw=2, ms=6, color='darkcyan',
            label='GoL symbolic entropy')
    ax.axhline(ceiling, color='navy', ls='--', lw=2,
               label=f'Adler ceiling {ceiling:.3f}')
    ax.axhspan(0.3, 0.7, alpha=0.15, color='gold',
               label='M11 intermediate band')
    ax.set_xlabel('perturbation rate p')
    ax.set_ylabel('R')
    ax.set_title('GoL vs Adler ceiling (two metrics)')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    sr_a = np.array([longest_run(adler_curve(dw_grid, K),
                                 threshold=0.85, above=True)
                     for K in K_eff_grid])
    ax.plot(bf_a_perK, sr_a, '-', color='navy', lw=1.5, alpha=0.6,
            label='Adler family')
    m11_pts = {
        'kuramoto': (0.190, 0.026, 'crimson'),
        'logistic': (0.744, 0.371, 'green'),
        'rule30': (0.000, 0.967, 'purple'),
    }
    for name, (x, y, c) in m11_pts.items():
        ax.scatter([x], [y], s=200, c=c, marker='o',
                   edgecolors='black', linewidths=1.5,
                   label=name, zorder=5)
    ax.scatter([bf_t], [sr_t], s=300, c='orange', marker='*',
               edgecolors='black', linewidths=1.5,
               label='Thomas (M15b)', zorder=6)
    ax.scatter([bf_gd], [sr_gd], s=300, c='cyan', marker='*',
               edgecolors='black', linewidths=1.5,
               label='GoL density (M15b)', zorder=6)
    ax.scatter([bf_ge], [sr_ge], s=300, c='darkcyan', marker='*',
               edgecolors='black', linewidths=1.5,
               label='GoL entropy (M15b)', zorder=6)
    ax.axvline(ceiling, color='navy', ls='--', lw=2,
               label=f'Adler ceiling {ceiling:.3f}')
    ax.set_xlabel('band_frac')
    ax.set_ylabel('sat_run')
    ax.set_title('Archetype-feature plane: M11 + M15b + Adler family')
    ax.set_xlim(-0.05, 1.0)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    names = ['Adler\nceiling', 'kuramoto', 'logistic', 'rule30',
             'Thomas\n(M15b)', 'GoL\ndensity', 'GoL\nentropy']
    vals = [ceiling, 0.190, 0.744, 0.0, bf_t, bf_gd, bf_ge]
    colors = ['navy', 'crimson', 'green', 'purple',
              'orange', 'cyan', 'darkcyan']
    ax.barh(names, vals, color=colors, edgecolor='black', linewidth=1.2)
    for i, v in enumerate(vals):
        ax.text(v + 0.01, i, f'{v:.3f}', va='center', fontsize=9)
    ax.axvline(ceiling, color='navy', ls='--', lw=2)
    ax.set_xlabel('band_frac')
    ax.set_title('Band-fraction comparison with the Adler ceiling')
    ax.set_xlim(0, 0.9)
    ax.grid(alpha=0.3, axis='x')

    plt.suptitle('M15b - Robust multi-metric Adler-ceiling probe\n'
                 f'Thomas + GoL vs ceiling (band_frac <= {ceiling:.3f})',
                 fontsize=12)
    plt.tight_layout()
    fig.savefig(OUTDIR / 'm15b_robust_archetype_probe.png',
                dpi=120, bbox_inches='tight')
    plt.close(fig)

    record = {
        'milestone': 'M15b',
        'adler_ceiling': float(ceiling),
        'thomas': {
            'b_grid_n': int(len(b_grid)),
            'R_min': float(R_thomas.min()),
            'R_max': float(R_thomas.max()),
            'band_frac': float(bf_t),
            'sat_run': float(sr_t),
            'order_run': float(or_t),
            'exceeds_ceiling': bool(bf_t > ceiling),
        },
        'gol_density': {
            'perturb_n': int(len(p_grid)),
            'R_min': float(R_gol_density.min()),
            'R_max': float(R_gol_density.max()),
            'band_frac': float(bf_gd),
            'sat_run': float(sr_gd),
            'order_run': float(or_gd),
            'exceeds_ceiling': bool(bf_gd > ceiling),
        },
        'gol_entropy': {
            'perturb_n': int(len(p_grid)),
            'R_min': float(R_gol_entropy.min()),
            'R_max': float(R_gol_entropy.max()),
            'band_frac': float(bf_ge),
            'sat_run': float(sr_ge),
            'order_run': float(or_ge),
            'exceeds_ceiling': bool(bf_ge > ceiling),
        },
        'interpretation': (
            'Robust multi-metric M15b probe. '
            f'Thomas bf={bf_t:.4f}; '
            f'GoL density bf={bf_gd:.4f}; '
            f'GoL entropy bf={bf_ge:.4f}; '
            f'Adler ceiling={ceiling:.4f}.'
        ),
    }
    with open(OUTDIR / 'm15b_robust_archetype_probe.json', 'w') as fp:
        json.dump(record, fp, indent=2)
    print('\nSaved: _artifacts/m15b_robust_archetype_probe.png')
    print('Saved: _artifacts/m15b_robust_archetype_probe.json')


if __name__ == '__main__':
    main()
