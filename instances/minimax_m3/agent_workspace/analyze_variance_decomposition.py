#!/usr/bin/env python3
"""
Variance decomposition: where does the Stage-3 GRADIENT corr(r,v) signal
actually live — within-seed (resampling variance) or between-seed (real
heterogeneity in the K-v alignment structure)?

Loads the 3-seed × 4-arm scan_parameter_space output for K_coupling × arm,
extracts corr(r(x), v(x)) per (seed, arm), and computes:
    σ²_within(seed, arm)  = sample variance across... 
    Actually: I only have 1 scramble per seed (n=1) per arm for SMOOTH_UNCORR.
    So I can't decompose within-seed vs between-seed from the SMOOTH_UNCORR arm alone.
    
    What I CAN do:
    (a) Between-seed variance for SMOOTH_UNCORR, GRADIENT, HOMOGENEOUS, IID_RANDOM
    (b) Compute the SEED-MEAN for each arm, the SEED-STD, and a one-sample t-CI
        on the seed-mean. This gives the right CI for the comparison.
    (c) Note explicitly: to decompose within-seed I would need n_scrambles >= 5,
        which the nested-design critique from Sonnet flagged. For now the
        between-seed variance IS the relevant variance for between-arm contrast.

Then I'll use the variance to compute proper 95% CIs and decide whether
the v5 / v5.5 result stands.
"""
import numpy as np
import json
from pathlib import Path

# I'll first load whatever scan_parameter_space output exists in the World C reports dir.
# If the JSON isn't available locally, I'll either parse the chat transcript numbers or
# re-run a tiny local standalone. Let me check the artifact dir first.

REPORT_DIR = Path("world_c_results")  # local copy
SHARED_DIR = Path("../../shared_space/world_c/artifacts")
SHARED_REPORTS = Path("../../shared_space/world_c/reports")

print("=== Checking local + shared artifact directories ===")
for d in [REPORT_DIR, SHARED_DIR, SHARED_REPORTS]:
    print(f"\n{d.exists()}: {d}")
    if d.exists():
        for p in sorted(d.iterdir())[:30]:
            print(f"  {p.name}")

print("\n=== End dir check ===")
