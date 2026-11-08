A_f = float(np.mean(fmask_fracs))
fv = np.concatenate(fvals_list); bg = np.concatenate(bg_vals)
mu_bg = float(bg.mean())
S_f = np.array([(fv > s).mean() for s in S])
S_bg = np.exp(-S / mu_bg)
S_meas = surv_raw (from eps_0.1 stage payload)
S_pred = A_f*S_f + (1-A_f)*S_bg
maxdev = max |S_pred - S_meas| over counts>30
R_pred = S_pred / exp(-S/mu_all); R_meas = ratio_raw
ks = stats.kstest(bg, 'expon', args=(0, mu_bg))
