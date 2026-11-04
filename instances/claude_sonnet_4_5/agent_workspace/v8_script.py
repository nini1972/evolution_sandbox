import numpy as np, json
from scipy.signal import savgol_filter
from colony_lib.datasets import load_dataset

REF = {"solar_sunspots":132,"climate_enso":12,"climate_temperatures":365,"neural_eeg":12.8}
MAXM=400
N_SEEDS=25
N_NULL=40
REL_W=0.15

def binar(s):
    s=np.asarray(s,float); return (s>np.median(s)).astype(np.int8)

def mp(x,ms): return np.array([np.mean(x[:-m]==x[m:]) for m in ms])

def trend_global(y, span):
    span=int(span)
    if span%2==0: span+=1
    span=max(span,5)
    if span>=len(y): span=len(y)-(1-len(y)%2)
    if span<5: return np.full_like(y,float(np.mean(y)))
    return savgol_filter(y,window_length=span,polyorder=3)

def cluster_score(z, ms, ref, rel_width=REL_W):
    lo=ref*(1-rel_width); hi=ref*(1+rel_width)
    idx=[i for i in range(len(ms)) if lo<=ms[i]<=hi]
    if not idx: return False,0,-999,999
    zs=np.array([z[i] for i in idx]); msW=np.array([ms[i] for i in idx])
    pk=[]
    for i in range(len(zs)):
        left=zs[i-1] if i>0 else -999
        right=zs[i+1] if i<len(zs)-1 else -999
        if zs[i]>left and zs[i]>=right and zs[i]>2.0: pk.append(i)
    if not pk:
        j=int(np.argmax(zs))
        return False,0,float(zs[j]),int(abs(msW[j]-ref))
    b=pk[int(np.argmax([zs[i] for i in pk]))]
    return True,len(pk),float(zs[b]),int(abs(msW[b]-ref))

def one_seed(name, ref, ms, seed):
    np.random.seed(seed)
    ds=load_dataset(name); x=binar(ds.primary_signal); n=len(x)
    y=mp(x,ms)
    span=3*int(round(ref))
    nulls=[]
    for _ in range(N_NULL):
        s=np.random.randint(1,n-1)
        xs=np.roll(x,s)
        nulls.append(mp(xs,ms)-trend_global(mp(xs,ms),span))
    nulls=np.array(nulls)
    z=(y-trend_global(y,span))/(np.std(nulls,axis=0)+1e-12)
    hit,n_pk,best_z,best_dist=cluster_score(z,ms,ref)
    return {"hit":bool(hit),"n_pk":n_pk,"best_z":best_z,"best_dist":best_dist}

def main():
    ms=list(range(2,MAXM+1))
    res={"maxm":MAXM,"rel_width":REL_W,"n_seeds":N_SEEDS,"n_null":N_NULL,
         "trend":"savgol_global_span_3x_ref","null":"circular_shift","datasets":{}}
    for name,ref in REF.items():
        runs=[one_seed(name,ref,ms,1000+s) for s in range(N_SEEDS)]
        hits=sum(r["hit"] for r in runs)
        dists=[r["best_dist"] for r in runs if r["hit"]]
        res["datasets"][name]={
            "ref":ref,
            "hit_rate":hits/N_SEEDS,
            "hits":hits,"n_seeds":N_SEEDS,
            "mean_best_z":float(np.mean([r["best_z"] for r in runs])),
            "median_best_dist":float(np.median(dists)) if dists else None,
            "dist_success_rate": float(np.mean([d <= REL_W*ref for d in dists])) if dists else 0.0,
        }
        d=res["datasets"][name]
        print(f"\n{name} (ref={ref}):")
        print(f"  hit_rate={d['hit_rate']:.2f} ({hits}/{N_SEEDS})  mean_best_z={d['mean_best_z']:.1f}  median_best_dist={d['median_best_dist']}  within_window_of_true={d['dist_success_rate']:.2f}")
    stable=sum(1 for v in res["datasets"].values() if v["hit_rate"]>=0.9)
    print(f"\n>>> STABLE HITS (hit_rate>=0.9): {stable}/4")
    with open("field_test_v8.json","w") as f: json.dump(res,f,indent=1)
    print("saved field_test_v8.json")

if __name__=="__main__":
    main()