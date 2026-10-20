#!/usr/bin/env python3
"""Map FLOAT orbit period vs SYMBOLIC (binarized) shadow period across the P4
tongue. Tests whether ANY region has genuine symbolic period-4, vs float-P4
whose bit shadow is P2 (amplitude breathing invisible to thresholding)."""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def float_period(x, r, eps, kmax=8):
    """Smallest k in 1..kmax with x(t+k) ~= x(t) in float; else 'chaotic'."""
    x0 = x
    best = None
    for k in range(1, kmax + 1):
        y = x.copy()
        for _ in range(k):
            y = step(y, r, eps)
        d = float(np.max(np.abs(y - x0)))
        if d < 1e-6:
            return k, d
        if best is None or d < best[1]:
            best = (k, d)
    return best  # (k, d)  -> chaotic-ish; d is the best residual

def symbol_period(x, r, eps, N=100, T=600):
    """Shadow period under global-median binarization, using per-site flip
    fractions at lag 1,2,4 (exact, over all sites)."""
    traj = [x.copy()]
    xt = x.copy()
    for _ in range(T):
        xt = step(xt, r, eps)
        traj.append(xt)
    traj = np.array(traj[1:])  # steady
    gmed = np.median(traj)
    b = (traj > gmed).astype(np.int8)
    def flip(k):
        if T - k < 10: return 0.5
        return float(np.mean(b[:-k] != b[k:]))
    f1, f2, f4 = flip(1), flip(2), flip(4)
    # period classification: f_k ~ 0 => period divides k; f_k ~ 1 => antiphase
    if f4 < 0.01 and f2 < 0.01:
        sp = 1
    elif f4 < 0.01 and f2 > 0.5:
        sp = 2
    elif f4 < 0.01 and f2 < 0.1 and f1 > 0.5:
        sp = 4  # genuine symbolic P4: repeats only at 4
    elif f4 < 0.05:
        sp = 4 if f2 < 0.2 else 2
    else:
        sp = 0  # 0 = not locked (chaotic/long)
    return sp, f1, f2, f4

def breathing(x, r, eps):
    """S0 vs S2 max distance (sub-symbolic amplitude breathing)."""
    S0 = x.copy()
    S2 = step(step(S0, r, eps), r, eps)
    return float(np.max(np.abs(S2 - S0)))

rs = np.round(np.arange(3.84, 3.9001, 0.01), 3)
es = np.round(np.arange(0.10, 0.1801, 0.01), 3)
N, seed, transient = 100, 42, 1000

rows = []
for r in rs:
    for eps in es:
        np.random.seed(seed)
        x = np.random.rand(N)
        for _ in range(transient):
            x = step(x, r, eps)
        fp, d = float_period(x, r, eps)
        sp, f1, f2, f4 = symbol_period(x, r, eps)
        br = breathing(x, r, eps)
        rows.append((r, eps, fp, round(d, 4), sp, round(f1,3), round(f2,3), round(f4,3), round(br,4)))

print(f"{'r':>6s} {'eps':>5s} {'floatP':>7s} {'d':>7s} {'symP':>5s} {'f1':>6s} {'f2':>6s} {'f4':>6s} {'breath':>7s}")
for row in rows:
    print(f"{row[0]:6.3f} {row[1]:5.3f} {str(row[2]):>7s} {row[3]:7.4f} {row[4]:5d} "
          f"{row[5]:6.3f} {row[6]:6.3f} {row[7]:6.3f} {row[8]:7.4f}")

# summarize regimes
f4s2 = [(r, e) for (r, e, fp, d, sp, *_rest) in rows if fp == 4 and sp == 2]
f4s4 = [(r, e) for (r, e, fp, d, sp, *_rest) in rows if fp == 4 and sp == 4]
print(f"\nfloat-P4 & sym-P2 (shadow folding): {len(f4s2)} pts {f4s2[:8]}")
print(f"float-P4 & sym-P4 (true symbolic P4): {len(f4s4)} pts {f4s4[:8]}")</think>

<tool_call>
<function=run_command>
<parameter=command>
cd /home/runner/work/evolution_sandbox/evolution_sandbox/instances/nex_n2_pro/agent_workspace && python shadow_map.py 2>&1