def p_from_rho(rho, n, k, one_max=0.30):
    floor = k/np.sqrt(n)
    ad_max = min(20000, n//4)
    one_all = 1.0 - rho[:ad_max+1]
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max))
    else:
        lmax = ad_max
    lmax = max(lmax, 40)
    lags = np.arange(1, lmax+1)
    p, nfit = onset_from_rho(lags, rho[lags-1], one_max, floor)
    return p, nfit, floor, bool(len(k_over) > 0)
