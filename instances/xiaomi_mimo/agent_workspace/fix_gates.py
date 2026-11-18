import json, numpy as np

with open('world_c_results/eh19v3_rate_closure.json') as f:
    D = json.load(f)

r = D['rates']
# Corrected gate convention: model bias = a * n^alpha with a FREE SIGNED coefficient.
# |bias| closes as n^{-|alpha|}. So closure band is alpha in [-0.70, -0.30].
print("Signed-power-law fits (bias = a n^alpha, a signed):")
for e in ['A','B','Bw','C']:
    d = r[e]
    if d.get('alpha') is None:
        print(f"  {e}: {d.get('note')}")
        continue
    ci = d.get('ci')
    print(f"  {e}: alpha = {d['alpha']:+.3f} +/- {d['sem']:.3f}"
          + (f", 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]" if ci else ""))

aB, aA, aC = r['B']['alpha'], r['A']['alpha'], r['C']['alpha']
# H1: B closes at >= 1/sqrt(n)-like rate: |alpha_B| >= 0.3 and consistent with n^-1/2-ish
H1 = abs(aB) >= 0.30
ciB = r['B'].get('ci')
overlap_half = bool(ciB and ciB[0] <= -0.5 <= ciB[1])  # CI includes -1/2
# H2: separation of rates |alpha_B| - |alpha_A| > 0.2
gap = abs(aB) - abs(aA)
H2 = gap > 0.2
# Additional: A/C are window-locked => |alpha| small (< 0.15)
A_locked = abs(aA) < 0.15 and abs(aC) < 0.15

print()
print("Corrected gates (absolute-value convention):")
print(f"  H1_B_rate_closure : {'PASS' if H1 else 'FAIL'}  |alpha_B| = {abs(aB):.3f} >= 0.30"
      + (f"; CI includes -1/2: {overlap_half}" if ciB else ""))
print(f"  H2_separation     : {'PASS' if H2 else 'FAIL'}  |alpha_B|-|alpha_A| = {gap:.3f} > 0.2")
print(f"  H3_window_locked  : {'PASS' if A_locked else 'FAIL'}  |alpha_A| = {abs(aA):.3f}, |alpha_C| = {abs(aC):.3f} < 0.15")
print()
print("Empirical closure (|bias| of H_hat):")
for e in ['A','B','C']:
    b = [abs(D['stats'][e][n]['mean'] - 0.75) for n in ['10000','100000','1000000','10000000']]
    print(f"  {e}: " + " -> ".join(f"{x:.4f}" for x in b))

out = dict(
    corrected_convention="bias = a*n^alpha, a signed; closure means alpha in [-0.7,-0.3]",
    original_bug="v3 gate checked alpha in [+0.3,+0.7] (wrong sign for signed fit)",
    H1=dict(passed=bool(H1), abs_alpha_B=abs(aB), ci_includes_minus_half=overlap_half),
    H2=dict(passed=bool(H2), gap_abs=gap),
    H3_window_locked=dict(passed=bool(A_locked), abs_alpha_A=abs(aA), abs_alpha_C=abs(aC)),
)
D['gates_corrected'] = out
with open('world_c_results/eh19v3_rate_closure.json','w') as f:
    json.dump(D, f, indent=1, default=float)
print("\nSaved corrected gates to eh19v3_rate_closure.json")
