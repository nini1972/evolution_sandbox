"""
Diagnostic: ground-truth for the three value-threshold census conventions at
the reference P4 point and the documented edge point, using the module's own
functions (no re-implementation, so no divergence).

Question we're answering:
  At (3.87, 0.136) [deep interior] and (3.925, 0.148) [documented edge],
  what does each convention report?
    float residual  -> min_period / class
    global05        (fixed 0.5)      -> bin_min_period
    globalmed       (median of all)  -> bin_min_period   <-- documented canonical
    perframe        (per-frame median)-> bin_min_period
"""
import numpy as np
import p4_cml_period_gate_module as M

def probe(r, eps, N=120, n_steps=2000):
    x = M.simulate_cml(r, eps, N, n_steps=n_steps, transient=20000)
    sig = M.minimal_period_signature(x, p_max=8)
    g05 = M.threshold_census(x, p_max=8, mode="global05")
    gmed = M.threshold_census(x, p_max=8, mode="globalmed")
    pf  = M.threshold_census(x, p_max=8, mode="perframe")
    thr = float(np.median(x))
    print("=" * 72)
    print(f"POINT r={r}  eps={eps}  N={N}   (global median of traj = {thr:.4f})")
    print(f"  float : d_p = {np.round(sig['d'],4).tolist()}")
    print(f"          min_period={sig['min_period']}  class={sig['classification']}")
    print(f"  global05  (fixed 0.5)   bin_min_period = {g05['bin_min_period']}   d2={g05['d'][2]:.2e}")
    print(f"  globalmed (median all)  bin_min_period = {gmed['bin_min_period']}   d2={gmed['d'][2]:.2e}")
    print(f"  perframe  (med/frame)   bin_min_period = {pf['bin_min_period']}    d2={pf['d'][2]:.2e}")
    # the deficit that matters for the flag (float P4 vs coarse P2)
    return {
        "float": sig["min_period"], "cls": sig["classification"],
        "g05": g05["bin_min_period"], "gmed": gmed["bin_min_period"],
        "pf": pf["bin_min_period"],
    }

if __name__ == "__main__":
    ref = probe(3.870, 0.136)
    edge = probe(3.925, 0.148)
    print("=" * 72)
    print("SUMMARY")
    print("  reference (3.870,0.136):", ref)
    print("  edge      (3.925,0.148):", edge)
    print()
    print("  => canonical documented convention = GLOBALMED (median of the four states)")
    print("  => interior should read  float=P4, globalmed=P2, perframe=P4")
    print("  => edge      should read  float=P4/P8, globalmed=lower, perframe=higher")
