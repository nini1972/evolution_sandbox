import numpy as np, time, json
L,T,trials=72,110,200
bs=np.linspace(0.25,0.55,13)
def step(a,b):
    ap=np.pad(a.astype(np.int8),1)
    n=ap[0:L,1:L+1]+ap[2:L+2,1:L+1]+ap[1:L+1,0:L]+ap[1:L+1,2:L+2]
    r=np.random.random(a.shape)
    birth=(a==0)&(n>0)&(r<b)
    surv=(a>0)&(r<b)
    na=np.zeros(a.shape,bool)
    na[birth]=True; na[surv]=True
    return na
def run(b,init):
    if init=='seed':
        A=np.zeros((L,L),bool); A[35:37,35:37]=True
    else:
        A=np.random.random((L,L))<0.5
    ext=False; out=np.zeros(T+1)
    for t in range(1,T+1):
        if not ext:
            A=step(A,b)
            if A.sum()==0: ext=True
        out[t]=0 if ext else 1
    return out
t0=time.time(); data={'bs':list(bs),'ps':[],'psd':[]}
for i,b in enumerate(bs):
    ps=0.0; psd=0.0
    for _ in range(trials):
        ps+=run(b,'soup')[-1]; psd+=run(b,'seed')[-1]
    ps/=trials; psd/=trials
    data['ps'].append(ps); data['psd'].append(psd)
    print('b=%.3f soup=%.3f seed=%.3f dt=%.1f'%(b,ps,psd,time.time()-t0),flush=True)
with open('loom/dp_scan.json','w') as f: json.dump(data,f)
