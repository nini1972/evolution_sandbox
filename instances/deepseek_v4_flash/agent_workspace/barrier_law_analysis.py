#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local analysis of escape_law_full.json: extract the barrier law.
Tests: is log(t_esc) linear in N (true nucleation barrier) or not?
Theory: barrier regime R0 < R_nuc -> t_esc ~ exp(N * c * (sigma^2/K0)^{2/alpha}).
"""
import json, math
import numpy as np

RTHR = 0.8
K0 = 5.0
d = json.load(open('world_c_results/escape_law_full.json'))

print("="*78)
print("BARRIER ANALYSIS of escape_law_full.json")
print("="*78)

results = {}
for key, blk in d.items():
    a = blk['alpha']; s = blk['sigma']
    Rnuc = blk['R_nuc']; Nstar = blk['Nstar_theory']
    Ns, meds, means, fracs, R0s, tmaxs = [], [], [], [], [], []
    for Ns_s, nn in blk['per_N'].items():
        Ns.append(int(Ns_s))
        meds.append(nn['median'] if nn['median'] is not None else np.nan)
        means.append(nn['mean_uncens'] if nn['mean_uncens'] is not None else np.nan)
        fracs.append(nn['frac_esc'])
        R0s.append(nn['R0'])
        tmaxs.append(nn['Tmax'])
    order = np.argsort(Ns)
    Ns = np.array(Ns)[order]; meds = np.array(meds,float)[order]
    means = np.array(means,float)[order]; fracs = np.array(fracs,float)[order]
    R0s = np.array(R0s)[order]
    ok = np.isfinite(means) & (means > 0)
    # fit log(mean_uncens) vs N for points in barrier regime (R0 < Rnuc)
    barrier_mask = ok & (R0s < Rnuc)
    line = {}
    if barrier_mask.sum() >= 3:
        x = Ns[barrier_mask]; y = np.log(means[barrier_mask])
        A = np.vstack([x, np.ones_like(x)]).T
        slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
        yhat = slope*x + intercept
        ss_res = np.sum((y-yhat)**2); ss_tot = np.sum((y-y.mean())**2)
        r2 = 1 - ss_res/ss_tot if ss_tot > 0 else np.nan
        # c coefficient: slope = c*(sigma^2/K0)^{2/alpha}
        cfac = (s*s/K0)**(2.0/a)
        c_est = slope/cfac if cfac>0 else np.nan
        line = dict(slope=float(slope), intercept=float(intercept), r2=float(r2),
                    c_est=float(c_est), npts=int(barrier_mask.sum()))
    results[key] = dict(alpha=a, sigma=s, Rnuc=Rnuc, Nstar=Nstar,
                        Ns=Ns.tolist(), meds=meds.tolist(), means=means.tolist(),
                        fracs=fracs.tolist(), R0s=R0s.tolist(), barrier_fit=line)
    bf = line if line else {}
    print(f"\n a={a:<4} s={s:<4} R_nuc={Rnuc:.4g} N*={Nstar:.4g}")
    print(f"   N   : {Ns.tolist()}")
    print(f"   R0  : {[round(r,3) for r in R0s]}")
    print(f"   med : {[round(m,2) if np.isfinite(m) else None for m in meds]}")
    print(f"   frac: {fracs.tolist()}")
    if bf:
        print(f"   -> barrier fit log(mean) vs N: slope={bf['slope']:.5f} "
              f"R2={bf['r2']:.4f} c_est={bf['c_est']:.5f} (n={bf['npts']})")

# Universal test: does c_est depend only on sigma^2/K0 and alpha?
print("\n" + "="*78)
print("UNIVERSALITY TEST: c_est across cells")
print("="*78)
print(f"{'alpha':>6}{'sigma':>7}{'sigma^2/K0':>12}{'(s^2/K0)^(2/a)':>16}{'slope':>12}{'c_est':>12}{'R2':>8}")
for key, r in results.items():
    bf = r['barrier_fit']
    if bf:
        cfac = (r['sigma']**2/K0)**(2.0/r['alpha'])
        print(f"{r['alpha']:>6.2f}{r['sigma']:>7.2f}{r['sigma']**2/K0:>12.4f}{cfac:>16.5f}"
              f"{bf['slope']:>12.4f}{bf['c_est']:>12.4f}{bf['r2']:>8.3f}")

json.dump(results, open('barrier_law_analysis.json','w'), indent=1)
print("\nSaved barrier_law_analysis.json")
