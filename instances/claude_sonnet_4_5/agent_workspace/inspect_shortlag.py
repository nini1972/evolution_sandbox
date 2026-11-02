import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset

REF={"solar_sunspots":132,"climate_enso":12,"climate_temperatures":365,"neural_eeg":12.8}

def binar(s): 
    s=np.asarray(s,float); return (s>np.median(s)).astype(np.int8)

def mp(x,ms): return np.array([np.mean(x[:-m]==x[m:]) for m in ms])

print(f"{'dataset':22s} {'n':>7s} {'M_p(2)':>7s} {'M_p(11)':>7s} {'M_p(12)':>7s} {'M_p(13)':>7s} {'local-dip':>9s}")
fig,axes=plt.subplots(4,1,figsize=(11,12))
for ax,(name,ref) in zip(axes,REF.items()):
    ds=load_dataset(name); sig=np.asarray(ds.primary_signal,float)
    x=binar(sig); n=len(x)
    ms=list(range(2,61)); y=mp(x,ms)
    # local contrast at true period: y(P) vs mean of y(P-3..P-1),y(P+1..P+3)
    if ref==12.8: P=13
    else: P=int(ref) if ref<=60 else None
    row=[name, n]
    if P:
        i12=ms.index(P); i11=ms.index(P-1); i13=ms.index(P+1)
        base=np.mean([y[i11],y[i13]])
        dip=y[i12]-base
        print(f"{name:22s} {n:7d} {y[ms.index(2)]:7.3f} {y[ms.index(11)]:7.3f} {y[i12]:7.3f} {y[i13]:7.3f} {dip:+9.4f}")
    else:
        print(f"{name:22s} {n:7d} {y[ms.index(2)]:7.3f} {y[ms.index(11)]:7.3f} {'--':>7s} {y[ms.index(13)]:7.3f}")
    ax.plot(ms,y,'b.-',ms=4)
    if ref<=60: ax.axvline(ref,color='g',ls='--',lw=1.5,label=f'ref={ref}')
    # detrend: local linear over +-15
    z=np.zeros(len(y))
    for i in range(len(y)):
        lo,hi=max(0,i-15),min(len(y),i+16)
        c=np.polyfit(ms[lo:hi],y[lo:hi],1); z[i]=y[i]-np.polyval(c,ms[i])
    ax.plot(ms,z,'r-',lw=1,label='local-linear resid')
    ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_title(name,fontsize=9)
fig.tight_layout(); fig.savefig("inspect_shortlag.png",dpi=110)
print("saved inspect_shortlag.png")
