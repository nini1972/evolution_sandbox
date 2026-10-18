"""
EXP: Does c_LZ(periodic string) ~ log2(N) + O(1) INDEPENDENT of period n?

Rationale (from codex #006): my R(n) sweep found flatness empirically. If the
LZ production count of a purely periodic string is asymptotically log2(N) + O(1)
with a remainder that does NOT depend on the period n, then flatness is a
theorem, and any claim of an n=4 collapse must be an estimator artifact.

Test:
  For each period n in {2,4,8,16,32}, and each length N (a multiple of n),
  compute c_LZ(primitive period-n word repeated to length N) using phrasal LZ76.
  Fit c_LZ = a + b*log2(N) per n.
  Hypothesis H: b ~ 1 (universal slope), and the intercept a varies O(1) with n
  (specifically a(n) ~ log2(n) + const, since building the primitive word itself
  costs ~log2(n)).
  Then c_LZ differences across n at FIXED N are O(log n) << log N, so
  R(n) = c_LZ(periodic)/c_LZ(random) is asymptotically flat in n.

Also compute the ratio to random to confirm flatness widens as N grows.
"""
import numpy as np, json, os, sys

def c_lz76_phrasal(s):
    """Phrasal LZ76: number of phrases in the Lempel-Ziv factorization."""
    n = len(s)
    dict_phrases = {s[0]} if n else set()
    i = 0; phrases = 0; w = ""
    while i < n:
        w += s[i]
        i += 1
        if w not in dict_phrases:
            dict_phrases.add(w)
            phrases += 1
            w = ""
    return phrases

def c_lz76_random(N, rng):
    s = ''.join(rng.choice(list('01'), size=N))
    return c_lz76_phrasal(s)

def period_n_string(n, N, rng=None):
    """Primitive random word of period n repeated to length N."""
    rng = rng or np.random.default_rng(0)
    word = ''.join(rng.choice(list('01'), size=n))
    reps = (N // n) + 1
    return (word * reps)[:N]

results = {"per_n": {}, "fits": {}}
N_list = [128, 256, 512, 1024, 2048, 4096]
periods = [2, 4, 8, 16, 32]

for n in periods:
    cs = []
    for N in N_list:
        # average over 20 random primitive words to kill word-specific noise
        vals = []
        for seed in range(20):
            rng = np.random.default_rng(1000 + seed)
            s = period_n_string(n, N, rng)
            vals.append(c_lz76_phrasal(s))
        cs.append(np.mean(vals))
    results["per_n"][n] = {"N": N_list, "c": cs}
    # fit c = a + b*log2(N)
    x = np.log2(np.array(N_list, dtype=float))
    y = np.array(cs, dtype=float)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    results["fits"][n] = {"slope_b": float(b), "intercept_a": float(a),
                          "rmse": float(np.sqrt(np.mean(resid**2)))}
    print(f"n={n:2d}: slope b={b:.4f} (want ~1), intercept a={a:.3f} (want ~log2(n)+c), rmse={np.sqrt(np.mean(resid**2)):.4f}")

# Cross-n comparison at largest N
big = N_list[-1]
print(f"\nAt N={big}:")
for n in periods:
    c = results["per_n"][n]["c"][-1]
    print(f"  n={n:2d}: c_LZ={c:.3f}  log2(N)={np.log2(big):.3f}  c-log2N={c-np.log2(big):.3f}")

# Ratio to random (R) at each N, averaged over n -> flatness check
print("\nR(n) = c_periodic / c_random  (flatness across n):")
R_table = {}
for i, N in enumerate(N_list):
    rng = np.random.default_rng(42)
    c_rand = np.mean([c_lz76_random(N, np.random.default_rng(100+s)) for s in range(20)])
    Rs = {}
    for n in periods:
        Rs[n] = results["per_n"][n]["c"][i] / c_rand
    R_table[N] = Rs
    spread = max(Rs.values()) / min(Rs.values())
    print(f"  N={N:4d}: " + "  ".join(f"n{n}:{Rs[n]:.3f}" for n in periods) +
          f"   spread(max/min)={spread:.3f}  (1.0=perfectly flat)")
results["R_table"] = {str(k): {str(kk): float(vv) for kk, vv in v.items()} for k, v in R_table.items()}

# Hypothesis verdict
slopes = [results["fits"][n]["slope_b"] for n in periods]
intercepts = [results["fits"][n]["intercept_a"] for n in periods]
spread_final = max(R_table[big].values()) / min(R_table[big].values())
verdict = {
    "slopes_all_near_1": bool(all(0.9 < s < 1.3 for s in slopes)),
    "slope_mean": float(np.mean(slopes)),
    "intercepts_range": [float(min(intercepts)), float(max(intercepts))],
    "R_spread_at_N4096": float(spread_final),
    "flat_asymptotic": bool(spread_final < 1.5),
}
results["verdict"] = verdict
print("\nVERDICT:", json.dumps(verdict, indent=2))

os.makedirs("exp_periodic_lz_theorem", exist_ok=True)
with open("exp_periodic_lz_theorem/results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved exp_periodic_lz_theorem/results.json")