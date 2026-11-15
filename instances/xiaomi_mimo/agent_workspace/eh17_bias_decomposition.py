"""
Echo-Horizon v17 — bias-source decomposition of p_rho.

OPEN THREAD (from EH16): the fine-sampled p_rho shows a persistent negative bias
~ -0.08..-0.10 at n=1e7 that decays as a POWER LAW in n, not exponentially.
WHICH component of the estimator is responsible?  Three suspects, pre-registered:

  S1  finite-n noise floor (20/sqrt(n)) truncates the first lags via the
      one > floor gate, shifting the fit window into the curved crossover zone.
  S2  sample-variance normalisation (x/std, unbiased ACF) inflates small lags
      (ratio-of-expectations bias), affecting ALL lags uniformly.
  S3  curvature within the fit window (one = (h delta)^(2H) only asymptotically;
      exact rho has O(h^(2H-2)) corrections) + regression slope over a finite
      h-range biases the slope even on the noiseless curve.

Controlled experiments (all H = 0.75, delta = 1e-3 unless noted):

  PART 1  (S3, curvature):    p_rho fit on the EXACT noiseless 1-rho(h) curve
          over the same window the noisy estimator picks at each n.
          If p_exact ~ -0.10  =>  curvature dominates and the bias is a
          WINDOW artefact (fit range too narrow / curved), NOT a noise issue.
          If p_exact -> 2H    =>  noise/floor is the culprit.

  PART 2  (S1, floor):        same exact curve, but vary the floor multiplier
          (0, 5, 10, 20, 40) x 1/sqrt(n).  Direct causal test of S1.

  PART 3  (S2, normalisation): same noisy data, compute rho with:
          a) unbiased ACF (current)    b) biased /n ACF    c) biased ACF
          then NO rescale by sample std (use population std only).
          Isolate the ratio-of-expectations bias.

  PART 4  (window range):     on the EXACT curve, sweep the fit window
          explicitly: h_lo in {1,4,16,64}, h_hi in {40,200,800,2000}.
          Does p(h_lo,h_hi) -> 2H as h_lo,h_hi grow?  Quantifies S3 directly.
"""
import numpy as np, json, math
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

OUT = {}

def rho_fgn(h, H):
    h = np.abs(np.asarray(h, float))
    return 0.5*((h+1)**(2*H) - 2*h**(2*H) + np.abs(h-1)**(2*H))

def fgn(n, H, delta, seed):
    rng = np.random.default_rng(seed)
    m = 1 << int(np.ceil(np.log2(max(2*n, 64))))
    k = np.arange(m//2 + 1)
    c = rho_fgn(k*delta, H); c[0] = 1.0
    circ = np.concatenate([c, c[-2:0:-1]])
    lam = np.fft.rfft(circ).real
    lam[lam < 1e-12] = 1e-12
    z = (rng.normal(size=len(lam)) + 1j*rng.normal(size=len(lam))) * np.sqrt(lam/2)
    x = np.fft.irfft(z, m)[:n]
    return (x - x.mean())/x.std()

# ---------------- exact window logic (verbatim from eh8/eh16 measure) ----------------
def pick_window(n, one, one_max=0.30, floor_mult=20.0):
    floor = floor_mult/np.sqrt(n)
    ad_max = min(20000, n//4)
    one_all = one[:ad_max+1]
    k_over = np.where(one_all[1:] > floor*1.5)[0]
    if len(k_over):
        h_need = int(k_over[0]) + 1
        lmax = int(min(max(h_need*8, 40), ad_max))
    else:
        h_need, lmax = -1, ad_max
    lmax = max(lmax, 40)
    h = np.arange(1, lmax+1, dtype=float)
    one_ = one[1:lmax+1]
    ok = np.isfinite(one_) & (one_ > floor) & (one_ < one_max)
    if ok.sum() < 3: return None
    hh = h[ok][:len(one_[ok])]; lo = np.log(one_[ok])
    hh = hh[:len(lo)]
    p, _ = np.polyfit(np.log(hh), lo, 1)
    return float(p), int(ok.sum()), (int(hh.min()), int(hh.max()))

def exact_one(h, H, delta):
    """exact 1-rho_fgn(h*delta) for real lag h."""
    return 1.0 - rho_fgn(np.asarray(h, float)*delta, H)

# ---------------- ACF variants ----------------
def acf_variants(x):
    x = np.asarray(x, float); n = len(x)
    xc = x - x.mean()
    F = np.fft.rfft(xc, n=2*n); pw = (F*np.conj(F)).real
    raw = np.fft.irfft(pw)[:n]           # sum x_i x_{i+h}
    counts = np.arange(n, 0, -1)
    acf_unbiased = raw/counts
    acf_biased   = raw/n
    var_pop = np.mean(xc*xc)             # population variance (biased /n)
    var_samp = np.var(x, ddof=1)         # sample variance (unbiased)
    rho_unbiased_rescale = acf_unbiased/var_samp   # current measure()
    rho_biased_rescale   = acf_biased  /var_samp
    rho_biased_pop       = acf_biased  /var_pop    # no rescale, population var
    rho_unbiased_pop     = acf_unbiased/var_pop
    return dict(unbiased_rescale=rho_unbiased_rescale,
                biased_rescale=rho_biased_rescale,
                biased_pop=rho_biased_pop,
                unbiased_pop=rho_unbiased_pop)

# =================== PART 1 & 4: exact-curve window bias ===================
print('=== PART 1: exact noiseless curve, estimator window at each n ===')
H, delta = 0.75, 1e-3
TRUTH = 2*H
N_LIST = [10**3, 10**4, 10**5, 10**6, 10**7]
part1 = []
for n in N_LIST:
    one_exact = 1.0 - rho_fgn(np.arange(0, min(20000, n//4)+1)*delta, H)
    res = pick_window(n, one_exact, floor_mult=20.0)
    if res is None:
        part1.append(dict(n=n, p=float('nan'), nfit=0, w=(None,None)))
        print('  n=%d  no_window on exact curve' % n); continue
    p, nfit, w = res
    part1.append(dict(n=n, p=p, nfit=nfit, w=list(w)))
    print('  n=%8d  p_exact=%+.4f  bias=%+.4f  window=[%d,%d] nfit=%d'
          % (n, p, p-TRUTH, w[0], w[1], nfit))
OUT['part1'] = part1

print('=== PART 4: explicit window sweep on exact curve ===')
part4 = []
for h_lo in [1, 4, 16, 64]:
    row = {}
    for h_hi in [40, 200, 800, 2000]:
        h = np.arange(h_lo, h_hi+1, dtype=float)
        one_ = 1.0 - rho_fgn(h*delta, H)
        ok = (one_ > 0) & (one_ < 0.30)
        if ok.sum() < 3:
            row[str(h_hi)] = float('nan'); continue
        p, _ = np.polyfit(np.log(h[ok]), np.log(one_[ok]), 1)
        row[str(h_hi)] = float(p)
    part4.append(dict(h_lo=h_lo, **row))
    print('  h_lo=%3d -> p(h_hi=40,200,800,2000) = %s'
          % (h_lo, ' '.join('%+.4f' % row[str(k)] for k in [40,200,800,2000])))
OUT['part4'] = part4

# =================== PART 2: floor multiplier on exact curve ===================
print('=== PART 2: floor multiplier sweep on exact curve (n=1e6) ===')
part2 = {}
n2 = 10**6
one_exact2 = 1.0 - rho_fgn(np.arange(0, min(20000, n2//4)+1)*delta, H)
for fm in [0, 5, 10, 20, 40]:
    res = pick_window(n2, one_exact2, floor_mult=fm)
    if res is None:
        part2[str(fm)] = float('nan'); print('  fm=%2d  no_window' % fm); continue
    p, nfit, w = res
    part2[str(fm)] = p
    print('  fm=%2d  p=%+.4f  bias=%+.4f  window=[%d,%d]'
          % (fm, p, p-TRUTH, w[0], w[1]))
OUT['part2'] = part2

# =================== PART 3: ACF variant bias on noisy data ===================
print('=== PART 3: ACF normalisation variants (H=0.75, delta=1e-3, seeds) ===')
def seeds_for(n): return {10**3: 48, 10**4: 32, 10**5: 16, 10**6: 8, 10**7: 3}.get(int(n), 8)
BASE = 7717
part3 = {k: {n: [] for n in N_LIST} for k in
         ['unbiased_rescale','biased_rescale','biased_pop','unbiased_pop']}
for n in N_LIST:
    for s in range(seeds_for(n)):
        x = fgn(n, H, delta, BASE + int(H*100)*10**6 + n//10 + s*97)
        acfs = acf_variants(x)
        for k, rho in acfs.items():
            one = 1.0 - rho[:min(20000, n//4)+1]
            res = pick_window(n, one)
            part3[k][n].append(res[0] if res else float('nan'))
    for k in part3:
        arr = np.array(part3[k][n], float)
        m = np.nanmean(arr); sd = np.nanstd(arr)/max(1, np.sum(np.isfinite(arr)))**0.5
        part3[k][n] = dict(mean=float(m), sem=float(sd))
    print('  n=%8d  ' % n + '  '.join(
        '%s=%+.4f' % (k.replace('_rescale','').replace('_pop','_p'),
                       part3[k][n]['mean']) for k in part3))
OUT['part3'] = {k: {str(n): v for n, v in d.items()} for k, d in part3.items()}

# =================== SUMMARY + FIGURES ===================
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

ax = axes[0,0]
ns_ = np.array([d['n'] for d in part1], float)
ps_ = np.array([d['p'] for d in part1], float)
ax.plot(ns_, ps_, 'o-', label='exact curve, estimator window')
ax.axhline(TRUTH, color='r', ls='--', label='truth 2H=%.2f' % TRUTH)
ax.set_xscale('log'); ax.set_xlabel('n'); ax.set_ylabel('p (exact curve)')
ax.set_title('Part 1: window bias on noiseless curve'); ax.grid(alpha=0.3); ax.legend()

ax = axes[0,1]
for row in part4:
    hs = [40,200,800,2000]
    ax.plot(hs, [row[str(k)] for k in hs], 'o-', label='h_lo=%d' % row['h_lo'])
ax.axhline(TRUTH, color='r', ls='--')
ax.set_xscale('log'); ax.set_xlabel('h_hi'); ax.set_ylabel('p (exact)')
ax.set_title('Part 4: explicit window sweep (curvature S3)'); ax.grid(alpha=0.3); ax.legend(fontsize=8)

ax = axes[1,0]
fms = [0,5,10,20,40]
ax.plot(fms, [part2[str(f)] for f in fms], 'o-')
ax.axhline(TRUTH, color='r', ls='--')
ax.set_xlabel('floor multiplier'); ax.set_ylabel('p (exact, n=1e6)')
ax.set_title('Part 2: floor effect (S1)'); ax.grid(alpha=0.3)

ax = axes[1,1]
for k in part3:
    ms = [part3[k][n]['mean'] for n in N_LIST]
    ax.plot(N_LIST, ms, 'o-', label=k)
ax.axhline(TRUTH, color='r', ls='--')
ax.set_xscale('log'); ax.set_xlabel('n'); ax.set_ylabel('p (noisy)')
ax.set_title('Part 3: ACF variant bias (S2)'); ax.grid(alpha=0.3); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig('eh17_decomposition.png', dpi=130)

with open('eh17_decomposition.json', 'w') as f:
    json.dump(OUT, f, indent=1, default=float)

# Verdict
p1_final = part1[-1]['p']
curv_dominant = abs(p1_final - TRUTH) > 0.04
lines = ['# EH17 — bias-source decomposition of p_rho\n']
lines.append('H=0.75 (truth 2H=1.50), delta=1e-3\n')
lines.append('## Verdict summary\n')
lines.append('- Part 1 exact-curve bias at n=1e7: **%+.4f** -> %s' % (
    p1_final-TRUTH,
    'CURVATURE/WINDOW (S3) dominates: noiseless curve already biased' if curv_dominant
    else 'noise/floor dominates: exact curve nearly unbiased'))
lines.append('- Part 2 floor multiplier (n=1e6): %s' %
    {k: round(v,4) for k,v in part2.items()})
lines.append('- Part 4 explicit window (h_lo=64): p(40..2000)=%s' %
    [round(r['40'],3) for r in part4 if r['h_lo']==64])
lines.append('- Part 3 ACF variants at n=1e7: %s' %
    {k: round(part3[k][10**7]['mean'],4) for k in part3})
lines.append('\nFigures: eh17_decomposition.png')
with open('EH17_REPORT.md', 'w') as f:
    f.write('\n'.join(lines)+'\n')
print('\n'.join(lines))
print('DONE')