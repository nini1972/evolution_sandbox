#!/usr/bin/env python3
"""
Does the P4-attractor family organize by WAVELENGTH (wavenumber band)?
Method: for each locked period-4 orbit, build a SHIFT-INVARIANT signature
  sigma(k) = the |FFT| spectrum of the mean spatial profile (invariant under
  site-shift by construction, since we compare periodograms not profiles).
Two orbits in the SAME family (differ only by shift) have near-equal sigma.
Two orbits with DIFFERENT wavelengths differ strongly in sigma.
We cluster by sigma to count distinct *wavelength classes*, then verify with
full d_orbit on representatives.
Also: is the count of wavelength classes N-dependent (band fixed => count ~ N/spacing
grows with N) or N-independent (discrete selection of a few wavelengths)?
"""
import numpy as np, json, time
def f(x,r): return r*x*(1.0-x)
def coupled(x,r,eps):
    fx=f(x,r); return (1.0-eps)*fx+(0.5*eps)*(np.roll(fx,1)+np.roll(fx,-1))
def lock(r,eps,trans,N,x0):
    x=x0.copy()
    for _ in range(trans): x=coupled(x,r,eps)
    P=np.empty((N,4))
    for k in range(4): P[:,k]=x; x=coupled(x,r,eps)
    return P
def sigma(P):
    prof=np.mean(P,axis=1)
    F=np.abs(np.fft.rfft(prof-np.mean(prof)))
    return F
def dist_sigma(a,b):
    L=min(len(a),len(b)); return float(np.max(np.abs(a[:L]-b[:L])))
def d_orbit(P,Q):
    N=P.shape[0]; best=np.inf
    for p in range(4):
        Pt=np.roll(P,p,axis=1)
        for s in range(N):
            d=float(np.max(np.abs(Pt-np.roll(Q,s,axis=0))))
            if d<best: best=d
    return best

r,eps=3.87,0.136
results={}
for Nn in [48,120,240]:
    tt=time.time()
    nseeds=16
    rgg=np.random.default_rng(100+Nn)
    Ps=[lock(r,eps,30000,Nn,rgg.random(Nn)) for _ in range(nseeds)]
    Sg=[sigma(P) for P in Ps]
    # cluster by sigma (tol 0.05 in max-abs of periodogram)
    rep=[]
    for i in range(nseeds):
        if all(dist_sigma(Sg[i],Sg[rep[j]])>0.05 for j in range(len(rep))):
            rep.append(i)
    # dominant wavenumbers of each class rep
    kdoms=[]
    for ri in rep:
        F=Sg[ri]; k=int(np.argsort(F)[::-1][0])+1
        kdoms.append(k)
    # verify distinctness of reps via full d_orbit (pairwise)
    D=np.zeros((len(rep),len(rep)))
    for a in range(len(rep)):
        for b in range(len(rep)):
            if a!=b: D[a,b]=d_orbit(Ps[rep[a]],Ps[rep[b]])
    offD=D[np.triu_indices(len(rep),1)]
    results[Nn]={'n_classes':len(rep),'kdoms':kdoms,
                 'min_pair_dorbit':float(offD.min()) if offD.size else None,
                 'frac_pairs_far(>0.3)':float((offD>0.3).mean()) if offD.size else None,
                 'wall_s':round(time.time()-tt,1)}
    print(f"N={Nn:3d}: {nseeds} seeds -> {len(rep)} wavelength classes; kdoms={kdoms}")
    if offD.size: print(f"        pairwise d_orbit among class reps: min={offD.min():.3f}  frac>0.3={float((offD>0.3).mean()):.2f}")

# Interpretation: if the same ~16 wavelengths recur across N => discrete band.
# If new wavelengths appear with N => continuous band (count ~ N).
json.dump({'r':r,'eps':eps,'per_N':results,
           'note':'shift-invariant periodogram clustering; verify by full d_orbit'},
          open('p4_wavenumber_band.json','w'),indent=2)
print("saved p4_wavenumber_band.json")
