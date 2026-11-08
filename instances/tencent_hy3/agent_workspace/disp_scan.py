import numpy as np

# --- fixed point of Gray-Scott for given (F,k) ---
def fixedpoint(F,k):
    u = np.sqrt(F+k)              # from v-equation (v!=0 branch)
    v = F*(1-u)/(F+k)
    return u,v

# --- Jacobian at fixed point ---
def jacobian(F,k):
    u,v = fixedpoint(F,k)
    J00 = -F - 2*u*v
    J01 = -u*u
    J10 = 2*u*v
    J11 = u*u - (F+k)
    return np.array([[J00,J01],[J10,J11]])

# Discrete operator eigenvalues (negative = diffusive). 
# 5-point:  mu5 = -4 + 2(cos kx + cos ky)
# 9-point:  mu9 = -1 + 0.4(cos kx + cos ky) + 0.2 cos kx cos ky
def mu5(kx,ky): return -4.0 + 2.0*(np.cos(kx)+np.cos(ky))
def mu9(kx,ky): return -1.0 + 0.4*(np.cos(kx)+np.cos(ky)) + 0.2*np.cos(kx)*np.cos(ky)

def max_re_lambda(F,k,Du,Dv,mu):
    J = jacobian(F,k)
    a,b,c,d = J[0,0],J[0,1],J[1,0],J[1,1]
    N=64
    ks = np.linspace(0, np.pi, N)
    best=-1e9; bestq=None
    for KX in ks:
        for KY in ks:
            m = mu(KX,KY)
            # linearization: dδ/dt = (J + D*mu) δ   [mu is negative]
            A = (a+d) + (Du+Dv)*m
            B = (a+Du*m)*(d+Dv*m) - b*c
            disc = A*A - 4*B
            if disc>=0:
                re = 0.5*(A + np.sqrt(disc))
            else:
                re = 0.5*A
            if re>best:
                best=re; bestq=(KX,KY)
    return best, bestq

# find a Turing-active (F,k) with 5-pt, Du=0.16,Dv=0.08
Du,Dv=0.16,0.08
results=[]
for F in np.linspace(0.03,0.07,21):
    for k in np.linspace(0.045,0.07,26):
        if F+k>=1: continue
        m5,bq5 = max_re_lambda(F,k,Du,Dv,mu5)
        if m5>0:
            qc=np.hypot(*bq5)
            results.append((m5,F,k,qc))
results.sort()
print("Turing-active (F,k) for 5-pt, sorted by growth rate:")
for m5,F,k,qc in results[:12]:
    wl = 2*np.pi/qc if qc>1e-6 else float('inf')
    print(f"  maxRe={m5:+.4f} F={F:.4f} k={k:.4f} qc={qc:.3f} wavelength~{wl:.1f} cells")

# pick one with modest growth and wavelength ~ 12-25 cells
chosen=None
for m5,F,k,qc in results:
    wl = 2*np.pi/qc if qc>1e-6 else 1e9
    if 0.002<m5<0.02 and 12<wl<30:
        chosen=(F,k); break
if chosen is None and results:
    chosen=(results[0][1],results[0][2])
print("CHOSEN:",chosen)
np.save('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/tencent_hy3/agent_workspace/chosen_Fk.npy', np.array(chosen))
