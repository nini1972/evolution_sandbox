#!/usr/bin/env python3
"""Sanity check of the FIXED escape classifier on 3 control velocities.
Expected (Anninos et al. 1991 normalization):
  v=0.05  -> capture  (1 bounce, bound bion)
  v=0.20  -> escape   (classic 2-bounce resonance window)
  v=0.265 -> escape   (supercritical, 1 bounce)
"""
import time, numpy as np
import phi4_resonance_vectorized as pv

CASES = [(0.05, "capture"), (0.20, "escape"), (0.265, "escape")]

for v, expect in CASES:
    t0 = time.time()
    r = pv.run_collision(v, verbose=False, extra_proj=False)
    dt_run = time.time() - t0
    ok = "OK " if r["escaped"] == (expect == "escape") else "FAIL"
    print(f"[{ok}] v_in={v:.3f} expect={expect:7s} got={'escape' if r['escaped'] else 'capture'} "
          f"| n_bounce={r['n_bounces']:2d} v_final={r['v_final']:.4f} "
          f"E_wob={r['E_wobble'] if r['E_wobble']==r['E_wobble'] else float('nan'):.5f} "
          f"|Edrift|={r['drift']:.2e} t={dt_run:.1f}s", flush=True)

print("sanity done")
