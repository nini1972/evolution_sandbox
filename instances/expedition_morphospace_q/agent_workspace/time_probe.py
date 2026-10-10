import time, sys
import morphospace_q_conservation as M

def t(name, fn):
    t0 = time.time()
    try:
        out = fn()
        print(f"[TIME] {name}: {time.time()-t0:.1f}s  -> {out}", flush=True)
    except Exception as e:
        print(f"[FAIL] {name}: {e}", flush=True)

t("lorenz rho=28 (T=300)", lambda: M.experiment_lorenz(rhos=(28.0,)))
t("henon a=1.4",           lambda: M.experiment_henon(as_=(1.4,)))
t("rule110 seed=0",        lambda: M.experiment_rule110(seeds=(0,)))
t("ks L=35 (T=300)",       lambda: M.experiment_ks(Ls=(35.0,)))
