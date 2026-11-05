import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
W_E,W_C=0.2,0.05; L=120
nn=np.arange(L); TX,TY=np.meshgrid(2*np.pi*nn/L,2*np.pi*nn/L)
LAM_DISC=-1+2*W_E*(np.cos(TX)+np.cos(TY))+4*W_C*np.cos(TX)*np.cos(TY)
qx=np.arange(0.01,np.pi+0.01,0.02); QX,QY=np.meshgrid(qx,qx)
LAM_CONT=-(2*np.pi/L*np.hypot(QX,QY))**2
MD=np.ones_like(LAM_DISC,bool); MD[0,0]=False
MC=np.ones_like(LAM_CONT,bool); MC[0,0]=False
LD=LAM_DISC[MD]; LC=LAM_CONT[MC]
def maxre(a,b,Du,Dv,lam):
    A=(b-1)+Du*lam; D=-a*a+Dv*lam; Jv=a*a; Gu=-b
    tr=A+D; det=A*D-Jv*Gu; disc=tr*tr-4*det
    re=np.where(disc<0,tr/2.0,(tr+np.sqrt(np.maximum(disc,0)))/2.0)
    return re.max()
def crit(a,b,Du,kind):
    lam=LD if kind=='disc' else LC
    lo,hi=Du*1.02, Du*5000.0
    if maxre(a,b,Du,lo,lam)<=1e-6: return np.nan
    if maxre(a,b,Du,hi,lam)>1e-6: return np.nan
    for _ in range(60):
        mid=0.5*(lo+hi)
        if maxre(a,b,Du,mid,lam)>1e-6: hi=mid
        else: lo=mid
    return 0.5*(lo+hi)/Du
as_=np.round(np.arange(0.4,1.0,0.05),2); Du=0.02
dr=[];cr=[];bs=[]
for a in as_:
    b=1.1+0.4*a*a   # HS stable (b<1+a^2) and b>1
    d=crit(a,b,Du,'disc'); c=crit(a,b,Du,'cont')
    dr.append(d); cr.append(c); bs.append(b)
    print(f"a={a} b={b:.3f} crit Dv/Du disc={d:.2f} cont={c:.1f} disc/cont={d/c:.3f}" if d==d and c==c else f"a={a} b={b:.3f} d={d} c={c}")
dr=np.array(dr);cr=np.array(cr);bs=np.array(bs);au=np.array(as_)
fig,ax=plt.subplots(1,2,figsize=(10,4))
ax[0].plot(au,dr,'o-',label='discrete lap9 (L=120)'); ax[0].plot(au,cr,'s--',label='continuous \u03bb=-k\u00b2')
ax[0].set_xlabel('a');ax[0].set_ylabel('critical Dv/Du');ax[0].legend();ax[0].set_title('Brusselator Turing onset (b=1.1+0.4a\u00b2)')
ax[1].plot(au,dr/cr,'o-');ax[1].set_xlabel('a');ax[1].set_ylabel('ratio discrete/continuous');ax[1].set_title('Discretization LOWERS Turing threshold')
fig.suptitle('Finite-lattice shift: discrete kernel eases Turing onset')
fig.tight_layout();fig.savefig('crit_line_shift.png',dpi=110);plt.close()
np.save('crit_line_data.npy',{'a':au,'b':bs,'disc':dr,'cont':cr})
print('saved')
