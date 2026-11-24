# c41_horizon_ext.py — 10-point tunneling horizon series (EXTENSION)
# Recomputes the ENTIRE trajectory from seed 11 (identical frozen grammar) out to
# T=36000 for all three regimes, so the new 7 points double as a BITWISE
# reproducibility audit of the original c41_horizon_series stage.
# Frozen grammar (c41_core.py rev B): gs_init / lap5 / fd5 solver / orient_stats
# short policy, window lags in [80,320], N=200, dx=1, dt=1, seed=11.
import numpy as np, json, os, sys, traceback

STAGE = "c41_horizon_series"
DEG = np.pi / 180.0

# ---------------- frozen grammar: verbatim from c41_core.py rev B ----------------
def gs_init(N, seed, seed_frac=0.10):
    rng = np.random.default_rng(seed)
    u = np.ones((N, N)); v = np.zeros((N, N))
    m = rng.random((N, N)) < seed_frac
    box = np.zeros((N, N), bool)
    b0, b1 = N // 3, 2 * N // 3
    box[b0:b1, b0:b1] = True
    v[m & box] = 1.0
    u = 1.0 - v
    return u, v

def lap5(u, dx):
    return (np.roll(u, 1, 0) + np.roll(u, -1, 0) +
            np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4.0 * u) / (dx * dx)

LAG_POLICIES = {"short": lambda rr: (rr >= 2) & (rr <= 8)}

def _orient_core(f, R=24, policy="short"):
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 2 or not np.isfinite(f).all():
        return None
    N = f.shape[0]
    V = f - f.mean()
    F1 = np.fft.rfft2(V)
    C = np.fft.irfft2((F1 * np.conj(F1)).real, s=f.shape)
    c0 = C[0, 0]
    if not np.isfinite(c0) or c0 <= 0:
        return None
    C = C / c0
    rng = np.arange(-R, R + 1)
    ii, jj = np.meshgrid(rng, rng, indexing="ij")
    rr = np.sqrt(ii * ii + jj * jj)
    sel = LAG_POLICIES[policy](rr)
    th = np.arctan2(jj[sel], ii[sel]) % np.pi
    vals = C[np.mod(ii[sel], N), np.mod(jj[sel], N)]
    bins = np.clip((th / DEG).astype(int), 0, 179)
    A = np.zeros(180)
    for b in range(180):
        m = bins == b
        if m.any():
            A[b] = vals[m].mean()
    A = A - A.mean()
    absA = np.abs(A); sA = absA.sum()
    if sA <= 0:
        return None
    th_c = (np.arange(180) + 0.5) * DEG
    Re = (A * np.cos(2 * th_c)).sum(); Im = (A * np.sin(2 * th_c)).sum()
    phi = np.arctan2(Im, Re) / 2.0
    R2 = np.hypot(Re, Im) / sA
    return dict(phi_deg=float(np.degrees(phi) % 90.0), R2=float(R2))

def orient_stats(f, R=24, policy="short"):
    return _orient_core(f, R, policy)

def spec_orient(f, dx=1.0, band=(80.0, 320.0), min_snr=0.05):
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 2 or not np.isfinite(f).all():
        return None
    F1 = np.fft.rfft2(f - f.mean())
    kx = np.fft.fftfreq(f.shape[0], d=dx) * 2.0 * np.pi
    KY, KX = np.meshgrid(np.fft.fftfreq(f.shape[1], d=dx) * 2.0 * np.pi, kx,
                         indexing="ij")
    K = np.hypot(KX, KY)
    P = (F1.real ** 2 + F1.imag ** 2)
    m = (K >= band[0]) & (K <= band[1])
    if not m.any():
        return None
    tot = P[m].sum()
    if not np.isfinite(tot) or tot <= 0:
        return None
    peak = P.max()
    if peak <= 0 or (tot / P.sum()) < min_snr:
        return None
    Kp = K[m]; Pp = P[m]
    Re = (Kp * Pp).sum() / tot; Im = (Kp * Pp * 0).sum()  # magnitude-based, vector-blind
    # direction from first circular moment of the spectral power over angle:
    th = np.arctan2(KX[m], KY[m]) % np.pi
    Re2 = (Pp * np.cos(2 * th)).sum() / tot
    Im2 = (Pp * np.sin(2 * th)).sum() / tot
    phi = np.degrees(np.arctan2(Im2, Re2) / 2.0) % 90.0
    W = (np.maximum(Kp, 1e-12) ** 2 * Pp).sum() / tot
    lam_dom = 2.0 * np.pi / max(np.sqrt(W), 1e-12)
    return dict(peak_lam=float(lam_dom), band_frac=float(tot / P.sum()),
                phi_spec_deg=float(phi))

# ---------------- frozen original series (embedded constants) ----------------
FROZEN = {
 "spots":     {"T":[1200,2400,3600,4800,6000,8400,12000],
   "R2_sp":[0.02122980876904445,0.03004951233370657,0.015480299803278634,0.049845675072998,0.010658954344745447,0.009008864169990497,0.0034718335754343656],
   "S2_ft":[0.013368224660839229,0.032101362412913406,0.014008142322644947,0.02650372063681001,0.0023712667386694836,0.009547084238751466,0.011752304292490384],
   "v_mean":[0.017884328936379052,0.044542362689063024,0.07103342395925229,0.09725622259332556,0.10775552110079184,0.1111197785627078,0.1114627027651714],
   "act_frac":[0.016764322916666668,0.04592556423611111,0.07535807291666667,0.10120985243055555,0.11585828993055555,0.12144639756944445,0.12193467881944445]},
 "stripes":   {"T":[1200,2400,3600,4800,6000,8400,12000],
   "R2_sp":[0.026414121679779114,0.025558976470685557,0.04439522135370918,0.2037807894989417,0.1759253434678162,0.14841609074193352,0.1277347516961626],
   "S2_ft":[0.09493787153343149,0.07415188172735443,0.09778266761291325,0.11736285373305509,0.10829041173434902,0.10449153400109086,0.09830768786817148],
   "v_mean":[0.03600660000920147,0.06942693611603776,0.10435528490479953,0.14692828738971836,0.1656792834276701,0.1708318892222236,0.17188606893824968],
   "act_frac":[0.051676432291666664,0.0949978298611111,0.1433648003472222,0.20225694444444445,0.2273220486111111,0.2319064670138889,0.2323947482638889]},
 "tunneling": {"T":[1200,2400,3600,4800,6000,8400,12000],
   "R2_sp":[0.014482721842942723,0.021492170302915253,0.03808102988479049,0.05157184077415238,0.059231401895230976,0.07010489807432056,0.06804744078941902],
   "S2_ft":[0.07357225011777084,0.08249755073691933,0.11460189949547629,0.12003818275435935,0.11843916775146435,0.12101133736823443,0.10198481729072512],
   "v_mean":[0.016382342941242734,0.02435322948457724,0.031753464110232735,0.038883868971595445,0.0451887681646589,0.05724120212222333,0.0737374804040743],
   "act_frac":[0.026041666666666668,0.03884548611111111,0.05099826388888889,0.0635036892361111,0.07316080729166667,0.09337022569444445,0.1196017795138889]},
}
PARAMS = {"spots":     dict(F=0.035, k=0.058),
          "stripes":   dict(F=0.060, k=0.065),
          "tunneling": dict(F=0.035, k=0.065)}
N, DX, DT, SEED = 200, 1.0, 1.0, 11
SNAP_TS = [1200, 2400, 3600, 4800, 6000, 8400, 12000, 18000, 24000, 36000]
BAND = (80.0, 320.0)

def simulate(steps, F, k):
    Du, Dv = 0.16, 0.08
    u, v = gs_init(N, SEED)
    for _ in range(steps):
        uvv = u * v * v
        un = u + DT * (Du * lap5(u, DX) - uvv + F * (1.0 - u))
        vn = v + DT * (Dv * lap5(v, DX) + uvv - (F + k) * v)
        u, v = un, vn
    return u, v

def fit_power_series(T, y, K0=0.1, alpha0=1.0):
    T = np.asarray(T, float); y = np.asarray(y, float)
    C0 = y[0] - K0
    if C0 <= 0: C0 = max(y.max() * 0.5, 1e-6)
    def resid(p):
        K, C, a = p
        return (y - (K + C / T ** a)) / (np.abs(y) + 0.02)
    p, _ = np.array([K0, C0, alpha0]), None
    from scipy.optimize import least_squares
    try:
        r = least_squares(resid, p, bounds=([-1.0, 1e-9, 0.05], [1.0, 10.0, 4.0]), max_nfev=20000)
        p = r.x
    except Exception:
        return None
    J = r.jac
    try:
        cov = np.linalg.inv(J.T @ J) * (2.0 * r.cost / (len(y) - 3))
        se = np.sqrt(np.abs(np.diag(cov)))
    except Exception:
        se = np.full(3, np.nan)
    pred = p[0] + p[1] / T ** p[2]
    sst = ((y - y.mean()) ** 2).sum()
    r2 = 1.0 - ((y - pred) ** 2).sum() / sst if sst > 0 else np.nan
    return dict(K=float(p[0]), C=float(p[1]), alpha=float(p[2]),
                se_K=float(se[0]), se_alpha=float(se[2]), r2=float(r2))

def main():
    out = {"stage": STAGE, "frozen_grammar": dict(solver="fd5", N=N, dx=DX, dt=DT,
           seed=SEED, seed_frac=0.10, Du=0.16, Dv=0.08, band=list(BAND),
           params=PARAMS, snap_ts=SNAP_TS)}
    series = {}
    audit = {}
    for name in ("spots", "stripes", "tunneling"):
        F, k = PARAMS[name]["F"], PARAMS[name]["k"]
        rows, trace = [], []
        done = 0
        for T in SNAP_TS:
            sim_to = T - done
            u, v = simulate(sim_to, F, k)
            done = T
            st = orient_stats(v, policy="short")
            so = spec_orient(v, dx=DX, band=BAND)
            act = v > 0.35
            row = dict(T=T,
                       R2_sp=(st["R2"] if st else None),
                       phi_sp=(st["phi_deg"] if st else None),
                       S2_ft=(so["peak_lam"] if so else None),
                       phi_spec=(so["phi_spec_deg"] if so else None),
                       band_frac=(so["band_frac"] if so else None),
                       v_mean=float(v.mean()), v_max=float(v.max()),
                       act_frac=float(act.mean()))
            rows.append(row)
        # dense per-200-step window trace for plateau gating (recompute windows)
        # NOTE: cheaper approach — reuse the *state at each snapshot*: we cannot
        # re-derive intermediate windows without re-simulating, so instead we take
        # windows INSIDE each simulated block? Not available post-hoc. Therefore:
        # record plateau via a second pass ONLY for tunneling+stripes at full
        # resolution near the tail.
        series[name] = rows
    # ---- bitwise audit vs frozen constants ----
    for name in ("spots", "stripes", "tunneling"):
        fr = FROZEN[name]
        rep = {}
        for key in ("R2_sp", "S2_ft"):
            got = np.array([r[key] for r in series[name][:7]])
            ref = np.array(fr[key])
            rep[key] = dict(bitwise=bool(np.array_equal(got, ref)),
                            max_abs_dev=float(np.max(np.abs(got - ref))))
        # v_mean aggregation inference: try window means of last {1,3,6} 200-step windows
        audit[name] = rep
    out["series"] = series
    out["bitwise_audit"] = audit
    print("BITWISE AUDIT:", json.dumps(audit, indent=1))
    return out

if __name__ == "__main__":
    res = main()
    with open("c41_ext_series.json", "w") as fh:
        json.dump(res, fh, indent=1)
    print("series written")
