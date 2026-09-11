import numpy as np
np.random.seed(0)

N=16
rng=np.random.default_rng(1)
omega=rng.standard_normal(N)

def order(theta): return np.abs(np.mean(np.exp(1j*theta)))

def run(omega, W, K, sigma=0.0, dt=0.01, T=20000, seed=0):
    rng=np.random.default_rng(seed)
    theta=rng.uniform(-np.pi,np.pi,N)
    Rs=[]
    for t in range(T):
        dtheta = omega + K*(W*np.sin(theta[:,None]-theta[None,:])).sum(axis=1)
        theta = theta + dt*dtheta + sigma*np.sqrt(dt)*rng.standard_normal(N)
        theta=(theta+np.pi)%(2*np.pi)-np.pi
        if t> T//2:
            Rs.append(order(theta))
    return np.mean(Rs)

# all-to-all symmetric, rows sum to N-1, coupling K
Wall=np.ones((N,N))-np.eye(N)
for K in [0.5,1.0,1.5,2.0,3.0,4.0,6.0]:
    print(f"all-to-all K={K}: R={run(omega,Wall,K):.3f}")

print("omega std:",omega.std(),"minmax:",omega.min(),omega.max())
