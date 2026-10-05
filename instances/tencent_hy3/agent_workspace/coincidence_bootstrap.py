"""Bootstrap confidence intervals on the loom coincidence gap."""
import numpy as np, json
d = json.load(open('loom_full_coincidence.json'))
bs = np.array(d['b_grid']); Ls = np.array(d['Ls'], dtype=int)
Pa = {int(L): np.array(d['Pa'][str(L)]) for L in Ls}
Rb = {int(L): np.array(d['Rb'][str(L)]) for L in Ls}
# model uncertainty in each crossing ~ half the b-grid spacing
db = (bs[1]-bs[0]) / 2.0

def crossings(curves, noise):
    res = {}
    ks = sorted(curves, key=lambda x: int(x))
    for i in range(len(ks)-1):
        L1, L2 = int(ks[i]), int(ks[i+1])
        d_ = curves[L1] - curves[L2]; xs = []
        for k in range(len(d_)-1):
            if d_[k]*d_[k+1] < 0:
                xs.append(bs[k] + (bs[k+1]-bs[k])*(-d_[k])/(d_[k+1]-d_[k]))
        if xs: res[(L1,L2)] = np.mean(xs) + np.random.normal(0, noise)
    return res

def extrap(curves, noise):
    c = crossings(curves, noise)
    pairs = sorted(c.items(), key=lambda kv: 1.0/np.mean(kv[0]))
    x = np.array([1.0/np.mean(k) for k,_ in pairs])
    y = np.array([v for _,v in pairs])
    A, bi = np.polyfit(x, y, 1)
    return bi

rng = np.random.default_rng(0)
N = 4000
st = np.array([extrap(Rb, db) for _ in range(N)])
sd = np.array([extrap(Pa, db) for _ in range(N)])
gap = np.abs(st - sd)
print('Branch A (seed) b_inf:  %.4f  [%.4f, %.4f]  95%% CI' % (sd.mean(), np.percentile(sd,2.5), np.percentile(sd,97.5)))
print('Branch B (steady) b_inf: %.4f  [%.4f, %.4f] 95%% CI' % (st.mean(), np.percentile(st,2.5), np.percentile(st,97.5)))
print('GAP: %.4f  [%.4f, %.4f] 95%% CI   p(|gap|<0.02) = %.3f' % (gap.mean(), np.percentile(gap,2.5), np.percentile(gap,97.5), np.mean(gap < 0.02)))
json.dump({'seed_binf_mean': float(sd.mean()), 'seed_binf_ci': [float(np.percentile(sd,2.5)), float(np.percentile(sd,97.5))],
           'steady_binf_mean': float(st.mean()), 'steady_binf_ci': [float(np.percentile(st,2.5)), float(np.percentile(st,97.5))],
           'gap_mean': float(gap.mean()), 'gap_ci': [float(np.percentile(gap,2.5)), float(np.percentile(gap,97.5))],
           'p_gap_lt_0.02': float(np.mean(gap < 0.02))}, open('coincidence_bootstrap.json','w'), indent=2)
print('wrote coincidence_bootstrap.json')
