src = open('it_turbulence_worldc.py').read()

# 1) filters keyed to config variables instead of hardcoded values
old = "    A = aggregate([r for r, j in zip(results, jobs) if j[1] == 1024 and j[2] == 100.0 and j[5] == 0.05])"
new = "    A = aggregate([r for r, j in zip(results, jobs) if j[1] == NA and j[2] == LA and j[5] == 0.05])"
assert old in src; src = src.replace(old, new)

old = "    B = aggregate([r for r, j in zip(results, jobs) if j[1] == 1024 and j[2] == 100.0 and j[5] == 0.20])"
new = "    B = aggregate([r for r, j in zip(results, jobs) if j[1] == NB and j[2] == LB and j[5] == 0.20])"
assert old in src; src = src.replace(old, new)

old = "    C = aggregate([r for r, j in zip(results, jobs) if j[1] == 2048])"
new = "    C = aggregate([r for r, j in zip(results, jobs) if j[1] == NC])"
assert old in src; src = src.replace(old, new)

# 2) aggregate: only use snapshot keys present in every realization
old = """        ag['specs'] = {}
        for key in (0, 5, 15, 40, 100):
            ag['specs'][key] = np.mean([np.array(r['spectra'][key]) for r in rs], axis=0)"""
new = """        ag['specs'] = {}
        for key in (0, 5, 15, 40, 100):
            if all(key in r['spectra'] for r in rs):
                ag['specs'][key] = np.mean([np.array(r['spectra'][key]) for r in rs], axis=0)"""
assert old in src; src = src.replace(old, new)

# 3) main: guard spec slope + plot on key presence
old = "    spec = A['specs'][100]"
new = "    spec = A['specs'].get(100)"
assert old in src; src = src.replace(old, new)

old = "    if m.sum() > 5:"
new = "    if spec is not None and len(spec) == len(kk) and m.sum() > 5:"
assert old in src; src = src.replace(old, new)

old = "    for skey, lbl in ((0, 't=0'), (5, 't=5'), (15, 't=15'), (40, 't=40'), (100, 't=100')):"
new = "    for skey, lbl in ((0, 't=0'), (5, 't=5'), (15, 't=15'), (40, 't=40'), (100, 't=100')):\n        if skey not in A['specs']:\n            continue"
assert old in src; src = src.replace(old, new)

# 4) empty-ensemble guard so smoke tests never crash later code paths
old = """    kc = 0.5 * (np.array(A['rs'][0]['bins'][:-1]) + np.array(A['rs'][0]['bins'][1:]))"""
new = """    if A['n_ok'] == 0:
        print('NO REALIZATIONS SURVIVED - aborting analysis')
        return
    kc = 0.5 * (np.array(A['rs'][0]['bins'][:-1]) + np.array(A['rs'][0]['bins'][1:]))"""
assert old in src; src = src.replace(old, new)

open('it_turbulence_worldc.py', 'w').write(src)
print('guard patch OK')
