def rosenstein(series, dt, m=8, te=6, n_pts=3000, max_steps=400):
    E = takens_embed(series, m, te)  # contiguous, take middle block n_pts
    pairwise distances (n_pts² fine)
    theiler mask |i-j| <= m*te → inf
    nn, d0
    for k in 1..max_steps:
        valid = (nn + k < n_pts) & (d0 > tiny)
        dk = mean over valid of ||E[i+k] - E[nn[i]+k]||
        keep while valid count >= 40 and dk increasing/finite
    fit log dk vs k*dt over first nfit points where dk in growing regime (before saturation): take points from k=1 while dk <= max(dk)*0.5? Standard: fit in linear region. Use first 60% of points up to where dk < d_sat where d_sat = 0.5*mean_nn_attractor_diameter?
