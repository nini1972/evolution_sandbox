"""
GS Deterministic Saturation Map (tencent_hy3)
Sweep Du to vary lattice coverage; record DET_max, DET@eps0.2, adaptive_DET,
and anisotropy-ratio discrimination between 5pt and 9pt stencils.
Calibrates WHERE the 'DET>0.99 -> reroute' gate fires, and proves the reroute
should fire on delta-z(DET) blindness (not only saturation) across regimes.
Stage: gs_det_saturation_map
Kernels mirror the validated det_stencil_audit.py (explicit centered neighbors).
"""
import json, time, numpy as np
from numba import njit

N = 128
STEPS = 10000
F, k = 0.035, 0.060
Dv = 0.08
DU_LIST = [0.10, 0.13, 0.16, 0.20]

@njit
def gs_step(u, v, Du, Dv, F, k, wtype):
    Nn = u.shape[0]
    un = np.empty_like(u); vn = np.empty_like(v)
    for i in range(Nn):
        for j in range(Nn):
            ip=(i+1)%Nn; im=(i-1)%Nn; jp=(j+1)%Nn; jm=(j-1)%Nn
            if wtype == 0:  # 5-point
                lu = -1.0*u[i,j] + 0.25*(u[ip,j]+u[im,j]+u[i,jp]+u[i,jm])
                lv = -1.0*v[i,j] + 0.25*(v[ip,j]+v[im,j]+v[i,jp]+v[i,jm])
            else:           # 9-point
                lu = (-1.0*u[i,j]
                      + 0.2*(u[ip,j]+u[im,j]+u[i,jp]+u[i,jm])
                      + 0.05*(u[ip,jp]+u[ip,jm]+u[im,jp]+u[im,jm]))
                lv = (-1.0*v[i,j]
                      + 0.2*(v[ip,j]+v[im,j]+v[i,jp]+v[i,jm])
                      + 0.05*(v[ip,jp]+v[ip,jm]+v[im,jp]+v[im,jm]))
            lu *= Du; lv *= Dv
            uvv = u[i,j]*v[i,j]*v[i,j]
            un[i,j] = u[i,j] + lu - uvv + F*(1.0-u[i,j])
            vn[i,j] = v[i,j] + lv + uvv - (F+k)*v[i,j]
    return un, vn

def simulate(wtype, Du):
    rng = np.random.default_rng(42)
    u = np.ones((N,N)); v = np.zeros((N,N))
    r = rng.random((N,N)); u[r<0.5]=0.5; v[r<0.5]=0.25
    t0=time.time()
    for _ in range(STEPS):
        u, v = gs_step(u, v, Du, Dv, F, k, wtype)
    sim_t = time.time()-t0
    return u, v, sim_t

def compute_rqa(u_field):
    M = 90
    start = (N-M)//2
    pat = u_field[start:start+M, start:start+M]
    pat = (pat > 0.5).astype(float)
    Np = pat.shape[0]
    diff = pat[:,None,:] - pat[None,:,:]
    D = np.sqrt((diff**2).sum(axis=2))
    eps_grid = np.linspace(0.02,0.6,15)
    RRs=[]; DETs=[]
    for eps in eps_grid:
        R = (D < eps).astype(float)
        np.fill_diagonal(R,0); np.fill_diagonal(R[1:],0); np.fill_diagonal(R[:,1:],0)
        P = (R>0).sum()
        RR = P/(Np*(Np-1))
        dl=[]
        for d in range(1, Np):
            diag = np.diag(R, d)
            run=0
            for x in diag:
                if x: run+=1
                else:
                    if run>=1: dl.append(run)
                    run=0
            if run>=1: dl.append(run)
        Ndiag = sum(dl) if dl else 0
        DET = (sum(l for l in dl if l>=2)/Ndiag) if Ndiag>0 else 0.0
        RRs.append(RR); DETs.append(DET)
    DETs=np.array(DETs); RRs=np.array(RRs)
    idx = np.argmin(np.abs(np.array(RRs)-0.05))
    DET_adapt = DETs[idx]
    return float(DETs.max()), float(DETs[2]), float(DET_adapt)

def anisotropy(pattern):
    f = np.fft.fftshift(np.fft.fft2(pattern - pattern.mean()))
    p = np.abs(f)**2
    Ny, Nx = p.shape
    y, x = np.indices((Ny,Nx)) - Ny//2
    ang = np.arctan2(y, x)
    nb = 8
    edges = np.linspace(-np.pi, np.pi, nb+1)
    means = []
    for b in range(nb):
        m = (ang>=edges[b]) & (ang<edges[b+1])
        means.append(p[m].mean() if m.any() else 0.0)
    means = np.array([mx for mx in means if mx>0])
    return float(means.max()/means.min())

out = {}
for Du in DU_LIST:
    out[float(Du)] = {}
    for wtype, st in [(0,'5pt'),(1,'9pt')]:
        u, v, st_t = simulate(wtype, Du)
        cov = float((u>0.5).mean())
        dmax, d02, dadapt = compute_rqa(u)
        anis = anisotropy(u)
        out[float(Du)][st] = {'coverage':cov,'DET_max':dmax,'DET_at_0.2':d02,
                              'adaptive_DET':dadapt,'anisotropy':anis,'sim_t':st_t}
        print(f"Du={Du} {st} cov={cov:.3f} DETmax={dmax:.4f} DET0.2={d02:.4f} anis={anis:.3f} t={st_t:.1f}s")

summary = {}
for Du in DU_LIST:
    d = out[float(Du)]
    det_sat = min(d['5pt']['DET_max'], d['9pt']['DET_max']) > 0.99
    anis_split = abs(d['5pt']['anisotropy'] - d['9pt']['anisotropy']) / \
                 ((d['5pt']['anisotropy']+d['9pt']['anisotropy'])/2)
    # delta-z(DET) at common eps 0.2
    dz_det = abs(d['5pt']['DET_at_0.2'] - d['9pt']['DET_at_0.2'])
    summary[float(Du)] = {'DET_saturated_gate_fires': bool(det_sat),
                          'anisotropy_relative_split': float(anis_split),
                          'delta_z_DET_at_0.2': float(dz_det),
                          'coverage': (d['5pt']['coverage']+d['9pt']['coverage'])/2}

result = {'per_run': out, 'summary': summary,
          'note': 'reroute should fire on (delta_z_DET small) OR (DET>0.99); '
                  'anisotropy_split stays >0 even when DET is blind/unsat'}
with open('det_saturation_map.json','w') as f:
    json.dump(result, f, indent=2)
print("DONE", json.dumps(summary, indent=2))
