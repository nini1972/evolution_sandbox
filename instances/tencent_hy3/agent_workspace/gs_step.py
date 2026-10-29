import numpy as np
from numba import njit

@njit(cache=True)
def gs_step(u, v, F, k, Du, Dv, dt, L):
    # Gray-Scott reaction-diffusion one step (3x3 kernel, periodic)
    LapU = np.empty_like(u)
    LapV = np.empty_like(v)
    for x in range(L):
        for y in range(L):
            sU = 0.0; sV = 0.0
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    w = 1.0 if (dx==0 or dy==0) else 0.5
                    if dx==0 and dy==0:
                        w = -6.0
                    lapu = u[(x+dx)%L, (y+dy)%L]
                    lapv = v[(x+dx)%L, (y+dy)%L]
                    sU += w * lapu
                    sV += w * lapv
            LapU[x,y] = sU
            LapV[x,y] = sV
    for i in range(L*L):
        x = i // L; y = i % L
        uvv = u[x,y]*v[x,y]*v[x,y]
        u[x,y] += (Du*LapU[x,y] - uvv + F*(1.0 - u[x,y]))*dt
        v[x,y] += (Dv*LapV[x,y] + uvv - (F + k)*v[x,y])*dt
