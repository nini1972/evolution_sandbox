import numpy as np
from numba import njit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

F,k=0.0739,0.0620
Du,Dv=0.16,0.08
L=64
disc=1.0-4.0*(F+k)**2/F
us=0.5*(1.0-np.sqrt(disc)); vs=(F+k)/us
print("FP u*=%.4f v*=%.4f"%(us,vs))
a=-vs*vs-F; b=-2*us*vs; c=vs*vs; d=2*us*vs-(F+k)
print("Jacobian a,b,c,d=%.4f %.4f %.4f %.4f  tr=%.5f det=%.6f"%(a,b,c,d,a+d,a*d-b*c))

@njit
def lap5(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            o[y,x]=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]-4.0*u[y,x]

@njit
def lap9(u,o):
    L=u.shape[0]
    for y in range(L):
        for x in range(L):
            orth=u[(y+1)%L,x]+u[(y-1)%L,x]+u[y,(x+1)%L]+u[y,(x-1)%L]
            diag=u[(y+1)%L,(x+1)%L]+u[(y+1)%L,(x-1)%L]+u[(y-1)%L,(x+1)%L]+u[(y-1)%L,(x-1)%L]
            o[y,x]=-5.0*u[y,x]+1.0*orth+0.25*diag

@njit
def step(du,dv,t1,t2,applyf,dt):
    L=du.shape[0]
    applyf(du,t1); applyf(dv,t2)
    for y in range(L):
        for x in range(L):
            lu=t1[y,x]; lv=t2[y,x]
            ndu=du[y,x]+dt*(a*du[y,x]+b*dv[y,x]+Du*lu)
            ndv=dv[y,x]+dt*(c*du[y,x]+d*dv[y,x]+Dv*lv)
            du[y,x]=ndu; dv[y,x]=ndv

# most unstable wavenumber (5-pt dispersion)
K=np.linspace(0,np.pi,120); best=-1e9; bq=None
for qx in K:
    for qy in K:
        m=-4+2*(np.cos(qx)+np.cos(qy))
        A=(a+d)+(Du+Dv)*m; B=(a+Du*m)*(d+Dv*m)-b*c
        disc2=A*A-4*B
        re=0.5*(A+np.sqrt(max(disc2,0))) if disc2>=0 else 0.5*A
        if re>best: best=re; bq=(qx,qy)
print("predicted q=(%.3f,%.3f) Re=%.4f  lambda=%.1f"%(bq[0],bq[1],best,2*np.pi/np.hypot(*bq)))

def run_mode(applyf,qx,qy,steps=500,dt=1.0):
    xx=np.arange(L); YY,XX=np.meshgrid(xx,xx)
    du=np.sin(qx*XX)*np.sin(qy*YY)*1e-3
    dv=np.zeros((L,L))
    t1=np.empty((L,L)); t2=np.empty((L,L))
    amps=[]
    for t in range(steps):
        step(du,dv,t1,t2,applyf,dt)
        amp=np.sqrt((du**2+dv**2).mean()); amps.append(amp)
        if not np.isfinite(amp) or amp>1e4: break
    amps=np.array(amps)
    good=np.isfinite(amps)&(amps>1e-8)&(amps<1e3)
    if good.sum()>10:
        tt=np.arange(len(amps))[good]
        fit=np.polyfit(tt,np.log(amps[good]),1)[0]
    else: fit=np.nan
    return fit

r5=run_mode(lap5,bq[0],bq[1])
r9=run_mode(lap9,bq[0],bq[1])
print("SIM growth rate: 5-pt=%.4f  9-pt=%.4f  | theory Re=%.4f"%(r5,r9,best))
print("agreement 5pt=%.2f  9pt=%.2f"%(r5/best,r9/best))

# anisotropy probe: DIAGONAL mode
qd=np.hypot(*bq)/np.sqrt(2)
rr5=run_mode(lap5,qd,qd); rr9=run_mode(lap9,qd,qd)
print("DIAGONAL q=(%.3f,%.3f): 5pt Re=%.4f  9pt Re=%.4f"%(qd,qd,rr5,rr9))
print("Anisotropy (axial-diagonal growth-rate gap): 5pt=%.4f  9pt=%.4f"%(r5-rr5,r9-rr9))
