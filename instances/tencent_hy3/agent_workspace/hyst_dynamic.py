import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng=np.random.default_rng(2026)
def step(a,A,X,b): return np.clip(X*a*a+(1-X)*(a+b*np.sin(2*np.pi*(a-A))),0,1)
def adiab_sweep(L,bgrid,n,T,direction):
    out=np.zeros((n,len(bgrid)))
    order=range(len(bgrid)) if direction=='up' else range(len(bgrid)-1,-1,-1)
    for i in range(n):
        A=rng.random(L)
        X0=rng.random(L)                      # single frozen temporal motif
        a=A.copy()                            # coherent start
        for j in order:
            bv=bgrid[j]
            for t in range(T): a=step(a,A,X0,bv)
            out[i,j]=np.mean(np.abs(a-A))
    return out.mean(0)
b=np.linspace(0,0.2,21); T=2000
res={}
plt.figure(figsize=(9,5))
for L in [60,100,150]:
    Xf=np.zeros((20,L)); 
    # pre-generate frozen motifs per trial inside adiab
    fu=adiab_sweep(L,b,12,T,'up')
    bd=adiab_sweep(L,b,12,T,'down')
    # critical points via threshold 0.2 on Phi
    thr=0.2
    fidx=np.argmax(fu>=thr) if np.any(fu>=thr) else 0
    b_f=b[fidx]
    didx=len(b)-1-np.argmax(bd[::-1]>=thr) if np.any(bd>=thr) else len(b)-1
    b_b=b[didx]
    width=(b_b-b_f) if (np.any(fu>=thr) and np.any(bd>=thr)) else np.nan
    res[L]=dict(b_f=float(b_f),b_b=float(b_b),width=float(width))
    print(f"L={L}: b_f(up)={b_f:.3f}  b_b(down)={b_b:.3f}  width={width:.3f}")
    c='tab:blue' if L==60 else ('tab:green' if L==100 else 'tab:red')
    plt.plot(b,fu,'--',color=c,label=f'L={L} sweep up'); plt.plot(b,bd,':',color=c,label=f'L={L} sweep down')
plt.axhline(0.2,color='gray',lw=0.6,ls='-.'); plt.xlabel(r'b'); plt.ylabel(r'$\Phi$ (mean |a-A|)')
plt.title('Dynamic frozen-noise Loom: hysteresis loop (coherent/fractured bistability)')
plt.legend(fontsize=7); plt.tight_layout(); plt.savefig('hyst_dynamic.png',dpi=130)
import json; json.dump(res,open('hyst_dynamic.json','w'),indent=2)
print("saved hyst_dynamic.png ; res=",res)
