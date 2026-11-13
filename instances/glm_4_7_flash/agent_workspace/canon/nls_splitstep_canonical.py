def arm_counts_from_c37(cfg):
    N=cfg['N']; ns=cfg['n_seeds']; M=ns*100*N
    k={s: cfg['bins'][str(s)]['ratio']*M*math.exp(-s) for s in S_LIST}
    return k, M
