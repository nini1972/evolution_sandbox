"""R19Z Phase 4: Anti-Resonance Phase Diagram — Full (A, N) sweep"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

class GrayScott:
    def __init__(self, size=12, Du=0.16, Dv=0.08, feed=0.035, kill=0.065):
        self.size = size; self.Du=Du; self.Dv=Dv; self.feed=feed; self.kill=kill
        self.u = np.ones((size,size)); self.v = np.zeros((size,size))
        r=max(2,size//8); cx,cy=size//2,size//2
        self.u[cx-r:cx+r,cy-r:cy+r]=0.50; self.v[cx-r:cx+r,cy-r:cy+r]=0.25
        self.u+=np.random.randn(size,size)*0.01; self.v+=np.random.randn(size,size)*0.01
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def laplacian(self,f):
        lap=np.zeros_like(f)
        lap[1:-1,1:-1]=f[2:,1:-1]+f[:-2,1:-1]+f[1:-1,2:]+f[1:-1,:-2]-4*f[1:-1,1:-1]
        lap[0,:]=lap[1,:]; lap[-1,:]=lap[-2,:]; lap[:,0]=lap[:,1]; lap[:,-1]=lap[:,-2]
        return lap
    def step(self,dt=1.0,pert=None):
        du=self.Du*self.laplacian(self.u)-self.u*self.v**2+self.feed*(1-self.u)
        dv=self.Dv*self.laplacian(self.v)+self.u*self.v**2-(self.feed+self.kill)*self.v
        if pert is not None: du+=pert
        self.u+=du*dt; self.v+=dv*dt
        self.u=np.clip(self.u,0,1); self.v=np.clip(self.v,0,1)
    def mean_v(self): return float(np.mean(self.v))
    def complexity(self): return float(np.var(self.v))

class BTW:
    def __init__(self, size=6, tm=4.0, ts=0.5):
        self.size=size
        self.thr=np.maximum(np.random.normal(tm,ts,(size,size)),2.0)
        self.h=np.random.uniform(0,1,(size,size))
        self.av_log=[]
    def add_grain(self):
        x,y=np.random.randint(0,self.size,2); self.h[x,y]+=1
    def relax(self):
        total=0
        for _ in range(30):
            mask=self.h>=self.thr
            if not np.any(mask): break
            total+=int(np.sum(mask))
            toppled=self.thr*mask; self.h-=toppled
            padded=np.zeros((self.size+2,self.size+2)); padded[1:-1,1:-1]=toppled
            self.h+=padded[:-2,1:-1]+padded[2:,1:-1]+padded[1:-1,:-2]+padded[1:-1,2:]
        return total
    def step(self,n=1):
        for _ in range(n): self.add_grain()
        av=self.relax(); self.av_log.append(av); return av
    def mean_h(self): return float(np.mean(self.h))

def xcorr(x,y,ml=30):
    x=(x-np.mean(x))/(np.std(x)+1e-10); y=(y-np.mean(y))/(np.std(y)+1e-10)
    n=len(x); lags=np.arange(-ml,ml+1); c=np.zeros(len(lags))
    for i,lag in enumerate(lags):
        if lag<0: c[i]=np.mean(x[-lag:]*y[:n+lag]) if n+lag>0 else 0
        elif lag>0: c[i]=np.mean(x[:n-lag]*y[lag:]) if n-lag>0 else 0
        else: c[i]=np.mean(x*y)
    return lags,c

def run_coupled(N_gap=1,coupling=0.5,n_steps=100,fa=0.0,ff=0.1,gs_size=12,sp_size=6):
    gs=GrayScott(size=gs_size); sp=BTW(size=sp_size)
    gv,sh,av,f=[],[],[],[]
    for t in range(n_steps):
        forcing=fa*np.sin(2*np.pi*ff*t); f.append(forcing)
        for _ in range(N_gap):
            cx=gs.complexity(); sp.thr*=0.99; sp.thr+=0.01*(1+coupling*cx*0.5)
            sp.step(1)
            if abs(forcing*0.5)>0.01:
                ne=int(abs(forcing*0.5)*3)
                for _ in range(ne): sp.add_grain()
                sp.relax()
        av_last=sp.av_log[-1] if sp.av_log else 0
        an=av_last/(sp.size*sp.size+1)
        gp=coupling*an*np.random.randn(gs.size,gs.size)*0.01+forcing*0.01*np.ones((gs.size,gs.size))
        gs.step(pert=gp)
        gv.append(gs.mean_v()); sh.append(sp.mean_h()); av.append(av_last)
    return {'gs_v':np.array(gv),'sp_h':np.array(sh),'av':np.array(av),'f':np.array(f)}

# Sweep (A, N) space — reduced grid for speed
As = [0.0, 1.0, 2.0, 3.0, 4.0]
Ns = [1, 10, 20, 50]
results = np.zeros((len(As), len(Ns), 3))  # [|C|, C+, C-]

print("Running anti-resonance phase diagram sweep...")
for i, A in enumerate(As):
    for j, N in enumerate(Ns):
        np.random.seed(42)
        r = run_coupled(N_gap=N, coupling=0.5, n_steps=60, fa=A)
        l, c = xcorr(r['gs_v'][20:], r['sp_h'][20:], ml=30)
        cmax = float(np.max(c))
        cmin = float(np.min(c))
        results[i,j,0] = max(abs(cmax), abs(cmin))
        results[i,j,1] = cmax
        results[i,j,2] = cmin
        sign = "+" if abs(cmax) > abs(cmin) else "-"
        print(f"  A={A:.1f}, N={N:2d}: |C|={results[i,j,0]:.3f}, C+={cmax:.3f}, C-={cmin:.3f} [{sign}]")

# Create phase diagram figure
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: |C| heatmap
im1 = axes[0].imshow(results[:,:,0], aspect='auto', cmap='viridis', origin='lower',
                     extent=[0.5, 50.5, -0.25, 5.25])
axes[0].set_xlabel('Timescale Gap N', fontsize=13)
axes[0].set_ylabel('Forcing Amplitude A', fontsize=13)
axes[0].set_title('|C| — Resonance Strength', fontsize=14)
plt.colorbar(im1, ax=axes[0], label='|C|')
# Add N values as xticks
axes[0].set_xticks(Ns)
axes[0].set_xticklabels(Ns)
axes[0].set_yticks(As)
axes[0].set_yticklabels([f'{a:.1f}' for a in As])

# Plot 2: C+ heatmap (positive correlation)
im2 = axes[1].imshow(results[:,:,1], aspect='auto', cmap='RdYlGn', origin='lower',
                     extent=[0.5, 50.5, -0.25, 5.25], vmin=-1, vmax=1)
axes[1].set_xlabel('Timescale Gap N', fontsize=13)
axes[1].set_ylabel('Forcing Amplitude A', fontsize=13)
axes[1].set_title('C+ — Positive Correlation', fontsize=14)
plt.colorbar(im2, ax=axes[1], label='C+')
axes[1].set_xticks(Ns)
axes[1].set_xticklabels(Ns)
axes[1].set_yticks(As)
axes[1].set_yticklabels([f'{a:.1f}' for a in As])

# Plot 3: C- heatmap (negative correlation)
im3 = axes[2].imshow(results[:,:,2], aspect='auto', cmap='RdYlGn_r', origin='lower',
                     extent=[0.5, 50.5, -0.25, 5.25], vmin=-1, vmax=0)
axes[2].set_xlabel('Timescale Gap N', fontsize=13)
axes[2].set_ylabel('Forcing Amplitude A', fontsize=13)
axes[2].set_title('C- — Negative Correlation (Anti-Resonance)', fontsize=14)
plt.colorbar(im3, ax=axes[2], label='C-')
axes[2].set_xticks(Ns)
axes[2].set_xticklabels(Ns)
axes[2].set_yticks(As)
axes[2].set_yticklabels([f'{a:.1f}' for a in As])

plt.suptitle('R19Z Phase 4: Anti-Resonance Phase Diagram (A × N)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('r19z_antiresonance_phase_diagram.png', dpi=150, bbox_inches='tight')
plt.close()

# Plot the sign map (positive vs negative dominant)
fig2, ax = plt.subplots(figsize=(10, 8))
sign_map = np.where(results[:,:,1] > -results[:,:,2], 1, -1)  # 1=positive dominant, -1=negative dominant
colors = np.where(sign_map > 0, '#4ecdc4', '#ff6b6b')
for i, A in enumerate(As):
    for j, N in enumerate(Ns):
        marker = 'o' if sign_map[i,j] > 0 else 's'
        ax.scatter(N, A, c=colors[i*len(Ns)+j], s=200, marker=marker, edgecolors='white', linewidth=1.5, zorder=3)
        ax.annotate(f'{results[i,j,0]:.2f}', (N, A), fontsize=8, ha='center', va='center', fontweight='bold', color='black')

ax.set_xlabel('Timescale Gap N', fontsize=14)
ax.set_ylabel('Forcing Amplitude A', fontsize=14)
ax.set_title('Anti-Resonance Phase Map\n○ = Positive correlation dominant, □ = Negative (anti-resonance)', fontsize=14)
ax.grid(True, alpha=0.3)
ax.set_xlim(-5, 55)
ax.set_ylim(-0.5, 5.5)

# Add legend
ax.scatter([], [], c='#4ecdc4', s=100, marker='o', label='Positive correlation')
ax.scatter([], [], c='#ff6b6b', s=100, marker='s', label='Anti-resonance (negative)')
ax.legend(fontsize=12, loc='upper left')

plt.tight_layout()
plt.savefig('r19z_antiresonance_phase_map.png', dpi=150, bbox_inches='tight')
plt.close()

# Save data
data = {
    'As': As, 'Ns': Ns,
    'results': results.tolist(),
    'sign_map': sign_map.tolist()
}
with open('r19z_antiresonance_phase.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\nDone. Anti-resonance phase diagram generated.")
print(f"Anti-resonance cells: {int(np.sum(sign_map < 0))}/{len(As)*len(Ns)}")