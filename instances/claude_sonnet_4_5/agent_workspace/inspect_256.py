import json, numpy as np
d = json.load(open("ca_256_results.json"))
rows = {r["rule"]: r for r in d["rows"]}

for r in [0,1,30,54,60,90,102,110,126,150,158,182,204,232,240]:
    rr = rows[r]
    print(f"rule {r:3d}  sym={rr['reflection_sym']}  xor={rr['xor_balanced']}  "
          f"lambda={rr['growth_rate']:.3f}  H={rr['entropy_rate']:.3f}")

sym = [r for r in d["rows"] if r["reflection_sym"]]
asym = [r for r in d["rows"] if not r["reflection_sym"]]

# separate chaotic rules only (H > 0.5) - does symmetry matter within chaos?
sc = [r["growth_rate"] for r in sym if r["entropy_rate"] > 0.5]
ac = [r["growth_rate"] for r in asym if r["entropy_rate"] > 0.5]
print(f"\nChaotic subset (H>0.5): sym n={len(sc)} mean lam={np.mean(sc):.3f} | "
      f"asym n={len(ac)} mean lam={np.mean(ac):.3f} ratio={np.mean(sc)/np.mean(ac):.3f}")

sh = [r["entropy_rate"] for r in sym if r["entropy_rate"] > 0.5]
ah = [r["entropy_rate"] for r in asym if r["entropy_rate"] > 0.5]
print(f"Chaotic subset entropy: sym={np.mean(sh):.3f} asym={np.mean(ah):.3f}")

# xor-balanced subset
xb = [r for r in d["rows"] if r["xor_balanced"]]
print(f"\nXOR-balanced rules n={len(xb)}: mean lam={np.mean([r['growth_rate'] for r in xb]):.3f} "
      f"H={np.mean([r['entropy_rate'] for r in xb]):.3f}")
nb = [r for r in d["rows"] if not r["xor_balanced"]]
print(f"non-XOR n={len(nb)}: mean lam={np.mean([r['growth_rate'] for r in nb]):.3f} "
      f"H={np.mean([r['entropy_rate'] for r in nb]):.3f}")

# joint symmetry classes
ss = [r for r in d["rows"] if r["reflection_sym"] and r["xor_balanced"]]
sna = [r for r in d["rows"] if r["reflection_sym"] and not r["xor_balanced"]]
ans = [r for r in d["rows"] if not r["reflection_sym"] and r["xor_balanced"]]
print(f"\nrefl+XOR: n={len(ss)} lam={np.mean([r['growth_rate'] for r in ss]):.3f} H={np.mean([r['entropy_rate'] for r in ss]):.3f}")
print(f"refl only: n={len(sna)} lam={np.mean([r['growth_rate'] for r in sna]):.3f} H={np.mean([r['entropy_rate'] for r in sna]):.3f}")
print(f"XOR only: n={len(ans)} lam={np.mean([r['growth_rate'] for r in ans]):.3f} H={np.mean([r['entropy_rate'] for r in ans]):.3f}")

# distribution of entropy classes
import collections
cls = collections.Counter()
for r in d["rows"]:
    if r["entropy_rate"] < 0.05: c = "frozen"
    elif r["entropy_rate"] < 0.35: c = "periodic"
    elif r["entropy_rate"] < 0.6: c = "edge"
    else: c = "chaotic"
    cls[(c, r["reflection_sym"])] += 1
print("\nphase class x symmetry:")
for c in ["frozen","periodic","edge","chaotic"]:
    print(f"  {c:9s} sym={cls[(c,True)]:3d}  asym={cls[(c,False)]:3d}")
