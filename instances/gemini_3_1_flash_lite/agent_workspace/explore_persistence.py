from colony_lib.dynamics import GrayScott2D
import numpy as np
from colony_lib.persistence import StageTracker

def analyze_bifurcation_persistence():
    # Tracker for multi-stage exploration
    tracker = StageTracker('gs_bifurcation_scan')
    
    # Range of feed and kill rates
    F_range = np.linspace(0.01, 0.05, 5)
    k_range = np.linspace(0.04, 0.08, 5)
    
    for f in F_range:
        for k in k_range:
            params = (f, k)
            if tracker.is_done(params):
                continue
                
            gs = GrayScott2D()
            gs.F = f
            gs.k = k
            
            # Seed and evolve
            gs.u[60:68, 60:68] = 0.5
            gs.v[60:68, 60:68] = 0.5
            
            for _ in range(3000):
                gs.step()
                
            # Log metric (persistence of variance)
            data = {'variance': float(np.var(gs.u)), 'mean': float(np.mean(gs.u))}
            tracker.save_stage(params, data)
            print(f"Computed F={f:.3f}, k={k:.3f}: {data}")

if __name__ == '__main__':
    analyze_bifurcation_persistence()
