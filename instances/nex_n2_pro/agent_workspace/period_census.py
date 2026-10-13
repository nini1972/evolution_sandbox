#!/usr/bin/env python3
"""RIGOROUS CENSUS: period-2 vs period-4 temporal orbits in coupled logistic lattices.

WHY THIS EXISTS: My earlier 'period-4 symbolic order near the edge of chaos'
(r=3.865, eps=0.132) was a FALSE POSITIVE. A period-2 signal has ACF peaks at
EVERY even lag (including lag 4), so a naive 'lag mod 4' motif analysis
mislabels a period-2 state as period-4. I now classify each cell with a
phase-invariant ACF discriminator that correctly separates the two:

  - period-2 state : ACF[2] >= ACF[4]   (repeats every 2 steps)
  - period-4 state : ACF[4]  >  ACF[2]  (repeats every 4 steps, NOT 2)
  - modulation     : m = ACF[4] - ACF[2]   ( >0 => genuine period-4,
                                              <0 => period-2 harmonic)

Output: period_census.json  +  period_census.png
"""
import numpy as np, json

def coupled(x, r, eps):
    f = r*x*(1-x)
    return (1-eps)*f + (eps/2)*(np.roll(f,1)+np.roll(f,-1))

def acf4(sig):
    """Return (acf2, acf4) over a long window, phase-invariant."""
    c = sig - sig.mean()
    var = (c*c).mean() + 1e-30
    n = len(c)
    def acf(k):
        return np.mean(c[:n-k]*c[k:]) / var
    return acf(2), acf(4)

def classify_cell(ts):           # ts: (T,)
    a2, a4 = acf4(ts)
    locked = a4 > 0.65           # some temporal order present
    if not locked:
        return 'aperiodic', a4-a2
    return ('period4' if a4 > a2 else 'period2'), a4-a2

def census(r, eps, n=120, T=256, trans=4000, seed=0):
    np.random.seed(seed); x = np.random.rand(n)
    for _ in range(trans): x = coupled(x, r, eps)
    series = []
    for _ in range(T):
        x = coupled(x, r, eps); series.append(x.copy())
    ts = np.array(series)                    # (T, n)
    cnt = {'period2':0,'period4':0,'aperiodic':0}
    mods = []
    for i in range(n):
        lab, m = classify_cell(ts[:,i])
        cnt[lab]+=1; mods.append(m)
    mods = np.array(mods)
    return dict(frac_period2=cnt['period2']/n,
                frac_period4=cnt['period4']/n,
                frac_aperiodic=cnt['aperiodic']/n,
                mean_modulation=float(mods.mean()),
                frac_mod_positive=float((mods>0).mean()))

def main():
    rs   = [3.40,3.45,3.50,3.54,3.57,3.68,3.74,3.80,3.828,3.85,3.865,3.868,3.90,4.00]
    eps  = [0.0,0.05,0.10,0.132,0.15,0.20]
    grid = {}
    print(f"{'r':>6} {'eps':>5} | {'P2':>5} {'P4':>5} {'aper':>5} | mod+ :  mean_mod")
    for r in rs:
        for e in eps:
            c = census(r, e)
            grid[(r,e)] = c
            print(f"{r:6.3f} {e:5.3f} | {c['frac_period2']:5.2f} {c['frac_period4']:5.2f} {c['frac_aperiodic']:5.2f} | {c['frac_mod_positive']:4.2f} : {c['mean_modulation']:+.3f}")
    with open('period_census.json','w') as f:
        json.dump({f"{r}|{e}":grid[(r,e)] for r in rs for e in eps}, f, indent=2)

    # ---- heatmap of mean_modulation ( >0 = genuine period-4 ) ----
    import matplotlib
    matplotlib.use('Agg'); import matplotlib.pyplot as plt
    M = np.array([[census(r,e)['mean_modulation'] for e in eps] for r in rs])  # (n_r, n_e)
    fig, ax = plt.subplots(figsize=(8.5,6))
    im = ax.imshow(M, aspect='auto', origin='lower', cmap='RdBu',
                   vmin=-1, vmax=1, extent=[0,len(eps)-1,0,len(rs)-1])
    ax.set_yticks(range(len(rs))); ax.set_yticklabels([f"{r:.3f}" for r in rs])
    ax.set_xticks(range(len(eps))); ax.set_xticklabels([f"{e}" for e in eps])
    ax.set_xlabel("coupling eps"); ax.set_ylabel("logistic r")
    ax.set_title("Genuine period-4 modulation  m = ACF[4]-ACF[2]\n(>0 = true period-4 orbit,  <0 = period-2 harmonic)")
    for i,r in enumerate(rs):
        for j,e in enumerate(eps):
            v = M[i,j]
            ax.text(j,i,f"{v:+.2f}",ha='center',va='center',
                    fontsize=7,color='k' if abs(v)<0.6 else 'w')
    fig.colorbar(im, ax=ax, label='m = ACF[4]-ACF[2]')
    fig.tight_layout(); fig.savefig('period_census.png', dpi=140)
    print("\nwrote period_census.json + period_census.png")

    # highlight the two hero cases
    print("\n== HERO CASES ==")
    for r,e,tag in [(3.865,0.132,"claimed 'period-4' (edge of chaos)"),
                    (3.50,0.132,"native period-4 window")]:
        c = grid[(r,e)]
        print(f"r={r} eps={e} [{tag}]: period4={c['frac_period4']:.2f}, period2={c['frac_period2']:.2f}, mod+={c['frac_mod_positive']:.2f}")

if __name__ == '__main__':
    main()
