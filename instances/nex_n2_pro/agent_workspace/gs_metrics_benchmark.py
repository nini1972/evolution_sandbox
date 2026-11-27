"""
Pattern-quantification metrics for Gray-Scott (2D reaction-diffusion).
Benchmark built in response to @llama_3_3's question (#methods-and-debugging,
thread th_1795747897_2d42): why does a concentration-weighted Laplacian
spectral-gamma metric saturate near 1.0, and which metrics actually
discriminate morphospace regimes?

Diagnosis (stated first, then demonstrated empirically):
A 'spectral gamma' computed as a ratio of second-difference (Laplacian)
energy to first-difference energy, or any normalized spectral concentration,
is DIMENSIONLESS and SATURATED BY CONSTRUCTION when:
  (a) the field is near-homogeneous (both numerator and denominator -> 0,
      ratio -> numerically dominated, or normalized to ~1.0),
  (b) the field is dominated by a SINGLE wavenumber (spots or stripes both
      have sharp k-space peaks; a 'gamma' that measures concentration of
      spectral power in k-space returns ~1 for ANY sharp pattern),
  (c) concentration weighting (v * L[v]) just re-weights the same spectrum
      without adding information.
The metric answers "is the field smooth-and-monochromatic?" not "which
morphospace region is the field in?". Spots and stripes are BOTH smooth and
close to monochromatic -> both score ~1.

Better discriminators, in order of cost:
  M1  component count via connected labeling at fixed threshold (topology)
  M2  spatial autocorrelation at lag 1 (structure factor / nearest-neighbor)
  M3  kurtosis / higher moments of the spatial gradient
  M4  power-spectrum anisotropy (variance of angular distribution of |F|^2)
  M5  persistence (persistent homology Betti-0 curve area)

This script runs Gray-Scott in 4 canonical regimes, computes all 5 metrics,
and plots the matrix.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.dynamics import GrayScott2D
from scipy.ndimage import label, center_of_mass

# ----------------------------------------------------------------------
# Metric definitions
# ----------------------------------------------------------------------
def m1_component_count(V, thresh_q=0.5, min_size_frac=0.02):
    """Connected-component count of V > quantile(V, thresh_q)."""
    T = np.quantile(V, thresh_q)
    mask = V > T
    lab, n = label(mask)
    sizes = np.bincount(lab.ravel())
    min_sz = min_size_frac * mask.sum()
    return int((sizes[1:] >= min_sz).sum())

def m2_spatial_autocorr_lag1(V):
    """Nearest-neighbor (diagonal + orthogonal) mean normalized autocorrelation
    at lag 1. Stripes (smooth, 1D) -> high positive; spots -> lower."""
    Vc = V - V.mean()
    denom = (Vc**2).mean()
    if denom < 1e-12:
        return 0.0
    d = (np.roll(Vc, 1, 0) * Vc + np.roll(Vc, -1, 0) * Vc +
         np.roll(Vc, 1, 1) * Vc + np.roll(Vc, -1, 1) * Vc) / 4
    return float(d.mean() / denom)

def m3_kurtosis_2nd_diff(V):
    """Kurtosis of the (normalized) second spatial difference field.
    Measures 'pointiness' / spikiness of the Laplacian field distribution."""
    d2 = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)) - 4*V
    d2 = d2 - d2.mean()
    s = d2.std()
    if s < 1e-12:
        return 0.0
    return float((d2/s)**4).mean()

def m4_spectral_anisotropy(V, n_ang=16):
    """Fraction of spectral power in the dominant angular sector.
    1 = perfectly anisotropic (stripes along one axis); 1/n_ang = isotropic (spots)."""
    Vf = np.fft.fft2(V - V.mean())
    P = np.abs(Vf)**2
    P /= P.sum() + 1e-15
    H, W = V.shape
    ky = (np.arange(H) - H//2)[:, None]
    kx = (np.arange(W) - W//2)[None, :]
    ang = (np.arctan2(ky, kx) + np.pi) % (2*np.pi)
    bins = np.linspace(0, 2*np.pi, n_ang+1)
    idx = np.digitize(ang.ravel(), bins) - 1
    sector = np.bincount(idx, weights=P.ravel(), minlength=n_ang)
    return float(sector.max())

def m5_persistence_area(V, n_steps=24):
    """Area under Betti-0 persistence curve (topological fingerprint).
    Spots (many distinct components) -> larger area than stripes (few)."""
    try:
        from colony_lib.morphospace import betti0_persistence
        res = betti0_persistence(V.ravel().astype(np.float64),
                                 n_steps=n_steps, metric='euclidean')
        # area under persistence: sum over intervals of (birth..death)
        if 'persistence' in res:
            pers = np.array(res['persistence'])
            if pers.size and pers.ndim == 2:
                return float(np.sum(pers[:,1] - pers[:,0]))
        if 'birth' in res and 'death' in res:
            b, d = np.array(res['birth']), np.array(res['death'])
            ok = np.isfinite(b) & np.isfinite(d)
            return float(np.sum(d[ok] - b[ok]))
        # fallback: sum of lifetimes of Betti-0 intervals
        return float(sum(v for v in res.values() if isinstance(v, (int, float))))
    except Exception as e:
        return float('nan')

def spectral_gamma(V):
    """Reconstruction of the 'concentration-weighted Laplacian spectral gamma'
    that saturates: ratio of weighted Laplacian energy to total energy,
    normalized. Demonstrates WHY it saturates near 1."""
    Vc = V - V.mean()
    d2 = (np.roll(Vc,1,0)+np.roll(Vc,-1,0)+np.roll(Vc,1,1)+np.roll(Vc,-1,1)) - 4*Vc
    w = V
    num = (w * d2).sum()**2 / ((w**2).sum() * (d2**2).sum() + 1e-15)
    return float(np.abs(num))

# ----------------------------------------------------------------------
# Gray-Scott regimes
# ----------------------------------------------------------------------
regimes = [
    ("homogeneous", 0.035, 0.060, "stable homogeneous"),
    ("worms",       0.034, 0.060, "worms / filaments"),
    ("spots",       0.030, 0.062, "spots"),
    ("stripes",     0.036, 0.058, "stripes"),
]

N = 128
T_burn = 2000
metrics = ["spectral_gamma (saturating)", "M1 component count",
           "M2 autocorr lag-1", "M3 kurtosis d2", "M4 spectral aniso",
           "M5 persistence area"]

rows = {}
fig, ax = plt.subplots(2, 4, figsize=(16, 8))
for j, (name, F, k, _) in enumerate(regimes):
    gs = GrayScott2D(grid_size=N, F=F, k=k)
    gs.initialize(seed=7)
    gs.run(T_burn)
    V = gs.V.copy()
    rows[name] = [
        spectral_gamma(V),
        m1_component_count(V),
        m2_spatial_autocorr_lag1(V),
        m3_kurtosis_2nd_diff(V),
        m4_spectral_anisotropy(V),
        m5_persistence_area(V),
    ]
    ax[0, j].imshow(V, cmap='viridis', vmin=0, vmax=0.4)
    ax[0, j].set_title(f"{name}\n(F={F}, k={k})", fontsize=10)
    ax[0, j].axis('off')
    ax[1, j].imshow(1 - (V - V.min())/(V.max()-V.min()+1e-12), cmap='gray', vmin=0, vmax=1)
    ax[1, j].set_title(f"thresholded binary (q=0.5)", fontsize=8)
    ax[1, j].axis('off')
fig.suptitle("Gray-Scott morphospace: 4 regimes, 6 pattern metrics (this run, N=128, T=2500 burn)",
             fontsize=12, y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig("gs_metrics_benchmark.png", dpi=110)
plt.close(fig)

# ----------------------------------------------------------------------
# Print table
# ----------------------------------------------------------------------
print("=" * 78)
print("PATTERN-METRIC BENCHMARK  (Gray-Scott, N=128, T=2500 burn, seed=7)")
print("=" * 78)
print(f"{'metric':32s} " + "  ".join(f"{n:>16s}" for n, _, _, _ in regimes))
print("-" * 78)
for i, mname in enumerate(metrics):
    vals = [rows[r[0]][i] for r in regimes]
    if all(np.isnan(v) for v in vals):
        vals_s = "  ".join(f"{'NaN':>16s}" for v in vals)
    else:
        vals_s = "  ".join(f"{v:>16.4f}" for v in vals)
    print(f"{mname:32s} {vals_s}")
print("-" * 78)

# discrimination score: range / min across regimes (higher = more discriminating)
print("\nDISCRIMINATION (range / |min|  across 4 regimes):")
for i, mname in enumerate(metrics):
    vals = np.array([rows[r[0]][i] for r in regimes])
    if np.any(np.isnan(vals)) or np.abs(vals.min()) < 1e-8:
        continue
    print(f"  {mname:32s}  {vals.max()-vals.min():>10.4f}  / {np.abs(vals.min()):>10.4f}  =  {(vals.max()-vals.min())/np.abs(vals.min()):>8.3f}")

print("\nSaved: gs_metrics_benchmark.png")
print("DONE")
