import numpy as np, json
from scipy.signal import savgol_filter
from scipy.stats import binomtest
from colony_lib.datasets import load_dataset

REF = {"solar_sunspots":132,"climate_enso":12,"climate_temperatures":365,"neural_eeg":12.8}
MAXM=400

def binar(s):
    s=np.asarray(s,float); return (s>np.median(s)).astype(np.int8)

def mp(x,ms): return np.array([np.mean(x[:-m]==x[m:]) for m in ms])

def trend_global(y, span):
    """Global Savitzky-Golay trend with window = span (odd), polyorder 3."""
    span = int(span)
    if span % 2 == 0: span += 1
    span = max(span, 5)
    if span >= len(y): span = len(y) - (1 - len(y)%2)
    if span < 5: return np.full_like(y, np.mean(y), dtype=float)
    return savgol_filter(y, window_length=span, polyorder=3)

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

def run_dataset(name, ref, ms, n_null=40, span_mult=3):
    ds=load_dataset(name); x=binar(ds.primary_signal); n=len(x)
    y=mp(x,ms)
    span = span_mult * int(round(ref))
    # circular-shift surrogate null, each detrended with SAME global trend
    nulls=[]
    for _ in range(n_null):
        s=np.random.randint(1,n-1)
        yy=mp(np.roll(x,s),ms)
        nulls.append(yy - trend_global(yy, span))
    nulls=np.array(nulls)
    resids_obs = y - trend_global(y, span)
    nscale = np.std(nulls, axis=0) + 1e-12
    z = resids_obs / nscale
    pk = peaks(z, 2.0, 1.0)
    top = sorted([(ms[i], float(z[i])) for i in pk], key=lambda t:-t[1])
    tol = max(2,int(round(0.10*ref))) if ref<100 else max(3,int(round(0.05*ref)))
    near = [(m,zz) for m,zz in top if abs(m-ref)<=tol]
    z_at_ref = float(z[ms.index(int(round(ref)))]) if int(round(ref)) in ms else float('nan')
    # parity (raw vs residual) — kept as negative control only
    pars_raw=[];pars_res=[]
    for k in range(1,121):
        if (2*k+1) in ms:
            i2,i3=ms.index(2*k),ms.index(2*k+1)
            pars_raw.append(y[i2]-y[i3]); pars_res.append(resids_obs[i2]-resids_obs[i3])
    pars_raw=np.array(pars_raw); pars_res=np.array(pars_res)
    p_sign=float(binomtest(int(np.sum(pars_raw>0)),len(pars_raw),0.5,alternative='greater').pvalue)
    return {
        "n":int(n),"ref":ref,"span":span,
        "n_peaks":len(top),"top_peaks":top[:8],
        "near_ref_hit":bool(len(near)>0),
        "nearest_peak_dist":int(min([abs(m-ref) for m,_ in top]) if top else 999),
        "z_at_ref":z_at_ref,
        "parity_raw_pos_frac":float(np.mean(pars_raw>0)),
        "parity_sign_p":p_sign,
        "parity_res_pos_frac":float(np.mean(pars_res>0)),
    }, (ms, z)

def main():
    np.random.seed(7)
    ms=list(range(2,MAXM+1))
    res={"maxm":MAXM,"trend":"savgol_global_span_3x_ref","null":"circular_shift","datasets":{}}
    plots={}
    for name,ref in REF.items():
        v, pl = run_dataset(name, ref, ms)
        res["datasets"][name]=v
        plots[name]=pl
    with open("field_test_v6.json","w") as f: json.dump(res,f,indent=1)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig,axes=plt.subplots(4,1,figsize=(12,14))
    for ax,(name,ref) in zip(axes,REF.items()):
        ms_,z = plots[name]; v=res["datasets"][name]
        ax.plot(ms_,z,'b-',lw=.9)
        ax.axhline(2,color='gray',ls=':',lw=.8); ax.axhline(-2,color='gray',ls=':',lw=.8)
        ax.axvline(ref,color='g',ls='--',lw=1.5,label=f'ref={ref}')
        for m,zz in v["top_peaks"][:5]:
            ax.plot([m],[zz],'rv',ms=8); ax.annotate(f"{m}",(m,zz),fontsize=7,color='r')
        ax.set_title(f"{name}: global-trend z | near-ref hit={v['near_ref_hit']} nearest_dist={v['nearest_peak_dist']} | z(ref)={v['z_at_ref']:.1f} span={v['span']}",fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("field_test_v6.png",dpi=110)

    print("=== FIELD TEST v6: global Savgol trend (3x ref) + circular-shift null ===")
    hits=0
    for k,v in res["datasets"].items():
        h=v['near_ref_hit']; hits+=h
        print(f"\n{k} (ref={v['ref']}, span={v['span']}, n={v['n']}):")
        print(f"  near_ref_hit={h}  nearest_peak_dist={v['nearest_peak_dist']}  z(ref)={v['z_at_ref']:.2f}")
        print(f"  top peaks: {[(m,round(z,1)) for m,z in v['top_peaks'][:5]]}")
        print(f"  parity(raw) pos-frac={v['parity_raw_pos_frac']:.3f} p={v['parity_sign_p']:.2e} | (res)={v['parity_res_pos_frac']:.3f}")
    print(f"\n>>> NEAR-REF HIT RATE: {hits}/4")
    print(f">>> v5 baseline was 2/4")

if __name__=="__main__":
    main()