import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
def step(a,A,X,b): return np.clip(X*a*a+(1-X)*(a+b*np.sin(2*np.pi*(a-A))),0,1)
def curve(L,bgrid,n,T,kind):
    out=np.zeros(len(bgrid))
    for j,bv in enumerate(bgrid):
        acc=0.0
        for _ in range(n):
            A=rng.random(L)
            a = A.copy() if kind=='soup' else rng.random(L)
            X=rng.random((T,L))
            for t in range(T): a=step(a,A,X[t],bv)
            acc+=np.mean(np.abs(a-A))
        out[j]=acc/n
    return out
b=np.linspace(0,0.45,23)
for L in [60,120]:
    T=20*L
    sf=curve(L,b,12,T,'soup')
    ss=curve(L,b,12,T,'seed')
    print(f"L={L} T={T}")
    print(" soup:", np.round(sf,3))
    print(" seed:", np.round(ss,3))
    plt.figure(figsize=(6,4))
    plt.plot(b,sf,'-o',label='soup (coherent start)',color='tab:blue')
    plt.plot(b,ss,'-s',label='seed (fractured start)',color='tab:orange')
    plt.xlabel(r'b'); plt.ylabel(r'$\Phi$'); plt.title(f'L={L}'); plt.legend(); plt.tight_layout()
    plt.savefig(f'diag_L{L}.png'); plt.close()
