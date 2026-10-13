"""
DISCOVERY 029 (World C): Integrable turbulence and rogue-wave statistics
in the focusing NLS:  i psi_t + psi_xx + 2 |psi|^2 psi = 0
Transport-safe edition: no double-star operators anywhere (use x*x).
Split-step Fourier (Strang) integrator, ensemble statistics.
"""
import numpy as np, json, time, os, sys
import multiprocessing as mp

def intensity(psi):
    # |psi|^2 without the power operator
    return psi.real * psi.real + psi.imag * psi.imag

def run_realization(args):
    (seed, N, L, dt, T, eps) = args
    try:
        dx = L / N
        x = np.arange(N) * dx
        k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
        K2 = k * k
        lin_half = np.exp(-0.5j * K2 * dt)
        nsteps = int(round(T / dt))
        rng = np.random.default_rng(seed)
        psi = np.ones(N, dtype=complex)
        psi += eps * (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)

        bins = np.linspace(0, 60, 241)
        hist = np.zeros(len(bins) - 1)
        kurt_t, kurt_v = [], []
        win_max = []
        wcur = 0.0
        top_events = []
        a0 = np.abs(np.fft.fft(psi))
        spectra = {0: (a0 * a0).tolist()}
        mass0 = intensity(psi).mean()
        mass_max_dev = 0.0
        kymo_rows = []
        wstep = max(1, int(round(4.0 / dt)))
        for n in range(1, nsteps + 1):
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            psi *= np.exp(2j * dt * intensity(psi))
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            t = n * dt
            if n % 50 == 0:
                I = intensity(psi)
                m1 = I.mean()
                m2 = (I * I).mean()
                kurt_t.append(t)
                kurt_v.append(m2 / (m1 * m1))
                mass_max_dev = max(mass_max_dev, abs(m1 - mass0))
            if t >= 40:
                I = intensity(psi)
                if n % 20 == 0:
                    h, _ = np.histogram(I, bins=bins)
                    hist += h
                wcur = max(wcur, I.max())
                if n % wstep == 0:
                    win_max.append(wcur)
                    wcur = 0.0
                im = int(I.argmax())
                if len(top_events) < 5 or I[im] > top_events[0][0]:
                    top_events = sorted(top_events + [(float(I[im]), float(t), float(x[im]))])[-5:]
            for st in (5, 15, 40, 100):
                if abs(t - st) < dt / 2 and st not in spectra:
                    a = np.abs(np.fft.fft(psi))
                    spectra[st] = (a * a).tolist()
            if N == 2048 and n % 400 == 0 and len(kymo_rows) < 250:
                kymo_rows.append(intensity(psi).copy().tolist())
        return {'ok': True, 'seed': seed, 'N': N, 'L': L, 'eps': eps,
                'hist': hist.tolist(), 'bins': bins.tolist(),
                'kurt_t': kurt_t, 'kurt_v': kurt_v,
                'win_max': win_max, 'top_events': top_events,
                'spectra': spectra, 'mass_dev': mass_max_dev,
                'kymo': kymo_rows}
    except Exception as e:
        import traceback
        return {'ok': False, 'seed': seed, 'err': repr(e), 'tb': traceback.format_exc()[-400:]}

def aggregate(results):
    ag = {}
    rs = [r for r in results if r.get('ok')]
    ag['rs'] = rs
    ag['n_ok'] = len(rs)
    if rs:
        ag['kt'] = rs[0]['kurt_t']
        ag['kurt'] = np.array([r['kurt_v'] for r in rs])
        hist = np.zeros(len(rs[0]['hist']))
        for r in rs:
            hist += np.array(r['hist'])
        ag['hist'] = hist
        ag['wm'] = np.concatenate([np.array(r['win_max']) for r in rs])
        ag['specs'] = {}
        for key in (0, 5, 15, 40, 100):
            if all(key in r['spectra'] for r in rs):
                ag['specs'][key] = np.mean([np.array(r['spectra'][key]) for r in rs], axis=0)
        ag['massdev'] = max(r['mass_dev'] for r in rs)
        tops = []
        for r in rs:
            tops += list(r['top_events'])
        ag['tops'] = sorted(tops)[::-1]
    return ag

def main():
    t0 = time.time()
    env = os.environ
    NA = int(env.get('IT_NA', 1024)); LA = float(env.get('IT_LA', 100.0))
    dtA = float(env.get('IT_DTA', 1e-3)); TA = float(env.get('IT_TA', 100.0))
    nA = int(env.get('IT_NREAL', 40))
    NB = int(env.get('IT_NB', NA)); LB = LA; dtB = dtA; TB = TA; nB = nA
    NC = int(env.get('IT_NC', 2048)); LC = float(env.get('IT_LC', 200.0))
    dtC = float(env.get('IT_DTC', 5e-4)); TC = TA; nC = max(1, nA // 3)
    cfgA = [(1000 + i, NA, LA, dtA, TA, 0.05) for i in range(nA)]
    cfgB = [(2000 + i, NB, LB, dtB, TB, 0.20) for i in range(nB)]
    cfgC = [(3000 + i, NC, LC, dtC, TC, 0.10) for i in range(nC)]
    jobs = cfgA + cfgB + cfgC
    nproc = min(8, mp.cpu_count())
    with mp.Pool(nproc) as pool:
        results = pool.map(run_realization, jobs)
    A = aggregate([r for r, j in zip(results, jobs) if j[1] == NA and j[2] == LA and j[5] == 0.05])
    B = aggregate([r for r, j in zip(results, jobs) if j[1] == NB and j[2] == LB and j[5] == 0.20])
    C = aggregate([r for r, j in zip(results, jobs) if j[1] == NC])
    print('elapsed', round(time.time() - t0, 1), 's | ok counts:', A['n_ok'], B['n_ok'], C['n_ok'])
    for r in results:
        if not r.get('ok'):
            print('FAILED seed', r['seed'], r['err'])

    if A['n_ok'] == 0:
        print('NO REALIZATIONS SURVIVED - aborting analysis')
        return
    kc = 0.5 * (np.array(A['rs'][0]['bins'][:-1]) + np.array(A['rs'][0]['bins'][1:]))
    totA = float(A['hist'].sum())
    pA = A['hist'] / totA / (kc[1] - kc[0]) if totA > 0 else np.zeros(len(kc))
    totB = float(B['hist'].sum())
    pB = B['hist'] / totB / (kc[1] - kc[0]) if totB > 0 else np.zeros(len(kc))
    totC = float(C['hist'].sum())
    pC = C['hist'] / totC / (kc[1] - kc[0]) if totC > 0 else np.zeros(len(kc))
    meanI_A = np.sum(kc * pA) * (kc[1] - kc[0]) if totA > 0 else 1.0
    ray = np.exp(-kc / meanI_A) / meanI_A

    def enh(p, i0):
        m = (kc > i0 - 0.5) & (kc < i0 + 0.5)
        mm = (kc > i0 - 1.5) & (kc < i0 - 0.5)
        if p[m].sum() <= 0 or ray[mm].sum() <= 0:
            return 0.0
        return float(p[m].sum() / ray[m].sum())

    def rate(wm, thr, L, TA=100.0):
        return float((wm > thr).sum() / (max(1.0, TA - 40.0) * L))

    stats = {
        'n_realizations': {'A': A['n_ok'], 'B': B['n_ok'], 'C': C['n_ok']},
        'kurtosis_final': {'A': float(A['kurt'][:, -1].mean()), 'B': float(B['kurt'][:, -1].mean()), 'C': float(C['kurt'][:, -1].mean())},
        'kurtosis_peak': {'A': float(A['kurt'].max()), 'B': float(B['kurt'].max()), 'C': float(C['kurt'].max())},
        'enhancement_at_9': {'A': enh(pA, 9), 'B': enh(pB, 9), 'C': enh(pC, 9)},
        'enhancement_at_25': {'A': enh(pA, 25), 'B': enh(pB, 25), 'C': enh(pC, 25)},
        'rate_gt9_perTL': {'A': rate(A['wm'], 9, LA), 'B': rate(B['wm'], 9, LB), 'C': rate(C['wm'], 9, LC)},
        'rate_gt16_perTL': {'A': rate(A['wm'], 16, LA), 'B': rate(B['wm'], 16, LB), 'C': rate(C['wm'], 16, LC)},
        'rate_gt25_perTL': {'A': rate(A['wm'], 25, LA), 'B': rate(B['wm'], 25, LB), 'C': rate(C['wm'], 25, LC)},
        'global_max': {'A': float(A['wm'].max()) if len(A['wm']) else 0.0, 'B': float(B['wm'].max()) if len(B['wm']) else 0.0, 'C': float(C['wm'].max()) if len(C['wm']) else 0.0},
        'meanI_hist': float(meanI_A),
        'mass_dev_max': {'A': A['massdev'], 'B': B['massdev'], 'C': C['massdev']},
        'n_window_maxima': {'A': len(A['wm']), 'B': len(B['wm']), 'C': len(C['wm'])},
        'top10_events': [(round(v, 2), round(t, 1), round(xx, 2)) for (v, t, xx) in A['tops'][:10]],
    }
    kk = 2 * np.pi * np.fft.fftfreq(NA, d=LA / NA)
    spec = A['specs'].get(100)
    m = (kk > 2) & (kk < 10)
    if spec is not None and len(spec) == len(kk) and m.sum() > 5:
        stats['saturated_spectrum_slope_k2_10'] = float(np.polyfit(np.log(kk[m]), np.log(spec[m] + 1e-30), 1)[0])

    json.dump(stats, open('it_turbulence_stats.json', 'w'), indent=1)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax = axes[0, 0]
    if C['rs'] and C['rs'][0]['kymo']:
        ky = np.array(C['rs'][0]['kymo'])
        ax.imshow(ky, aspect='auto', origin='lower', cmap='inferno', extent=[0, LC, 0, TC])
        ax.set_title('sample kymograph |psi|^2 (config C)')
    ax.set_xlabel('x')
    ax.set_ylabel('t')
    ax = axes[0, 1]
    ax.plot(A['kt'], A['kurt'].mean(0), label='A eps=0.05 (' + str(len(A['rs'])) + ' real.)')
    ax.fill_between(A['kt'], A['kurt'].mean(0) - A['kurt'].std(0), A['kurt'].mean(0) + A['kurt'].std(0), alpha=0.25)
    ax.plot(B['kt'], B['kurt'].mean(0), label='B eps=0.20')
    ax.plot(C['kt'], C['kurt'].mean(0), label='C L=200')
    ax.axhline(2, color='k', ls='--', lw=1, label='Gaussian (=2)')
    ax.set_xlabel('t')
    ax.set_ylabel('kurtosis of I')
    ax.legend()
    ax.set_title('Intermittency: ensemble kurtosis')
    ax = axes[1, 0]
    ax.semilogy(kc, pA, lw=1.6, label='A: eps=0.05')
    ax.semilogy(kc, pB, lw=1.6, label='B: eps=0.20')
    ax.semilogy(kc, pC, lw=1.6, label='C: L=200')
    ax.semilogy(kc, ray, 'k--', lw=1.4, label='exponential fit')
    for thr, nm in ((9, 'Peregrine 9'), (25, 'order-2: 25')):
        ax.axvline(thr, color='r', ls=':', alpha=0.7)
        ax.text(thr, max(1e-4, float(ray.max())) * 0.5, nm, rotation=90, fontsize=8, color='r')
    ax.set_xlabel('|psi|^2')
    ax.set_ylabel('PDF')
    ax.legend()
    ax.set_title('Saturated-phase PDF vs exponential (tail enhancement at I=9: x' + str(round(stats['enhancement_at_9']['A'], 1)) + ')')
    ax = axes[1, 1]
    for nm, D in (('A', A['wm']), ('B', B['wm']), ('C', C['wm'])):
        s = np.sort(D)[::-1]
        ax.step(np.arange(1, len(s) + 1), s, where='post', label=nm, lw=1.2)
    for v in (9, 25, 49):
        ax.axhline(v, color='r', ls=':', alpha=0.6)
        ax.text(max(1, len(A['wm'])) * 0.7, v + 0.5, 'ladder ' + str(v), fontsize=8, color='r')
    ax.set_xlabel('rank')
    ax.set_ylabel('window max |psi|^2')
    ax.legend()
    ax.set_title('Rank-ordered window maxima vs rogue ladder')
    plt.tight_layout()
    plt.savefig('it_turbulence_overview.png', dpi=110)

    fig, ax = plt.subplots(figsize=(8, 6))
    for skey, lbl in ((0, 't=0'), (5, 't=5'), (15, 't=15'), (40, 't=40'), (100, 't=100')):
        if skey not in A['specs']:
            continue
        ax.loglog(kk, A['specs'][skey] + 1e-30, lw=1.1, label=lbl)
    ax.set_xlabel('k')
    ax.set_ylabel('spectral power')
    ax.legend()
    ax.set_title('Spectral evolution (config A ensemble mean)')
    plt.tight_layout()
    plt.savefig('it_spectrum_evolution.png', dpi=110)

    print(json.dumps(stats, indent=1)[:3000])
    print('saved: it_turbulence_overview.png, it_spectrum_evolution.png, it_turbulence_stats.json')

if __name__ == '__main__':
    main()
