# c41_prefit.py — local pre-fit of the 7-horizon dual series (R2_sp + S2_ft)
# before xiaomi_mimo's World C extract_finite_horizon_scaling run.
# Grammar check: for observables whose TRUE asymptote is 0 (spots S2_ft),
# the tool returns ARTIFACT — semantically right ("no persistent anisotropy")
# but conflates "relaxes to zero" with "truth is zero". Hence we also fit the
# SEPARATION observables dS2/dR2, whose asymptotic persistence is what Stage-4
# actually certifies.
import numpy as np
from colony_lib.persistence import StageTracker
from colony_lib.scaling import extract_finite_horizon_scaling

P = StageTracker("c41_horizon_series").load_stage("final")
hs = np.array(P["setup"]["horizons"], float)
S = P["series"]
KEYS = ["asymptotic_limit", "asymptotic_limit_stderr", "scaling_exponent",
        "prefactor", "T_star", "crossover_timescale", "T_star_95"]


def show(tag, r):
    if not r.get("success", False):
        print(f"  {tag:24s} {r.get('verdict','FAIL'):30s} {r.get('error','')[:50]}")
        return
    ki = r["asymptotic_limit"]; e = r.get("asymptotic_limit_stderr", 0.0)
    al = r.get("scaling_exponent", float("nan"))
    ts = [r[k] for k in ("T_star", "crossover_timescale", "T_star_95") if k in r]
    tstr = f" T*={ts[0]:.0f}" if ts and np.isfinite(ts[0]) else ""
    print(f"  {tag:24s} {r['verdict']:30s} Kinf={ki:+.4f}±{e:.4f} alpha={al:+.3f}{tstr}")
    extra = {k: round(float(r[k]), 4) for k in r if isinstance(r[k], (int, float))
             and k not in KEYS + ["success", "K_inf", "alpha", "C"]}
    if extra:
        print(f"  {'':24s} extra={extra}")


for reg in ["spots", "stripes", "tunneling"]:
    d = S[reg]
    print(f"--- {reg} ---")
    show("R2_sp", extract_finite_horizon_scaling(hs, d["R2_sp"], 0.01))
    show("S2_ft", extract_finite_horizon_scaling(hs, d["S2_ft"], 0.02))
    vm = np.array(d["v_mean"])
    dv = np.abs(np.diff(vm) / np.diff(hs))
    print(f"  {'plateau |dv_mean/dT|':24s} last={dv[-1]:.2e} prev={dv[-2]:.2e} "
          f"ratio={dv[-1]/max(dv[-2],1e-12):.2f}")

sp, st_, tu = S["spots"], S["stripes"], S["tunneling"]
print("--- separation observables ---")
for tag, a, b in [("dS2 stripes-spots", st_["S2_ft"], sp["S2_ft"]),
                  ("dR2 stripes-spots", st_["R2_sp"], sp["R2_sp"]),
                  ("dS2 tunnel-spots", tu["S2_ft"], sp["S2_ft"])]:
    show(tag, extract_finite_horizon_scaling(hs, np.array(a, float) - np.array(b, float), 0.02))
print("--- horizon values ---")
for reg in ["spots", "stripes", "tunneling"]:
    d = S[reg]
    print(f"{reg:10s} R2_sp={['%.3f' % x for x in d['R2_sp']]}")
    print(f"{reg:10s} S2_ft={['%.3f' % x for x in d['S2_ft']]}")
