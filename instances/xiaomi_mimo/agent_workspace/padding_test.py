#!/usr/bin/env python3
"""Challenge #2 test: does the d-factor in z = lambda * D2 * d survive
embedding-dimension padding? Also expose the amplitude confound between
lambda (mean |dx|) and D2 (mean temporal std)."""
import json, numpy as np
from types import SimpleNamespace
from self_referential_systems import (create_self_referential_library,
                                      SelfReferentialSystem)

rng = np.random.default_rng(42)
systems = create_self_referential_library()

def metrics_of(states, self_model, n_obs, n_vars, param_history):
    obj = SimpleNamespace(state_history=list(states), self_model=self_model,
                          observation_count=n_obs, n_vars=n_vars,
                          param_history=list(param_history))
    return SelfReferentialSystem.compute_metrics(obj)

def pad_states(states, d_pad, mode):
    """Return states padded from d0 -> d0+d_pad coords."""
    d0 = states.shape[1]
    if mode == 'zero':
        extra = np.zeros((len(states), d_pad))
    else:  # noise: same mean/std per coord as coord 0 (matched stochastic padding)
        s = states[:, 0].std() or 1.0
        extra = rng.normal(states[:, 0].mean(), s, (len(states), d_pad))
    return np.hstack([states, extra])

def pad_model(model, d_pad, mode, states):
    """Pad self-model mean consistently with the state padding."""
    if model is None:
        return None
    m = dict(model)
    mean = np.asarray(model['mean'], float)
    if mode == 'zero':
        extra = np.zeros(d_pad)
    else:
        extra = np.full(d_pad, states[:, 0].mean())
    m['mean'] = np.concatenate([mean, extra])
    return m

results = {}
print(f"{'system':32s} {'pad':6s} {'d':>4s} {'z=lambda*D2*d':>14s} {'dz/z0':>8s} {'A=z*acc':>9s} {'dA/A0':>8s}")
for sys in systems:
    name = getattr(sys, 'name', type(sys).__name__)
    sys.run(steps=500)
    st = np.asarray(sys.state_history, dtype=float)
    d0 = st.shape[1]
    base = metrics_of(st, sys.self_model, sys.observation_count, sys.n_vars,
                      sys.param_history)
    z0 = base['lyapunov'] * base['correlation_dim'] * d0
    A0 = z0 * base['self_prediction_accuracy']
    results[name] = {'d0': d0, 'z0': z0, 'A0': A0, 'variants': []}
    for mode in ('zero', 'noise'):
        for d_pad in (2, 7, 17, 47):
            stp = pad_states(st, d_pad, mode)
            mdl = pad_model(sys.self_model, d_pad, mode, st)
            m = metrics_of(stp, mdl, sys.observation_count,
                           d0 + d_pad, sys.param_history)
            z = m['lyapunov'] * m['correlation_dim'] * (d0 + d_pad)
            A = z * m['self_prediction_accuracy']
            results[name]['variants'].append(
                {'mode': mode, 'd': d0 + d_pad, 'z': z, 'A': A,
                 'dz_rel': (z - z0) / z0, 'dA_rel': (A - A0) / A0})
            print(f"{name:32s} {mode:6s} {d0+d_pad:4d} {z:14.4f} "
                  f"{(z-z0)/z0:8.1%} {A:9.4f} {(A-A0)/A0:8.1%}")

# amplitude confound: lambda vs D2 correlation
lam = np.array([metrics_of(np.asarray(s.state_history, float), s.self_model,
                           s.observation_count, s.n_vars, s.param_history)['lyapunov']
                for s in systems])
# recompute D2 directly (mean temporal std) for clarity
d2 = np.array([np.mean(np.std(np.asarray(s.state_history, float), axis=0))
               for s in systems])
r = np.corrcoef(lam, d2)[0, 1]
print(f"\nAmplitude confound: corr(lambda=mean|dx|, D2=mean temporal std) = {r:.4f}")

json.dump({'per_system': results, 'corr_lam_d2': float(r)},
          open('padding_test_results.json', 'w'), indent=1)
print("saved padding_test_results.json")