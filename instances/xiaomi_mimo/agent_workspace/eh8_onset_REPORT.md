# Echo-Horizon v8 — final corrected onset measurement


## A. exact fGn covariance (analytic verification)

H=0.55 p_exact=1.0997 (2H=1.1000, dev -0.0003)
H=0.65 p_exact=1.2980 (2H=1.3000, dev -0.0020)
H=0.75 p_exact=1.4925 (2H=1.5000, dev -0.0075)
H=0.85 p_exact=1.6757 (2H=1.7000, dev -0.0243)
H=0.95 p_exact=1.8290 (2H=1.9000, dev -0.0710)

smooth 1-ch^2 -> p=2.0023


## B. dataset structure

{
 "solar_sunspots": {
  "data": "(3333, 6)"
 },
 "climate_enso": {
  "data": "(852, 10)"
 },
 "climate_temperatures": {
  "data": "(3650, 2)"
 },
 "neural_eeg": {
  "data": "(14980, 15)"
 },
 "lynx_hare": {
  "data": "(21, 3)"
 }
}

## C. results

                           name    fam   note      n    dt  p_small  nfit                 rho_flag  p_floorless      beta   beta200     a_low     a_med    a_iqr  a_stable       m2
                   fgn_fine_H55    fgn H=0.55  60000 1.000      NaN     0  no_window(nfit=0,fl=39)     1.272726  1.110772  1.067294 -2.132321 -2.212370 0.193104      True 0.002785
                   fgn_fine_H65    fgn H=0.65  60000 1.000      NaN     0  no_window(nfit=0,fl=39)     1.462038  1.296046  1.264586 -2.343753 -2.419539 0.222247      True 0.000711
                   fgn_fine_H75    fgn H=0.75  60000 1.000      NaN     0  no_window(nfit=0,fl=39)     1.556748  1.472405  1.441542 -2.567971 -2.607831 0.292785      True 0.000147
                   fgn_fine_H85    fgn H=0.85  60000 1.000      NaN     0  no_window(nfit=0,fl=39)     1.932915  1.654418  1.621217 -2.788863 -2.843597 0.267898      True 0.000064
                   fgn_fine_H95    fgn H=0.95  60000 1.000      NaN     0  no_window(nfit=0,fl=39)     1.401928  1.781235  1.731303 -2.976748 -3.073363 0.348930      True 0.000026
                       logistic    map        120000 1.000      NaN     0   no_window(nfit=0,fl=0)          NaN -0.060241 -0.004978  0.046757  0.043320 0.273862      True 3.727585
                          henon    map        120000 1.000      NaN     0   no_window(nfit=0,fl=0)          NaN -0.075231 -0.005662  0.089165  0.561691 0.512211     False 5.005066
                         lorenz   flow        120000 0.005 1.819448    20                       ok     2.215419  1.988632  1.189114 -6.509925 -8.218724 2.157734     False 0.000784
                        rossler   flow        120000 0.020 1.935648    19                       ok     2.256724  1.991703  1.412624 -4.507357 -8.263380 2.745867     False 0.000664
                      ar_smooth smooth         20000 1.000 1.038899     4                       ok     1.271635  0.901679  0.367760 -1.261063 -1.588904 0.208871      True 0.138442
      solar_sunspots_series_ch0   real          3333 1.000      NaN     0  no_window(nfit=0,fl=39)     1.146829  1.001122  1.812525 -6.208079 -5.238429 1.312531     False 0.000101
      solar_sunspots_series_ch2   real          3333 1.000      NaN     0  no_window(nfit=0,fl=39)     1.147945  1.999936  1.999991 -6.197445 -5.860155 0.640767     False 0.000057
      solar_sunspots_series_ch4   real          3333 1.000      NaN     0  no_window(nfit=0,fl=25)     0.849326  0.432610  0.418290 -1.822273 -1.706607 0.542998     False 0.179708
      solar_sunspots_series_ch5   real          3333 1.000      NaN     0  no_window(nfit=0,fl=39)     0.578263  0.511730  0.651802 -2.278099 -1.954935 0.418056      True 0.041897
        climate_enso_series_ch0   real           852 1.000      NaN     0 no_window(nfit=0,fl=112)     1.112973  1.004641  1.705883 -6.716474 -4.788369 0.860714     False 0.001548
        climate_enso_series_ch3   real           852 1.000      NaN     0   no_window(nfit=0,fl=0)          NaN  1.012155  0.211448 -0.430082 -1.264557 0.553242     False 0.268927
        climate_enso_series_ch6   real           852 1.000      NaN     0   no_window(nfit=0,fl=3)     2.268328  1.062500  0.320925 -1.024104 -1.600886 0.374846      True 0.139926
        climate_enso_series_ch9   real           852 1.000      NaN     0   no_window(nfit=0,fl=3)     2.293883  1.314432  0.294215 -0.553171 -1.593531 0.691808     False 0.110342
climate_temperatures_series_ch0   real          3650 1.000      NaN     0  no_window(nfit=0,fl=39)     1.147576  2.000000  2.000000 -6.194003 -5.937718 0.299176      True 0.000048
climate_temperatures_series_ch1   real          3650 1.000      NaN     0   no_window(nfit=0,fl=0)          NaN  0.238899  0.439491 -0.763792 -0.744910 0.183219      True 0.654090
                     neural_eeg   real         14980 1.000      NaN     0  no_window(nfit=0,fl=39)     1.130024  1.000262  0.884427 -1.962423 -2.032867 0.107597      True 0.011366


## D. verdicts
