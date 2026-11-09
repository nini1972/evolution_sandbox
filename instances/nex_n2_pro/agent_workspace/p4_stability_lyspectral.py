#!/usr/bin/env python3
"""
DECISIVE STABILITY TEST for the period-4 tongue.

Question: is the P4 state a GENUINELY STABLE period-4 orbit (a real attractor)
or a weakly-chaotic / near-locked orbit that only *looks* period-4 because of
finite precision or long transients?

Three complementary probes, all on the canonical ring-coupled logistic lattice:

    x_i(t+1) = (1-eps)*g(x_i) + (eps/2)*[ g(x_{i-1}) + g(x_{i+1}) ],  g(x)=r*x*(1-x)

(1) MAX LYAPUNOV EXPONENT (Benettin, leading vector) + leading-8 QR spectrum.
    - lambda_max < 0  => asymptotically stable orbit (true attractor).
    - lambda_max ~ 0 or > 0 => near-lock / chaotic / saddle (P4 is not an attractor).
    For a genuine discrete period-4 attractor we expect ALL exponents <= 0,
    the leading one clearly negative, and a spectrum with a "zero" only if the
    orbit carries a continuous parameter (it should not for an isolated orbit).

(2) LONG-TRANSIENT PERIODICITY. Iterate T=4*10^5 steps, then check
    x(t+4)=x(t) residual vs x(t+2)=x(t) residual. A true P4 has
    res4 ~ O(eps_machine) and res2 >> res4 (definitely not period-2).

(3) PRECISION ROBUSTNESS. Run the same cell in float64 AND longdouble (eps~1e-19)
    from the same seed; compare the locked 4-tuple. If identical to ~1e-15 the
    state is numerically robust; if it drifts by O(1e-6..) the 'period-4' is a
    precision artifact (weak lock).

Cells tested (ring core from N-independence job + tongue_diagnostic anchor):
    (r=3.865, eps=0.132)  diagnostic anchor
    (r=3.87,  eps=0.136)  core cell
    (r=3.88,  eps=0.144)  core cell
"""
import json
import numpy as np

N = 120
rng = np.random.default_rng

def g(x, r):
    return r*x*(1.0-x)

def coupled(x, r, eps):
    f = g(x, r)
    return (1.0-eps)*f + (0.5*eps)*(np.roll(f,1)+np.roll(f,-1))

def jacobian(x, r, eps, dtype=np.float64):
    gp = r*(1.0-2.0*x).astype(dtype)
    n = x.size
    J = np.zeros((n,n), dtype=dtype)
    i = np.arange(n)
    J[i,i] = (1.0-eps)*gp
    J[i,(i-1)%n] = (0.5*eps)*np.roll(gp,1)
    J[i,(i+1)%n] = (0.5*eps)*np.roll(gp,-1)
    return J

def lyapunov(r, eps, trans, T, dtype=np.float64, nvec=8, seed=0):
    """Benettin. Returns (lambda_max, leading exponents list)."""
    x = rng(seed).random(N).astype(dtype)
    for _ in range(trans):
        x = coupled(x, r, eps).astype(dtype)
    one = np.ones(N, dtype=dtype)
    V = rng(seed+1).random((N,nvec)).astype(dtype)
    V = (V - V.mean(0,keepdims=True))/ (np.linalg.norm(V,axis=0)+1e-300)
    # QR-orthogonalize
    Q,R = np.linalg.qr(V); V = Q
    acc_max = dtype(0.0)
    acc = np.zeros(nvec, dtype=np.float64)
    step = 20  # re-orthogonalize every step (cheap for nvec=8)
    for t in range(T):
        x = coupled(x, r, eps).astype(dtype)
        J = jacobian(x, r, eps, dtype)
        V = (J.astype(np.float64) @ V)
        norm0 = np.linalg.norm(V[:,0])
        acc_max += np.log(norm0+1e-300)
        Q,R = np.linalg.qr(V)
        for k in range(nvec):
            acc[k] += np.log(abs(R[k,k])+1e-300)
        V = Q
    return float(acc_max/T), (acc/T).tolist()

def periodicity(r, eps, trans, T, seed=0):
    x = rng(seed).random(N)
    for _ in range(trans):
        x = coupled(x, r, eps)
    # capture a long tail
    tail = np.empty((T, N))
    for t in range(T):
        x = coupled(x, r, eps)
        tail[t] = x
    s = T-4000  # steady window
    base = tail[s]
    res4 = np.max(np.abs(tail[s+4: s+8000:4] - base[s % 1])) if False else None
    # simpler: x at phase offsets
    a = tail[s]            # phase 0
    a2 = tail[s+2]
    a4 = tail[s+4]
    # check periodicity by comparing a window 4 apart vs 2 apart
    w = 8000
    seg0 = tail[s:s+w]
    res4 = float(np.max(np.abs(seg0 - np.roll(seg0, -4, axis=0))))
    res2 = float(np.max(np.abs(seg0 - np.roll(seg0, -2, axis=0))))
    res1 = float(np.max(np.abs(seg0 - np.roll(seg0, -1, axis=0))))
    # 4-tuple spread (P4 amplitude)
    tup = np.array([tail[s], tail[s+1], tail[s+2], tail[s+3]])
    spread = float(np.max(np.abs(tup - tup[0])))
    return dict(res1=res1, res2=res2, res4=res4, spread=spread,
                period_is_4=(res4 < 1e-6 and res2 > 1e-3),
                not_period_2=(res2 > 1e-3))

def precision(r, eps, trans, seed=0):
    def lock(dtype):
        x = rng(seed).random(N).astype(dtype)
        for _ in range(trans):
            x = coupled(x, r, eps).astype(dtype)
        P = np.empty((N,4), dtype=dtype)
        for k in range(4):
            P[:,k] = x
            x = coupled(x, r, eps).astype(dtype)
        return P
    P64 = lock(np.float64)
    PLD = lock(np.longdouble)
    # compare 4-tuples in float64 space
    d = float(np.max(np.abs(PLD.astype(np.float64) - P64)))
    return dict(P64=P64, PLD=PLD, max_abs_diff_f64=d,
                robust=(d < 1e-9))

CELLS = [(3.865,0.132),(3.87,0.136),(3.88,0.144)]

out = {}
for (r,eps) in CELLS:
    key = f"r{r}_eps{eps}"
    print(f"\n===== cell {key}  (N={N}, ring) =====")
    lam, spec = lyapunov(r, eps, trans=20000, T=60000, nvec=8)
    print(f"  lambda_max = {lam:+.6e}   leading8 = {[f'{s:+.3e}' for s in spec[:4]]}")
    per = periodicity(r, eps, trans=20000, T=12000)
    print(f"  periodicity: res1={per['res1']:.2e} res2={per['res2']:.2e} res4={per['res4']:.2e} spread={per['spread']:.4f}")
    print(f"  period_is_4={per['period_is_4']}  not_period_2={per['not_period_2']}")
    prec = precision(r, eps, trans=20000)
    print(f"  precision f64 vs ld: max|diff|={prec['max_abs_diff_f64']:.3e} robust={prec['robust']}")
    P4head = [f"{v:.6f}" for v in prec['P64'][0]]
    print(f"  4-tuple cell0: {P4head}")
    out[key] = dict(r=r, eps=eps, lambda_max=lam, lyap_spec=spec,
                    **per, **{k:v for k,v in prec.items() if k!='P64' and k!='PLD'},
                    tuple_cell0=[float(v) for v in prec['P64'][0]])

# verdict
print("\n\n================ VERDICT ================")
for key,v in out.items():
    stable = v['lambda_max'] < -1e-5
    p4 = v['period_is_4']
    rob = v['robust']
    label = "STABLE P4 ATTRACTOR" if (stable and p4 and rob) else \
            ("NEAR-LOCK / WEAK (lambda~0)" if p4 and not stable else "NOT A P4 ATTRACTOR")
    print(f"  {key}: lambda_max={v['lambda_max']:+.3e} P4={p4} robust={rob} -> {label}")

with open('p4_stability_lyspectral.json','w') as f:
    json.dump(out, f, indent=2)
print("\nsaved p4_stability_lyspectral.json")
