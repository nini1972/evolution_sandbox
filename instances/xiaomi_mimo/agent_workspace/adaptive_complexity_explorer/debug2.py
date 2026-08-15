"""Debug execution flow"""
import random
import numpy as np
random.seed(42)

def new_forager():
    return [60.0, 0, random.uniform(0.5, 0.9), random.uniform(0.2, 0.6), 
            random.uniform(0.3, 0.8), random.uniform(0.08, 0.2)]

def new_hunter():
    return [70.0, 0, random.uniform(0.3, 0.7), random.uniform(0.3, 0.7),
            random.uniform(0.3, 0.7), random.uniform(0.03, 0.1)]

foragers = [new_forager() for _ in range(20)]
hunters = [new_hunter() for _ in range(4)]
resources = 200.0

print(f"Start: {len(foragers)} foragers, {len(hunters)} hunters")
print(f"Forager 0: {foragers[0]}")

# Simulate 3 steps
for step in range(3):
    # Growth
    K = 300.0
    r = 0.25
    growth = r * resources * (1.0 - resources/K)
    resources += max(growth, 1.0)
    resources = min(K, max(1.0, resources))
    
    nf, nh = len(foragers), len(hunters)
    
    new_f = []
    for f in foragers:
        f[1] += 1
        f[0] -= 0.3 + f[3] * 0.1
        
        if f[0] <= 0:
            continue
        
        per_capita = resources / max(1.0, nf + nh)
        gain = f[2] * per_capita * 0.2
        gain = min(gain, 10)
        f[0] += gain
        resources -= gain * 0.8
        resources = max(0.1, resources)
        
        new_f.append(f)
    
    foragers = new_f
    
    new_h = []
    for h in hunters:
        h[1] += 1
        h[0] -= 0.5 + h[3] * 0.12
        
        if h[0] <= 0:
            continue
        
        if foragers:
            density = min(1.0, len(foragers) / 15.0)
            avg_def = np.mean([f[4] for f in foragers])
            prob = h[2] * 0.15 * density * (1.0 - avg_def * 0.3)
            if random.random() < prob:
                prey_idx = random.randint(0, len(foragers)-1)
                h[0] += 15 + h[4] * 8
                foragers.pop(prey_idx)
        
        new_h.append(h)
    
    hunters = new_h
    
    print(f"\nStep {step+1}: F={len(foragers)} H={len(hunters)} Res={resources:.1f}")
    if foragers:
        print(f"  F energies: {[round(f[0],1) for f in foragers[:5]]}")
    if hunters:
        print(f"  H energies: {[round(h[0],1) for h in hunters[:3]]}")
