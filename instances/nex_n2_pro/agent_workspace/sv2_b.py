
N, seed = 100, 42
np.random.seed(seed)
x0 = np.random.rand(N)

# --- coarse regime scan ---
rs = np.round(np.arange(3.84, 3.901, 0.02), 3)
es = np.round(np.arange(0.10, 0.181, 0.02), 3)
print('--- coarse: r, eps -> symP A B A/B f1 f2 f4')
for r in rs:
    line = []
    for eps in es:
        sp, f1, f2, f4, A, B = stats(x0, float(r), float(eps))
        ratio = (A / B) if B > 1e-12 else 99.0
        line.append(f"{sp}:{A:5.3f}/{B:5.3f}")
    print(f"r={r:5.3f} | " + " ".join(line))

# --- fine scan for P4 birth at eps = 0.10, 0.12 ---
print('--- fine: P4 birth, eps=0.10, r in [3.86, 3.90] step 0.002')
for eps in (0.10, 0.12):
    r = 3.86
    while r <= 3.9001:
        sp, f1, f2, f4, A, B = stats(x0, r, eps, T=300, transient=1200)
        if sp == 4:
            print(f"eps={eps} r={r:5.3f} P4 born: A={A:8.4f} B={B:8.4f} A/B={A/B:7.3f}")
        r = round(r + 0.002, 3)

# --- breathing fine scan across P4 tongue ---
print('--- breathing A across P4 tongue (eps, r -> A)')
es2 = [0.10, 0.12, 0.14, 0.16]
rs2 = [3.88, 3.90, 3.92, 3.94, 3.96]
out = []
for eps in es2:
    for r in rs2:
        sp, f1, f2, f4, A, B = stats(x0, r, eps)
        out.append((eps, r, sp, A))
        print(f"eps={eps:.2f} r={r:5.2f} symP={sp} A={A:8.4f}")
np.save('shadow_v2.npy', np.array(out, dtype=float))
