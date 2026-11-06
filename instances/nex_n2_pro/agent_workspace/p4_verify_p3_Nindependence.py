#!/usr/bin/env python3
"""P3 (N-independence) + P2 (amplitude-encoding restores P4) self-verification.

FIXED BUG from v1: state list must copy arrays (v1 aliased x -> all gaps 0).
N=100 column is validated against the canonical sweep
(p4_robustness/p4_float_vs_binary_grid.json) which must reproduce exactly.
"""
import numpy as np, json, os

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

T_settle, T_rec, seed = 2000, 2000, 42

def analyze(r, eps, N):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(T_settle):
        x = step(x, r, eps)
    S0 = x.copy(); x = step(x, r, eps); S1 = x.copy()
    x = step(x, r, eps); S2 = x.copy();   x = step(x, r, eps); S3 = x.copy()
    x4 = step(step(step(step(S0, r, eps), r, eps), r, eps), r, eps)
    d4 = np.max(np.abs(x4 - S0))
    d2 = np.max(np.abs(S2 - S0))
    float_period4 = (d4 < 1e-6) and (d2 > 1e-3)

    # --- canonical binary census (global median over full trajectory) ---
    traj = np.empty((T_rec, N))
    t = S3
    for k in range(T_rec):
        t = step(t, r, eps)
        traj[k] = t
    gmed = np.median(traj)
    bits = (traj > gmed)
    m1 = (bits[1:] == bits[:-1]).all(axis=1).mean()
    m2 = (bits[2:] == bits[:-2]).all(axis=1).mean()
    m4 = (bits[4:] == bits[:-4]).all(axis=1).mean()
    binary_period = 1 if m1 > 0.99 else (2 if m2 > 0.99 and m1 < 0.01 else (4 if m4 > 0.99 and m2 < 0.5 else 'chaos/mixed'))

    # --- P2 probe: amplitude-sensitive encoding on the SAME trajectory ---
    # A(t) = lattice mean; encode dA(t)=A(t+2)-A(t); period-4 in float space
    # means dA alternates sign with period 4 (up/down/up/down cycle).
    A = traj.mean(axis=1)
    dA = A[2:] - A[:-2]                 # length T_rec-2
    sign = np.sign(dA)
    nonz = sign != 0
    if nonz.mean() > 0.5:
        s = sign[nonz]
        alt4 = (s[4:] == s[:-4]).mean()      # period-4 consistency
        alt2 = (s[2:] == s[:-2]).mean()      # period-2 consistency
        amp_p4 = bool(alt4 > 0.99 and alt2 < 0.5)
    else:
        alt4 = alt2 = np.nan
        amp_p4 = False

    return dict(r=r, eps=eps, N=N, float_period4=bool(float_period4),
                d4=float(d4), d2=float(d2), binary_period=binary_period,
                m1=float(m1), m2=float(m2), m4=float(m4),
                degen_gap=float(d2),
                alt4=float(alt4), alt2=float(alt2), amp_p4=amp_p4,
                hidden_p4=bool(float_period4 and binary_period == 2))

gr = [3.860, 3.865, 3.875, 3.900, 3.915, 3.925]
ge = [0.126, 0.132, 0.138, 0.144]
Ns = [80, 100, 120, 200]
out = []
for N in Ns:
    for r in gr:
        for e in ge:
            d = analyze(r, e, N)
            out.append(d)

# ---- validate N=100 against canonical ----
canon = json.load(open('p4_robustness/p4_float_vs_binary_grid.json'))
cmap = {(z['r'], z['eps']): z for z in canon}
print("=== VALIDATION N=100 vs canonical ===")
bad = 0
for d in [d for d in out if d['N'] == 100]:
    c = cmap.get((d['r'], d['eps']))
    ok = c and c['float_period4'] == d['float_period4'] and c['binary_period'] == d['binary_period']
    ok = ok and abs(c['d2'] - d['d2']) < 1e-9
    if not ok:
        bad += 1
        print(f"  MISMATCH r={d['r']} eps={d['eps']}: canon fP4={c['float_period4']}/{c['binary_period']} vs new fP4={d['float_period4']}/{d['binary_period']}")
print(f"mismatches: {bad}/24  -> {'VALIDATED' if bad==0 else 'NOT VALIDATED'}")

print("\n=== N-INDEPENDENCE (P3) ===")
for N in Ns:
    rows = [d for d in out if d['N'] == N]
    fp  = [d for d in rows if d['float_period4']]
    hid = [d for d in fp if d['binary_period'] == 2]
    gaps = [d['d2'] for d in hid]
    inband = [g for g in gaps if 0.155 <= g <= 0.190]
    print(f"N={N:3d}: floatP4={len(fp):2d}/24  hiddenP4(fP4+binP2)={len(hid):2d}/24  "
          f"gap[min,max]={'['+f'{min(gaps):.4f},{max(gaps):.4f}'+']' if gaps else 'n/a'}  "
          f"inband[0.155,0.190]={len(inband)}/{len(gaps)}")
    # exact set agreement with N=100?
print("\nset identity of hidden-P4 (r,eps) pairs vs N=100:")
base = { (d['r'], d['eps']) for d in out if d['N'] == 100 and d['hidden_p4'] }
for N in [80, 120, 200]:
    s = { (d['r'], d['eps']) for d in out if d['N'] == N and d['hidden_p4'] }
    print(f"  N={N:3d}: {len(s)} pts, same as N=100: {s == base}, diff={s ^ base if s != base else 'none'}")

print("\n=== P2 PROBE: amplitude encoding on hidden-P4 (N=100) ===")
hid100 = [d for d in out if d['N'] == 100 and d['hidden_p4']]
ok2 = sum(1 for d in hid100 if d['amp_p4'])
print(f"amplitude P4 restored on hidden-P4 points: {ok2}/{len(hid100)}")
for d in hid100:
    print(f"  r={d['r']:.3f} eps={d['eps']:.3f} binP2={d['binary_period']} alt4={d['alt4']:.3f} alt2={d['alt2']:.3f} ampP4={d['amp_p4']}")

os.makedirs('p4_robustness', exist_ok=True)
with open('p4_robustness/p4_verify_p2p3.json', 'w') as f:
    json.dump(out, f, indent=2)
print("\nsaved p4_robustness/p4_verify_p2p3.json")