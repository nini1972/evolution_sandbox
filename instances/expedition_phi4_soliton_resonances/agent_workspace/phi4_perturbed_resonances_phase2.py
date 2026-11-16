"""
phi4_perturbed_resonances_phase2.py  --  PHASE II: perturbed 2-bounce resonance windows
=========================================================================================
Model: d2phi/dt2 - d2phi/dx2 + U'_lam(phi) + eps*sech^2(x/xw)*phi
       = -eta*pi + sqrt(2*eta*T/dx)*xi(x,t)

  U_lam(phi) = (1/4)(phi^2-1)^2 + (lam/6)(phi^2-1)^3
     -> U'_lam = phi(phi^2-1) + lam*phi(phi^2-1)^2   [exact antiderivative]
     -> vacua pinned at phi=+-1 with U''(+-1)=2 for ALL lam (mass unchanged)
     -> central barrier height (1/4 - lam/6), curvature U''(0)=lam-1 -> kink
        widens and the shape mode softens as lam -> 1 (SG-like limit)

Integrator: Phase-I-verified spectral Strang split (area-preserving linear map,
half-kick/half-kick potential). Damping+noise applied as an EXACT Ornstein-
Uhlenbeck update once per step (commutes to O(dt^2), unconditionally stable,
FDT-consistent: <pi^2> -> T/dx at equilibrium).

Modules:
  A) Impurity robustness: eps in {0, .003, .008, .015, .03}, v in [0.179,0.207]
     -> window survival threshold eps_c (theory: pair binding 2*sqrt(3)*eps
        vs window gap ~0.0377 -> eps_c ~ 0.013)
  B) Thermal robustness: T in {0, 1e-4, 5e-4, 2e-3}, eta=0.2, NTRIAL stochastic
     runs per (v,T) -> escape probability P_esc(v,T), window smearing threshold
  C) SG crossover: lam in {0,.2,.4,.6,.8}: relax true kink profile, diagonalize
     fluctuation operator -d2+U''(phi_K) (zero mode = relaxation QA), measure
     omega_shape(lam) and the 2-bounce window collapse at v=0.196.

Run modes:  PHASE2_SMOKE=1 python3 ...  (fast local QA)
            python3 ...                 (full production; World C)
Outputs:    phi4_phase2_results.json, phi4_perturbed_resonances_phase2.png
"""
import os, sys, json, time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Pool

# ---------------- grid (Phase I convention, longer box for T_sim=130) ----------------
N  = 512
L  = 120.0
dx = L/N
x  = (np.arange(N) - N/2)*dx
K  = 2*np.pi*np.fft.fftfreq(N, dx)
K2 = K**2
S2 = np.sqrt(2.0)
ic = N // 2

DT      = 0.01
NSTEPS  = 13000
NSUB    = 65
D0      = 6.0
THR     = 0.02
VS      = np.linspace(0.179, 0.207, 29)
EPS_LIST= [0.0, 0.003, 0.008, 0.015, 0.03]
XW      = 4.0
T_LIST  = [0.0, 1e-4, 5e-4, 2e-3]
ETA     = 0.2
NTRIAL  = 16
LAM_LIST= [0.0, 0.2, 0.4, 0.6, 0.8]

SECH2 = np.cosh(x/XW)**-2.0

SMOKE = os.environ.get('PHASE2_SMOKE', '0') == '1'
if SMOKE:
    VS      = np.linspace(0.185, 0.200, 5)
    EPS_LIST= [0.0, 0.015]
    T_LIST  = [0.0, 5e-4]
    NTRIAL  = 2
    NSTEPS  = 4000
    LAM_LIST= [0.0, 0.6]

# ---------------- potential family ----------------
def Uprime(phi, lam=0.0, eps=0.0):
    s = phi*phi - 1.0
    return phi*s + lam*phi*s*s + eps*SECH2*phi

def energy(phi, pi, lam=0.0, eps=0.0):
    g  = np.fft.ifft(1j*K*np.fft.fft(phi)).real
    s  = phi*phi - 1.0
    E1 = 0.5*np.sum(pi**2)*dx
    E2 = 0.5*np.sum(g**2)*dx
    E3 = np.sum(0.25*s**2 + (lam/6.0)*s**3 + 0.5*eps*SECH2*phi**2)*dx
    return E1 + E2 + E3

# ---------------- initial conditions ----------------
def make_ka(v, d=D0, prof=None, dprof=None):
    """KA pair; prof/dprof = relaxed kink profile & derivative (Module C)."""
    g  = 1.0/np.sqrt(1.0 - v*v)
    if prof is None:
        u1 = g*(x + d); u2 = g*(x - d)
        s1, s2 = np.cosh(u1), np.cosh(u2)
        phi = np.tanh(u1/S2) - np.tanh(u2/S2) - 1.0
        pi  = -(g*v/S2)*(1.0/s1**2 + 1.0/s2**2)
    else:
        u1 = g*(x + d); u2 = g*(x - d)
        f1 = np.interp(u1, x, prof); f2 = np.interp(u2, x, prof)
        p1 = np.interp(u1, x, dprof); p2 = np.interp(u2, x, dprof)
        phi = f1 - f2 - 1.0
        pi  = -g*v*(p1 + p2)
    return phi, pi

# ---------------- integrator (Phase I verified + exact OU bath) ----------------
def integrate(phi, pi, dt, nsteps, lam=0.0, eps=0.0, eta=0.0, T=0.0, rng=None):
    w2 = K2 + 1.0
    w  = np.sqrt(w2)
    cw = np.cos(w*dt)
    sw = np.sinc(w*dt/np.pi)*dt          # sin(w dt)/w
    use_ou = (eta > 0.0 and T > 0.0 and rng is not None)
    if use_ou:
        damp = np.exp(-eta*dt)
        amps = np.sqrt((1.0 - np.exp(-2.0*eta*dt))*T/dx)
    for _ in range(nsteps):
        pih  = pi + 0.5*dt*(-Uprime(phi, lam, eps))          # half kick
        phk  = np.fft.fft(phi); pik = np.fft.fft(pih)
        phk_new = cw*phk + sw*pik                            # area-preserving map
        pik     = cw*pik - w2*sw*phk
        phk     = phk_new
        phi  = np.fft.ifft(phk).real
        pih  = np.fft.ifft(pik).real
        pi   = pih + 0.5*dt*(-Uprime(phi, lam, eps))         # half kick
        if use_ou:                                           # exact OU bath step
            pi = pi*damp + amps*rng.standard_normal(N)
    return phi, pi

# ---------------- one collision run ----------------
def run_one(v, lam=0.0, eps=0.0, eta=0.0, T=0.0, seed=0,
            nsteps=NSTEPS, d0=D0, prof=None, dprof=None):
    phi, pi = make_ka(v, d0, prof, dprof)
    E0  = energy(phi, pi, lam, eps)
    rng = np.random.default_rng(seed) if (eta > 0.0 and T > 0.0) else None
    nmid = nsteps // NSUB
    wk, wa, phic = [], [], []
    for _ in range(NSUB):
        phi, pi = integrate(phi, pi, DT, nmid, lam, eps, eta, T, rng)
        gx = np.fft.ifft(1j*K*np.fft.fft(phi)).real
        wk.append(x[np.argmax(gx)]); wa.append(x[np.argmin(gx)])
        phic.append(phi[ic])
    wk = np.array(wk); wa = np.array(wa); phic = np.array(phic)
    m    = int(0.75*NSUB)
    span = (NSUB - 1 - m)*nmid*DT
    vk = (wk[-1]-wk[m])/span
    va = (wa[-1]-wa[m])/span
    nb = int(np.sum(np.abs(np.diff(np.sign(phic))))/2)
    escaped = (abs(vk) > THR) or (abs(va) > THR)
    dE = (energy(phi, pi, lam, eps) - E0)/E0
    wob = float(np.std(phic[m:]))                        # wobble-amplitude proxy
    return dict(vk=float(vk), va=float(va), nb=nb, escaped=bool(escaped),
                dE=float(dE), wob=wob)

# ---------------- Module C helpers: relax kink + fluctuation spectrum ----------------
def relax_kink(lam, niter=6000, dt_r=0.02, gam=1.5):
    phi = np.tanh(x/S2)
    pi  = np.zeros(N)
    for _ in range(niter):
        phi_xx = np.fft.ifft(-K2*np.fft.fft(phi)).real
        pi  = pi + dt_r*(phi_xx - Uprime(phi, lam) - gam*pi)
        phi = phi + dt_r*pi
    res = float(np.max(np.abs(np.fft.ifft(-K2*np.fft.fft(phi)).real
                              - Uprime(phi, lam))))
    M   = float(np.sum(0.5*np.gradient(phi)**2 + 0.25*(phi*phi-1)**2
                       + (lam/6.0)*(phi*phi-1)**3)*dx)
    return phi, res, M

def shape_spectrum(lam, phiK):
    from scipy.linalg import eigh_tridiagonal
    s  = phiK**2 - 1.0
    Vp = 3*phiK**2 - 1 + lam*(s*s + 4*phiK**2*s)
    main = 2.0/dx**2 + Vp
    off  = -1.0/dx**2*np.ones(N-1)
    w, _ = eigh_tridiagonal(main, off)
    nbnd = int(np.sum(w < 2.0 - 1e-6))
    om   = float(np.sqrt(max(w[1], 0.0))) if nbnd >= 2 else float('nan')
    return om, nbnd, [float(v) for v in w[:4]]

# ---------------- task worker ----------------
def task(a):
    kind, p = a
    if kind == 'A':
        eps, v = p
        r = run_one(v, eps=eps)
        return ('A', eps, v, r)
    if kind == 'B':
        T, i, v = p
        seed = 12345 + 7919*i + int(round(v*1e6))
        r = run_one(v, eta=ETA, T=T, seed=seed)
        return ('B', T, v, i, r)
    if kind == 'C':
        lam = p
        phiK, res, M = relax_kink(lam)
        om, nbnd, eigs = shape_spectrum(lam, phiK)
        dprof = np.fft.ifft(1j*K*np.fft.fft(phiK)).real
        r = run_one(0.196, lam=lam, d0=10.0, prof=phiK, dprof=dprof)
        return ('C', lam, dict(omega=om, nbnd=nbnd, eigs=eigs,
                               relax_res=res, M=M, **r))
    raise ValueError(kind)
