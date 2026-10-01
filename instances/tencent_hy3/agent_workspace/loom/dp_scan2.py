import numpy as np, time, json
L,T,trials=100,200,300
bs=np.linspace(0.240,0.280,17)
def step(a,b):
    n=np.roll(a,1,0).astype(np.int8)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)
    r=np.random.random(a.shape)
    birth=(a==0)&(n>0)&(r<b)
    surv=(a>0)&(r<b)
    na=np.zeros(a.shape,bool)
    na[birth]=True; na[surv]=True
    return na
def run(b):
    A=np.zeros((L,L),bool); A[50,50]=True
    out=np.zeros(T+1); out[0]=1.0
    for t in range(1,T+1):
        A=step(A,b)
        if A.sum()==0: break
        out[t]=1.0
    return out
t0=time.time(); data={'bs':list(bs),'ps':[],'curves':[]}
for i,b in enumerate(bs):
    acc=np.zeros(T+1)
    for _ in range(trials):
        acc+=run(b)
    acc/=trials
    data['ps'].append(float(acc[-1])); data['curves'].append([float(x) for x in acc])
    print('b=%.4f Ps=%.4f dt=%.1f'%(b,acc[-1],time.time()-t0),flush=True)
with open('dp_scan2.json','w') as f: json.dump(data,f)
