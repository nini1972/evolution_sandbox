import numpy as np, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import laplace, label

def run(F,k,N=90,Da=0.16,Db=0.08,steps=6000,seed=11):
    rng=np.random.default_rng(seed)
    U=np.ones((N,N)); V=np.zeros((N,N))
    y0,x0=rng.integers(25,N-25,2)
    U[y0-5:y0+5,x0-5:x0+5]=0.5; V[y0-5:x0+5,x0-5:x0+5]=0.25
    ts=[]; ns=[]
    for s in range(steps):
        uv2=U*V*V
        U=np.clip(U+Da*laplace(U)-uv2+F*(1-U),0,1)
        V=np.clip(V+Db*laplace(V)+uv2-(F+k)*V,0,1)
        if s%500==0:
            ns.append(label(V>0.2)[1]); ts.append(s)
    return np.array(ts),np.array(ns)

k=0.0626
Fs=np.linspace(0.022,0.034,13)
res={}
for F in Fs:
    ts,ns=run(F,k)
    # growth rate from log(N) in window where N between 2 and 200
    m=(ns>=2)&(ns<=200)
    if m.sum()>=3 and ns[m].min()>0:
        g=np.polyfit(ts[m],np.log(ns[m]),1)[0]
    else:
        g=0.0
    res[round(float(F),5)]={'g':float(g),'traj':[int(x) for x in ns]}
    print(f"F={F:.4f} g={g:+.4f} Nend={ns[-1]}")

plt.figure(figsize=(7,4))
for F in Fs:
    plt.plot(np.linspace(0,6000,len(res[round(float(F),5)]['traj'])),
             res[round(float(F),5)]['traj'],label=f"F={F:.4f}")
plt.yscale('log'); plt.xlabel('step'); plt.ylabel('cluster count N'); plt.title(f'Edge of Life, k={k}')
plt.legend(fontsize=7); plt.tight_layout(); plt.savefig('gs_edge_probe.png',dpi=130)
# growth rate vs F
ff=sorted(res); gg=[res[f]['g'] for f in ff]
plt.figure(figsize=(7,4)); plt.plot(ff,gg,'o-'); plt.axhline(0,color='k',lw=.5)
plt.xlabel('F'); plt.ylabel('replication rate g (1/step)'); plt.title('Replication rate at life boundary')
plt.tight_layout(); plt.savefig('gs_edge_g.png',dpi=130)
json.dump({'k':k,'res':res},open('gs_edge_probe.json','w'))
print('done')
