import numpy as np, json
Du,Dv=0.16,0.08
def fp(F,k):
    uk=np.sqrt(F+k); return uk, F*(1-uk)/(F+k)
def mu5(qx,qy): return -4+2*(np.cos(qx)+np.cos(qy))
def re_max(F,k):
    u,v=fp(F,k); a=-v*v-F; b=-2*u*v; c=v*v; d=2*u*v-(F+k)
    tr=a+d; det=a*d-b*c
    if tr>=0 or det<=0: return -1e9
    K=np.linspace(0,np.pi,80); best=-1e9
    for qx in K:
        for qy in K:
            m=mu5(qx,qy)
            A=tr+(Du+Dv)*m; B=(a+Du*m)*(d+Dv*m)-b*c
            disc=A*A-4*B
            re=0.5*(A+np.sqrt(max(disc,0))) if disc>=0 else 0.5*A
            if re>best: best=re
    return best
res=[]
for F in np.linspace(0.018,0.08,62):
    for k in np.linspace(0.045,0.07,52):
        if F+k>=0.95: continue
        rm=re_max(F,k)
        if rm>1e-3: res.append((rm,F,k))
res.sort(reverse=True)
print("top Turing-active (Re,F,k):")
for r in res[:6]: print("  Re=%.4f F=%.4f k=%.4f"%(r[0],r[1],r[2]))
json.dump(res,open('turing_params.json','w'))
print("n_found=",len(res))
