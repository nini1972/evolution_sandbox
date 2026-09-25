import numpy as np, time, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

t0=time.time()
L=200.0; N=200; dx=L/N; x=np.linspace(0,L,N)
dt=0.1; D=1.0; gamma=1.0

u_c=2*np.sqrt(gamma*D)  # absolute/convective threshold
def briggs(u): return gamma - u**2/(4*D)  # >0 absolute, <0 convective (n=0 stable)

def fisher(u, source=False, T=120.0, seed_pos=100.0):
    n=0.1*np.exp(-((x-seed_pos)**2)/(2*5.0**2))
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

# Cases
nA, sA = fisher(0.0, T=120.0)            # absolute: bootstrap, fills domain
nB, sB = fisher(4.0, T=80.0)             # convective no-source: advects out, domain returns to 0
nS, sS = fisher(4.0, source=True, T=120.0)  # convective + continuous source: persistent wake

print('u_c=%.3f  briggs(u=0)=%.3f  briggs(u=4)=%.3f'%(u_c,briggs(0),briggs(4)))
print('final max A=%.3f  B=%.3f  S=%.3f'%(nA.max(),nB.max(),nS.max()))

fig,ax=plt.subplots(2,2,figsize=(13,9))
im0=ax[0,0].imshow(sA.T,origin='lower',aspect='auto',cmap='magma',extent=[0,120,0,L])
ax[0,0].set_title('Case A  u=0  (ABSOLUTE)  seed bootstraps -> fills domain')
ax[0,0].set_xlabel('time'); ax[0,0].set_ylabel('space')
im1=ax[0,1].imshow(sB.T,origin='lower',aspect='auto',cmap='magma',extent=[0,80,0,L])
ax[0,1].set_title('Case B  u=4  (CONVECTIVE, no source)  packet exits -> returns to 0')
ax[0,1].set_xlabel('time'); ax[0,1].set_ylabel('space')
ax[1,0].plot(x,nA,label='A u=0 (absolute)',lw=2)
ax[1,0].plot(x,nB,label='B u=4 no-source',lw=2)
ax[1,0].plot(x,nS,label='B+source (persistent wake)',lw=2)
ax[1,0].set_title('Final profiles'); ax[1,0].set_xlabel('space'); ax[1,0].legend(); ax[1,0].set_ylim(-0.1,1.2)
im2=ax[1,1].imshow(sS.T,origin='lower',aspect='auto',cmap='magma',extent=[0,120,0,L])
ax[1,1].set_title('Convective + continuous source -> sustained structure')
ax[1,1].set_xlabel('time'); ax[1,1].set_ylabel('space')
fig.suptitle('Loom Refinement: trivial-state stability is the BRIGGS absolute criterion.\n'+
              'Convective (drift-stabilized) trivial is linearly stable yet supports a source-maintained wake',fontsize=11)
plt.tight_layout(); plt.savefig('loom/fig_convective_refinement.png',dpi=110); print('saved fig; elapsed %.1f'%(time.time()-t0))

payload={'u_c':u_c,'briggs_u0':briggs(0),'briggs_u4':briggs(4),
         'final_max_A':float(nA.max()),'final_max_B':float(nB.max()),'final_max_S':float(nS.max())}
json.dump(payload,open('loom/convective_payload.json','w'),indent=2)
