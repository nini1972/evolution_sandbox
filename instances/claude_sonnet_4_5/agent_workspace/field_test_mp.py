#!/usr/bin/env python3
"""
FIELD TEST of the parity-blindness theorem + M_p detector on real empirical
series (colony_lib.datasets). Questions:

 Q1 (Thm 1 on REAL data): is parity_contrast(p) p-flat on real signals just
    as on synthetic? If yes, no real-data "period-p" claim can rest on
    parity_contrast for p>2.
 Q2 (Thm 2 in the field): does argmax_p M_p recover a physically plausible
    period for genuinely periodic series (sunspots ~132 months, lynx ~10 yr,
    EEG alpha ~10 Hz -> 12.8 samples), and what does it give for aperiodic
    ones?
 Q3 (controls): M_p on shuffled surrogates -> flat/low floor, same code path.

Honesty guards:
 - thresholds fixed a priori: normalize to [0,1], threshold 0.5, max_lag=120
   (>= 8x largest p), p in 2..16 for M_p; p in {2,4,6,8,10,12} for parity.
 - argmax reported WHATEVER it is; no cherry-picking of decimation factors.
 - each dataset failure recorded explicitly, never silent.
"""
import json, traceback
import numpy as np
from colony_lib.datasets import load_dataset, list_datasets

import importlib.util
spec = importlib.util.spec_from_file_location(
    "pa", "../../shared_space/periodicity_archaeology.py")
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

P_PARITY = [2, 4, 6, 8, 10, 12]
P_MP = list(range(2, 17))
MAX_LAG = 120

# known reference periods in SAMPLES of the native series (a priori)
REFERENCE = {
    "solar_sunspots":      dict(period_samples=132, note="11-yr cycle, monthly data"),
    "lynx_hare":           dict(period_samples=10,  note="~10-yr lynx limit cycle, annual"),
    "climate_enso":        dict(period_samples=36,  note="~3-yr ENSO, monthly-ish; band 24-84"),
    "neural_eeg":          dict(period_samples=12.8,note="alpha 10 Hz at 128 Hz"),
    "climate_temperatures":dict(period_samples=365, note="annual cycle, daily data (beyond max_lag)"),
}


def M_p(lc, p):
    lags = np.array(sorted(lc.keys()))
    mus = []
    for r in range(p):
        sel = lags[(lags % p) == r]
        mus.append(float(np.mean([lc[int(l)] for l in sel])) if len(sel) else 0.0)
    mus = np.array(mus)
    d = mus.max() + mus.min()
    return float((mus.max() - mus.min()) / d) if d > 0 else 0.0


def norm1(s):
    s = np.asarray(s, float)
    s = s - np.nanmin(s)
    mx = np.nanmax(s)
    return s / mx if mx > 0 else s


def lc_of(signal, max_lag):
    traj = norm1(signal).reshape(-1, 1)
    motifs = pa.extract_symbolic_motifs(traj, motif_width=1, threshold=0.5)
    return pa.compute_temporal_consistency(motifs, max_lag=max_lag)


def profile(lc):
    return {p: M_p(lc, p) for p in P_MP}


def main():
    out = {"p_mp": P_MP, "max_lag": MAX_LAG, "datasets": {}, "errors": []}
    rng = np.random.default_rng(7)

    for name in list_datasets():
        try:
            ds = load_dataset(name)
            if name == "lynx_hare":
                cols = list(ds.metadata.get("columns", []))
                j = cols.index("lynx") + 1  # +1: col 0 is year
                sig = np.asarray(ds.data[:, j], float)
            else:
                sig = np.asarray(ds.primary_signal, float)
            sig = sig[np.isfinite(sig)]
            if len(sig) < 256:
                raise ValueError(
                    f"too short: n={len(sig)} (need n>=256 so max_lag>=64>=4*max_p)")

            ml = int(min(MAX_LAG, len(sig) // 4))  # >= 4*max_p margin
            lc = lc_of(sig, ml)
            # parity p-flatness via REAL instrument path
            st = pa.analyze_periodic_structure(lc, period_candidates=P_PARITY)
            parity = {p: float(st[p]["parity_contrast"]) for p in P_PARITY}

            prof = profile(lc)

            # --- bias correction: M_p grows with p mechanically (fewer lags
            # per residue class -> higher sampling variance). Calibrate with
            # a shuffle ENSEMBLE through the identical code path and report
            # z-scores; detection = argmax of z, not of raw M_p.
            N_SHUF = 20
            acc = {p: [] for p in P_MP}
            for _ in range(N_SHUF):
                sh = np.array(sig); rng.shuffle(sh)
                ps = profile(lc_of(sh, ml))
                for p in P_MP:
                    acc[p].append(ps[p])
            z = {}
            for p in P_MP:
                mu = float(np.mean(acc[p]))
                sd = float(np.std(acc[p]))
                z[p] = (prof[p] - mu) / sd if sd > 1e-15 else 0.0
            arg = max(z, key=z.get)
            sh_flat = float(np.ptp([np.mean(acc[p]) for p in P_MP]))
            sh_max = float(max(np.mean(acc[p]) for p in P_MP))

            ref = REFERENCE.get(name, {})
            out["datasets"][name] = {
                "n": int(len(sig)),
                "parity_contrast": parity,
                "parity_spread_pflat": float(np.ptp(list(parity.values()))),
                "Mp_profile": prof,
                "Mp_z": z,
                "shuffle_ensemble_mean_Mp": {str(p): float(np.mean(acc[p]))
                                             for p in P_MP},
                "max_lag_used": ml,
                "Mp_argmax_p_z": int(arg),
                "Mp_argmax_z_value": float(z[arg]),
                "Mp_argmax_p_raw": int(max(prof, key=prof.get)),
                "reference_period_samples": ref.get("period_samples"),
                "reference_note": ref.get("note"),
                "shuffle_floor_max_Mp": sh_max,
                "shuffle_profile_spread": sh_flat,
                "signal_exceeds_max_lag": bool(
                    ref.get("period_samples", 0) > ml),
            }
        except Exception as e:
            out["errors"].append({"dataset": name, "error": str(e),
                                  "trace": traceback.format_exc()[-500:]})
    with open("field_test_mp.json", "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()