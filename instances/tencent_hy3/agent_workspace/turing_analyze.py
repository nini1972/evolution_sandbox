import numpy as np

def fp(F,k):
    # real uniform interior FP: u*=sqrt(F+k), v*=F(1-u*)/(F+k)  (requires u*<1)
    s=F+k
    if s>=1: return None,None
    u=np.sqrt(s); v=F*(1-u)/s
    return u,v

def Jmat(F,k):
    u,v=fp(F,k)
    if u is None: return None
    J11=-F-v*v
    J12=-2*u*v
    J21=v*v
    J22=2*u*v-(F+k)
    return np.array([[J11,J12],[J21,J22]])

def max_growth(F,k,Du,Dv,k2max=4.0,nk=800):
    J=Jmat(F,k)
    if J is None: return -1e9,None
    ks=np.linspace(0,k2max,nk)
    best=-1e9; bestk=0
    for k2 in ks:
        M=J-np.diag([Du*k2,Dv*k2])
        ev=np.linalg.eigvals(M)
        m=ev.real.max()
        if m>best: best=m; bestk=k2
    return best,bestk

# Scan (F,k) for Turing instability with canonical ratio Du/Dv=2
Du,Dv=0.16,0.08
Fs=np.linspace(0.005,0.10,40)
Ks=np.linspace(0.03,0.075,30)
print("Turing-unstable (F,k) region for Du=%.2f Dv=%.2f (ratio %.1f):"%(Du,Dv,Du/Dv))
hits=[]
for F in Fs:
    row=[]
    for k in Ks:
        sg,bk=max_growth(F,k,Du,Dv)
        row.append(sg>0)
        if sg>0: hits.append((F,k,sg,bk))
    print("F=%.3f "%F + "".join("#" if r else "." for r in row))
print("\n%d Turing-unstable points found."%len(hits))
if hits:
    hits.sort(key=lambda x:-x[2])
    print("Top: ", [(round(F,4),round(k,4),round(sg,4),round(bk,3)) for F,k,sg,bk in hits[:8]])

# Also test the literature-famous (Du,Dv)=(2e-5,1e-5)? magnitude shouldn't matter for existence
print("\n--- ratio r=4 (Du=0.32,Dv=0.08) ---")
Du,Dv=0.32,0.08
hits2=[]
for F in Fs:
    for k in Ks:
        sg,bk=max_growth(F,k,Du,Dv)
        if sg>0: hits2.append((F,k,sg,bk))
print("ratio 4: %d unstable points"%len(hits2))
if hits2:
    hits2.sort(key=lambda x:-x[2])
    print("Top: ", [(round(F,4),round(k,4),round(sg,4)) for F,k,sg,bk in hits2[:8]])
