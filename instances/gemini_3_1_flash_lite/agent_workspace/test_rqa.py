import numpy as np
from colony_lib.dynamics import GrayScott2D
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

def get_gs_timeseries(f, k, steps=1000, grid_size=64):
    gs = GrayScott2D(size=(grid_size, grid_size), f=f, k=k)
    gs.u[:] = 1.0
    gs.v[:] = 0.0
    gs.v[32-5:32+5, 32-5:32+5] = 0.5
    gs.u[32-5:32+5, 32-5:32+5] = 0.5
    
    ts = []
    for _ in range(steps):
        gs.step()
        ts.append(gs.v.mean())
    return np.array(ts)

f_vals = [0.03, 0.04]
k_val = 0.06

for f in f_vals:
    ts = get_gs_timeseries(f, k_val)
    # RQA
    embedded = takens_embedding(ts, m=3, tau=1)
    R = recurrence_matrix(embedded, epsilon=0.01)
    rqa = compute_rqa_metrics(R)
    print(f"f={f}: DET={rqa['DET']:.4f}")
