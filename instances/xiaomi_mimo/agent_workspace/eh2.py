# Echo Horizon law, honest test v2 (imports systems from eh_forms.py)
# v1 flaw: acc was measured AT the decorrelation lag -> tautological ~0.24.
# v2: (i) collapse of acc(h) vs u=lam*h across families+padding,
#     (ii) echo horizon H(q)=min{h:acc(h)<q} ~ A(q)*D2/lam, A independent of d,
#     (iii) both must beat the replicate seed noise floor.
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from eh_forms import (Sys, lorenz, rossler, logmap, clog, hubble, henon, chain)

def acc_curve(ts, hmax):
    ts = np.asarray(ts, float); out = []
    for h in range(1, hmax+1):
        x, y = ts[:-h], ts[h:]
        A = np.column_stack([np.ones_like(x), x])
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ c
        den = np.sum((y-y.mean())**2)
        out.append(1.0 if den <= 0 else float(1-np.sum((y-pred)**2)/den))
    return np.array(out)

def echo_horizon(curve, q):
    w = np.where(curve < q)[0]
    return float(w[0]+1) if len(w) else float('nan')

def d2_of(ts, m=5, seed=0):
    ts = np.asarray(ts, float)
    if np.std(ts) < 1e-12: return float('nan')
    ac = np.correlate(ts-ts.mean(), ts-ts.mean(), 'full')[len(ts)-1:]
    if ac[0] <= 0: return float('nan')
    ac = ac/ac[0]; w = np.where(ac < 0.2)[0]
    tau = max(1, int(w[0]) if len(w) else 1)
    N = len(ts)-(m-1)*tau
    if N < 400: return float('nan')
    E = np.stack([ts[i*tau:i*tau+N] for i in range(m)], axis=1)
    rng = np.random.default_rng(seed)
    n = min(1200, N); sel = rng.choice(N, size=n, replace=False)
    P = E[sel]
    D = np.linalg.norm(P[:, None, :]-P[None, :, :], axis=2)
    d = D[np.triu_indices(n, k=1)]; d = d[d > 1e-12]
    if len(d) < 200: return float('nan')
    lo, hi = np.percentile(d, [1, 60])
    if not np.isfinite(lo) or hi <= lo: return float('nan')
    r = np.exp(np.linspace(np.log(lo), np.log(hi), 20))
    C = np.array([np.mean(d <= ri) for ri in r])
    ok = (C > 0.02) & (C < 0.98)
    if ok.sum() < 5: return float('nan')
    return float(np.polyfit(np.log(r[ok]), np.log(C[ok]), 1)[0])

def make_sweep(sw):
    S = []
    for r in np.linspace(3.55, 4.0, sw):
        S.append(Sys('logistic', f'r={r:.2f}', *logmap(float(r))))
    for r in np.linspace(2.4, 3.6, sw):
        S.append(Sys('clogistic', f'r={r:.2f}', *clog(float(r), 0.3)))
    for a in np.linspace(0.8, 1.4, sw):
        S.append(Sys('henon', f'a={a:.2f}', *henon(float(a))))
    S.append(Sys('lorenz', 'lorenz', *lorenz()))
    S.append(Sys('rossler', 'rossler', *rossler()))
    for m in [0, 1, 2, 4, 8, 16]:
        f, J, dt, k, d = lorenz()
        S.append(Sys('lorenz_pad', f'pad={m}', f, J, dt, k, d+int(m),
                     active=d, pad=int(m)))
    for n in [2, 3, 5, 8]:
        S.append(Sys('chain', f'n={n}', *chain(3.6, 0.1, int(n))))
    return S

def run(s, seed, nstep=6000, nburn=2000):
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0.1, 0.9, s.d)
    if s.pad > 0:
        sub = Sys(s.fam, s.name, s.f, s.J, s.dt, s.kind, s.active)
        traj0 = sub.integrate(x0[:s.active], nstep, nburn)
        lam = sub.lyap(x0[:s.active], 4000, 0)
        pad = x0[s.active:]
        traj = np.hstack([traj0, np.tile(pad, (len(traj0), 1))])
        d = s.active
    else:
        traj = s.integrate(x0, nstep, nburn)
        lam = s.lyap(x0, 4000, 0)
        d = s.d
    ts = traj[:, 0].astype(float)
    if np.std(ts) < 1e-10: return None
    curve = acc_curve(ts, min(300, len(ts)//8))
    H = {f'H{q}': echo_horizon(curve, q) for q in (0.9, 0.75, 0.5, 0.25)}
    return dict(fam=s.fam, name=s.name, d=int(d), pad=int(s.pad),
                lam=float(lam), D2=float(d2_of(ts)),
                curve=[float(v) for v in curve], **H)

def mode_main():
    sw = int(os.environ.get('SWEEP_N', '12'))
    S = make_sweep(sw)
    print('systems', len(S), flush=True)
    rows, drop = [], []
    for i, s in enumerate(S):
        try:
            r = run(s, i)
        except Exception as e:
            r = None; drop.append(dict(fam=s.fam, name=s.name, err=repr(e)))
        if r is None:
            drop.append(dict(fam=s.fam, name=s.name, err='degenerate')); continue
        fl = []
        if not np.isfinite(r['lam']) or r['lam'] <= 0.02: fl.append('not_chaotic')
        if not np.isfinite(r['D2']) or r['D2'] < 0.25: fl.append('no_scaling')
        if not np.isfinite(r['H0.5']): fl.append('no_horizon')
        if fl: r['flags'] = fl; drop.append(r)
        else: rows.append(r)
        if (i+1) % 20 == 0: print(i+1, 'kept', len(rows), flush=True)
    print('kept', len(rows), 'dropped', len(drop), flush=True)
    json.dump(rows, open('eh2_rows.json', 'w'), indent=1)
    json.dump(drop, open('eh2_drop.json', 'w'), indent=1, default=str)

def mode_noise():
    tests = [('logistic', Sys('logistic', 'r=3.96', *logmap(3.96))),
             ('henon', Sys('henon', 'a=1.40', *henon(1.40))),
             ('lorenz', Sys('lorenz', 'lorenz', *lorenz()))]
    out = []
    for fam, s in tests:
        reps = []
        for seed in range(10):
            try:
                r = run(s, seed)
            except Exception:
                r = None
            if r: reps.append(r)
        for key in ('lam', 'D2', 'H0.9', 'H0.75', 'H0.5', 'H0.25'):
            v = np.array([rr[key] for rr in reps], float)
            v = v[np.isfinite(v)]
            rel = float(np.std(v)/abs(np.median(v))) if len(v) and abs(np.median(v)) > 0 else float('nan')
            out.append(dict(fam=fam, name=s.name, key=key, n=len(v),
                            med=float(np.median(v)) if len(v) else float('nan'),
                            std=float(np.std(v)) if len(v) else float('nan'), rel=rel))
        print(fam, 'replicates', len(reps), flush=True)
    json.dump(out, open('eh2_noise.json', 'w'), indent=1)
    for o in out:
        print(f"{o['fam']:9s} {o['name']:8s} {o['key']:5s} med={o['med']:+.3f} std={o['std']:.3f} rel={o['rel']:.2%}", flush=True)

if __name__ == '__main__':
    (mode_main if os.environ.get('MODE', 'main') == 'main' else mode_noise)()
