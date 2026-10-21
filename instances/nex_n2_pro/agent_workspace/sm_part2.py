
rs = np.round(np.arange(3.84, 3.9001, 0.01), 3)
es = np.round(np.arange(0.10, 0.1801, 0.01), 3)
N, seed, transient = 100, 42, 1000

rows = []
for r in rs:
    for eps in es:
        np.random.seed(seed)
        x = np.random.rand(N)
        for _ in range(transient):
            x = step(x, r, eps)
        fp, d = float_period(x, r, eps)
        sp, f1, f2, f4 = symbol_period(x, r, eps)
        br = breathing(x, r, eps)
        rows.append((float(r), float(eps), fp, d, sp, f1, f2, f4, br))

hdr = '{:>6s} {:>5s} {:>7s} {:>7s} {:>5s} {:>6s} {:>6s} {:>6s} {:>7s}'.format(
    'r', 'eps', 'floatP', 'd', 'symP', 'f1', 'f2', 'f4', 'breath')
print(hdr)
for row in rows:
    print('{:6.3f} {:5.3f} {:>7s} {:7.4f} {:5d} {:6.3f} {:6.3f} {:6.3f} {:7.4f}'.format(*row))

f4s2 = [(row[0], row[1]) for row in rows if row[2] == 4 and row[4] == 2]
f4s4 = [(row[0], row[1]) for row in rows if row[2] == 4 and row[4] == 4]
print('')
print('float-P4 & sym-P2 (shadow folding):', len(f4s2), 'pts', f4s2[:10])
print('float-P4 & sym-P4 (true symbolic P4):', len(f4s4), 'pts', f4s4[:10])
np.save('shadow_grid.npy', np.array(rows, dtype=float))
