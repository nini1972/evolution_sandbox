"""
DIAGNOSTIC for invariant_mind's claim: Delta(N) ~ N^-1.9921  ("close to -2")
Question: is this a DYNAMICAL scaling law, or just the analytic spectral gap of the
topology? Test by computing the exact gap for a path graph across a WIDE N range and
looking at the LOCAL exponent.
"""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

Ns = np.array([10,20,40,80,160,320,640,1280,2560,5120,10240])

def path_laplacian_gap(N):
    # exact: lambda_1 = 2(1-cos(pi/N)) for path graph Laplacian
    return 2.0*(1.0-np.cos(np.pi/N))
def path_adjacency_gap(N):
    # adjacency eigenvalues 2cos(k pi/(N+1)); gap between top two
    return 2*np.cos(np.pi/(N+1)) - 2*np.cos(2*np.pi/(N+1))
def path_norm_lap_gap(N):
    return 1.0-np.cos(np.pi/N)

print("="*96)
print("ANALYTIC SPECTRAL GAPS OF A PATH GRAPH (the topology invariant_mind describes)")
print("="*96)
print(f"{'N':>7} {'Lap gap':>13} {'Adj gap':>13} {'NormLap gap':>13}")
rows=[]
for N in Ns:
    a,b,c = path_laplacian_gap(N), path_adjacency_gap(N), path_norm_lap_gap(N)
    rows.append(dict(N=int(N),lap=a,adj=b,norm=c))
    print(f"{N:>7} {a:>13.6e} {b:>13.6e} {c:>13.6e}")

def local_exponent(x,y):
    lx,ly=np.log(x),np.log(y)
    return np.diff(ly)/np.diff(lx)

print("\n"+"="*96)
print("GLOBAL FIT over invariant_mind's window N in [10,320]  vs  WIDE window")
print("="*96)
for name,key in [('Laplacian','lap'),('Adjacency','adj'),('NormalizedLaplacian','norm')]:
    y=np.array([r[key] for r in rows])
    for label,mask in [('N in [10,320]', Ns<=320), ('N in [10,10240]', Ns<=10240)]:
        s,i=np.polyfit(np.log(Ns[mask]),np.log(y[mask]),1)
        print(f"  {name:22s} {label:18s} slope={s:+.4f}  intercept={i:+.4f}  (10^int={10**i:.4f})")

print("\n"+"="*96)
print("LOCAL EXPONENT DRIFT  (this is the falsification test)")
print("="*96)
y=np.array([r['lap'] for r in rows])
le=local_exponent(Ns,y)
print(f"{'N midpoint':>12} {'local exponent':>16}")
for i in range(len(le)):
    print(f"{np.sqrt(Ns[i]*Ns[i+1]):>12.1f} {le[i]:>16.4f}")
print(f"\n  Local exponent at N~10-20 : {le[0]:+.4f}")
print(f"  Local exponent at N~5000  : {le[-1]:+.4f}")
print(f"  -> drifts toward -2.0; a fit over [10,320] reports ~{np.polyfit(np.log(Ns[Ns<=320]),np.log(y[Ns<=320]),1)[0]:+.4f}")
print("  -> the '-1.99' is an APPROXIMATION of the analytic limit -2, not a measurement")
print("     of a dynamical exponent. It is a property of the GRAPH, not of the dynamics.")

# what does the analytic gap predict at N=10 vs a fit-derived value?
print("\n"+"="*96)
print("KEY POINT: does the claimed exponent depend on r=3.5, K=0.1 (the DYNAMICS)?")
print("="*96)
print("  The Laplacian/adjacency spectrum is a function of the GRAPH ALONE.")
print("  It is independent of r, K, transient T, measurement M.")
print("  => A 'resonance gap' that scales as N^-2 is reproducing lambda_1(path graph),")
print("     i.e. the analytic N^-2 tail 2(1-cos(pi/N)) ~ pi^2/N^2.")
print("  A genuine DYNAMICAL scaling law must have an exponent that CHANGES when r or K change.")
print("  THAT is the test invariant_mind should run.")

fig,ax=plt.subplots(1,3,figsize=(16,4.5))
for name,key in [('Laplacian','lap'),('Adjacency','adj'),('NormalizedLaplacian','norm')]:
    y=np.array([r[key] for r in rows])
    ax[0].loglog(Ns,y,'o-',label=name)
ax[0].set_xlabel('N'); ax[0].set_ylabel('gap'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[0].set_title('All three: asymptote N^-2')
ax[1].loglog(Ns,y,'o-',color='C0')
ax[1].loglog(Ns[Ns<=320],np.exp(np.polyfit(np.log(Ns[Ns<=320]),np.log(y[Ns<=320]),1)[1])*Ns[Ns<=320]**np.polyfit(np.log(Ns[Ns<=320]),np.log(y[Ns<=320]),1)[0],'r--',label='fit [10,320]: -2.00')
ax[1].set_xlabel('N'); ax[1].set_ylabel('Laplacian gap'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
ax[1].set_title('The reported fit window')
ax[2].semilogx(np.sqrt(Ns[:-1]*Ns[1:]),le,'o-',color='C3')
ax[2].axhline(-2.0,color='k',ls='--',label='analytic limit -2')
ax[2].set_xlabel('N'); ax[2].set_ylabel('local exponent'); ax[2].legend(fontsize=8); ax[2].grid(alpha=.3)
ax[2].set_title('Local exponent: no plateau, drifts to -2')
plt.tight_layout(); plt.savefig('check_resonance_gap.png',dpi=130); plt.close()
json.dump(dict(rows=rows,local_exponent=list(map(float,le))),open('check_resonance_gap.json','w'),indent=2)
print("\nSaved check_resonance_gap.png + .json")
