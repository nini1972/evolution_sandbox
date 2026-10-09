import numpy as np, json
# Verify peak law |psi|^2_max = (1 + 2 sqrt(1 - K^2/4))^2 exactly, and its Peregrine limit.
results = []
for K in [1.0, 0.8, 0.5, 0.3, 0.2, 0.1, 0.05]:
    b = np.sqrt(1 - K**2/4)
    law_intensity = (1 + 2*b)**2
    # direct evaluation on fine x grid at t=0
    x = np.linspace(0, 2*np.pi/K, 20001, endpoint=False)
    den = 1.0 - b*np.cos(K*x)          # cosh(0)=1
    psi = 1.0 + (-0.5*K**2)/den        # sinh(0)=0
    num_intensity = np.max(np.abs(psi)**2)
    results.append((K, law_intensity, num_intensity, abs(law_intensity-num_intensity)))
    print(f"K={K:5.2f}: law={law_intensity:.10f}  numeric={num_intensity:.10f}  diff={abs(law_intensity-num_intensity):.2e}")
# Peregrine limit of the law: K->0 gives (1+2)^2 = 9
print("Peregrine limit intensity:", (1+2*1.0)**2, "(the famous 9x rogue wave)")
json.dump({"peak_law": [(k, l, n, d) for k, l, n, d in results]}, open("ab_peaklaw_exact.json", "w"), indent=1)
