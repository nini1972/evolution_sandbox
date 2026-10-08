import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng=np.random.default_rng(314)
def step(a,A,X,b): return np.clip(X*a*a+(1-X)*(a+b*np.sin(2*np.pi*(a-A))),0,1)
def measure(L,bv,n,T,kind):
    f_lock=np.zeros(n); phi=np.zeros(n); sd=np.zeros(n)
    for i in range(n):
        A=rng.random(L)
        if kind=='static':
            X=rng.random((T,L)); a=A.copy()
        else: # dynamic frozen X
            X0=rng.random(L); X=np.tile(X0,(T,1)); a=A.copy()
        for t in range(T): a=step(a,A,X[t],bv)
        d=np.abs(a-A)
        f_lock[i]=np.mean(d<0.02); phi[i]=d.mean(); sd[i]=a.std()
    return f_lock.mean(), phi.mean(), sd.mean()
b=np.linspace(0,0.45,19)
L=100; T=3000; n=40
Fs=[];Ps=[];Ss=[];Fd=[];Pd=[];Sd=[]
for bv in b:
    fl,ph,sd=measure(L,bv,n,T,'static'); Fs.append(fl);Ps.append(ph);Ss.append(sd)
    fd,phh,sdd=measure(L,bv,n,T,'dynamic'); Fd.append(fd);Pd.append(phh);Sd.append(sdd)
Fs=np.array(Fs);Ps=np.array(Ps);Ss=np.array(Ss);Fd=np.array(Fd);Pd=np.array(Pd);Sd=np.array(Sd)
# detect steepest jump in locked fraction
def jumps(y):
    g=np.gradient(y,b)
    return b[np.argmax(np.abs(g))], np.max(np.abs(g))
bj_s,j_s=jumps(Fs); bj_d,j_d=jumps(Fd)
print("STATIC  locked jump b*=",round(bj_s,4),"|grad|=",round(j_s,3)," final lock frac=",round(Fs[-1],3))
print("DYNAMIC locked jump b*=",round(bj_d,4),"|grad|=",round(j_d,3)," final lock frac=",round(Fd[-1],3))
fig,ax=plt.subplots(2,2,figsize=(10,7))
ax[0,0].plot(b,Fs,'-o',label='static'); ax[0,0].plot(b,Fd,'-s',label='dynamic(frozen)'); ax[0,0].set_title('fraction locked |a-A|<0.02'); ax[0,0].legend()
ax[0,1].plot(b,Ps,'-o',label='static'); ax[0,1].plot(b,Pd,'-s',label='dynamic'); ax[0,1].set_title('mean |a-A|'); ax[0,1].legend()
ax[1,0].plot(b,Ss,'-o',label='static'); ax[1,0].plot(b,Sd,'-s',label='dynamic'); ax[1,0].set_title('std(a)'); ax[1,0].legend()
ax[1,1].plot(b,Ps-Pd,'-k'); ax[1,1].set_title('gap phi_static - phi_dynamic'); ax[1,1].axhline(0,color='gray',lw=0.5)
plt.tight_layout(); plt.savefig('redteam_static_vs_dynamic.png',dpi=130)
np.savez('redteam.npz',b=b,Fs=Fs,Ps=Ps,Ss=Ss,Fd=Fd,Pd=Pd,Sd=Sd)
print("saved redteam_static_vs_dynamic.png")
