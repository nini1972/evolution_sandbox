import sys; sys.path.insert(0, '.')
from worldc_sweep import Simulation
import numpy as np

for seed in range(100, 106):
    s = Simulation({'A':0.75,'sigma_e':0.3,'rho':0.5,'sigma_cue':0.3,'L':16,'K':80,'generations':20,'burn_in':5,'d_max':10,'seed':seed})
    for t in range(1, 21):
        s.update_environment(t)
        ok = s.step(t)
        if not ok:
            print('seed', seed, 'died at t', t)
            break
        alive = s.alive.sum()
        ncell = np.bincount(s.cell_id[s.alive], minlength=s.L*s.L)
        over = (ncell > s.K).sum()
        if over:
            print('seed', seed, 't', t, 'overfull cells', over, 'max', ncell.max())
    print('seed', seed, 'final', s.history[-1]['N'])
