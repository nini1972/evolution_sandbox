import numpy as np, json, time, scipy.ndimage as ndi
t0=time.time()
N=160; Du,Dv,dt=0.16,0.08,1.0; F=0.040; k=0.0648
lap=lambda u: (np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)-4*u)
def run(sigma, seed):
    rng=np.random.default_rng(seed)
    A=np.ones((N,N),np.float32); B=(rng.random((N,N))<0.02).astype(np.float32)*rng.random((N,N))
    cells=[]
    for step in range(6001):
        LapA=lap(A); LapB=lap(B)
        AB2=A*B*B
        A+=dt*(Du*LapA-AB2+F*(1-A))
        B+=dt*(Dv*LapB+AB2-(k+F)*B)
        if sigma>0: B*= (1.0+sigma*rng.standard_normal((N,N)))
        B=np.clip(B,0,1); A=np.clip(A,0,1)
        if step%20==0:
            lab,n=ndi.label(B>0.2)
            cells.append(lab)
    # division detector: parent component at frame f splits into >=2 at f+1
    div=0
    for f in range(len(cells)-1):
        lab0,cnt0=cells[f],cells[f].max()
        lab1=cells[f+1]
        for p in range(1,cnt0+1):
            mask=lab0==p
            if mask.sum()<4: continue
            kids=np.unique(lab1[mask]); kids=kids[kids>0]
            # require >=2 daughters each covering >=30% of parent overlap count
            good=0
            for kd in kids:
                if (lab1[mask]==kd).sum()/mask.sum()>0.3: good+=1
            if good>=2: div+=1
    return div
sigs=[0.0,0.002,0.005,0.01,0.03,0.05]
out={}
for s in sigs:
    d=run(s, 12345+int(s*1000))
    out[s]=d
    print(f"  sigma={s:.3f} N_div={d} t={time.time()-t0:.0f}s")
print("WROTE clade_zeta_noise_repl.json", out)
json.dump(out, open('clade_zeta_noise_repl.json','w'), indent=2)
