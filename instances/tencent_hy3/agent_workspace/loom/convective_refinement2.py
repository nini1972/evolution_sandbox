import numpy as np, time, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
t0=time.time()
L=200.0; N=200; dx=L/N; x=np.linspace(0,L,N)
dt=0.1; D=1.0; gamma=1.0; seed=100.0
u_c=2*np.sqrt(gamma*D)
def briggs(u): return gamma - u**2/(4*D)
def fisher(u, source=False, T=120.0):
    n=0.1*np.exp(-((x-seed)**2)/(2*5.0**2))
    snap=[]; nsteps=int(T/dt); rec=max(1,nsteps//60)
    for step in range(nsteps):
        nw=np.empty(N)
        for i in range(N):
            nL = n[i-1] if i>0 else (1.0 if source else n[i])
            nR = n[i+1] if i<N-1 else n[i]
            lap=(nR-2*n[i]+nL)/dx**2
            adv=(n[i]-nL)/dx if u>0 else (nR-n[i])/dx
            nw[i]=n[i]+dt*(gamma*n[i]*(1-n[i]) + D*lap - u*adv)
        n=nw
        if step%rec==0: snap.append(n.copy())
    return n, np.array(snap)
nA,sA=fisher(0.0,T=120.0)
nB,sB=fisher(4.0,T=120.0)
nS,sS=fisher(4.0,source=True,T=120.0)
def upstream(n): return float(np.mean(n[x<seed]>0.1))
print('u_c=%.2f briggs(0)=%.2f briggs(4)=%.2f'%(u_c,briggs(0),briggs(4)))
print('upstream_alive: A=%.2f B=%.2f S=%.2f'%(upstream(nA),upstream(nB),upstream(nS)))
fig,ax=plt.subplots(2,2,figsize=(13,9))
ax[0,0].imshow(sA.T,origin='lower',aspect='auto',cmap='magma',extent=[0,120,0,L]); ax[0,0].axhline(seed,ls='--',c='cyan')
ax[0,0].set_title('A: u=0 ABSOLUTE - front spreads both ways, whole domain boots up')
ax[0,1].imshow(sB.T,origin='lower',aspect='auto',cmap='magma',extent=[0,120,0,L]); ax[0,1].axhline(seed,ls='--',c='cyan')
ax[0,1].set_title('B: u=4 CONVECTIVE - only downstream fills; upstream is empty horizon')
ax[1,0].plot(x,nA,label='A u=0'); ax[1,0].plot(x,nB,label='B u=4 (upstream empty)'); ax[1,0].plot(x,nS,label='B+source (sustained)')
ax[1,0].axvline(seed,ls='--',c='cyan'); ax[1,0].axvspan(0,seed,alpha=0.12,color='red'); ax[1,0].set_ylim(-0.1,1.2)
ax[1,0].set_title('final profiles (red = upstream / empty horizon)'); ax[1,0].legend()
ax[1,1].axis('off')
ax[1,1].text(0.02,0.92,'LOOM REFINEMENT - Briggs absolute criterion',fontsize=12,fontweight='bold')
ax[1,1].text(0.02,0.80,'Trivial-state stability for BOOTSTRAP = Briggs saddle:\n  L(k)=gamma - D k^2 - i u k ;  L_s = gamma - u^2/(4D)',fontsize=10)
ax[1,1].text(0.02,0.66,'  u < u_c=2 : ABSOLUTE -> seed bootstraps everywhere (Branch A)\n  u > u_c=2 : CONVECTIVE -> n=0 stable upstream;\n               structure only in downstream wake / needs a source',fontsize=10)
ax[1,1].text(0.02,0.44,'Even a UNIFORMLY-unstable trivial (L(0)=gamma>0) becomes\nabsolutely stable under drift -> upstream is a lawful EMPTY\nHORIZON where life can never bootstrap.',fontsize=10)
ax[1,1].text(0.02,0.22,'Implication: replace "sign of uniform mode" with "Briggs\nabsolute growth". Branch B splits into convective (needs\nsource) vs impossible.',fontsize=10)
fig.suptitle('Loom Refinement: the empty-horizon law from convective instability',fontsize=12)
plt.tight_layout(); plt.savefig('loom/fig_convective_refinement.png',dpi=110); print('saved; elapsed %.1f'%(time.time()-t0))
json.dump({'u_c':u_c,'briggs_u0':briggs(0),'briggs_u4':briggs(4),
           'upstream_alive_A':upstream(nA),'upstream_alive_B':upstream(nB),'upstream_alive_S':upstream(nS)},
          open('loom/convective_payload.json','w'),indent=2)
