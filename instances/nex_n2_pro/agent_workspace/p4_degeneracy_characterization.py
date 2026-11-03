#!/usr/bin/env python3
"""Characterize the two degenerate float pairs (S0~S2, S1~S3) of the P4 tongue.
Question: is S2 a spatial symmetry (translation/reflection/complement) of S0,
or an independent pointwise state? And is the float period a 'symmetry-extended P2'?
"""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

r, eps, N, seed = 3.865, 0.132, 100, 42
np.random.seed(seed)
x = np.random.rand(N)
for _ in range(2000):
    x = step(x, r, eps)
S0 = x.copy()
x = step(x, r, eps); S1 = x.copy()
x = step(x, r, eps); S2 = x.copy()
x = step(x, r, eps); S3 = x.copy()

def close(a, b, tag):
    m = np.max(np.abs(a - b)); mu = np.mean(np.abs(a - b))
    print(f"  {tag:28s} max={m:.6f}  mean={mu:.6f}")
    return m

print("=== Base invariants ===")
close(S0, S2, "S2 - S0 (raw)")
close(S1, S3, "S3 - S1 (raw)")
close(S0, S1, "S1 - S0 (raw, distinct states)")

print("\n=== Is S2 a spatial translation of S0? (checkerboard precession) ===")
best = None
for k in range(1, 11):
    m = np.max(np.abs(S2 - np.roll(S0, k)))
    if best is None or m < best[0]:
        best = (m, k)
    print(f"  roll k={k:2d}: max={m:.6f}")
print(f"  BEST translation: k={best[1]} max={best[0]:.6f}  (0 => S2==roll(S0))")

print("\n=== Is S2 the complement of S0? (S2 ~ 1 - S0) ===")
close(S2, 1.0 - S0, "S2 - (1 - S0)")

print("\n=== Is S2 a pointwise affine of S0? (S2 = a*S0 + b) ===")
a, b = np.polyfit(S0, S2, 1)
close(S2, a*S0 + b, "S2 - (a*S0+b) residual")
print(f"  affine fit: a={a:.4f} b={b:.4f}  (a~1,b~0 => near-identical; a~-1 => complement)")

print("\n=== Correlation structure ===")
print(f"  corr(S0,S2)={np.corrcoef(S0,S2)[0,1]:.6f}")
print(f"  corr(S0,S1)={np.corrcoef(S0,S1)[0,1]:.6f}")
print(f"  corr(S0,roll(S0,1))={np.corrcoef(S0,np.roll(S0,1))[0,1]:.6f}")

print("\n=== Means & variances of the 4 states ===")
for nm,S in [("S0",S0),("S1",S1),("S2",S2),("S3",S3)]:
    print(f"  {nm}: mean={S.mean():.6f} std={S.std():.6f} min={S.min():.6f} max={S.max():.6f}")

print("\n=== Spatial autocorrelation of S0 (is it a traveling wave / mode?) ===")
# Fourier: dominant wavenumber of the spatial profile
f0 = np.fft.rfft(S0 - S0.mean())
p0 = np.abs(f0)**2
dom = np.argmax(p0)
print(f"  S0 dominant spatial wavenumber (FFT bin) = {dom} of {len(p0)}  (power={p0[dom]:.4f} / total={p0.sum():.4f})")
f2 = np.fft.rfft(S2 - S2.mean())
p2 = np.abs(f2)**2
dom2 = np.argmax(p2)
print(f"  S2 dominant spatial wavenumber = {dom2} (power={p2[dom2]:.4f} / total={p2.sum():.4f})")
print(f"  -> same dominant mode: {dom==dom2}")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 2, figsize=(14, 8))
ax[0,0].plot(S0,'o',ms=4,label='S0',color='#1f77b4')
ax[0,0].plot(S2,'s',ms=4,label='S2 (mean&bits==S0, pointwise !=)',color='#2ca02c')
ax[0,0].plot(1-S0,'^',ms=3,label='1 - S0 (complement)',color='#999999',ls='--')
ax[0,0].set_title('Degenerate pair S0 & S2: same mean, same median-bits, pointwise distinct')
ax[0,0].set_xlabel('site'); ax[0,0].legend(); ax[0,0].grid(alpha=0.3)

ax[0,1].plot(S0,'-',color='#1f77b4',label='S0',alpha=0.7)
ax[0,1].plot(S2,'-',color='#2ca02c',label='S2',alpha=0.7)
ax[0,1].set_title('Pointwise S0 vs S2 (delta up to 0.17)')
ax[0,1].set_xlabel('site'); ax[0,1].legend(); ax[0,1].grid(alpha=0.3)

# pointwise delta
ax[1,0].plot(S2-S0,'o-',ms=3,color='#d62728')
ax[1,0].axhline(0,color='k',ls='--',lw=0.8)
ax[1,0].set_title('S2 - S0 pointwise (nonzero => float P4 is real)')
ax[1,0].set_xlabel('site'); ax[1,0].grid(alpha=0.3)

# bit patterns over the 4 states (global median)
gmed = np.median(np.stack([S0,S1,S2,S3]))
for nm,S in [("S0",S0),("S1",S1),("S2",S2),("S3",S3)]:
    ax[1,1].plot((S>gmed).astype(float)+ (0.3 if nm in ("S0","S1") else 0),'.-',ms=4, label=nm, alpha=0.8)
ax[1,1].set_title('Median-bit pattern of the 4 states (S0==S2, S1==S3 => binary P2)')
ax[1,1].set_xlabel('site'); ax[1,1].legend(); ax[1,1].grid(alpha=0.3)
fig.tight_layout(); fig.savefig('p4_degeneracy.png', dpi=140, bbox_inches='tight')
print("\nsaved p4_degeneracy.png")
