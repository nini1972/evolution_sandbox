import numpy as np
import c39_lobe_injection as m

rhos = [1e-4, 2e-4, 4e-4, 8e-4, 1.6e-3, 3.2e-3]
As = [6., 8., 10.]; ws = [1.5, 3.]; Ds = [0., 0.9]
N = 2048; nreal = 6
feas = tot = 0
for rho in rhos:
    for A in As:
        for w in ws:
            for D in Ds:
                tot += 1
                rng = np.random.default_rng(7)
                ok = True
                for _ in range(nreal):
                    I, nl, mm, cm = m.field_realization(N, rho, A, w, D, rng)
                    if I is None:
                        ok = False; break
                feas += ok
print('feasible %d/%d grid cells' % (feas, tot))

rng = np.random.default_rng(3)
Is = []
for _ in range(32):
    I, nl, mm, cm = m.field_realization(4096, 8e-4, 10., 3., 0.9, rng)
    Is.append(I)
st = m.tail_stats(np.concatenate(Is))
print('rep cell rho=8e-4 A=10 w=3 D=0.9:')
print('  kurt=%.3f dens6=%.3e cond=%.4f mu=%.3f R2dip=%.3f R5bump=%.3f' % (
    st['kurt'], st['dens6'], st['cond_exc'], st['mu'], st['R2dip'], st['R5bump']))
print('  R:', {k: round(v, 3) for k, v in st['R'].items()})

tgt = {'R2dip': -0.05, 'R5bump': 0.08, 'kurt': 2.0,
       'R': {'9': 1.05}, 'dens6': 2e-3, 'cond_exc': 0.01}
s, d = m.score_cell(st, tgt)
print('score test: max_dev_units=%.2f' % s,
      {k: round(v, 2) for k, v in d.items()})
print('SMOKE_OK')
