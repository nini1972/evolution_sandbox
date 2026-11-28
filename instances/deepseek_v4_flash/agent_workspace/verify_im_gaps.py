import numpy as np, json
N=np.array([10,20,40,80,160,320],float)
gap=np.array([0.19098300562505244,0.0489434837048458,0.01231165940486223,
              0.003082666266871592,0.0007709637592772101,0.00019275951793518153])
print("="*90)
print("STEP 1: identify the exact closed form of invariant_mind's 'spectral_gaps'")
print("="*90)
cands={
 "2 sin^2(pi/N)  [norm.Lap gap of CYCLE C_N]": 2*np.sin(np.pi/N)**2,
 "1-cos(2pi/N)   [same, trig identity]":      1-np.cos(2*np.pi/N),
 "2(1-cos(pi/N)) [PATH graph Laplacian gap]": 2*(1-np.cos(np.pi/N)),
 "1-cos(pi/N)    [PATH norm.Lap gap]":        1-np.cos(np.pi/N),
}
print(f"{'N':>5} {'reported':>14} " + " ".join(f"{k.split()[0][:12]:>14}" for k in cands))
for i in range(len(N)):
    print(f"{N[i]:>5.0f} {gap[i]:>14.9f} " + " ".join(f"{v[i]:>14.9f}" for v in cands.values()))
print()
for k,v in cands.items():
    rel=np.max(np.abs(v-gap)/gap)
    print(f"  {k:45s} max rel.err = {rel:.3e}  {'<== EXACT MATCH' if rel<1e-12 else ''}")

print("\n"+"="*90)
print("STEP 2: is the reported fit (slope -1.9921, intercept 2.9436) self-consistent?")
print("="*90)
s,i=-1.9921381913131377,2.9435526022718466
for base,lab in [(10,'log10'),(np.e,'ln')]:
    pred=base**(i)*N**s
    print(f"  assume {lab}: gap_pred(N=10) = {pred[0]:.6f}   actual = {gap[0]:.6f}")
s2,i2=np.polyfit(np.log10(N),np.log10(gap),1)
print(f"\n  REFIT by me on log10: slope={s2:+.6f} intercept={i2:+.6f}")
print(f"  invariant_mind reported: slope={s:+.6f} intercept={i:+.6f}")
print(f"  -> slope agrees to {abs(s2-s):.2e}, intercept DISAGREES by {abs(i2-i):.4f}")
print(f"  -> their intercept {i:.4f} implies prefactor 10^{i:.4f}={10**i:.2f};")
print(f"     correct log10 intercept for this data is {i2:.4f} (prefactor {10**i2:.4f})")
print(f"     analytic 2*pi^2 = {2*np.pi**2:.4f}, log10 = {np.log10(2*np.pi**2):.4f}")

print("\n"+"="*90)
print("STEP 3: does the exponent depend on the DYNAMICS (r=3.5, K=0.1)?")
print("="*90)
print("  The exact form 2sin^2(pi/N) contains NO r, NO K, NO T, NO M.")
print("  The 'resonance gap' is the normalized-Laplacian spectral gap of a cycle graph.")
print("  It is a pure GRAPH INVARIANT. The coupled-logistic dynamics contributed nothing.")
print("  Any N^-2 'scaling law' here is lambda_1(C_N) ~ 2pi^2/N^2, textbook.")
print("\n  FALSIFICATION TEST for invariant_mind: change K from 0.1 to 0.01 or 1.0.")
print("  If Delta(N) is unchanged, the 'law' is topological, not dynamical.")
print("  If it changes, then the exponent is NOT -2 and their fit is window-limited.")
out=dict(closed_form="2*sin^2(pi/N) = 1-cos(2pi/N) = normalized Laplacian gap of cycle C_N",
         max_rel_err=float(min(np.max(np.abs(v-gap)/gap) for v in cands.values())),
         reported_slope=s, reported_intercept=i, refit_slope=float(s2), refit_intercept=float(i2),
         analytic_prefactor=float(2*np.pi**2), analytic_log10_intercept=float(np.log10(2*np.pi**2)))
json.dump(out,open('verify_im_gaps.json','w'),indent=2)
print("\nSaved verify_im_gaps.json")
