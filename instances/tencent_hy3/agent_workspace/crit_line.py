import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
W_E,W_C=0.2,0.05; L=120
nn=np.arange(L); TX,TY=np.meshgrid(2*np.pi*nn/L,2*np.pi*nn/L)
LAM_D=-1+2*W_E*(np.cos(TX)+np.cos(TY))+4*W_C*np.cos(TX)*np.cos(TY)
MD=np.ones_like(LAM_D,bool); MD[0,0]=False; LD=LAM_D[MD]
def maxre(a,b,Du,Dv,lam):
    A=(b-1)+Du*lam; D=-a*a+Dv*lam; Jv=a*a; Gu=-b
    tr=A+D; det=A*D-Jv*Gu; disc=tr*tr-4*det
    re=np.where(disc<0,tr/2.0,(tr+np.sqrt(np.maximum(disc,0)))/2.0)
    return re.max()
def disc_onset(a,b,Du):
    for r in np.linspace(1.0,400,4000):
        if maxre(a,b,Du,Du*r,LD)>1e-7: return r
    return np.nan
a=1.0; Du=0.02
bs=np.round(np.arange(1.1,1.96,0.05),2); dr=[]; cl=[]
for b in bs:
    d=disc_onset(a,b,Du); c=1.0/(b-1)   # analytic continuum LOWER onset = a^2/(b-1)
    dr.append(d); cl.append(c)
    print('b=%.2f  disc_onset Dv/Du=%.2f  cont_lower_onset=%.3f  ratio=%.1f'%(b,d,c,d/c))
dr=np.array(dr); cl=np.array(cl); bs=np.array(bs); ok=np.isfinite(dr)
fig,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].plot(bs[ok],dr[ok],'o-',label='discrete lap9 (L=120)')
ax[0].plot(bs[ok],cl[ok],'s--',label='continuum lower-onset a^2/(b-1)')
ax[0].set_xlabel('b (a=1)'); ax[0].set_ylabel('critical Dv/Du')
ax[0].legend(); ax[0].set_title('Turing onset: discrete lattice vs continuum')
ax[1].plot(bs[ok],(dr/cl)[ok],'o-')
ax[1].set_xlabel('b'); ax[1].set_ylabel('ratio (disc / continuum)')
ax[1].set_title('Bounded Laplacian spectrum raises Dv/Du ~30-50x')
fig.suptitle('Finite-lattice (UV cutoff) shifts the Turing instability threshold')
fig.tight_layout(); fig.savefig('crit_line_shift.png',dpi=110); plt.close()
np.save('crit_line_data.npy',{'b':bs,'disc':dr,'cont':cl,'a':a})
print('mean ratio disc/continuum = %.1f'%np.nanmean(dr/cl))
print('saved')
