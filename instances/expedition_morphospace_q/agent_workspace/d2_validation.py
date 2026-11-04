#!/usr/bin/env python3
"""D2 estimator validation: plateau method vs main/suite estimators. Systems turn."""
import numpy as np, json, warnings, time
from scipy.integrate import odeint
from scipy.spatial.distance import pdist
warnings.filterwarnings('ignore')
import morphospace_q_conservation as M
t0=time.time()
OUT={}

# ---------------- data ----------------
def lorenz(rho=28.0, T=6000, dt=0.01, ds=4):
    f=lambda x,t:[10*(x[1]-x[0]), x[0]*(rho-x[2])-x[1], x[0]*x[1]-8/3*x[2]]
    ts=np.arange(0,T,dt)
    X=odeint(f,[1.,1.,11.5],ts,rtol=1e-8,atol=1e-8,mxstep=100000)
    return X[::ds]                       # dt_sample=0.04, Nx150000x3

def henon(a=1.4,b=0.3,n=200000):
    x=np.empty(n); xx,yy=0.1,0.1
    for i in range(n):
        xx,yy = 1-a*xx*xx+yy, b*xx
        x[i]=xx
    return x[5000:]

X=lorenz(); Lx=X[:,0]; Hx=henon()
print(f"data: Lorenz {X.shape}, Henon {len(Hx)}")

def embed(x,m,tau):
    N=len(x)-(m-1)*tau
    return np.column_stack([x[i*tau:i*tau+N] for i in range(m)])

def dists(x,m,tau,maxp=4000,seed=0):
    E=embed(np.asarray(x,float),m,tau); r=np.random.default_rng(seed)
    if len(E)>maxp: E=E[r.choice(len(E),maxp,False)]
    d=pdist(E); return d[d>0]

def acf_tau(x,maxlag=120):
    x=np.asarray(x,float); x=x[:min(len(x),40000)]
    x=x-x.mean(); n=len(x)
    ac=np.array([np.dot(x[:n-k],x[k:])