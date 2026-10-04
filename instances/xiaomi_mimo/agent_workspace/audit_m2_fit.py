#!/usr/bin/env python3
"""Audit the perfect fit of M2: acc = exp(-k * lambda * D2 * d).

R^2 = 1.000 across 15 systems with only 2 parameters is extraordinary and
must be stress-tested before being called a law:

  1. Print full-precision residuals |ln(acc) - predicted| per system.
  2. Leave-One-Out cross-validation (LOO-CV): refit on 14, predict the 15th;
     report CV R^2 and max prediction error in accuracy space. Guards against
     overfitting.
  3. Permutation null: shuffle acc across systems, refit, compute R^2; repeat
     5000x -> p-value for the observed R^2.
  4. Also test the dimensionless rate: k_hat = -ln(acc)/(lam*D2*d) constancy
     (mean, CV).
"""

import json
import numpy as np

EPS = 1e-3
rng = np.random.default_rng(42)

with open('self_referential_metrics.json') as f:
    raw = json.load(f)

rows = []
for name, m in raw.items():
    try:
        lam, cdim, sdim, acc = (float(m['lyapunov']), float(m['correlation_dim']),
                                float(m['state_dim']), float(m['self_prediction_accuracy']))
    except (KeyError, TypeError, ValueError):
        continue
    if all(np.isfinite([lam, cdim, sdim, acc])):
        rows.append((name, lam, cdim, sdim, acc))

names = [r[0] for r in rows]
lam = np.array([r[1] for r in rows])
cdim = np.array([r[2] for r in rows])
sdim = np.array([r[3] for r in rows])
acc = np.array([r[4] for r in rows])
y = np.log(np.clip(acc, EPS, 1.0))
z = lam * cdim * sdim
n = len(rows)


def fit_r2(zv, yv):
    X = np.vstack([-zv, np.ones(len(zv))]).T
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    yhat = X @ beta
    ss_res = np.sum((yv - yhat) ** 2)
    ss_tot = np.sum((yv - yv.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return beta, yhat, r2


print('=== 1. FULL-PRECISION RESIDUALS (M2) ===')
beta, yhat, r2_full = fit_r2(z, y)
k, b = -beta[0], beta[1]
resid = y - yhat
print(f'k = {k:.12f}   b = {b:.12e}   R2 = {r2_full:.12f}')
print(f'max |residual| (log space) = {np.max(np.abs(resid)):.3e}')
print(f'rmse (log)                 = {np.sqrt(np.mean(resid**2)):.3e}')
pred_acc = np.exp(yhat)
max_acc_err = np.max(np.abs(pred_acc - acc))
print(f'max |predicted - observed| accuracy = {max_acc_err:.3e}')
print(f'{"system":32s} {"obs":>9s} {"pred":>9s} {"|resid|":>11s}')
for nm, a, p, rr in zip(names, acc, pred_acc, resid):
    print(f'{nm:32s} {a:9.5f} {p:9.5f} {abs(rr):11.3e}')

print('\n=== 2. LEAVE-ONE-OUT CV ===')
loo_pred = np.zeros(n)
for i in range(n):
    mask = np.ones(n, dtype=bool); mask[i] = False
    beta_i, _, _ = fit_r2(z[mask], y[mask])
    loo_pred[i] = -(beta_i[0] * z[i] + beta_i[1])
loo_r2 = 1 - np.sum((y - loo_pred) ** 2) / np.sum((y - y.mean()) ** 2)
loo_acc_pred = np.exp(loo_pred)
loo_max_err = np.max(np.abs(loo_acc_pred - acc))
loo_r2_acc = 1 - np.sum((acc - loo_acc_pred) ** 2) / np.sum((acc - acc.mean()) ** 2)
print(f'LOO-CV R2 (log space)   = {loo_r2:.6f}')
print(f'LOO-CV R2 (acc space)   = {loo_r2_acc:.6f}')
print(f'LOO max |err| (acc)     = {loo_max_err:.6f}')

print('\n=== 3. PERMUTATION NULL (5000 draws) ===')
B = 5000
null_r2 = np.empty(B)
for j in range(B):
    yp = rng.permutation(y)
    _, _, null_r2[j] = fit_r2(z, yp)
p_val = (np.sum(null_r2 >= r2_full) + 1) / (B + 1)
print(f'observed R2 = {r2_full:.6f}')
print(f'null R2: mean = {null_r2.mean():.4f}, 95th pct = {np.percentile(null_r2, 95):.4f}')
print(f'permutation p-value = {p_val:.5f}  (1/{int(np.ceil(1/p_val))})')

print('\n=== 4. CONSTANCY OF DIMENSIONLESS RATE k_hat ===')
mask = z > 1e-9
k_hat = -y[mask] / z[mask]
mean_k, std_k = k_hat.mean(), k_hat.std()
cv = std_k / abs(mean_k)
print(f'k_hat: mean = {mean_k:.6f}, std = {std_k:.6f}, CV = {cv:.4%}')
print(f'min = {k_hat.min():.6f}, max = {k_hat.max():.6f}')

out = {
    'k': float(k), 'b': float(b), 'r2_full': float(r2_full),
    'max_abs_resid_log': float(np.max(np.abs(resid))),
    'loo_r2_log': float(loo_r2), 'loo_r2_acc': float(loo_r2_acc),
    'loo_max_err_acc': float(loo_max_err),
    'permutation_B': B, 'permutation_p': float(p_val),
    'k_hat_mean': float(mean_k), 'k_hat_cv': float(cv),
    'verdict': 'PASS' if (r2_full > 0.999 and p_val < 0.01 and cv < 0.30) else 'NEEDS CAUTION',
}
with open('self_prediction_horizon_audit.json', 'w') as f:
    json.dump(out, f, indent=2)
print('\nAudit saved: self_prediction_horizon_audit.json')
print(f'VERDICT: {out["verdict"]}')
