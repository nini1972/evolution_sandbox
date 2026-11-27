"""SYN-062 :: Betti-0 component-count sweep for Gray-Scott pattern discrimination.

WHY THIS FILE EXISTS
--------------------
`colony_lib.morphospace.betti0_persistence` returns a flat array of 1s when fed a
PRE-BINARIZED field (e.g. `u > 0.5`). That is a *method* artifact, not topology:
a binary image has no continuous structure left to *filter* over, so any
sub/super-level filtration sees exactly one connected component at every epsilon.

The fix (two options):
  (A) Single-threshold component count on the RAW field  -> fastest discriminator.
      spots  -> MANY components (one per dot)
      labyrinth/stripes -> FEW components (long connected bands)
  (B) Quantile sweep of the RAW field  -> a genuine persistence-style curve that
      actually varies (n_comp rises as the threshold climbs the value range).

Plug your real GrayScott2D `v` (or `u`) snapshot in place of the demo fields.
"""

import numpy as np
from scipy import ndimage


def count_components(field, thr, structure=None):
    """Number of 8-connected components of `field > thr`."""
    if structure is None:
        structure = np.ones((3, 3), dtype=int)  # 8-connectivity
    lab, n = ndimage.label(field > thr, structure=structure)
    return int(n)


def betti0_quantile_sweep(field, qs=(0.30, 0.50, 0.70, 0.90)):
    """Component count as the threshold sweeps the quantiles of the RAW field.

    Spots: n_comp grows steeply with q (each blob becomes its own island).
    Labyrinth: n_comp stays low even at high q (bands stay connected).
    Returns {quantile: n_components}. Genuinely varies -- no flat-1s trap.
    """
    out = {}
    for q in qs:
        thr = float(np.quantile(field, q))
        out[round(q, 2)] = count_components(field, thr)
    return out


def anisotropy_ratio(field, thr):
    """Spectral anisotropy gamma* = lambda2/lambda_max of the binary mask graph.

    Spots -> near-isotropic (gamma* ~ 0.5+); stripes -> strongly anisotropic
    (gamma* -> small). Use as a SECOND axis alongside component count.
    """
    mask = (field > thr).astype(float)
    if mask.sum() == 0:
        return np.nan
    ys, xs = np.where(mask)
    pts = np.stack([xs, ys], axis=1).astype(float)
    pts -= pts.mean(0)
    cov = pts.T @ pts
    ev = np.linalg.eigvalsh(cov)
    ev = np.sort(ev)
    return float(ev[1] / ev[0]) if ev[0] > 0 else np.nan


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    x = np.linspace(0, 1, 128, endpoint=False)
    X, Y = np.meshgrid(x, x)

    # Synthetic SPOTS: isolated circular blobs.
    spots = np.zeros((128, 128))
    for cx, cy in [(0.3, 0.3), (0.7, 0.35), (0.45, 0.7), (0.8, 0.8)]:
        spots += np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / 0.002)
    spots += rng.normal(0, 0.02, (128, 128))

    # Synthetic STRIPES: sinusoidal bands.
    stripes = 0.5 * (np.sin(8 * np.pi * (X + Y)) > 0) + rng.normal(0, 0.02, (128, 128))

    for name, f in [("SPOTS", spots), ("STRIPES", stripes)]:
        print(f"\n=== {name} ===")
        print("  quantile sweep:", betti0_quantile_sweep(f))
        print("  n_comp @ thr=0.12:", count_components(f, 0.12))
        print("  anisotropy @ thr=0.12:", round(anisotropy_ratio(f, 0.12), 4))
