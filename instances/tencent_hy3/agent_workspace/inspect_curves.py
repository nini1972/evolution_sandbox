import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng=np.random.default_rng(909)
def step(a,A,X,b): return np.clip(X*a*a+(1-X)*(a+b*np.sin(2*np.pi*(a-A))),0,1)
def final_phi(L,bv,n,T,kind):
    acc=0.0
    for i in range(n):
        A=rng.random(L)
        X0=rng.random(L)                 # frozen temporal motif
        a = A.copy() if kind=='coherent' else rng.random(L)
        for t in range(T): a=step(a,A,X0,bv)
        acc+=np.mean(np.abs(a-A))
    return acc/n
b=np.linspace(0.0,0.08,33)
L=100; T=2000; n=20
coh=[final_phi(L,bv,n,T,'coherent') for bv in b]
fra=[final_phi(L,bv,n,T,'fractured') for bv in b]
coh=np.array(coh); fra=np.array(fra)
print("b      coh_phi   fra_phi   gap")
for bv,c,f in zip(b,coh,fra):
    print(f"{bv:.4f}  {c:.4f}   {f:.4f}   {f-c:+.4f}")
bist_lo=None; bist_hi=None
for k,bv in enumerate(b):
    if abs(fra[k]-coh[k])>0.05:
        if bist_lo is None: bist_lo=bv
        bist_hi=bv
print("BISTABLE window (gap>0.05):", bist_lo, bist_hi, "width=", (None if bist_lo is None else bist_hi-bist_lo))
plt.figure(figsize=(7,4.5))
plt.plot(b,coh,'-o',label='coherent start (a=A)',color='tab:blue')
plt.plot(b,fra,'-s',label='fractured start (random a)',color='tab:orange')
plt.fill_between(b,coh,fra,where=(fra-coh)>0.05,alpha=0.2,color='green',label='bistable window')
plt.xlabel(r'b'); plt.ylabel(r'$\Phi$'); plt.title(f'Dynamic Loom L={L}: coherent vs fractured attractors')
plt.legend(); plt.tight_layout(); plt.savefig('inspect_curves.png',dpi=130)
print("saved inspect_curves.png  (L=100, T=2000, frozen X)")
