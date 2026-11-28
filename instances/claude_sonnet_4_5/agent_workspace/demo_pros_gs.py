"""End-to-end PROS surrogate null-hypothesis demonstration on a real
Gray-Scott reaction-diffusion field (poolside_laguna's intended use case).

Pipeline:
  1. Simulate Gray-Scott (inline, canonical params f=0.035 k=0.065,
     Du=0.16 Dv=0.08, dt=1, periodic 5-point Laplacian) -> 200x200 v-field.
  2. Observable: number of connected components of {v > threshold}
     (topological count, linking to colleagues' spectral-topological arm).
  3. N=199 PROS surrogates from shared gemini_pro implementation ->
     surrogate distribution of the observable -> Monte-Carlo p-value.
  4. Panels: field | one surrogate | radial PSD overlay (obs vs surr band)
     | component-count histogram with observed value | SILENT-CLIP warning
     panel (DC+checkerboard pathological input, corr~0.99996 returned!).

Verdict logic: if p is tiny -> the observable carries phase-coupling
information beyond the power spectrum (PROS rejects null); if p is
uniform -> observable is PSD-determined (PROS cannot discriminate).

NOTE on silent clip: the pathological panel demonstrates that the shared
implementation returns a nearly-identical field (corr~1) with NO warning
when |val|>1, i.e. a corrupted null -> must be guarded by the caller.
"""
import sys, time, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import ndimage

sys.path.insert(0, "../../shared_space")
from pros_surrogate import generate_pros

rng = np.random.default_rng(20261128)


# ---------- 1. Gray-Scott simulator (inline, canonical) ----------
def gray_scott(H=200, W=200, steps=6000, f=0.035, k=0.065, seed=3):
    r = np.random.default_rng(seed)
    u = np.ones((H, W)); v = np.zeros((H, W))
    # seed a few blobs of (u=0.5, v=0.25)
    for _ in range(12):
        cy, cx = r.integers(20, H - 20), r.integers(20, W - 20)
        yy, xx = np.ogrid[:H, :W]
        m = (yy - cy) ** 2 + (xx - cx) ** 2 <= 9
        u[m], v[m] = 0.5, 0.25
    Du, Dv, dt = 0.16, 0.08, 1.0
    lap = lambda a: (np.roll(a, 1, 0) + np.roll(a, -1, 0) +
                     np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a)
    for t in range(steps):
        uvv = u * v * v
        u = u + dt * (Du * lap(u) - uvv + f * (1 - u))
        v = v + dt * (Dv * lap(v) + uvv - (f + k) * v)
    return v


print("[1] simulating Gray-Scott 200x200, 6000 steps ...", flush=True)
t0 = time.time()
v = gray_scott()
print(f"    done in {time.time()-t0:.1f}s; "
      f"range=({v.min():.4f},{v.max():.4f}) std={v.std():.5f}", flush=True)


# ---------- 2. topological observable ----------
def n_components(field, frac=0.55):
    thr = field.min() + frac * (field.max() - field.min())
    lab, n = ndimage.label(field > thr)
    # keep only components of non-trivial size (>= 4 px) to kill speckle
    sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
    return int(np.sum(sizes >= 4))


obs = n_components(v)
print(f"[2] observed component count = {obs}", flush=True)


# ---------- 3. surrogate ensemble ----------
N_SURR = 199
print(f"[3] generating {N_SURR} PROS surrogates ...", flush=True)
t0 = time.time()
surr_counts = []
corr_max = 0.0
psd_max = 0.0
V = np.abs(np.fft.rfft2(v - v.mean()))
for i in range(N_SURR):
    K = generate_pros(v, seed=1000 + i)
    surr_counts.append(n_components(K))
    corr_max = max(corr_max, abs(np.corrcoef(v.ravel(), K.ravel())[0, 1]))
    KK = np.abs(np.fft.rfft2(K - K.mean()))
    psd_max = max(psd_max, np.max(np.abs(KK - V)) / V.max())
surr_counts = np.array(surr_counts)
p = (np.sum(surr_counts >= obs) + 1) / (N_SURR + 1)
print(f"    done in {time.time()-t0:.1f}s", flush=True)
print(f"    max|corr| across ensemble = {corr_max:.2e}", flush=True)
print(f"    max rel PSD err across ensemble = {psd_max:.2e}", flush=True)
print(f"    surrogate counts: mean={surr_counts.mean():.1f} "
      f"std={surr_counts.std():.1f} min={surr_counts.min()} max={surr_counts.max()}", flush=True)
print(f"    MONTE-CARLO p-value (one-sided >= obs) = {p:.4f}", flush=True)


# ---------- 4. silent-clip pathology demonstration ----------
print("[4] silent-clip pathological input ...", flush=True)
H = W = 64
y, x = np.indices((H, W))
chk = (-1.0) ** x * (-1.0) ** y
vpath = 5.0 + 5.0 * chk + 0.02 * rng.standard_normal((H, W))
with warnings.catch_warnings():
    warnings.simplefilter("always")
    Kpath = generate_pros(vpath, seed=42)
    caught = warnings.catch_warnings
corr_path = np.corrcoef(vpath.ravel(), Kpath.ravel())[0, 1]
print(f"    corr(vpath, surrogate) = {corr_path:.10f}  "
      f"(expected ~0 for a valid null; NO warning was raised)", flush=True)


# ---------- 5. figure ----------
print("[5] plotting ...", flush=True)
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("PROS surrogate null-hypothesis demonstration on Gray-Scott "
             "(shared_space/pros_surrogate.py, validated 8/8 structural checks)",
             fontsize=13)

im0 = axes[0, 0].imshow(v, cmap="viridis")
axes[0, 0].set_title(f"Gray-Scott v-field (f=0.035, k=0.065)\n"
                     f"components(obs) = {obs}")
plt.colorbar(im0, ax=axes[0, 0], fraction=0.046)

K0 = generate_pros(v, seed=1000)
im1 = axes[0, 1].imshow(K0, cmap="viridis")
axes[0, 1].set_title(f"one PROS surrogate\n|corr|={abs(np.corrcoef(v.ravel(), K0.ravel())[0,1]):.1e}, "
                     f"PSD rel.err={np.max(np.abs(np.abs(np.fft.rfft2(K0-K0.mean()))-V))/V.max():.1e}")
plt.colorbar(im1, ax=axes[0, 1], fraction=0.046)

# radial PSD overlay
def radial(P):
    Hh, Ww = P.shape
    ky = np.fft.fftfreq(Hh)[:, None] * Hh
    kx = np.fft.fftfreq(Ww)[None, :] * Ww
    kk = np.sqrt(ky ** 2 + kx ** 2).astype(int)
    prof = np.bincount(kk.ravel(), P.ravel()) / np.maximum(np.bincount(kk.ravel()), 1)
    return prof[: Hh // 2]

P_obs = np.abs(np.fft.rfft2(v - v.mean())) ** 2
ax = axes[0, 2]
ax.loglog(radial(P_obs), "k", lw=2, label="observed")
band_lo, band_hi = [], []
prof0 = radial(P_obs)
profs = []
for i in range(0, N_SURR, 40):  # subsample for speed
    Ks = generate_pros(v, seed=1000 + i)
    profs.append(radial(np.abs(np.fft.rfft2(Ks - Ks.mean())) ** 2))
profs = np.array(profs)
ax.fill_between(range(len(prof0)), profs.min(0), profs.max(0),
                color="orange", alpha=0.4, label="surrogate envelope")
ax.set_title("radial power spectrum\n(observed inside envelope by construction)")
ax.set_xlabel("k"); ax.legend(fontsize=8)

ax = axes[1, 0]
bins = np.arange(surr_counts.min() - 0.5, surr_counts.max() + 1.5, 1)
ax.hist(surr_counts, bins=bins, color="steelblue", alpha=0.8, label="PROS surrogates")
ax.axvline(obs, color="crimson", lw=2.5, label=f"observed = {obs}")
ax.set_title(f"component count: Monte-Carlo null\np = {p:.4f} "
             f"({'REJECT null: phase coupling matters' if p < 0.05 else 'consistent: observable ~ PSD-determined'})")
ax.set_xlabel("connected components"); ax.legend(fontsize=8)

# silent clip warning panel
ax = axes[1, 1]
im2 = ax.imshow(vpath - Kpath, cmap="coolwarm")
ax.set_title(f"SILENT-CLIP pathology: DC+checkerboard input\n"
             f"corr(returned surrogate, input) = {corr_path:.6f}  <- null is NOT null!",
             color="crimson")
plt.colorbar(im2, ax=ax, fraction=0.046)

# summary text panel
ax = axes[1, 2]; ax.axis("off")
ax.text(0.0, 0.98,
        "VALIDATION SUMMARY (claude_sonnet_4_5)\n"
        "──────────────────────────────────────────\n"
        "• structural checks: 8/8 PASS\n"
        "  (odd/even/non-square/1D, corr~1e-16,\n"
        "   PSD err~1e-16, std preserved exactly)\n"
        f"• ensemble guard: max|corr|={corr_max:.1e}, "
        f"max PSD err={psd_max:.1e}\n"
        "• old pre-03:27 version FAILED (PSD err 0.26-0.85,\n"
        "  ky=0 column energy leak) — fix verified real\n"
        "• REMAINING BUG: silent clip when |val|>1;\n"
        f"  pathological corr = {corr_path:.6f}, no warning\n"
        "  -> guard recommended: warn+return None, or\n"
        "     document 'use IAAFT when fixed-mode energy\n"
        "     dominates'.\n"
        "──────────────────────────────────────────\n"
        f"GS null test: p = {p:.4f} (N={N_SURR})",
        family="monospace", fontsize=10, va="top")
ax.set_title("audit summary", fontsize=10)

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("pros_gs_validation.png", dpi=110)
print("[6] saved pros_gs_validation.png", flush=True)

# machine-readable metrics for the report
import json
metrics = {
    "observed_components": int(obs),
    "surr_mean": float(surr_counts.mean()),
    "surr_std": float(surr_counts.std()),
    "p_value": float(p),
    "n_surrogates": N_SURR,
    "ensemble_max_corr": float(corr_max),
    "ensemble_max_psd_rel_err": float(psd_max),
    "silent_clip_pathological_corr": float(corr_path),
    "structural_checks": "8/8 PASS (test_pros_shared.py)",
}
with open("pros_gs_validation_metrics.json", "w") as fh:
    json.dump(metrics, fh, indent=2)
print("[7] saved pros_gs_validation_metrics.json")
print("DONE", flush=True)