from r19z_deep_lib import *
import json

f_values = [0.050, 0.060, 0.064, 0.068, 0.072, 0.076, 0.080, 0.090]

seed_avg = []
for f in f_values:
    corrs_all = []
    zero_lags_all = []
    for seed in [42, 123]:
        res = run_gs_sandpile(f, n_steps=2000, N_gap=10, seed=seed, burn_in=800)
        corrs_all.append(res['best_corr'])
        zero_lags_all.append(res['zero_lag'])
    avg_corr = float(np.mean(corrs_all))
    avg_zero = float(np.mean(zero_lags_all))
    std_corr = float(np.std(corrs_all))
    sign = '+' if avg_corr > 0 else '-'
    seed_avg.append({
        'f': float(f),
        'avg_corr': avg_corr,
        'avg_zero_lag': avg_zero,
        'std_corr': std_corr,
        'sign': sign,
    })
    print('f=%.3f: C_avg=%+.4f +/- %.4f, C_zero=%+.4f, sign=%sC' % (f, avg_corr, std_corr, avg_zero, sign))

with open('r19z_seed_avg_data.json', 'w') as fp:
    json.dump(seed_avg, fp, indent=2)
print('Saved seed_avg data')
