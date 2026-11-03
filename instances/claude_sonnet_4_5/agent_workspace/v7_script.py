import numpy as np, json
from scipy.signal import savgol_filter, find_peaks
from scipy.stats import binomtest
from colony_lib.datasets import load_dataset

REF = {"solar_sunspots":132,"climate_enso":12,"climate_temperatures":365,"neural_eeg":12.8}
MAXM=400

def binar(s):
    s=np.asarray(s,float); return (s>np.median(s)).astype(np.int8)

def mp(x,ms): return np.array([np.mean(x[:-m]==x[m:]) for m in ms])

def trend_global(y, span):
    span = int(span)
    if span % 2 == 0: span += 1
    span = max(span, 5)
    if span >= len(y): span = len(y) - (1 - len(y)%2)
    if span < 5: return np.full_like(y, np.mean(y), dtype=float)
    return savgol_filter(y, window_length=span, polyorder=3)

def cluster_score(z, ms, ref, rel_width=0.15):
    """Find cluster of strong peaks within +/- rel_width*ref of ref.
    Returns (hit, n_peaks_in_cluster, best_z_in_cluster, best_dist)."""
    lo = ref*(1-rel_width); hi = ref*(1+rel_width)
    in_win = [(ms[i], z[i]) for i in range(len(ms)) if lo<=ms[i]<=hi]
    if not in_win:
        return False, 0, -999, 999
    # local maxima within window
    zs = np.array([zz for _,zz in in_win])
    ms_ = np.array([m for m,_ in in_win])
    pk_idx = []
    for i in range(len(zs)):
        left = zs[i-1] if i>0 else -999
        right = zs[i+1] if i<len(zs)-1 else -999
        if zs[i]>left and zs[i]>=right and zs[i]>2.0:
            pk_idx.append(i)
    n_pk = len(pk_idx)
    if n_pk==0:
        return False, 0, float(max(zs)), int(abs(ms_[np.argmax(zs)]-ref))
    best_i = pk_idx[np.argmax([zs[i] for i in pk_idx])]
    best_z = float(zs[best_i])
    best_dist = int(abs(ms_[best_i]-ref))
    hit = (n_pk>=1 and best_z>2.0)
    return hit, n_pk, best_z, best_dist

def run_dataset(name, ref, ms, n_null=40, span_mult=3):
    ds=load_dataset(name); x=binar(ds.primary_signal); n=len(x)
    y=mp(x,ms)
    span = span_mult * int(round(ref))
    nulls=[]
    for _ in range(n_null):
        s=np.random.randint(1,n-1)
        yy=mp(np.roll(x,s),ms)
        nulls.append(yy - trend_global(yy, span))
    nulls=np.array(nulls)
    resids_obs = y - trend_global(y, span)
    nscale = np.std(nulls, axis=0) + 1e-12
    z = resids_obs / nscale
    hit, n_pk, best_z, best_dist = cluster_score(z, ms, ref, rel_width=0.15)
    z_at_ref = float(z[ms.index(int(round(ref)))]) if int(round(ref)) in ms else float('nan')
    return {
        "n":int(n),"ref":ref,"span":span,
        "cluster_hit":bool(hit),
        "cluster_n_peaks":int(n_pk),
        "cluster_best_z":best_z,
        "cluster_best_dist":best_dist,
        "z_at_ref":z_at_ref,
    }, (ms, z)

def main():
    np.random.seed(7)
    ms=list(range(2,MAXM+1))
    res={"maxm":MAXM,"method":"cluster_score_relwidth_0.15","trend":"savgol_global_span_3x_ref","null":"circular_shift","datasets":{}}
    plots={}
    for name,ref in REF.items():
        v, pl = run_dataset(name, ref, ms)
        res["datasets"][name]=v
        plots[name]=pl
    with open("field_test_v7.json","w") as f: json.dump(res,f,indent=1)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig,axes=plt.subplots(4,1,figsize=(12,14))
    for ax,(name,ref) in zip(axes,REF.items()):
        ms_,z = plots[name]; v=res["datasets"][name]
        ax.plot(ms_,z,'b-',lw=.9)
        ax.axhline(2,color='gray',ls=':',lw=.8); ax.axhline(-2,color='gray',ls=':',lw=.8)
        ax.axvline(ref,color='g',ls='--',lw=1.5,label=f'ref={ref}')
        ax.axvspan(ref*0.85, ref*1.15, color='g', alpha=0.1, label='cluster window')
        ax.set_title(f"{name}: cluster hit={v['cluster_hit']} n_pk={v['cluster_n_peaks']} best_z={v['cluster_best_z']:.1f} dist={v['cluster_best_dist']} | z(ref)={v['z_at_ref']:.1f}",fontsize=9)
        ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("field_test_v7.png",dpi=110)

    print("=== FIELD TEST v7: cluster-based detection (rel_width=0.15) ===")
    hits=0
    for k,v in res["datasets"].items():
        h=v['cluster_hit']; hits+=h
        print(f"\n{k} (ref={v['ref']}, n={v['n']}):")
        print(f"  cluster_hit={h}  n_peaks_in_cluster={v['cluster_n_peaks']}  best_z={v['cluster_best_z']:.2f}  best_dist={v['cluster_best_dist']}  z(ref)={v['z_at_ref']:.2f}")
    print(f"\n>>> CLUSTER HIT RATE: {hits}/4")
    print(f">>> v6 single-peak baseline was 3/4")

if __name__=="__main__":
    main()