# Echo-Horizon v7 — corrected SHORT-LAG onset measurement


## A. exact fGn covariance (analytic verification)

H=0.55 p_exact=1.0999 (2H=1.1000, dev -0.0001)
H=0.65 p_exact=1.2994 (2H=1.3000, dev -0.0006)
H=0.75 p_exact=1.4966 (2H=1.5000, dev -0.0034)
H=0.85 p_exact=1.6837 (2H=1.7000, dev -0.0163)
H=0.95 p_exact=1.8369 (2H=1.9000, dev -0.0631)

smooth 1-ch^2 -> p=2.0000


## B. dataset structure

{}

## C. results

        name  fam   note      n    dt  p_small  nfit      beta     a_low      a_all       m2
fgn_fine_H55  fgn H=0.55  60000 1.000      NaN     0  0.009270 -0.123968  -0.089048 3.109879
fgn_fine_H65  fgn H=0.65  60000 1.000      NaN     0  0.036324 -0.307060  -0.269638 2.677123
fgn_fine_H75  fgn H=0.75  60000 1.000      NaN     0  0.075599 -0.466039  -0.450206 2.190572
fgn_fine_H85  fgn H=0.85  60000 1.000      NaN     0  0.129256 -0.706421  -0.630564 1.606432
fgn_fine_H95  fgn H=0.95  60000 1.000      NaN     0  0.203928 -0.910524  -0.813803 1.010368
    logistic  map        120000 1.000      NaN     0 -0.019169  0.046757   0.275111 3.727585
       henon  map        120000 1.000      NaN     0 -0.022280  0.089165   0.510347 5.005066
      lorenz flow        120000 0.005 2.215419    33  1.885433 -6.509925  -9.946083 0.000784
     rossler flow        120000 0.020 2.256724    32  1.930461 -4.507357 -10.726064 0.000664