import numpy as np, json
from colony_lib.datasets import load_dataset

REF = {"solar_sunspots":132,"climate_enso":12,"climate_temperatures":365,"neural_eeg":12.8}
MAXM=400

def binar(s):
    s=np.asarray(s,float); return (s>np.median(s)).astype(np.int8)

def mp(x,ms): return np.array([np.mean(x[:-m]==x[m:]) for m in ms])

def local_detrend(ms,y,w):
    """Local linear fit over +-w lags -> residual."""
    r=np.zeros(len(y))
    for i in range(len(y)):
        lo,hi=max(0,i-w),min(len(y),i+w+1)
        c=np.polyfit(ms[lo:hi],y[lo:hi],1)
        r[i]=y[i]-np.polyval(c,ms[i])
    return r

def peaks(z, zmin=2.0, prom=1.0):
    out=[]
    for i in range(2,len(z)-2):
        if z[i]>z[i-1] and z[i]>=z[i+1] and z[i]>zmin:
            l=z[i]; j=i-1
            while j>=0 and z[j]<z[i]: l=min(l,z[j]); j-=1
            rr=z[i]; k=i+1
            while k<len(z) and z[k]<z[i]: rr=min(rr,z[k]); k+=1
            if z[i]-max(l,rr)>=prom: out.append(i)
    return out

def main():
    np.random.seed(7)
    ms=list(range(2,MAXM+1)); n_null=40; w=20
    res={"maxm":MAXM,"datasets":{}}
    plots={}
    for name,ref in REF.items():
        ds=load_dataset(name); x=binar(ds.primary_signal); n=len(x)
        y=mp(x,ms)
        # surrogate null: circular shift of ORIGINAL series (keeps local
        # autocorr envelope, destroys exact global periodicity alignment)
        nulls=[]
        for _ in range(n_null):
            s=np.random.randint(1,n-1)
            nulls.append(mp(np.roll(x,s),ms))
        nulls=np.array(nulls)
        resids_obs=local_detrend(ms,y,w)
        null_res=np.array([local_detrend(ms,row,w) for row in nulls])
        nscale=np.std(null_res,axis=0)+1e-12
        z=resids_obs/nscale
        pk=peaks(z,2.0,1.0)
        top=sorted([(ms[i],float(z[i])) for i in pk],key=lambda t:-t[1])
        tol=max(2,int(round(0.10*ref))) if ref<100 else max(3,int(round(0.05*ref)))
        near=[(m,zz) for m,zz in top if abs(m-ref)<=tol]
        near_hit=len(near)>0
        z_at_ref=float(z[ms.index(int(round(ref)))] if int(round(ref)) in ms else float('nan'))
        pars_raw=[];pars_res=[]
        for k in range(1,121):
            if (2*k+1) in ms:
                i2,i3=ms.index(2*k),ms.index(2*k+1)
                pars_raw.append(y[i2]-y[i3])
                pars_res.append(resids_obs[i2]-resids_obs[i3])
        pars_raw=np.array(pars_raw); pars_res=np.array(pars_res)
        from scipy.stats import binomtest
        p_sign=float(binomtest(int(np.sum(pars_raw>0)),len(pars_raw),0.5,alternative='greater').pvalue)
        divs=[m for m in ms if m<=60 and abs(ref/m-round(ref/m))<1e-9 and round(ref/m)>=1]
        z_div={str(m):float(z[ms.index(m)]) for m in divs}
        res["datasets"][name]={
          "n":int(n),"ref":ref,
          "n_peaks":len(top),
          "top_peaks":top[:8],
          "near_ref_hit":bool(near_hit),
          "nearest_peak_dist":int(min([abs(m-ref) for m,_ in top]) if top else 999),
          "z_at_ref":z_at_ref,
          "parity_raw_pos_frac":float(np.mean(pars_raw>0)),
          "parity_sign_p":p_sign,
          "parity_res_pos_frac":float(np.mean(pars_res>0)),
          "z_at_short_divisors":z_div,
        }
        plots[name]=(ms,z,v if (v:=res["datasets"][name]) else None)
    with open("field_test_v5.json","w") as f: json.dump(res,f,indent=1)
    # figure (z already computed above; no recompute needed)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig,axes=plt.subplots(4,1,figsize=(12,14))
    for ax,(name,ref) in zip(axes,REF.items()):
        ms_,z,v=plots[name]
        ax.plot(ms_,z,'b-',lw=.9)
        ax.axhline(2,color='gray',ls=':',lw=.8); ax.axhline(-2,color='gray',ls=':',lw=.8)
        ax.axvline(ref,color='g',ls='--',lw=1.5,label=f'ref={ref}')
        for m,zz in v["top_peaks"][:5]:
            ax.plot([m],[zz],'rv',ms=8)
            ax.annotate(f"{m}",(m,zz),fontsize=7,color='r')
        ax.set_title(f"{name}: local-z residual | near-ref hit={v['near_ref_hit']} nearest_dist={v['nearest_peak_dist']} | z(ref)={v['z_at_ref']:.1f}",fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("field_test_v5.png",dpi=110)

    print("=== FIELD TEST v5: local detrend + circular-shift null ===")
    for k,v in res["datasets"].items():
        print(f"\n{k} (ref={v['ref']}, n={v['n']}):")
        print(f"  near_ref_hit={v['near_ref_hit']}  nearest_peak_dist={v['nearest_peak_dist']}  z(ref)={v['z_at_ref']:.2f}")
        print(f"  top peaks: {v['top_peaks'][:5]}")
        print(f"  parity pos-frac(raw)={v['parity_raw_pos_frac']:.3f} sign-p={v['parity_sign_p']:.2e} pos-frac(res)={v['parity_res_pos_frac']:.3f}")
        print(f"  z at short divisors: {v['z_at_short_divisors']}")

if __name__=="__main__":
    main()
