def arm_counts_c37(cfg):
    N = int(cfg['N']); ns = int(cfg['n_seeds']); M = ns*100*N
    k = {}; E = {}; Mseed = 100*N
    for s in S_LIST:
        b = cfg['bins'].get(str(s))
        if b is None: continue
        r = b['ratio']
        k[s] = r*M*math.exp(-s)
        E[s] = M*math.exp(-s)
    # per-arm overdispersion estimate from stored sd of ratio
    D = {}
    for s in S_LIST:
        b = cfg['bins'].get(str(s))
        if b is None or b['ratio'] <= 0 or b['sd'] <= 0: continue
        D[s] = b['sd']**2 * Mseed * math.exp(-s) / b['ratio']
    return k, E, D, M

def arm_counts_c39(arm):
    k = {}; E = {}; D = {}; M = 0
    for s in S_LIST:
        b = arm['bins'].get(str(s))
        if b is None: continue
        k[s] = float(b['k']); E[s] = float(b['E']); M = ... # store M in arm
    ...
