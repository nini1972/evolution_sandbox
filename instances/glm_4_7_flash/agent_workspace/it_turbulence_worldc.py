"""
DISCOVERY 029 (World C): Integrable turbulence & rogue-wave statistics in
the focusing NLS  i psi_t + psi_xx + 2|psi|^2 psi = 0.

Ensemble study:
  A) N=1024, L=100, eps=0.05, 40 realizations, T=100  (weak seed)
  B) N=1024, L=100, eps=0.20, 40 realizations, T=100  (strong seed)
  C) N=2048, L=200, eps=0.10, 12 realizations, T=100  (double domain)

Questions:
 1. PDF of |psi|^2 in the saturated regime vs Rayleigh/exponential: tail enhancement.
 2. Do peaks approach higher-order rogue-wave intensities (1+2n)^2 = 9, 25, 49?
 3. Is the saturated statistics seed-independent (A vs B)?
 4. Extensivity: is the rogue-event rate per (time x length) constant (A vs C)?
 5. Spectral evolution: power law of saturated spectrum.
 6. Kurtosis (intermittency) dynamics; mass conservation check.
"""
import numpy as np, json, time, os, sys
import multiprocessing as mp

def run_realization(args):
    (seed, N, L, dt, T, eps) = args
    try:
        dx = L / N
        x = np.arange(N) * dx
        k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
        K2 = k * k
        lin_half = np.exp(-1j * K2 * dt / 2)
        nsteps = int(T / dt)
        rng = np.random.default_rng(seed)
        psi = np.ones(N, dtype=complex)
        psi += eps * (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)

        # histogram of |psi|^2 over saturated phase t in [40, T]
        bins = np.linspace(0, 45, 181)
        hist = np.zeros(len(bins) - 1)
        kurt_t, kurt_v = [], []
        win_max = []          # window maxima (dt_win = 4, over t in [40, T])
        wcur = 0.0
        top_events = []       # (value, t, x)
        spectra = {}          # snapshots of |fft(psi)|^2
        snap_times = [0, 5, 15, 40, 100]
        mass0 = np.mean(np.abs(psi) ** 2)
        mass_max_dev = 0.0
        kymo_rows = []
        for n in range(1, nsteps + 1):
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            psi *= np.exp(1j * 2.0 * np.abs(psi) ** 2 * dt)
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            t = n * dt
            if n % 50 == 0:
                I = np.abs(psi) ** 2
                m1 = I.mean(); m2 = (I ** 2).mean()
                kurt_t.append(t); kurt_v.append(m2 / m1 ** 2)
                mass_max_dev = max(mass_max_dev, abs(m1 - mass0))
            if t >= 40:
                I = np.abs(psi) ** 2
                if n % 20 == 0:
                    h, _ = np.histogram(I, bins=bins)
                    hist += h
                wcur = max(wcur, I.max())
                if n % int(4 / dt) == 0:
                    win_max.append(wcur); wcur = 0.0
                im = I.argmax()
                if len(top_events) < 5 or I[im] > top_events[0][0]:
                    top_events = sorted(top_events + [(float(I[im]), float(t), float(x[im]))])[-5:]
            for st in snap_times:
                if abs(t - st) < dt / 2 and st not in spectra:
                    spectra[st] = np.abs(np.fft.fft(psi)) ** 2
            if N == 2048 and n % 400 == 0 and len(kymo_rows) < 250:
                kymo_rows.append(np.abs(psi.copy()) ** 2)
        return {'ok': True, 'seed': seed, 'N': N, 'L': L, 'eps': eps,
                'hist': hist.tolist(), 'bins': bins.tolist(),
                'kurt_t': kurt_t, 'kurt_v': kurt_v,
                'win_max': win_max, 'top_events': top_events,
                'spectra': {str(s): v.tolist() for s, v in spectra.items()},
                'mass_dev': mass_max_dev,
                'kymo': (np.array(kymo_rows).tolist() if kymo_rows else [])}
    except Exception as e:
        return {'ok': False, 'seed': seed, 'err': repr(e)}

def main():
    t0 = time.time()
    cfgA = [(1000 + i, 1024, 100.0, 1e-3, 100.0, 0.05) for i in range(40)]
    cfgB = [(2000 + i, 1024, 100.0, 1e-3, 100.0, 0.20) for i in range(40)]
    cfgC = [(3000 + i, 2048, 200.0, 5e-4, 100.0, 0.10) for i in range(12)]
    jobs = cfgA + cfgB + cfgC
    results = []
    nproc = min(8, mp.cpu_count())
    print(f"cpu_count={mp.cpu_count()}, using {nproc} workers, {len(jobs)} realizations")
    try:
        with mp.Pool(nproc) as pool:
            results = pool.map(run_realization, jobs)
    except Exception as e:
        print("pool failed, sequential:", e)
        results = [run_realization(j) for j in jobs]
    ok = [r for r in results if r.get('ok')]
    print(f"done {len(ok)}/{len(results)} realizations in {time.time()-t0:.0f}s")

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    def agg(cfg, Nv, Lv, epsv):
        rs = [r for r in ok if r['N'] == Nv and abs(r['eps'] - epsv) < 1e-9]
        hist = np.sum([np.array(r['hist']) for r in rs], axis=0)
        bins = np.array(rs[0]['bins'])
        kc = np.array(rs[0]['bins'][:-1]) + 0.5 * (bins[1] - bins[0])
        kurt = np.array([r['kurt_v'] for r in rs])
        kt = np.array(rs[0]['kurt_t'])
        wm = np.concatenate([np.array(r['win_max']) for r in rs])
        specs = {}
        for skey in ['0', '5', '15', '40', '100']:
            specs[skey] = np.mean([np.array(r['spectra'][skey]) for r in rs], axis=0)
        tops = sorted([ev for r in rs for ev in r['top_events']], reverse=True)[:10]
        massdev = max(r['mass_dev'] for r in rs)
        return dict(rs=rs, hist=hist, kc=kc, kurt=kurt, kt=kt, wm=wm, specs=specs,
                    tops=tops, massdev=massdev)

    A = agg(0, 1024, 100, 0.05); B = agg(0, 1024, 100, 0.20); C = agg(0, 2048, 200, 0.10)
    L_A, L_B, L_C = 100.0, 100.0, 200.0

    # ---- PDF analysis ----
    def norm_pdf(agg):
        h = agg['hist'].astype(float); c = h.sum() * (agg['kc'][1] - agg['kc'][0])
        return h / c
    pA, pB, pC = norm_pdf(A), norm_pdf(B), norm_pdf(C)
    kc = A['kc']
    meanI_A = (kc * pA).sum() * (kc[1] - kc[0])
    ray = np.exp(-kc / meanI_A) / meanI_A

    # enhancement at I=9 and I=25
    def enh(p, thr):
        i = np.searchsorted(kc, thr)
        return float(p[i] / ray[i]) if i < len(kc) and ray[i] > 0 else float('nan')

    # ---- extreme stats ----
    def rate(wm, thr, L, Tstat=60.0, nreal=None):
        return float((wm > thr).sum()) / (Tstat * L)
    stats = {
        'kurtosis_final': {'A': float(A['kurt'][:, -1].mean()), 'B': float(B['kurt'][:, -1].mean()), 'C': float(C['kurt'][:, -1].mean())},
        'kurtosis_max':   {'A': float(A['kurt'].max(axis=1).mean()), 'B': float(B['kurt'].max(axis=1).mean()), 'C': float(C['kurt'].max(axis=1).mean())},
        'enhancement_at_9':  {'A': enh(pA, 9),  'B': enh(pB, 9),  'C': enh(pC, 9)},
        'enhancement_at_25': {'A': enh(pA, 25), 'B': enh(pB, 25), 'C': enh(pC, 25)},
        'rate_per_t_len_gt9':  {'A': rate(A['wm'], 9, L_A),  'B': rate(B['wm'], 9, L_B),  'C': rate(C['wm'], 9, L_C)},
        'rate_per_t_len_gt16': {'A': rate(A['wm'], 16, L_A), 'B': rate(B['wm'], 16, L_B), 'C': rate(C['wm'], 16, L_C)},
        'rate_per_t_len_gt25': {'A': rate(A['wm'], 25, L_A), 'B': rate(B['wm'], 25, L_B), 'C': rate(C['wm'], 25, L_C)},
        'global_max': {'A': float(A['wm'].max()), 'B': float(B['wm'].max()), 'C': float(C['wm'].max())},
        'meanI_hist': float(meanI_A),
        'mass_dev_max': {'A': A['massdev'], 'B': B['massdev'], 'C': C['massdev']},
        'n_window_maxima': {'A': len(A['wm']), 'B': len(B['wm']), 'C': len(C['wm'])},
        'top10_events': A['tops'][:10],
    }
    # spectral slope fit on saturated spectrum (t=100), k in [2,10]
    kk = 2 * np.pi * np.fft.fftfreq(1024, d=100.0 / 1024)
    spec = A['specs']['100']
    m = (kk > 2) & (kk < 10)
    if m.sum() > 5:
        slope = np.polyfit(np.log(kk[m]), np.log(spec[m] + 1e-30), 1)[0]
        stats['saturated_spectrum_slope_k2_10'] = float(slope)

    json.dump(stats, open('it_turbulence_stats.json', 'w'), indent=1)

    # ---- FIG 1: overview ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax = axes[0, 0]
    if A['rs'][0].get('kymo'):
        ky = np.array(A['rs'][0]['kymo'])
        ax.imshow(ky, aspect='auto', origin='lower', cmap='inferno', extent=[0, 100, 0, 100])
        ax.set_title('sample kymograph |psi|^2 (config C realization)')
    ax.set_xlabel('x'); ax.set_ylabel('t')
    ax = axes[0, 1]
    ax.plot(A['kt'], A['kurt'].mean(0), label=f"A eps=0.05 ({len(A['rs'])} real.)")
    ax.fill_between(A['kt'], A['kurt'].mean(0) - A['kurt'].std(0), A['kurt'].mean(0) + A['kurt'].std(0), alpha=0.25)
    ax.plot(B['kt'], B['kurt'].mean(0), label=f"B eps=0.20 ({len(B['rs'])})")
    ax.plot(C['kt'], C['kurt'].mean(0), label=f"C L=200 ({len(C['rs'])})")
    ax.axhline(2, color='k', ls='--', lw=1, label='Gaussian field (=2)')
    ax.set_xlabel('t'); ax.set_ylabel('kurtosis  <I^2>/<I>^2'); ax.legend(); ax.set_title('Intermittency: ensemble kurtosis')
    ax = axes[1, 0]
    ax.semilogy(kc, pA, lw=1.6, label='A: eps=0.05')
    ax.semilogy(kc, pB, lw=1.6, label='B: eps=0.20')
    ax.semilogy(kc, pC, lw=1.6, label='C: L=200')
    ax.semilogy(kc, ray, 'k--', lw=1.4, label='Rayleigh/exponential')
    for thr, nm in [(9, 'Peregrine 9'), (25, '2nd order 25')]:
        ax.axvline(thr, color='r', ls=':', alpha=0.7)
        ax.text(thr, ray.max() * 0.5, nm, rotation=90, fontsize=8, color='r')
    ax.set_xlabel('|psi|^2'); ax.set_ylabel('PDF'); ax.legend()
    ax.set_title(f'Saturated-phase PDF: tail enhancement x{stats["enhancement_at_9"]["A"]:.0f} at I=9')
    ax = axes[1, 1]
    for nm, D in [('A', A['wm']), ('B', B['wm']), ('C', C['wm'])]:
        s = np.sort(D)[::-1]
        ax.step(np.arange(1, len(s) + 1), s, where='post', label=nm, lw=1.2)
    for v in [9, 25, 49]:
        ax.axhline(v, color='r', ls=':', alpha=0.6)
        ax.text(len(A['wm']) * 0.7, v + 0.5, f'(1+2n)^2={v}', fontsize=8, color='r')
    ax.set_xlabel('rank'); ax.set_ylabel('window max |psi|^2'); ax.legend()
    ax.set_title('Rank-ordered window maxima vs rogue-wave ladder')
    plt.tight_layout(); plt.savefig('it_turbulence_overview.png', dpi=110)

    # ---- FIG 2: spectra ----
    fig, ax = plt.subplots(figsize=(8, 6))
    for skey, lbl in [('0', 't=0'), ('5', 't=5'), ('15', 't=15'), ('40', 't=40'), ('100', 't=100')]:
        ax.loglog(kk, A['specs'][skey] + 1e-30, lw=1.1, label=lbl)
    ax.set_xlabel('k'); ax.set_ylabel('|psi_k|^2'); ax.legend(); ax.set_title('Spectral evolution (config A ensemble mean)')
    plt.tight_layout(); plt.savefig('it_spectrum_evolution.png', dpi=110)

    print(json.dumps(stats, indent=1)[:2500])
    print("saved: it_turbulence_overview.png, it_spectrum_evolution.png, it_turbulence_stats.json")

if __name__ == '__main__':
    main()
