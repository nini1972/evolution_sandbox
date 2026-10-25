import importlib.util, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

import kimi_worldc_sweep as mod

out_dir = Path('verify_local_out')
out_dir.mkdir(exist_ok=True)

param_grid = {
    'A': [0.0, 1.0],
    'sigma_e': [0.0, 0.4],
    'rho': [0.0],
    'sigma_cue': [0.0],
}

df = mod.run_sweep(param_grid, replicates=2, n_workers=4)
print('shape', df.shape)
print(df[['A','sigma_e','rho','sigma_cue','alpha','beta','h0','hb']].head())
df.to_csv(out_dir/'results.csv', index=False)

traits = ['alpha','beta','h0','hb']
X = np.column_stack((np.ones(len(df)), df['A'], df['sigma_e'], df['rho'], df['sigma_cue']))
for trait in traits:
    y = df[trait].values
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    r2 = 1 - np.sum((y-pred)**2)/np.sum((y-y.mean())**2)
    print(trait, coef, r2)

# plot
fig, ax = plt.subplots()
y = df['alpha'].values
coef = np.linalg.lstsq(X, y, rcond=None)[0]
pred = X @ coef
ax.scatter(pred, y)
ax.plot([pred.min(), pred.max()], [pred.min(), pred.max()], 'k--')
fig.savefig(out_dir/'alpha_fit.png')
print('done')
