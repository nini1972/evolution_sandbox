import json, os
cands=['../../shared_space/loom_dp_metrics.json','loom/loom_dp_metrics.json']
m=None
for c in cands:
    if os.path.exists(c):
        m=json.load(open(c)); print('loaded',c); break
if m is None:
    print('NOT_READY: world C DP job not finished yet')
else:
    beta_lit=m['lit']['beta']; nu_lit=m['lit']['nu']; z_lit=m['lit']['z']
    beta_est=m['beta_est']; z_est=m['slope_tau(z)']
    print('--- DP exponent check vs literature ---')
    print('beta (lit %.3f)  est %.3f  -> %s'%(beta_lit,beta_est,'PASS' if abs(beta_est-beta_lit)<0.15 else 'CHECK'))
    print('z    (lit %.3f)  est %.3f  -> %s'%(z_lit,z_est,'PASS' if abs(z_est-z_lit)<0.2 else 'CHECK'))
    print('b_c =',m['b_c'],' slope_rho =',round(m['slope_rho'],3))
    # verdict
    ok = abs(beta_est-beta_lit)<0.15 and abs(z_est-z_lit)<0.2
    print('VERDICT:', 'DP exponents confirmed at viability edge (quantitative)' if ok else 'mismatch -> re-examine (possible falsifier)')
