import os, re, json, difflib
import numpy as np
np.random.seed(0)

ROOT = "/home/runner/work/evolution_sandbox/evolution_sandbox/instances"
CORES = {
    "claude_haiku":"claude_haiku/agent_workspace/existential_core.md",
    "claude_sonnet_4_5":"claude_sonnet_4_5/agent_workspace/existential_core.md",
    "deepseek_v4_flash":"deepseek_v4_flash/agent_workspace/existential_core.md",
    "gemini_3_1_flash_lite":"gemini_3_1_flash_lite/agent_workspace/existential_core.md",
    "gemini_flash":"gemini_flash/agent_workspace/existential_core.md",
    "gemini_pro":"gemini_pro/agent_workspace/existential_core.md",
    "glm_4_7_flash":"glm_4_7_flash/agent_workspace/existential_core.md",
    "glm_5_2":"glm_5_2/agent_workspace/existential_core.md",
    "kimi_code":"kimi_code/agent_workspace/existential_core.md",
    "llama_3_3":"llama_3_3/agent_workspace/synthesis.md",
    "llama_4_scout":"llama_4_scout/agent_workspace/existential_core.md",
    "minimax_m3":"minimax_m3/agent_workspace/existential_core.md",
    "nex_n2_pro":"nex_n2_pro/agent_workspace/existential_core.md",
    "poolside_laguna":"poolside_laguna/agent_workspace/existential_core.md",
    "tencent_hy3":"tencent_hy3/agent_workspace/existential_core.md",
    "xiaomi_mimo":"xiaomi_mimo/agent_workspace/existential_core.md",
}
def load(n):
    p=os.path.join(ROOT,CORES[n])
    return open(p,encoding="utf-8",errors="ignore").read() if os.path.exists(p) else ""
names=list(CORES.keys()); N=len(names)
texts={n:re.sub(r"\s+"," ",load(n)).strip() for n in names}
def norm_lev(a,b): return 1.0-difflib.SequenceMatcher(None,a,b).ratio()
D=np.zeros((N,N))
for i in range(N):
    for j in range(N): D[i,j]=norm_lev(texts[names[i]],texts[names[j]])
S=1.0-D; np.fill_diagonal(S,0.0)
W=S/(S.sum(axis=1,keepdims=True)+1e-12); np.fill_diagonal(W,0.0)
omega=D.mean(axis=1)
omega=(omega-omega.mean())/omega.std()
print("omega std",omega.std())

def order(th): return np.abs(np.mean(np.exp(1j*th)))
def run(K,sigma=0.0,dt=0.005,T=40000,seed=0):
    rng=np.random.default_rng(seed)
    theta=rng.uniform(-np.pi,np.pi,N)
    Rs=[]
    for t in range(T):
        dtheta=omega+K*(W*np.sin(theta[None,:]-theta[:,None])).sum(axis=1)
        theta=theta+dt*dtheta+sigma*np.sqrt(dt)*rng.standard_normal(N)
        theta=(theta+np.pi)%(2*np.pi)-np.pi
        if t>T//2: Rs.append(order(theta))
    return np.mean(Rs)

for K in [0.0,0.5,1.0,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0]:
    r=run(K,dt=0.002,T=30000)
    print(f"K={K:.1f} R={r:.3f}")
