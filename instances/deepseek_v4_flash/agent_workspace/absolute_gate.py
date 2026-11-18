#!/usr/bin/env python3
"""
absolute_gate.py  —  THE PARAMETER-FREE ABSOLUTE GATE for the Kuramoto/R-escape barrier.

Model under test (km_barrier_corrected.py, deepseek_v4_flash):
    dR = 0.5*R*(K0*R^alpha*(1-R^2) - sigma^2)*dt + (sigma/sqrt(N))*dW ,  R=0 stable
    R0 = 0.2*Rc ,  escape = first passage to R > Rc ,  TMAX=400 , M=256

Key structural fact everyone has been treating as a *fit*:
    the drift is an exact gradient flow  f(R) = -dU/dR ,  so the barrier is ANALYTIC.
    U(R) = -int_0^R f = -0.5*K0*R^(a+2)/(a+2) + 0.5*K0*R^(a+4)/(a+4) + 0.25*sigma^2*R^2
    D   = sigma^2/(2N)      (additive noise, overdamped)
    =>  slope  d ln(lambda)/dN  =  -2*dU/sigma^2     [ZERO free parameters]

So we do NOT fit the slope. We PREDICT it. And we go further: the exact
overdamped MFPT (not the Arrhenius asymptote) is parameter-free in BOTH the
slope AND the prefactor:

    T(R0->Rc) = (1/D) * int_{R0}^{Rc} exp(U(y)/D) * [int_0^y exp(-U(x)/D) dx] dy

Absolute gate = compare measured rates to 1/T with k=0 free parameters.
AIC with k=0: AIC = -2*LL.  A 2-parameter fit must beat that by >2 to be worth anything.
"""
import json, math
import numpy as np

# ---------------- model constants (must match the simulation exactly) ----------------
K0, ALPHA, SIG = 1.0, 1.5, 0.25
R0_FRAC = 0.2
TMAX, M = 400.0, 256

# ---------------- barrier position: K0*Rc^a*(1-Rc^2) = sigma^2 ----------------
def Rc_solve(K0=K0, a=ALPHA, sig=SIG):
    lo, hi = 1e-12, 1.0
    for _ in range(300):
        m = 0.5*(lo+hi)
        if K0*m**a*(1.0-m*m) - sig*sig < 0: lo = m
        else: hi = m
    return 0.5*(lo+hi)

RC = Rc_solve()
R0 = R0_FRAC*RC

def U(R):
    """Potential, analytic. U(0)=0, monotone increasing on [0,Rc]."""
    return (-0.5*K0*R**(ALPHA+2)/(ALPHA+2)
            + 0.5*K0*R**(ALPHA+4)/(ALPHA+4)
            + 0.25*SIG*SIG*R*R)

def f(R):
    """drift = -U'(R)"""
    return 0.5*R*(K0*R**ALPHA*(1.0-R*R) - SIG*SIG)

DU = U(RC) - U(R0)
SLOPE_PRED = 2.0*DU/(SIG*SIG)          # d ln(lambda)/dN  (positive), lambda ~ exp(-slope*N)

# curvature prefactor (Arrhenius asymptote) -- for reference only
Upp0 = 0.5*SIG*SIG                      # U''(0)
Uppb = -0.5*(ALPHA*SIG*SIG - 2.0*K0*RC**(ALPHA+2))   # U''(Rc) = -f'(Rc)
w0, wb = math.sqrt(Upp0), math.sqrt(max(Uppb, 1e-30))
C_ARR = w0*wb/(2*math.pi)

def mfpt_exact(N, ngrid=40001):
    """Exact overdamped MFPT R0->Rc by composite trapezoid. Parameter-free."""
    D = SIG*SIG/(2.0*N)
    R = np.linspace(0.0, RC, ngrid)
    Uv = U(R)
    # log-space safety: shift by max so exp never overflows
    s = Uv/D
    smax = s.max()
    e = np.exp(s - smax)                # exp(U/D) up to a common constant
    # inner integral I(y) = int_0^y exp(-U/D) dx  -> use exp(-(s - smin)) trick
    em = np.exp(-(s - s.min()))         # exp(-U/D) up to a common constant
    # T = (1/D) * [int e(y) I(y) dy] ; constants cancel exactly:
    #   e(y)*I(y) = exp(s-smax) * exp(-smin)*int exp(-(s-smin)) dx
    #   -> rescale, ratio of exp(smax)/exp(smin) is the constant we must keep:
    # we compute T = (1/D) * exp(smax - smin) * trapz( exp(s-smax) * cumtrapz(exp(-(s-smin))) )
    from scipy.integrate import cumulative_trapezoid
    inner = cumulative_trapezoid(em, R, initial=0.0)
    prod = e*inner
    T = np.trapezoid(prod, R) * math.exp(smax - s.min()) / D
    return T

def mfpt_arrhenius(N):
    """Asymptotic Arrhenius: T = (2*pi/(w0*wb)) exp(DU/D)"""
    D = SIG*SIG/(2.0*N)
    return (2.0*math.pi/(w0*wb))*math.exp(DU/D)

# ---------------- empirical data ----------------
d = json.load(open('km_barrier_corrected.json'))
rows = d['rows']
Ns = np.array([r['N'] for r in rows], float)
nesc = np.array([r['n_escaped'] for r in rows], float)
rate = np.array([r['rate'] for r in rows], float)
tot = np.where(nesc > 0, nesc/np.where(rate > 0, rate, 1), np.nan)

print("="*92)
print("ANALYTIC BARRIER  (zero free parameters)")
print("="*92)
print(f"  K0={K0}  alpha={ALPHA}  sigma={SIG}   Rc={RC:.6f}   R0={R0:.6f}")
print(f"  U(R0)={U(R0):.8e}   U(Rc)={U(RC):.8e}   dU={DU:.8e}")
print(f"  sigma^2/2 = {SIG*SIG/2:.6f}  -> dU/(sigma^2/2) = {DU/(SIG*SIG/2):.4f}  (barrier in kT)")
print(f"  PREDICTED SLOPE  dln(lambda)/dN = 2*dU/sigma^2 = {SLOPE_PRED:.6f}")
print(f"  Arrhenius prefactor w0*wb/2pi = {C_ARR:.6e}   (ln = {math.log(C_ARR):.4f})")

print("\n" + "="*92)
print("EXACT MFPT PREDICTION vs MEASURED RATE  (k=0 free parameters)")
print("="*92)
print(f"{'N':>6} {'dU/D':>8} {'T_exact':>12} {'lam_pred':>12} {'lam_meas':>12} {'ratio':>8} {'ln-resid':>9}")
lam_pred = np.zeros_like(Ns)
for i, N in enumerate(Ns):
    T = mfpt_exact(N)
    lp = 1.0/T
    lam_pred[i] = lp
    lm = rate[i]
    rr = (lm/lp) if lp > 0 else np.nan
    lr = (math.log(lm) - math.log(lp)) if lm > 0 else np.nan
    print(f"{N:>6.0f} {DU/(SIG*SIG/(2*N)):>8.3f} {T:>12.4e} {lp:>12.4e} {lm:>12.4e} "
          f"{rr if np.isfinite(rr) else float('nan'):>8.4f} {lr if np.isfinite(lr) else float('nan'):>9.4f}")

# ---------------- likelihoods: absolute (k=0) vs fitted ----------------
def censored_ll(lnlam, Ns, nesc, M, TMAX):
    """binomial: p = 1-exp(-lam*TMAX)"""
    lnr = np.clip(lnlam + math.log(TMAX), -60, 40)
    pr = 1.0 - np.exp(-np.exp(lnr))
    pr = np.clip(pr, 1e-12, 1-1e-12)
    return float(np.sum(nesc*np.log(pr) + (M-nesc)*np.log(1-pr)))

ll_abs = censored_ll(np.log(lam_pred), Ns, nesc, M, TMAX)

# fitted 2-param Kramers: ln lam = c0 - c1*N  (profile over c0,c1 analytically-ish)
from scipy.optimize import minimize
def negll2(p):
    return -censored_ll(p[0] - p[1]*Ns, Ns, nesc, M, TMAX)
best2 = None
for c0 in np.linspace(-6, 12, 37):
    for c1 in np.linspace(0.0, 0.02, 41):
        r = minimize(negll2, [c0, c1], method='Nelder-Mead',
                     options=dict(maxiter=4000, xatol=1e-10, fatol=1e-10))
        if best2 is None or r.fun < best2.fun: best2 = r
ll_2 = -best2.fun
c0_fit, c1_fit = best2.x

# fitted 3-param crossover: ln lam = c0 - c1*N - b*lnN
def negll3(p):
    return -censored_ll(p[0] - p[1]*Ns - p[2]*np.log(Ns), Ns, nesc, M, TMAX)
best3 = None
for c0 in np.linspace(-6, 12, 13):
    for c1 in np.linspace(0.0, 0.02, 13):
        for b in np.linspace(-1.5, 2.5, 13):
            r = minimize(negll3, [c0, c1, b], method='Nelder-Mead',
                         options=dict(maxiter=8000, xatol=1e-10, fatol=1e-10))
            if best3 is None or r.fun < best3.fun: best3 = r
ll_3 = -best3.fun

print("\n" + "="*92)
print("ABSOLUTE GATE — AIC COMPARISON  (k = number of FREE parameters)")
print("="*92)
print(f"  ABSOLUTE  analytic barrier, k=0      LL={ll_abs:9.3f}  AIC={-2*ll_abs:9.3f}")
print(f"  Kramers   2-param fit,      k=2      LL={ll_2:9.3f}  AIC={-2*ll_2+4:9.3f}  "
      f"c0={c0_fit:+.4f} c1={c1_fit:.6f}")
print(f"  Crossover 3-param fit,      k=3      LL={ll_3:9.3f}  AIC={-2*ll_3+6:9.3f}  "
      f"params={np.round(best3.x,6)}")
print(f"\n  dAIC(2-param fit - ABSOLUTE) = {(-2*ll_2+4)-(-2*ll_abs):+.3f}")
print(f"  dAIC(3-param fit - ABSOLUTE) = {(-2*ll_3+6)-(-2*ll_abs):+.3f}")
print(f"  measured slope c1_fit = {c1_fit:.6f}   vs PREDICTED {SLOPE_PRED:.6f}   "
      f"-> ratio {c1_fit/SLOPE_PRED:.4f}")

# ---------------- parametric bootstrap GOF on the absolute model ----------------
rng = np.random.default_rng(20261118)
p_abs = 1.0 - np.exp(-lam_pred*TMAX)
p_abs = np.clip(p_abs, 1e-15, 1-1e-15)
obs = nesc
def chi2(obs, exp, var):
    return float(np.sum((obs-exp)**2/np.maximum(var, 1e-12)))
exp_abs = p_abs*M
var_abs = M*p_abs*(1-p_abs)
chi2_obs = chi2(obs, exp_abs, var_abs)
# bootstrap null distribution under the ABSOLUTE model
NB = 20000
sim = rng.binomial(M, p_abs, size=(NB, len(Ns)))
chi2_null = np.sum((sim-exp_abs)**2/np.maximum(var_abs,1e-12), axis=1)
pval = float((chi2_null >= chi2_obs).mean())
print("\n" + "="*92)
print("PARAMETRIC BOOTSTRAP GOF  (H0 = analytic barrier, k=0)")
print("="*92)
print(f"  chi2_obs = {chi2_obs:.3f}   dof={len(Ns)}   bootstrap p = {pval:.4f}")
print(f"  observed escapes : {obs.astype(int).tolist()}")
print(f"  expected escapes : {np.round(exp_abs,2).tolist()}")

# ---------------- dof-corrected p-value: with 8 points, k=0 -> no correction needed
out = dict(
    constants=dict(K0=K0, ALPHA=ALPHA, SIG=SIG, R0_frac=R0_FRAC, TMAX=TMAX, M=M),
    Rc=RC, R0=R0, U_R0=U(R0), U_Rc=U(RC), dU=DU, barrier_in_kT=DU/(SIG*SIG/2),
    slope_predicted=SLOPE_PRED, arrhenius_prefactor=C_ARR, ln_prefactor=math.log(C_ARR),
    Ns=Ns.tolist(), lam_pred=lam_pred.tolist(), lam_meas=rate.tolist(),
    log_residual=[float(math.log(r)-math.log(l)) if r>0 else None for r,l in zip(rate,lam_pred)],
    LL=dict(absolute_k0=ll_abs, kramers_k2=ll_2, crossover_k3=ll_3),
    AIC=dict(absolute_k0=-2*ll_abs, kramers_k2=-2*ll_2+4, crossover_k3=-2*ll_3+6),
    fitted_slope=c1_fit, fitted_slope_ratio_to_pred=c1_fit/SLOPE_PRED,
    bootstrap=dict(chi2_obs=chi2_obs, p_value=pval, n_boot=NB),
    expected_escapes=exp_abs.tolist(),
)
json.dump(out, open('absolute_gate.json','w'), indent=1)
print("\nwrote absolute_gate.json")
