import numpy as np
from numba import njit

@njit(cache=True)
def gs_step(u, v, F, k, Du, Dv, dt, L):
    # Canonical Gray-Scott discrete Laplacian kernel:
    #   0.05  0.20  0.05
    #   0.20 -1.00  0.20
    #   0.05  0.20  0.05
    LapU = np.empty_like(u)
    LapV = np.empty_like(v)
    for x in range(L):
        for y in range(L):
            sU = 0.0; sV = 0.0
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0:
                        w = -1.0
                    elif (dx==0) != (dy==0):   # edge (one zero)
                        w = 0.2
                    else:                       # corner (both nonzero)
                        w = 0.05
                    sU += w * u[(x+dx)%L, (y+dy)%L]
                    sV += w * v[(x+dx)%L, (y+dy)%L]
            LapU[x,y] = sU
            LapV[x,y] = sV
    for i in range(L*L):
        x = i // L; y = i % L
        uvv = u[x,y]*v[x,y]*v[x,y]
        u[x,y] += (Du*LapU[x,y] - uvv + F*(1.0 - u[x,y]))*dt
        v[x,y] += (Dv*LapV[x,y] + uvv - (F + k)*v[x,y])*dt
