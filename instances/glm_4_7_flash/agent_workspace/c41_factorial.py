# c41_factorial.py — where does labyrinth anisotropy live: spectrum or positions?
# Factorial test on T=6000 equilibrated fields:
#   metric A: spatial annulus R2 (real-space rim tensor)
#   metric B: S2_ft (Fourier-band angular second moment, same annulus band k in [12,40])
#   nulls: density-matched CSR (positions random) + phase randomization (spectrum kept, features destroyed)
# Decision rule: stripe R2 rejected by CSR but accepted by phase null -> anisotropy is SPECTRAL.
#                stripe S2_ft rejected by both nulls -> spectral anisotropy confirmed independently.
import numpy as np, json, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from c41_core import gs_simulate, orient_stats

N, SEED, T = 192, 11, 6000
KBAND = (12.0, 40.0)
NB = 24
REG = [("spots", 0.030, 0.062), ("stripes", 0.042, 0.062), ("tunneling", 0.058, 0.065)]
NUL = 200


def spec_orient(field):
    """Angular power distribution I(theta_k) in band, same second-moment tensor math
    as the spatial estimator. Returns (stats_dict or None, I_profile or None)."""
    V = np.fft.fftshift(np.fft.fft2(field - field.mean()))
    P = np.abs(V) ** 2
    f = np.fft.fftshift(np.fft.fftfreq(N)) * N
    KX, KY = np.meshgrid(f, f)
    K = np.hypot(KX, KY)
    TH = np.degrees(np.arctan2(KY, KX)) % 180.0
    kb = np.round(K).astype(int).ravel()
    prof = np.bincount(kb, weights=P.ravel())
    cnt = np.bincount(kb)
    prof = np.divide(prof, np.maximum(cnt, 1))
    prof[:2] = 0.0
    kpk = int(np.argmax(prof))
    band = (K >= KBAND[0]) & (K <= KBAND[1])
    b = np.minimum((TH / (180.0 / NB)).astype(int), NB - 1)
    I = np.bincount(b[band].ravel(), weights=P[band].ravel(), minlength=NB)
    s = I.sum()
    if s <= 0:
        return None, None
    I = I / s
    ang = np.radians(np.arange(NB) * 180.0 / NB + 90.0 / NB)
    c, sn = np.cos(ang), np.sin(ang)
    Sxx, Syy, Sxy = (I * c * c).sum(), (I * sn * sn).sum(), (I * c * sn).sum()
    tr = Sxx + Syy
    if tr <= 0:
        return None, None
    d = np.hypot((Sxx - Syy) / 2.0, Sxy)
    phi = 0.5 * np.degrees(np.arctan2(2.0 * Sxy, Sxx - Syy)) % 180.0
    return dict(S2=float(2.0 * d / tr), phi=float(phi), k_peak=kpk), I


def csr_field(dens, rng):
    m = np.zeros(N * N, bool)
    m[rng.choice(N * N, size=int(round(dens * N * N)), replace=False)] = True
    return m.reshape(N, N).astype(float)


def phase_randomize(field, rng):
    V = np.fft.fft2(field - field.mean())
    A = rng.uniform(0, 2 * np.pi, V.shape)
    Th = A - np.flip(np.flip(A, 0), 1)   # conjugate-antisymmetric -> real output
    return np.fft.ifft2(V * np.exp(1j * Th)).real


t0 = time.time()
res = {}
fig, axs = plt.subplots(2, 3, figsize=(15, 9))
hdr = (f"{'regime':10s} {'act%':>5s} {'k_pk':>4s} | {'R2_sp':>6s} {'phi_sp':>6s} | "
       f"{'S2_ft':>6s} {'phi_ft':>6s} | {'c95R2':>6s} {'pR2':>5s} | "
       f"{'c95S2':>6s} {'pS2':>5s} | {'ph_pR2':>6s}")
print(hdr)
print("-" * len(hdr))
for j, (name, F, K) in enumerate(REG):
    out = gs_simulate(N, 1.0, 1.0, T, 0.16, 0.08, F, K, "fd5", SEED)
    if out is None:
        print(f"{name}: SIM BLEW UP, skipped")
        continue
    u, v = out
    vh = float((v > 0.3).mean())
    vf = v - v.min()
    st = orient_stats(vf, R=24, policy="short")
    ss, Iobs = spec_orient(vf)
    rng = np.random.default_rng(101)
    cR2, cS2 = [], []
    for d in range(NUL):
        fc = csr_field(vh, rng)
        stc = orient_stats(fc, R=24, policy="short")
        ssc, _ = spec_orient(fc)
        if stc is not None:
            cR2.append(stc["R2"])
        if ssc is not None:
            cS2.append(ssc["S2"])
    cR2, cS2 = np.asarray(cR2), np.asarray(cS2)
    pR2 = float((cR2 > st["R2"]).mean())
    pS2 = float((cS2 > ss["S2"]).mean())
    rng2 = np.random.default_rng(202)
    ph = []
    for d in range(NUL):
        stp = orient_stats(phase_randomize(vf, rng2), R=24, policy="short")
        if stp is not None:
            ph.append(stp["R2"])
    ph = np.asarray(ph)
    pph = float((ph > st["R2"]).mean())
    c95R2, c95S2 = float(np.percentile(cR2, 95)), float(np.percentile(cS2, 95))
    res[name] = dict(act=vh, k_peak=ss["k_peak"], R2_sp=st["R2"], phi_sp=st["phi_deg"],
                     S2_ft=ss["S2"], phi_ft=ss["phi"], csr_p95_R2=c95R2,
                     csr_rank_R2=pR2, csr_p95_S2=c95S2, csr_rank_S2=pS2,
                     phase_rank_R2=pph, I_obs=Iobs.tolist())
    print(f"{name:10s} {100*vh:5.1f} {ss['k_peak']:4d} | {st['R2']:6.4f} "
          f"{st['phi_deg']:6.1f} | {ss['S2']:6.4f} {ss['phi']:6.1f} | "
          f"{c95R2:6.4f} {pR2:5.2f} | {c95S2:6.4f} {pS2:5.2f} | {pph:6.2f}")
    axs[0, j].imshow(v, cmap="viridis")
    axs[0, j].set_xticks([]); axs[0, j].set_yticks([])
    axs[0, j].set_title(f"{name}  (k_pk={ss['k_peak']}, phi_ft={ss['phi']:.0f}deg)")
    th = np.arange(NB) * 180.0 / NB + 90.0 / NB
    axs[1, j].plot(th, Iobs, "k-", lw=2, label="field I(theta)")
    for d in range(60):
        ssc, Ic = spec_orient(csr_field(vh, np.random.default_rng(303 + d)))
        if Ic is not None:
            axs[1, j].plot(th, Ic, "r-", lw=0.4, alpha=0.25)
    axs[1, j].set_title(f"{name}: angular spectrum vs CSR (red)")
    axs[1, j].set_xlabel("k-direction (deg)")
    axs[1, j].set_ylabel("I(theta) (norm)")
    if j == 0:
        axs[1, j].legend(fontsize=8)
plt.tight_layout()
plt.savefig("c41_factorial.png", dpi=110)
json.dump({k: {kk: vv for kk, vv in d.items() if kk != "I_obs"}
           for k, d in res.items()}, open("c41_factorial.json", "w"), indent=1)
print("-" * len(hdr))
sp, stp = res["spots"], res["stripes"]
print(f"VERDICT: S2_ft stripes/spots ratio = {stp['S2_ft']/max(sp['S2_ft'],1e-9):.1f}x")
print(f"  stripe S2_ft vs CSR null:  rank = {stp['csr_rank_S2']:.3f} "
      f"({'REJECT CSR' if stp['csr_rank_S2'] < 0.05 else 'consistent with CSR'})")
print(f"  stripe R2_sp vs CSR null:  rank = {stp['csr_rank_R2']:.3f} "
      f"({'REJECT CSR' if stp['csr_rank_R2'] < 0.05 else 'consistent with CSR'})")
print(f"  stripe R2_sp vs PHASE null: rank = {stp['phase_rank_R2']:.3f} "
      f"({'anisotropy is SPECTRAL' if stp['phase_rank_R2'] > 0.05 and stp['csr_rank_R2'] < 0.05 else 'positional/other'})")
print(f"runtime {time.time()-t0:.1f}s; saved c41_factorial.png / .json")
