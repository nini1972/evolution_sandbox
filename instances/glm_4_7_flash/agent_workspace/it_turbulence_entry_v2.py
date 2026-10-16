# World C job v2: integrable turbulence / rogue-wave statistics, focusing NLS
# i psi_t + psi_xx + 2|psi|^2 psi = 0. Strang split-step Fourier, ensemble stats.
# v2 vs v1 (timed out 3600s, no artifacts): guard-clock chunked execution,
# per-config JSON checkpoints, analysis on partial data, trimmed IPC payloads.
import os, time, json, sys
import numpy as np
import multiprocessing as mp

T0 = time.time()
GUARD = float(os.environ.get('IT_GUARD', '2400'))
CH = int(os.environ.get('IT_CHUNK', '16'))

def say(msg):
    print('[IT ' + str(round(time.time() - T0, 1)) + 's] ' + str(msg)); sys.stdout.flush()

def intensity(psi):
    return psi.real * psi.real + psi.imag * psi.imag

def run_realization(args):
    (seed, N, L, dt, T, eps, keep_spec, keep_kymo) = args
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
        spectra = {}
        if keep_spec:
            a0 = np.abs(np.fft.fft(psi))
            spectra[0] = (a0 * a0).tolist()
        mass0 = intensity(psi).mean()
        mass_max_dev = 0.0
        kymo_rows = []
        wstep = max(1, int(round(4.0 / dt)))
        for n in range(1, nsteps + 1):
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            psi *= np.exp(2j * dt * intensity(psi))
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            t = n * dt
            I = None
            if n % 50 == 0:
                I = intensity(psi)
                m1 = I.mean()
                m2 = (I * I).mean()
                kurt_t.append(t)
                kurt_v.append(m2 / (m1 * m1))
                mass_max_dev = max(mass_max_dev, abs(m1 - mass0))
            if t >= 40:
                if I is None:
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
            if keep_spec:
                for st in (5, 15, 40, 100):
                    if abs(t - st) < dt / 2 and st not in spectra:
                        a = np.abs(np.fft.fft(psi))
                        spectra[st] = (a * a).tolist()
            if keep_kymo and n % 400 == 0 and len(kymo_rows) < 250:
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
        ag['bins'] = np.array(rs[0]['bins'])
        ag['hist'] = np.sum([np.array(r['hist']) for r in rs], axis=0)
        ag['wm'] = np.array([w for r in rs for w in r['win_max']])
        ag['tops'] = [ev for r in rs for ev in r['top_events']]
        ag['tops'].sort(key=lambda ev: ev[0])
        ag['massdev'] = float(np.max([r['mass_dev'] for r in rs]))
    else:
        ag['kt'] = []; ag['kurt'] = np.zeros((0, 0))
        ag['bins'] = np.zeros(0); ag['hist'] = np.zeros(0)
        ag['wm'] = np.zeros(0); ag['tops'] = []; ag['massdev'] = None
    ag['wall'] = round(time.time() - T0, 1)
    return ag

def run_config(name, jobs, pool):
    say('config ' + name + ': ' + str(len(jobs)) + ' realizations')
    results = []
    i = 0
    while i < len(jobs):
        if time.time() - T0 > GUARD:
            say('GUARD hit in ' + name + ' after ' + str(len(results)) + ' results; degrade')
            break
        chunk = jobs[i:i + CH]
        try:
            if pool is not None:
                ars = [pool.apply_async(run_realization, (j,)) for j in chunk]
                got = [a.get(timeout=600) for a in ars]
            else:
                got = []
                for j in chunk:
                    if time.time() - T0 > GUARD:
                        break
                    got.append(run_realization(j))
        except mp.TimeoutError:
            say('async timeout chunk ' + name + ' #' + str(i) + '; skip')
            got = []
        except Exception as e:
            say('pool chunk fail ' + name + ' #' + str(i) + ': ' + repr(e) + ' -> serial fallback')
            pool = None
            got = []
            for j in chunk:
                if time.time() - T0 > GUARD:
                    break
                got.append(run_realization(j))
        results.extend(got)
        nok = sum(1 for r in got if r.get('ok'))
        i += CH
        say(name + ' chunk done: ' + str(nok) + '/' + str(len(chunk)) + ' ok, total ' + str(sum(1 for r in results if r.get('ok'))))
    ag = aggregate(results)
    say('config ' + name + ' done: n_ok=' + str(ag['n_ok']) + ' wall=' + str(ag['wall']) + 's')
    try:
        cp = {'name': name, 'n_ok': ag['n_ok'], 'wall': ag['wall'],
              'guard_hit': time.time() - T0 > GUARD}
        if ag['n_ok']:
            cp['hist'] = ag['hist'].tolist()
            cp['bins'] = ag['bins'].tolist()
            cp['kt'] = ag['kt']
            cp['kurt_mean'] = ag['kurt'].mean(axis=0).tolist()
            cp['kurt_std'] = ag['kurt'].std(axis=0).tolist()
            cp['wm'] = ag['wm'].tolist()
            cp['massdev'] = ag['massdev']
            cp['tops'] = [[round(v, 2), round(s, 1), round(xx, 2)] for (v, s, xx) in ag['tops'][-10:]]
        json.dump(cp, open('it_checkpoint_' + name + '.json', 'w'))
        say('checkpoint ' + name + ' saved')
    except Exception as e:
        say('checkpoint fail ' + name + ': ' + repr(e))
    return ag, pool

def main():
    say('entry v2 start: guard=' + str(GUARD) + 's chunk=' + str(CH) + ' cpus=' + str(mp.cpu_count()))
    NA = int(os.environ.get('IT_NA', '1024')); LA = float(os.environ.get('IT_LA', '100.0'))
    dtA = float(os.environ.get('IT_DTA', '1e-3')); TA = float(os.environ.get('IT_TA', '100.0'))
    nA = int(os.environ.get('IT_NREAL_A', '96'))
    nB = int(os.environ.get('IT_NREAL_B', '96'))
    NC = int(os.environ.get('IT_NC', '2048')); LC = float(os.environ.get('IT_LC', '200.0'))
    dtC = float(os.environ.get('IT_DTC', '5e-4')); nCr = int(os.environ.get('IT_NREAL_C', '24'))
    jobsA = [(1000 + i, NA, LA, dtA, TA, 0.05, False, False) for i in range(nA)]
    jobsB = [(2000 + i, NA, LA, dtA, TA, 0.20, False, False) for i in range(nB)]
    jobsC = [(3000 + i, NC, LC, dtC, TA, 0.10, (i == 0), (i == 0)) for i in range(nCr)]
    pool = None
    try:
        nw = min(4, mp.cpu_count())
        pool = mp.Pool(nw)
        say('pool started with ' + str(nw) + ' workers')
    except Exception as e:
        say('pool create failed ' + repr(e) + ' -> serial')
        pool = None
    t1 = time.time()
    A, pool = run_config('A', jobsA, pool)
    paceA = (time.time() - t1) / max(1, A['n_ok'])
    say('pace A: ' + str(round(paceA, 2)) + 's/real (wall)')
    t2 = time.time()
    B, pool = run_config('B', jobsB, pool)
    paceB = (time.time() - t2) / max(1, B['n_ok'])
    say('pace B: ' + str(round(paceB, 2)) + 's/real (wall)')
    paceC = paceA * (NC / NA) * (dtA / dtC) * 1.15
    rem = GUARD - (time.time() - T0) - 420
    nfit = int(rem / max(1e-9, paceC)) if paceC > 0 else nCr
    if nfit < len(jobsC):
        say('guard trim C: ' + str(len(jobsC)) + ' -> ' + str(max(2, nfit)) + ' (paceC~' + str(round(paceC, 1)) + 's)')
        jobsC = jobsC[:max(2, nfit)]
    t3 = time.time()
    C, pool = run_config('C', jobsC, pool)
    paceC_real = (time.time() - t3) / max(1, C['n_ok'])
    say('pace C: ' + str(round(paceC_real, 2)) + 's/real (wall)')
    if pool is not None:
        try:
            pool.close(); pool.join()
        except Exception as e:
            say('pool close fail ' + repr(e))
    return A, B, C, paceA, paceB, paceC_real

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def analyze(A, B, C, paceA, paceB, paceC_real):
    stats = {'meta': {'guard': GUARD, 'wall': round(time.time() - T0, 1),
                      'paceA': round(paceA, 2), 'paceB': round(paceB, 2), 'paceC': round(paceC_real, 2),
                      'nA': A['n_ok'], 'nB': B['n_ok'], 'nC': C['n_ok']}}
    for nm, ag, L in (('A', A, 100.0), ('B', B, 100.0), ('C', C, 200.0)):
        s = {}
        if ag['n_ok']:
            bins = ag['bins']
            h = ag['hist']
            c = 0.5 * (bins[:-1] + bins[1:])
            s['enh'] = {}
            if h.sum() > 0 and ag['wm'].size > 0:
                Ibar = float((c * h).sum() / float(h.sum()))
                pdf = h / (h.sum() * (bins[1] - bins[0]))
                s['pdf'] = pdf.tolist(); s['c'] = c.tolist(); s['meanI'] = Ibar
                y = c / Ibar
                py = Ibar * pdf
                ry = np.exp(-y)
                for thr in (8, 9, 16):
                    s['enh'][str(thr)] = float(np.interp(thr, y, py) / max(1e-300, np.interp(thr, y, ry)))
            else:
                s['pdf'] = []; s['c'] = []; s['meanI'] = None
            kt = np.array(ag['kt'])
            km = ag['kurt'].mean(axis=0)
            s['kurt_at_40'] = float(km[np.argmin(np.abs(kt - 40))]) if kt.size else None
            s['kurt_at_100'] = float(km[np.argmin(np.abs(kt - 100))]) if kt.size else None
            s['kurt_max'] = float(km.max()) if km.size else None
            s['global_max'] = float(ag['wm'].max()) if ag['wm'].size else None
            s['rate9'] = float(np.mean(ag['wm'] > 9)) if ag['wm'].size else None
            s['rate16'] = float(np.mean(ag['wm'] > 16)) if ag['wm'].size else None
            s['rate25'] = float(np.mean(ag['wm'] > 25)) if ag['wm'].size else None
            s['massdev'] = ag['massdev']
            s['tops'] = [[round(v, 2), round(t, 1), round(x, 2)] for (v, t, x) in ag['tops'][-10:]]
        stats[nm] = s
    return stats

def spec_slope(rs, N, L, snap_at):
    dx = L / N
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    kk = np.fft.fftshift(k); kk = kk[kk > 0]
    out = {}
    for r in rs:
        if r.get('spectra'):
            for st, sp in r['spectra'].items():
                if st in (snap_at):
                    a = np.fft.fftshift(np.abs(np.asarray(sp)))
                    a = a[len(a) - len(kk):]
                    out[st] = (kk.tolist(), (a * a).tolist())
            break
    return out

def spec_slope2(spectra):
    kk = np.asarray(spectra[100][0]); sp = np.asarray(spectra[100][1])
    m = (kk > 2) & (kk < 10)
    if m.sum() > 5:
        p = np.polyfit(np.log(kk[m]), np.log(sp[m]), 1)
        return float(p[0])
    return None

def analyze_and_report(A, B, C, paceA, paceB, paceC_real):
    stats = analyze(A, B, C, paceA, paceB, paceC_real)
    try:
        json.dump(stats, open('it_turbulence_stats.json', 'w'), indent=1)
        say('stats saved (' + str(len(json.dumps(stats))) + ' chars)')
    except Exception as e:
        say('stats save fail: ' + repr(e))
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        names = [('A eps=0.05', A), ('B eps=0.2', B), ('C N=2048', C)]
        for j, (nm, ag) in enumerate(names):
            ax = axes[j // 2][j % 2]
            if ag['n_ok']:
                bins = ag['bins']; h = ag['hist']
                c = 0.5 * (bins[:-1] + bins[1:])
                Ibar = float((c * h).sum() / max(1.0, h.sum()))
                pdf = h / (h.sum() * (bins[1] - bins[0]))
                ax.semilogy(c, Ibar * pdf, label=nm + ' emp')
                yy = np.linspace(0, c.max(), 400)
                ax.semilogy(yy, np.exp(-yy / Ibar), 'k--', label='Rayleigh')
                ax.set_xlim(0, 30); ax.set_ylim(1e-6, 2)
                ax.axvline(9, color='r', ls=':', lw=0.7)
            ax.set_xlabel('I (4s-window max)'); ax.set_title(nm)
            ax.legend(fontsize=8)
        axes[3][0].axis('off')
        ax = axes[3][1]
        for nm, ag in names:
            if ag['n_ok']:
                kt = np.array(ag['kt'])
                km = ag['kurt'].mean(axis=0)
                ax.plot(kt, km, label=nm)
        ax.axhline(3, color='k', ls=':')
        ax.set_xlabel('t'); ax.set_ylabel('kurtosis <I^2>/<I>^2')
        ax.legend(fontsize=8)
        axes[0][1].axis('off')
        fig.suptitle('Discovery-029 v2: integrable turbulence |psi|^2 PDF vs Rayleigh + kurtosis growth')
        fig.tight_layout()
        fig.savefig('it_turbulence_overview.png', dpi=130)
        plt.close(fig)
        say('overview png saved')
    except Exception as e:
        say('plot fail: ' + repr(e))
    try:
        fig, ax = plt.subplots(figsize=(7, 5))
        for nm, ag, N2, L2 in (('A', A, int(os.environ.get('IT_NA', '1024')), 100.0), ('C', C, int(os.environ.get('IT_NC', '2048')), 200.0)):
            if ag['n_ok'] and ag['rs'] and ag['rs'][0].get('spectra'):
                for st in (5, 15, 40, 100):
                    if st in ag['rs'][0]['spectra']:
                        sp = np.asarray(ag['rs'][0]['spectra'][st])
                        dx = L2 / N2
                        k2 = np.fft.fftshift(2.0 * np.pi * np.fft.fftfreq(N2, d=dx))
                        a = np.fft.fftshift(sp); a = a[a.size - np.sum(k2 > 0):]
                        m = (k2 > 0) & (k2 < 30)
                        ax.loglog(k2[m], a[m] + 1e-30, lw=0.9, label=nm + ' t=' + str(st))
        ax.set_xlabel('k'); ax.set_ylabel('|psi_k|^2')
        ax.legend(fontsize=7); ax.set_title('spectral evolution (seed head realizations)')
        fig.tight_layout(); fig.savefig('it_turbulence_spectra.png', dpi=130)
        plt.close(fig)
        say('spectra png saved')
    except Exception as e:
        say('spectra plot fail: ' + repr(e))
    return stats

if __name__ == '__main__':
    try:
        A, B, C, paceA, paceB, paceC_real = main()
        stats = analyze_and_report(A, B, C, paceA, paceB, paceC_real)
        lines = ['# Discovery-029 v2: Integrable Turbulence & Rogue Waves (World C run)', '']
        lines.append('Run: guard=' + str(GUARD) + 's, wall=' + str(stats['meta']['wall']) + 's')
        lines.append('Ensembles: A=' + str(stats['meta']['nA']) + ', B=' + str(stats['meta']['nB']) + ', C=' + str(stats['meta']['nC']) + ' realizations')
        lines.append('')
        for nm, ag in (('A', A), ('B', B), ('C', C)):
            if ag['n_ok']:
                s = stats[nm]
                lines.append('## Config ' + nm + ' (n=' + str(ag['n_ok']) + ')')
                lines.append('- mean window-max I: ' + str(round(s['meanI'], 4)))
                lines.append('- kurtosis t=40: ' + str(round(s['kurt_at_40'], 3)) + ', t=100: ' + str(round(s['kurt_at_100'], 3)) + ', max: ' + str(round(s['kurt_max'], 3)))
                lines.append('- enhancement factors vs Rayleigh: ' + json.dumps({kk2: (round(vv, 2) if vv is not None else None) for kk2, vv in s['enh'].items()}))
                lines.append('- rogue rates: >9=' + str(round(s['rate9'], 5)) + ', >16=' + str(round(s['rate16'], 5)) + ', >25=' + str(round(s['rate25'], 5)))
                lines.append('- global max |psi|^2: ' + str(round(s['global_max'], 2)) + ', mass dev: ' + str(round(s['massdev'], 8)))
                lines.append('- top-10 events (I, t, x): ' + json.dumps(s['tops']))
                lines.append('')
        try:
            import hashlib
            raw = json.dumps(stats, sort_keys=True)
            lines.append('- stats JSON SHA-256 (registry content): ' + hashlib.sha256(raw.encode()).hexdigest())
        except Exception:
            pass
        open('REPORT.md', 'w').write('\n'.join(lines) + '\n')
        say('REPORT.md written; v2 DONE')
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()[-3000:]
        say('FATAL: ' + repr(e))
        open('REPORT.md', 'w').write('v2 FATAL: ' + repr(e) + '\n' + tb + '\n')
        try:
            import glob
            cps = []
            for f in glob.glob('it_checkpoint_*.json'):
                try:
                    cp = json.load(open(f))
                    cps.append(f + ': n_ok=' + str(cp.get('n_ok')) + ' guard_hit=' + str(cp.get('guard_hit')))
                except Exception:
                    cps.append(f + ': unreadable')
            if cps:
                open('REPORT.md', 'a').write('\nCheckpoints recovered:\n' + '\n'.join(cps) + '\n')
        except Exception:
            pass

