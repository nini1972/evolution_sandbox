# Job v4: Discovery-029 sharpened - tail excess vs INITIAL SPECTRAL BANDWIDTH
# Focusing NLS i psi_t + psi_xx + 2|psi|^2 psi = 0, Strang split-step.
# Hypothesis H1: coherent tail excess (ratio>1 at s>=10) requires BROADBAND IC;
#                narrow IC thermalizes to exact Rayleigh (ratio=0).
# Series: eps in {0.05,0.10,0.20,0.40} UNFILTERED (029 scheme) + narrow-filter 0.20 control.
# Dense frames (every 1.0 tu over t in [40,100]) -> per-frame tail ratios + tau_corr.
import os, time, json, sys
import numpy as np
import multiprocessing as mp

T0 = time.time()
GUARD = float(os.environ.get('IT_GUARD', '2600'))
CH = int(os.environ.get('IT_CHUNK', '8'))

def say(m):
    print('[BW ' + str(round(time.time() - T0, 1)) + 's] ' + str(m)); sys.stdout.flush()

def run_real(args):
    (seed, N, L, dt, T, eps, narrow) = args
    try:
        dx = L / N
        k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
        lin_half = np.exp(-0.5j * (k * k) * dt)
        nsteps = int(round(T / dt))
        rng = np.random.default_rng(seed)
        psi = np.ones(N, dtype=complex)
        psi += eps * (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)
        if narrow:
            fk = np.exp(-0.5 * (k / 2.0) ** 2)   # Gaussian spectral filter (kw~2), as in 50c8
            psi = np.fft.ifft(fk * np.fft.fft(psi))
            psi += (1.0 - psi.real)              # re-pin mean to 1 (keep condensate)
        if abs(psi.real.mean()) > 1e-9:
            psi += (1.0 - psi.real.mean())
        I0 = (psi.real ** 2 + psi.imag ** 2).mean()
        bins = np.linspace(0, 60, 241)
        hist = np.zeros(len(bins) - 1)
        frames_s = []      # per-frame max s
        frames_kt = []     # frame times
        kurt_series = []   # per-frame kurtosis
        tnext = 40.0
        massdev = 0.0
        for n in range(1, nsteps + 1):
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            psi *= np.exp(2j * dt * (psi.real ** 2 + psi.imag ** 2))
            psi = np.fft.ifft(lin_half * np.fft.fft(psi))
            t = n * dt
            if t >= tnext - 1e-12 and t >= 40.0:
                I = psi.real ** 2 + psi.imag ** 2
                m1 = I.mean()
                massdev = max(massdev, abs(m1 - I0))
                kurt_series.append(float((I * I).mean() / (m1 * m1)))
                frames_s.append(float(I.max() / m1))
                frames_kt.append(float(t))
                h, _ = np.histogram(I, bins=bins)
                hist += h
                tnext += 1.0
        return {'ok': True, 'seed': seed, 'hist': hist.tolist(),
                'fs': frames_s, 'kt': frames_kt, 'kurt': kurt_series,
                'massdev': massdev}
    except Exception as e:
        return {'ok': False, 'seed': seed, 'err': repr(e)}

def aggregate(res):
    ok = [r for r in res if r.get('ok')]
    if not ok:
        return None
    hist = np.sum([np.array(r['hist']) for r in ok], axis=0)
    bins = np.linspace(0, 60, 241)
    # tau_corr from kurtosis series: lag-1 autocorr averaged over reals
    lags = []
    for r in ok:
        v = np.array(r['kurt'])
        if len(v) > 12:
            v = v - v.mean()
            c0 = (v * v).mean()
            if c0 > 0:
                lags.append((v[:-1] * v[1:]).mean() / c0)
    return {'n_ok': len(ok), 'hist': hist.tolist(), 'bins': bins.tolist(),
            'tau1': float(np.mean(lags)) if lags else None,
            'massdev': float(np.mean([r['massdev'] for r in ok])),
            'frames_s': [r['fs'] for r in ok],
            'kurt_last': [r['kurt'][-1] for r in ok]}

def run_cfg(name, jobs, pool):
    res = []
    i = 0
    while i < len(jobs):
        chunk = jobs[i:i + CH]
        got = []
        try:
            if pool is not None:
                ars = [pool.apply_async(run_real, (j,)) for j in chunk]
                got = [a.get(timeout=900) for a in ars]
            else:
                for j in chunk:
                    if time.time() - T0 > GUARD:
                        break
                    got.append(run_real(j))
        except Exception as e:
            say('chunk fail ' + name + ': ' + repr(e)[:120])
            if pool is not None:
                pool.terminate(); pool = None
                say('-> serial fallback')
            got = []
            for j in chunk:
                if time.time() - T0 > GUARD:
                    break
                got.append(run_real(j))
        res.extend([g for g in got if g.get('ok')])
        i += CH
        say(name + ' chunk: total ok=' + str(len(res)) + '/' + str(len(jobs)))
        json.dump({'name': name, 'n_ok': len(res), 'guard': time.time() - T0 > GUARD},
                  open('bw_progress_' + name + '.json', 'w'))
    ag = aggregate(res)
    out = {'name': name, 'n_ok': ag['n_ok'] if ag else 0,
           'wall': round(time.time() - T0, 1), 'guard_hit': time.time() - T0 > GUARD}
    if ag:
        bins = np.array(ag['bins']); hist = np.array(ag['hist'])
        c = 0.5 * (bins[:-1] + bins[1:]); bw = np.diff(bins)
        pdf = hist / hist.sum() / bw
        I = c; wbar = (pdf * I * bw).sum()
        sn = I / wbar
        out['wbar'] = float(wbar); out['nsamp'] = float(hist.sum())
        out['tau1'] = ag['tau1']; out['massdev'] = ag['massdev']
        out['kurt_last_mean'] = float(np.mean(ag['kurt_last']))
        tails = {}
        fs_all = ag['frames_s']
        nframes = sum(len(f) for f in fs_all)
        for thr in (6, 8, 10, 12, 14):
            m = sn >= thr
            P = (pdf[m] * bw[m]).sum()
            e = np.exp(-thr)
            nex = float(hist.sum() * (m * bw).sum() * wbar * e)  # expected counts
            nob = float((pdf[m] * bw[m]).sum() * hist.sum())
            fmax = float(np.mean([np.mean(np.array(f) >= thr) for f in fs_all])) if nframes else 0
            tails[str(thr)] = {'P': float(P), 'ratio': float(P / e),
                               'n_obs': nob, 'n_exp': nex,
                               'frame_frac': float(fmax), 'nframes': int(nframes)}
        out['tails'] = tails
        # per-frame kurtosis series mean (temporal profile)
        out['kurt_profile'] = None
    json.dump(out, open('bw_result_' + name + '.json', 'w'))
    say('saved bw_result_' + name + '.json  n_ok=' + str(out['n_ok']))
    return out, pool

def main():
    say('v4 start guard=' + str(GUARD) + ' cpus=' + str(mp.cpu_count()))
    N, L, dt, T = 2048, 100.0, 1e-3, 100.0
    nreal = int(os.environ.get('IT_NREAL', '12'))
    eps_list = [0.05, 0.10, 0.20, 0.40]
    jobsets = []
    for ei, eps in enumerate(eps_list):
        jobsets.append(('broad_e' + str(eps), [(7000 + ei * 100 + i, N, L, dt, T, eps, False)
                                               for i in range(nreal)]))
    jobsets.append(('narrow_e0.20', [(8000 + i, N, L, dt, T, 0.20, True)
                                     for i in range(nreal)]))
    pool = None
    try:
        nw = min(8, mp.cpu_count())
        pool = mp.Pool(nw)
        say('pool ' + str(nw))
    except Exception as e:
        say('pool fail ' + repr(e)[:80])
    results = {}
    for name, jobs in jobsets:
        r, pool = run_cfg(name, jobs, pool)
        results[name] = r
        # early stop if guard nearly hit
        if time.time() - T0 > GUARD - 200:
            say('guard margin low -> stop series')
            break
    json.dump(results, open('bw_all_results.json', 'w'))
    say('ALL DONE')
    try:
        if pool is not None:
            pool.close(); pool.join()
    except Exception:
        pass

if __name__ == '__main__':
    main()
