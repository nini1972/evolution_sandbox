import json, math, numpy as np
from exact_mfpt import RC, S2, K0, ALPHA, B
from decouple_factors import decompose
d=json.load(open('exact_model_comparison.json'))
print("keys:", list(d.keys()))
Ns=np.asarray(d['Ns'],float); lnrate=np.asarray(d['lnrate'],float)
print("n=",len(Ns),"N range",Ns[0],Ns[-1])
print(f"RC={RC:.6f}  B(RC)={B(RC):.6f}  -2B(RC)/S2={-2*B(RC)/S2:.4f}")
print()
print(f"{'N':>7} {'lnrate':>12} {'-c1*N':>12} {'resid':>12} {'L1':>9} {'L2':>9} {'L3':>9} {'L4':>9} {'sum':>9}")
for i in range(0,len(Ns),max(1,len(Ns)//18)):
    N=Ns[i]; r=decompose(N)
    s=r['L1']+r['L2']+r['L3']+r['L4']
    print(f"{N:>7.0f} {lnrate[i]:>12.4f} {'':>12} {'':>12} {r['L1']:>9.4f} {r['L2']:>9.4f} {r['L3']:>9.4f} {r['L4']:>9.4f} {s:>9.4f}")
print()
print("check lnrate + sum(L)  (should be ~0):")
tot=[]
for i,N in enumerate(Ns):
    r=decompose(N); tot.append(lnrate[i]+r['L1']+r['L2']+r['L3']+r['L4'])
tot=np.array(tot)
print(f"  mean={tot.mean():+.6f}  std={tot.std():.6f}  max|.|={np.abs(tot).max():.6f}")
