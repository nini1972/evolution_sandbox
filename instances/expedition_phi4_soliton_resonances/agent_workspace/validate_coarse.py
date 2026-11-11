import numpy as np, time
import phi4_resonance_vectorized as P

t0=time.time()
vs = np.linspace(0.18, 0.26, 21)
dt, nsteps, d0 = 0.01, 13000, 6.0
thr = 0.04
vk=[]; va=[]; dE=[]; nb=[]
for v in vs:
    a,b,c,n = P.run_one(v, dt, nsteps, d0)
    vk.append(a); va.append(b); dE.append(c); nb.append(n)
    print("v=%.4f  vk=%+.4f va=%+.4f  |v|=%.4f  nb=%d  dE/E=%.2e %s"%(
        v,a,b,np.hypot(a,b),n,c, "<-- ESC" if np.hypot(a,b)>thr else "<-- CAP"))

vk=np.array(vk); va=np.array(va); vf=np.hypot(vk,va); nb=np.array(nb); dE=np.abs(np.array(dE))
print("\nmax|dE/E| = %.2e   mean|dE/E| = %.2e"%(dE.max(), dE.mean()))
print("runtime = %.1fs"%(time.time()-t0))
# crude window detection on |vf|<thr
cap = vf < thr
print("\ncapture points (|vf|<%.2f):"%thr)
print([round(x,4) for x in vs[cap]])
print("bounce counts at capture points:", nb[cap].tolist())
