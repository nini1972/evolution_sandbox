"""Q-conservation suite v2: exact-QR Lyap + robust GP D2 + K-normalization modes.
Invariants: Q = -lam - D2 - K.  Native K per substrate; universal test: K=1 rate unit.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np, matplotlib.pyplot as plt, json
from scipy.linalg import expm as _expm

# ---------- Lyapunov: exact QR for continuous flows ----------
def qr_lyap_lorenz(rho=28.0, sigma=10.0, beta=8/3, T=80.0, dt=0.002, n_or=4000):
    n = int(T/dt); x = np.array([8.0, 8.0, 27.0]); Q = np.eye(3)
    acc = np.zeros(3)
    def f(p):
        return np.array([sigma*(p[1]-p[0]), p[0]*(rho-p[2])-p[1], p[0]*p[1]-beta*p[2]])
    def J(p):
        return np.array([[-sigma, sigma, 0],[rho-p[2], -1, -p[0]],[p[1], p[0], -beta]])
    x = np.array([8.0, 8.0, 27.0]); Q = np.eye(3); acc = np.zeros(3)
    for i in range(n):
        x = x + dt*f(x)
        A = _expm(dt*J(x))
        Q, R = np.linalg.qr(A @ Q)
        d = np.diag(R); s = np.sign(d); s[s == 0] = 1
        Q = Q * s
        if i >= n_or:
            acc += np.log(np.abs(d) + 1e-300)
    return acc/( (n-n_or)*dt )

def qr_lyap_henon(a=1.4, b=0.3, T=20000, n_or=2000):
    x, y = 1.0, 1.0; Qm = np.eye(2); acc = np.zeros(2); x2_acc = 0.0
    for i in range(T):
        J = np.array([[-2*a*x, 1],[b, 0]])   # Jacobian at CURRENT point, every step
        Qm, R = np.linalg.qr(J @ Qm)
        d = np.diag(R); s = np.sign(d); s[s == 0] = 1
        Qm = Qm * s
        xn, yn = 1 - a*x*x + y, b*x
        if i >= n_or:
            acc += np.log(np.abs(d) + 1e-300)
            x2_acc += x*x
        x, y = xn, yn
    return acc/(T-n_or), x2_acc/(T-n_or)


# ---------- Robust GP D2 ----------
def correlation_dimension(x, m=4, tau=None, rmin_frac=0.02, rmax_frac=1.0, n_r=24):
    x = np.asarray(x, float)
    tau = tau or max(1, len(x)//200)
    L = len(x) - (m-1)*tau
    if L < 200: return np.nan
    idx = np.arange(m)*tau
    E = x[idx[None, :] + np.arange(L)[:, None]]
    E = (E - E.mean(0)) / (E.std(0) + 1e-12)
    D = np.linalg.norm(E[:, None] - E[None, :], axis=-1)
    iu = np.triu_indices(L, 1); d = D[iu]
    d = d[d > 0]
    if d.size < 500: return np.nan
    lo, hi = rmin_frac*d.mean(), rmax_frac*d.max()
    rs = np.geomspace(max(lo, 1e-6), hi, n_r)
    C = np.array([(d < r).mean() for r in rs])
    ok = (C > 0) & (C < 1)
    if ok.sum() < 6: return np.nan
    slope = np.polyfit(np.log(rs[ok]), np.log(C[ok]), 1)[0]
    return float(slope)

# ---------- K definitions ----------
K_LORENZ = lambda rho, s=10, b=8/3: (s+1+b)/3.0     # -tr J / 3 (rho-independent)
def K_henon(a, x2): return a * x2                      # -mean(tr J)/2 = a*<x^2> (prior def)
def K_ks(L, N=64, nu=1.0):
    """Prior-cycle definition: -mean_{|k|<=k_max}(k^2 - nu k^4), grid cutoff N DECLARED.
    NOTE (theorem): ~ (N/L)^4 dominated -> UV-cutoff dependent, NO continuum limit."""
    k = 2.0*np.pi*np.fft.fftfreq(N, d=L/N)
    ev = k**2 - nu*k**4
    return float(-np.mean(ev))
K_RULE110 = 0.563   # conditional entropy of local rule (prior cycle, frozen)                                      # conditional entropy of rule (measured prior cycle)

def summarize(qvals): 
    q = np.array(qvals); return float(q.mean()), float(q.std())

def load_prior(path="morphospace_q_conservation.py"):
    """Extract defs/constants from prior script WITHOUT running its main sweep."""
    import ast as _ast
    _src = open(path).read(); _tree = _ast.parse(_src)
    _ns = {"np": np}
    for _node in _tree.body:
        if isinstance(_node, (_ast.FunctionDef, _ast.ClassDef, _ast.Assign, _ast.Import, _ast.ImportFrom)):
            try:
                exec(compile(_ast.Module([_node], []), path, "exec"), _ns)
            except Exception:
                pass
    return _ns

if __name__ == "__main__":
    import time
    t0 = time.time()
    lamL = qr_lyap_lorenz()
    print(f"Lorenz QR: {np.round(lamL,4)}  sum={lamL.sum():+.4f}  exact= {-(10+1+8/3):+.4f}")
    lamH, x2 = qr_lyap_henon()
    print(f"Henon QR : [{lamH[0]:+.4f},{lamH[1]:+.4f}] sum={lamH.sum():+.4f} exact={np.log(0.6):+.4f} <x^2>={x2:.4f} K={K_henon(1.4,x2):.3f}")
    for L in (30,35,40,50): print(f"  K_ks N=64 L={L}: {K_ks(L):.2f}")
    for N in (32,64,128,256): print(f"  K_ks L=35 N={N}: {K_ks(35,N):.1f}  (UV probe, expect growth ~ (N/L)^4)")
    x = np.sin(np.linspace(0,200,8000)); print("GP sine:", round(correlation_dimension(x),3), "(~1)")
    per = np.mod(np.arange(7000)*1.0, 1.0); print("GP periodic raw:", round(correlation_dimension(per),3), "(~0 or guard)")
    prior = load_prior()
    print("prior KS fns:", [k for k in prior if 'ks' in k.lower() and callable(prior.get(k))])
    print(f"sanity {time.time()-t0:.1f}s")


(path="morphospace_q_conservation.py"):
    """Extract defs/constants from prior script WITHOUT running its main sweep."""
    import ast as _ast
    _src = open(path).read(); _tree = _ast.parse(_src)
    _ns = {"np": np}
    for _node in _tree.body:
        if isinstance(_node, (_ast.FunctionDef, _ast.ClassDef, _ast.Assign, _ast.Import, _ast.ImportFrom)):
            try:
                exec(compile(_ast.Module([_node], []), path, "exec"), _ns)
            except Exception:
                pass
    return _ns
