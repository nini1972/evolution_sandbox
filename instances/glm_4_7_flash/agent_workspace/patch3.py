src = open('it_turbulence_worldc.py').read()

old = """    meanI_A = np.sum(kc * pA) * (kc[1] - kc[0])
    ray = np.exp(-kc / meanI_A) / meanI_A"""
new = """    totA = float(A['hist'].sum())
    meanI_A = np.sum(kc * pA) * (kc[1] - kc[0]) if totA > 0 else 1.0
    ray = np.exp(-kc / meanI_A) / meanI_A"""
assert old in src; src = src.replace(old, new)

old = "    pA = A['hist'] / A['hist'].sum() / (kc[1] - kc[0])\n    pB = B['hist'] / B['hist'].sum() / (kc[1] - kc[0])\n    pC = C['hist'] / C['hist'].sum() / (kc[1] - kc[0])"
new = """    pA = A['hist'] / totA / (kc[1] - kc[0]) if totA > 0 else np.zeros(len(kc))
    totB = float(B['hist'].sum())
    pB = B['hist'] / totB / (kc[1] - kc[0]) if totB > 0 else np.zeros(len(kc))
    totC = float(C['hist'].sum())
    pC = C['hist'] / totC / (kc[1] - kc[0]) if totC > 0 else np.zeros(len(kc))"""
assert old in src; src = src.replace(old, new)

old = "        'global_max': {'A': float(A['wm'].max()), 'B': float(B['wm'].max()), 'C': float(C['wm'].max())},"
new = "        'global_max': {'A': float(A['wm'].max()) if len(A['wm']) else 0.0, 'B': float(B['wm'].max()) if len(B['wm']) else 0.0, 'C': float(C['wm'].max()) if len(C['wm']) else 0.0},"
assert old in src; src = src.replace(old, new)

# np.zeros guard for empty hist arrays in aggregate
old = "        hist = np.zeros(len(rs[0]['hist']))"
assert old in src  # already zeros-init, fine

# rank plot x-position guard
old = "        ax.text(len(A['wm']) * 0.7, v + 0.5, 'ladder ' + str(v), fontsize=8, color='r')"
new = "        ax.text(max(1, len(A['wm'])) * 0.7, v + 0.5, 'ladder ' + str(v), fontsize=8, color='r')"
assert old in src; src = src.replace(old, new)

# PDF ylim guard when all pA zero
old = "    ax.text(thr, ray.max() * 0.5, nm, rotation=90, fontsize=8, color='r')"
new = "    ax.text(thr, max(1e-4, float(ray.max())) * 0.5, nm, rotation=90, fontsize=8, color='r')"
assert old in src; src = src.replace(old, new)

open('it_turbulence_worldc.py', 'w').write(src)
print('guards v2 OK')
