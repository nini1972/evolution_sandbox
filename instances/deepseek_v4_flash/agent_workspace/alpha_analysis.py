import json, numpy as np
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

r = json.load(open('barrier_sweep.json'))
model = r['model']
rows = r['rows']
N = np.array([x['N'] for x in rows], float)
esc = np.array([x['n_escaped'] for x in rows], float)
M = np.array([x['M'] for x in rows], float)
Tmax = model['Tmax']
K0 = model['K0']; alpha = model['alpha']; sigma = model['sigma']

# ---- potential / barrier ----
def f(R):
    return R*(K0*R**alpha*(1-R**2) - sigma**2)

# V(R) = -∫_0^R f dR'  (with V(0)=0)
def V(R):
    return -(K0*R**(alpha+2)/(alpha+2) - K0*R**(alpha+4)/(alpha+4) - sigma**2*R**2/2)
