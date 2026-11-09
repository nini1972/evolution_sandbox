"""
C37: GROWTH SCAN — does the high-s tail behavior recede with box size L at fixed dx?

Arc context (D30 -> C36, dossier DOSSIER_final.md 2026-11-05):
  C32 reference profile (N=1024, L=50, eps=0.1): suppression s=2, peak +5.0sigma
    at s~6, "null return by s>=8" (window ended at s=9).
  C35 mechanism test (fixed dx=0.0488, L=50/100/200): mid-tail excess 1.04-1.17
    is bulk and L-independent; kurt ~1.96-2.00; dens(I>6)/L = 0.058/0.055/0.056.
  OPEN QUESTION: is the s>=8 rolloff/reversal a transition that RECEDES with L
    (FTG/Gumbel extreme-value logic: s*(L) ~ s0*ln L), or does the ratio blow up
    with s (power-law parent tail), or is the whole profile L-saturated?

Methodology (bit-compatible with C35, canonical canon/nls_splitstep_canonical.py):
  i psi_t + psi_xx + |psi|^2 psi = 0 (focusing), Strann splitting:
    linear half: psi <- ifft(exp(-i k^2 dt) * fft(psi))   [FULL dt]
    nonlinear:   psi <- exp(i |psi|^2 dt) * psi
  IC: psi = 1 + eps*(CN(0,1)+i*CN(0,1))/sqrt(2), numpy default_rng(seed)
  dt = 2.5e-4, T_end = 100, t_trans = 50 (post-transient only), eps = 0.1
  seeds 1..12 (12 per config), sample every 0.5 t-units after t=50.
  dx = 0.048828125 FIXED for every config (L/2^11): L=50->N=1024, 100->2048,
  200->4096, 400->8192, 800->16384.

Pre-registered hypotheses (discriminated by ratio(s) shape at s in [10,14]):
  H-FTG:        null-return point s*(L) recedes ~ ln L; Delta(s) profile
                stretches right with L; bounded amplitudes.
  H-power-law:  ratio keeps growing with s with NO return to null, independent
                of L (parent tail heavier than Rayleigh e^{-s}).
  H-saturated:  profiles collapse across ALL L including the new L=400/800
                arms (dx-family saturates; no L-growth at any s).

Observables per config (between-seed stats over 12 seeds):
  ratio(s) = P_obs(I>s) / e^{-s}         s in {2,...,14}
  sig(s)   = (mean_ratio - 1) / SD_seeds  (primary; Poisson fallback if starved)
  kurt     = ((I-1)^4).mean()             (canonical c35 observable)
  dens6    = mean frac(I>6) / L           (filament density per unit length)
  maxI     = max over all post-transient samples
Starvation flag: expected null counts below threshold e^{-s}*N_samples < 20.

Resumable: StageTracker stage 'c37_growth_scan', checkpoint key per config
  ('L50','L100','L200','L400','L800'), final key 'final'.
Runtime guard: seeds parallelized with multiprocessing Pool (<=4 workers).
"""

import os, json, math, time
import numpy as np

# ----------------------------------------------------------------------------
# CANONICAL INTEGRATOR — verbatim from canon/nls_splitstep_canonical.py
# (Established 2026-11-06 after incident C36. Do not modify. SHA-256 2bd620cb...)
# ----------------------------------------------------------------------------
from numpy.fft import fft, ifft, fftfreq

def make_grid(N, L):
    dx = L / N
    k = 2.0 * np.pi * fftfreq(N, d=dx)
    x = (np.arange(N) - N/2) * dx
    return x, k, dx

def initial_condition(N, eps, seed):
    rng = np.random.default_rng(seed)
    return 1.0 + eps*(rng.standard_normal(N) + 1j*rng.standard_normal(N))/sqrt2

def step_strang(psi, D, dt):
    psi = ifft(D * fft(psi))
    psi = np.exp(1j*np.abs(psi)**2 * dt) * psi
    return psi

def simulate(N, L, dt, T_end, eps, seed, sample_every=None, t_trans=0.0):
    """Returns (times, samples, diagnostics). samples: list of |psi|^2 arrays
    taken every sample_every steps after t_trans."""
    x, k, dx = make_grid(N, L)
    D = np.exp(-1j * k**2 * dt)
    psi = initial_condition(N, eps, seed)
    nsteps = int(round(T_end/dt))
    ntrans = int(round(t_trans/dt))
    times, samples = [], []
    if sample_every is None:
        sample_every = max(1, int(round(0.5/dt)))
    for s in range(1, nsteps+1):
        psi = step_strang(psi, D, dt)
        if s > ntrans and (s - ntrans) % sample_every == 0:
            times.append(s*dt)
            samples.append(np.abs(psi)**2)
    I = np.abs(psi)**2
    diag = dict(mass=I.mean(), kurt=float(((I-1)**4).mean()))
    return np.array(times), samples, diag

sqrt2 = np.sqrt(2.0)   # defined AFTER the verbatim block; used by initial_condition

# ----------------------------------------------------------------------------
# C37 SCAN CONFIG
# ----------------------------------------------------------------------------
CONFIGS = [(50, 1024), (100, 2048), (200, 4096), (400, 8192), (800, 16384)]
KEYS    = ['L50', 'L100', 'L200', 'L400', 'L800']
DX      = 50.0/1024.0          # 0.048828125 — fixed for every config
DT      = 2.5e-4
T_END   = 100.0
T_TRANS = 50.0
EPS     = 0.1
SEEDS   = list(range(1, 13))   # 12 seeds, C35 convention
S_LIST  = [2,3,4,5,6,7,8,9,10,11,12,13,14]

# ---- multiprocessing worker -------------------------------------------------
def _run_seed(args):
    L, N, seed = args
    t0 = time.time()
    times, samples, diag = simulate(N, L, DT, T_END, EPS, seed, t_trans=T_TRANS)
    I = np.asarray(samples)                       # (n_samples, N) post-transient
    n_samp = I.size
    per_seed = {'ratios': {}, 'poisson_sig': {}}
    for s in S_LIST:
        p_obs = float((I > s).mean())
        exp_null = math.exp(-s)
        ratio = p_obs / exp_null
        per_seed['ratios'][s] = ratio
        # Poisson fallback sigma on the ratio: (p_obs - exp) / sqrt(exp/n_samp)
        sigma_p = math.sqrt(exp_null / n_samp)
        per_seed['poisson_sig'][s] = (p_obs - exp_null) / sigma_p if sigma_p > 0 else 0.0
    per_seed['kurt'] = float(((I - 1.0)**4).mean())
    per_seed['dens6'] = float((I > 6).mean()) / L
    per_seed['maxI'] = float(I.max())
    per_seed['mass'] = float(diag['mass'])
    per_seed['wall_s'] = time.time() - t0
    return per_seed

# ----------------------------------------------------------------------------
def main():
    from colony_lib.persistence import StageTracker
    tr = StageTracker('c37_growth_scan')
    n_workers = min(4, os.cpu_count() or 1)
    print(f"[C37] growth scan start: dx={DX:.6f} dt={DT} T={T_END} "
          f"t_trans={T_TRANS} eps={EPS} seeds={SEEDS[0]}..{SEEDS[-1]} "
          f"workers={n_workers}", flush=True)

    summary = {}
    for (L, N), key in zip(CONFIGS, KEYS):
        if tr.is_done(key):
            summary[key] = tr.get_stage(key)
            print(f"[C37] {key}: checkpoint hit, skipped.", flush=True)
            continue
        print(f"[C37] {key}: N={N} L={L} dx={L/N:.10f} — running {len(SEEDS)} seeds",
              flush=True)
        t_cfg = time.time()
        with __import__('multiprocessing').Pool(n_workers) as pool:
            results = pool.map(_run_seed, [(L, N, s) for s in SEEDS])
        n_samp = int(round((T_END - T_TRANS)/0.5)) * N   # samples per seed

        cfg = {'N': N, 'L': L, 'dx': L/N, 'n_seeds': len(SEEDS), 'bins': {}}
        rats = np.array([[r['ratios'][s] for s in S_LIST] for r in results])
        for j, s in enumerate(S_LIST):
            rr = rats[:, j]
            mean = float(rr.mean()); sd = float(rr.std(ddof=1))
            sig = (mean - 1.0)/sd if sd > 0 else 0.0
            exp_null = math.exp(-s)
            starved = exp_null * n_samp < 20.0
            sig_p = float(np.mean([r['poisson_sig'][s] for r in results]))
            cfg['bins'][str(s)] = dict(
                ratio=mean, sd=sd, sig=sig, sig_poisson=sig_p,
                starved=bool(starved))
        cfg['kurt']  = dict(mean=float(np.mean([r['kurt'] for r in results])),
                            sd=float(np.std([r['kurt'] for r in results], ddof=1)))
        cfg['dens6'] = dict(mean=float(np.mean([r['dens6'] for r in results])),
                            sd=float(np.std([r['dens6'] for r in results], ddof=1)))
        cfg['maxI']  = float(np.max([r['maxI'] for r in results]))
        cfg['mass']  = float(np.mean([r['mass'] for r in results]))
        cfg['wall_s'] = time.time() - t_cfg
        summary[key] = cfg
        tr.save_stage(key, cfg)
        print(f"[C37] {key}: done in {cfg['wall_s']:.0f}s — "
              f"kurt={cfg['kurt']['mean']:.4f} dens6={cfg['dens6']['mean']:.4f} "
              f"maxI={cfg['maxI']:.2f}", flush=True)
        # incremental partial save
        with open('c37_summary.json', 'w') as f:
            json.dump(summary, f, indent=1)

    tr.save_stage('final', summary)
    with open('c37_summary.json', 'w') as f:
        json.dump(summary, f, indent=1)

    # ---------------- plot ----------------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = plt.cm.viridis(np.linspace(0.08, 0.92, len(KEYS)))
    for (key, c) in zip(KEYS, colors):
        cfg = summary[key]
        ss = np.array([int(k) for k in cfg['bins'].keys()])
        rr = np.array([cfg['bins'][k]['ratio'] for k in cfg['bins'].keys()])
        dd = np.array([cfg['bins'][k]['sd'] for k in cfg['bins'].keys()])
        ax.errorbar(ss, rr, yerr=dd, label=f"{key} (N={cfg['N']})",
                    color=c, marker='o', ms=4, lw=1.4, capsize=2, alpha=0.9)
    ax.axhline(1.0, color='gray', lw=1.0, ls='--')
    ax.set_xlabel('threshold s (intensity)')
    ax.set_ylabel('tail ratio  P(I>s) / e^{-s}   (mean over 12 seeds, ±SD)')
    ax.set_title(f"C37 GROWTH SCAN — fixed dx={DX:.4f}, dt={DT}, eps={EPS}, "
                 f"t>=50, seeds 1-12\nH-FTG: s* recedes with L | H-power-law: "
                 f"no return, blowup | H-saturated: collapse across all L")
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig('d37_growth_scan.png', dpi=140)

    print("[C37] COMPLETE. summary=c37_summary.json plot=d37_growth_scan.png",
          flush=True)

if __name__ == '__main__':
    main()
