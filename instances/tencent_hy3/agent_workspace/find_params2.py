import numpy as np, json
Du,Dv=0.16,0.08

def fp(F,k):
    disc=1.0-4.0*(F+k)**2/F
    if disc<=0: return None
    u=0.5*(1.0-np.sqrt(disc))     # smaller root (u<0.5)
    v=(F+k)/u
    return u,v

def turing_max(F,k):
    p=fp(F,k)
    if p is None: return None
    u,v=p
    a=-v*v-F; b=-2*u*v; c=v*v; d=2*u*v-(F+k)
    tr=a+d; det=a*d-b*c
    if tr>=0 or det<=0: return None        # temporal instability
    cross=Dv*a+Du*d
    if cross<=0: return None               # need Dv*a11+D1*a22>0
    if cross*cross-4*Du*Dv*det<=0: return None  # Turing discriminant
    # find max Re over k-space (5-pt eigenvalue mu5)
    K=np.linspace(0,np.pi,90); best=-1e9; bk=None
    for qx in K:
        for qy in K:
            m=-4+2*(np.cos(qx)+np.cos(qy))
            A=tr+(Du+Dv)*m; B=(a+Du*m)*(d+Dv*m)-b*c
            disc2=A*A-4*B
            re=0.5*(A+np.sqrt(max(disc2,0))) if disc2>=0 else 0.5*A
            if re>best: best=re; bk=(qx,qy)
    if best<=1e-3: return None
    qc=np.hypot(*bk); wl=2*np.pi/qc
    return best,wl

res=[]
for F in np.linspace(0.03,0.09,57):
    for k in np.linspace(0.03,0.066,37):
        if F+k>=0.5: continue
        r=turing_max(F,k)
        if r is not None:
            res.append((r[0],r[1],F,k))
res.sort(reverse=True)
print("Turing-active (Re, lambda, F, k):")
for r in res[:10]:
    print("  Re=%.4f lambda=%.1f F=%.4f k=%.4f"%(r[0],r[1],r[2],r[3]))
json.dump(res,open('turing_params.json','w'))
print("n_found=",len(res))
if res:
    # choose one with interior wavelength 8-20 and solid growth
    pick=[r for r in res if 8<r[1]<22 and r[0]>0.02]
    p=pick[len(pick)//2] if pick else res[len(res)//2]
    print("CHOSEN Re=%.4f lambda=%.1f F=%.4f k=%.4f"%(p[0],p[1],p[2],p[3]))
    json.dump({'F':p[2],'k':p[3]},open('chosen.json','w'))
