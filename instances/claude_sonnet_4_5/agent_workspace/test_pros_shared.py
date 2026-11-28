"""Empirical audit of the SHARED gemini_pro implementation
(../../shared_space/pros_surrogate.py) — static analysis was inconclusive.

Checks, on realistic smooth random fields:
  1. corr(K, v) == 0 and PSD match for square/even grids (the published case).
  2. Edge shapes: odd H, odd W, non-square (H != W), 1D odd N.
  3. Non-zero-mean v (does centering/return keep corr at eps?).
  4. THE SILENT-CLIP PATH: the script does `val = clip(val,-1,1)` when |val|>1
     (unsolvable). If that triggers, the delta no longer zeroes <K,v> and corr
     becomes nonzero *without any warning*. Force near-unsolvable cases
     (tiny/DC-dominated fields where S_fixed ~ R) and see if corr survives.
  5. Variance: does K keep std(K)/std(v) == 1?
"""
import sys, importlib.util, numpy as np

spec = importlib.util.spec_from_file_location("pros", "../../shared_space/pros_surrogate.py")
pros = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pros)

rng = np.random.default_rng(7)

def smooth_field(shape, xi=8.0, zero_mean=True):
    sh = np.array(shape)
    k = [np.fft.fftfreq(s) * s for s in sh]
    KX = np.meshgrid(*k, indexing="ij")
    K2 = sum(ki**2 for ki in KX)
    psd = np.exp(-K2 / (2 * (2 * np.pi / xi) ** 2)) / (1 + K2)
    psd.flat[0] = 0.0
    ph = rng.uniform(0, 2 * np.pi, shape)
    f = np.real(np.fft.ifftn(np.sqrt(psd) * np.exp(1j * ph)))
    if zero_mean:
        f -= f.mean()
    return f / f.std()

results = []
def record(name, corr, psd_err, std_ratio, extra=""):
    ok = abs(corr) < 1e-12 and psd_err < 1e-10
    results.append((name, abs(corr), psd_err, std_ratio, ok, extra))
    print(f"{'PASS' if ok else 'FAIL'}  {name:46s} |corr|={abs(corr):.2e} psd={psd_err:.2e} stdK/stdv={std_ratio:.6f} {extra}")

print("=== 1-3: shape & mean edge cases (5 seeds each) ===")
shapes_2d = {"64x64 (published)": (64, 64), "63x64 (odd H)": (63, 64),
             "64x65 (odd W)": (64, 65), "50x96 (non-square)": (50, 96)}
for name, shp in shapes_2d.items():
    c, p, s = 0.0, 0.0, 0.0
    for t in range(5):
        v = smooth_field(shp)
        K = pros.generate_pros_2d(v, seed=100 + t)
        c = max(c, abs(np.corrcoef(v.ravel(), K.ravel())[0, 1]))
        V = np.abs(np.fft.rfft2(v - v.mean())); KK = np.abs(np.fft.rfft2(K - K.mean()))
        p = max(p, np.max(np.abs(KK - V)) / max(V.max(), 1e-300))
        s = max(s, K.std() / v.std())
    record(f"2D {name}", c, p, s)

# nonzero-mean v
v = smooth_field((64, 64), zero_mean=False) * 3.0 + 7.0
K = pros.generate_pros_2d(v, seed=11)
record("2D nonzero-mean v (+7 offset, x3 scale)",
       np.corrcoef(v.ravel(), K.ravel())[0, 1],
       np.max(np.abs(np.abs(np.fft.rfft2(K - K.mean())) -
                     np.abs(np.fft.rfft2(v - v.mean())))) / np.abs(np.fft.rfft2(v - v.mean())).max(),
       K.std() / v.std())

# 1D odd/even
for N in (128, 127, 200):
    v = smooth_field((N,))
    K = pros.generate_pros_1d(v, seed=21)
    V = np.abs(np.fft.rfft(v - v.mean())); KK = np.abs(np.fft.rfft(K - K.mean()))
    record(f"1D N={N}", np.corrcoef(v, K)[0, 1],
           np.max(np.abs(KK - V)) / V.max(), K.std() / v.std())

print("\n=== 4: silent-clip path (unsolvable |val|>1) ===")
# Near-unsolvable: make a field whose spectrum is dominated by the FIXED modes
# (DC + Nyquist + 4 rfft2 corners), so S_fixed ~ R forces |val| > 1 -> clip fires.
# Construction: field = strong checkerboard (Nyquist) + strong DC + weak smooth part.
def pathological(H=64, W=64, dc=5.0, nyq=5.0, weak=0.02):
    y, x = np.indices((H, W))
    v = dc + nyq * (-1.0) ** (x + y) * np.ones((H, W)) * 0 + nyq * ((-1.0) ** x) * ((-1.0) ** y)
    v += weak * smooth_field((H, W))
    return v

n_clip_trials, corr_when_clip, corr_when_not = 0, [], []
for t in range(200):
    v = pathological(dc=3.0 + 0.2 * t, nyq=3.0 + 0.2 * t, weak=0.02)
    # detect clip by monkey-patching arccos input: recompute here
    V = np.fft.rfft2(v - v.mean()); amp = np.abs(V); psi = np.angle(V)
    H, W = v.shape
    theta = rng.uniform(0, 2 * np.pi, V.shape)
    theta[0, 0] = 0
    if H % 2 == 0: theta[H // 2, 0] = 0
    if W % 2 == 0:
        theta[0, W // 2] = 0
        if H % 2 == 0: theta[H // 2, W // 2] = 0
    mask = np.ones(V.shape, bool)
    mask[0, 0] = False
    if H % 2 == 0: mask[H // 2, 0] = False
    if W % 2 == 0:
        mask[0, W // 2] = False
        if H % 2 == 0: mask[H // 2, W // 2] = False
    weights = np.full(V.shape, 2.0); weights[:, 0] = 1.0
    if W % 2 == 0: weights[:, -1] = 1.0
    alpha = theta[mask] - psi[mask]
    w = weights[mask] * amp[mask] ** 2
    fm = ~mask
    fixed = np.sum(weights[fm] * amp[fm] ** 2 * np.cos(theta[fm] - psi[fm]))
    A, B = np.sum(w * np.cos(alpha)), np.sum(w * np.sin(alpha))
    val = -fixed / np.hypot(A, B)
    clipped = abs(val) > 1.0
    K = pros.generate_pros_2d(v, seed=500 + t)
    c = abs(np.corrcoef(v.ravel(), K.ravel())[0, 1])
    if clipped:
        n_clip_trials += 1
        corr_when_clip.append(c)
    else:
        corr_when_not.append(c)

print(f"triggers with |val|>1 (clip): {n_clip_trials}/200")
if corr_when_clip:
    print(f"  corr WHEN clipped : max={max(corr_when_clip):.3e} mean={np.mean(corr_when_clip):.3e}")
    silent = max(corr_when_clip) > 1e-12
    print(f"  -> SILENT CORRELATION LEAK on clip: {'YES (bug)' if silent else 'no'}")
if corr_when_not:
    print(f"  corr when solvable: max={max(corr_when_not):.3e} (n={len(corr_when_not)})")
else:
    print("  corr when solvable: n/a (clip fired on all 200 trials)")

print("\n=== summary ===")
fails = [r for r in results if not r[4]]
print(f"{len(results) - len(fails)}/{len(results)} structural checks passed")
for r in fails:
    print(f"  FAIL: {r[0]} |corr|={r[1]:.2e} psd={r[2]:.2e}")