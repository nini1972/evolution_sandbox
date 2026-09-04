from r19z_deep_lib import *
import json

gs_dyn = {}
for f in [0.050, 0.060, 0.064, 0.068, 0.072, 0.080, 0.090]:
    comp, mv = run_gs_only(f, n_steps=3000, burn_in=1000)
    ac10 = 0
    ac50 = 0
    if np.std(comp) > 0:
        ac10 = float(np.corrcoef(comp[:-10], comp[10:])[0,1])
        ac50 = float(np.corrcoef(comp[:-50], comp[50:])[0,1])
    gs_dyn[f] = {
        'complexity_mean': float(np.mean(comp)),
        'complexity_std': float(np.std(comp)),
        'v_mean': float(np.mean(mv)),
        'v_std': float(np.std(mv)),
        'autocorr_10': ac10,
        'autocorr_50': ac50,
    }
    print('f=%.3f: complexity=%.4f, v_mean=%.4f, ac(10)=%.3f, ac(50)=%.3f' % (
        f, gs_dyn[f]['complexity_mean'], gs_dyn[f]['v_mean'], ac10, ac50))

with open('r19z_gs_dyn_data.json', 'w') as fp:
    json.dump({str(k): v for k, v in gs_dyn.items()}, fp, indent=2)
print('Saved gs_dyn data')