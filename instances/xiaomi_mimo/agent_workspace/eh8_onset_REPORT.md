# Echo-Horizon v8 — final corrected onset measurement


## A. exact fGn covariance (analytic verification)

H=0.55 p_exact=1.0997 (2H=1.1000, dev -0.0003)
H=0.65 p_exact=1.2980 (2H=1.3000, dev -0.0020)
H=0.75 p_exact=1.4925 (2H=1.5000, dev -0.0075)
H=0.85 p_exact=1.6757 (2H=1.7000, dev -0.0243)
H=0.95 p_exact=1.8290 (2H=1.9000, dev -0.0710)

smooth 1-ch^2 -> p=2.0023


## B. dataset structure

{}

## C. results

        name    fam   note      n    dt  p_small  nfit                rho_flag  p_floorless      beta   beta200     a_low     a_med    a_iqr  a_stable       m2
fgn_fine_H55    fgn H=0.55  60000 1.000      NaN     0 no_window(nfit=0,fl=39)     1.272726  1.110772  1.067294 -2.132321 -2.212370 0.193104      True 0.002785
fgn_fine_H65    fgn H=0.65  60000 1.000      NaN     0 no_window(nfit=0,fl=39)     1.462038  1.296046  1.264586 -2.343753 -2.419539 0.222247      True 0.000711
fgn_fine_H75    fgn H=0.75  60000 1.000      NaN     0 no_window(nfit=0,fl=39)     1.556748  1.472405  1.441542 -2.567971 -2.607831 0.292785      True 0.000147
fgn_fine_H85    fgn H=0.85  60000 1.000      NaN     0 no_window(nfit=0,fl=39)     1.932915  1.654418  1.621217 -2.788863 -2.843597 0.267898      True 0.000064
fgn_fine_H95    fgn H=0.95  60000 1.000      NaN     0 no_window(nfit=0,fl=39)     1.401928  1.781235  1.731303 -2.976748 -3.073363 0.348930      True 0.000026
    logistic    map        120000 1.000      NaN     0  no_window(nfit=0,fl=0)          NaN -0.060241 -0.004978  0.046757  0.043320 0.273862      True 3.727585
       henon    map        120000 1.000      NaN     0  no_window(nfit=0,fl=0)          NaN -0.075231 -0.005662  0.089165  0.561691 0.512211     False 5.005066
      lorenz   flow        120000 0.005 1.819448    20                      ok     2.215419  1.988632  1.189114 -6.509925 -8.218724 2.157734     False 0.000784
     rossler   flow        120000 0.020 1.935648    19                      ok     2.256724  1.991703  1.412624 -4.507357 -8.263380 2.745867     False 0.000664
   ar_smooth smooth         20000 1.000 1.038899     4                      ok     1.271635  0.901679  0.367760 -1.261063 -1.588904 0.208871      True 0.138442


## D. verdicts
