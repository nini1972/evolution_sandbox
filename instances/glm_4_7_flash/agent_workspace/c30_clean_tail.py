# DISCOVERY 030-CLEAN: count-level tail measurement, focusing NLS integrable turbulence.
# Purpose: settle the October (h5) vs D30 discrepancy on heavy-tail sign-class ratios.
# Design principles (lessons from the forensic audit):
#   1. RAW COUNTS are the primary output. Ratios are derived post-hoc, never summed.
#   2. The null for Re psi > s under a Rayleigh field (I ~ Exp(1), phi uniform) is
#      P(Re psi > s) = int_{a>s^2} e^{-a} * arccos(s/sqrt(a))/pi da  -- computed
#      numerically here, NOT the (wrong) formula exp(-s^2)*(1+s^2).
#   3. Internal control: the SAME counting code is applied to a synthetic Rayleigh
#      field (I ~ Exp(1), phi ~ U(0,2pi)); its ratios must be ~1.0. Any deviation
#      indicts the estimator, not the physics.
# Physics: i psi_t + psi_xx + 2|psi|^2 psi = 0, Strang split-step Fourier.
import numpy as np, json, sys, time
from scipy.integrate import quad
from scipy import stats

T0 = time.time()
def say(m):
    print('[C30 %.1fs] %s' % (time.time()-T0, m)); sys.stdout.flush()

# ---------------- correct analytic nulls ----------------
def p_re_psi_null(s):
    """P(Re psi > s) for |psi|^2 ~ Exp(1), phi uniform.
    P = int_{s^2}^inf e^{-a} * arccos(s/sqrt(a))/pi da  (correct, < 1 always)."""
    def integrand(a):
        c = s/np.sqrt(a)
        if c >= 1: return 0.0
        return np.exp(-a)*np.arccos(c)/np.pi
    val, err = quad(integrand, s*s, 80.0, limit=400)
    return val

def p_intensity_null(s):
    """P(I > s) for I ~ Exp(1): e^{-s}."""
    return float(np.exp(-s))

# ---------------- counting engine (shared by real + control) ----------------
def tail_counts(I, Repsi, thresholds_I, thresholds_R):
    out_I = {}
    for s in thresholds_I:
        out_I[str(s)] = int(np.sum(I > s))
    out_R = {}
    for s in thresholds_R:
        out_R[str(s)] = int(np.sum(Repsi > s))
    return out_I, out_R

def run_realization(args):
    (seed, N, L, dt, T, eps, mode) = args
    # mode='nls' -> real dynamics; mode='rayleigh_control' -> synthetic Exp(1) field
    if mode == 'rayleigh_control':
        rng = np.random.default_rng(seed)
        I = rng.exponential(1.0, N)
        phase = rng.uniform(0, 2*np.pi, N)
        psi = np.sqrt(I) * (np.cos(phase) + 1j*np.sin(phase))
        Repsi = psi.real
        out_I, out_R = tail_counts(I, Repsi, TI, TR)
        return {'ok': True, 'seed': seed, 'mode': mode,
                'I_counts': out_I, 'R_counts': out_R,
                'mean_I': float(I.mean()), 'kurt': float((I*I).mean()/I.mean()**2)}
    # ---- real NLS run ----
    dx = L/N
    x = np.arange(N)*dx
    k = 2*np.pi*np.fft.fftfreq(N, d=dx)
    lin_half = np.exp(-0.5j*(k*k)*dt)
    nsteps = int(round(T/dt))
    rng = np.random.default_rng(seed)
    psi = np.ones(N, dtype=complex)
    psi += eps*(rng.standard_normal(N) + 1j*rng.standard_normal(N))/np.sqrt(2)
    # record frames in the turbulent steady state (t in [T/2, T])
    frames = []
    rec_every = max(1, int(round(0.5/dt)))  # every 0.5 time units
    for n in range(1, nsteps+1):
        psi = np.fft.ifft(lin_half*np.fft.fft(psi))
        psi = psi*np.exp(2j*dt*(psi.real*psi.real + psi.imag*psi.imag))
        psi = np.fft.ifft(lin_half*np.fft.fft(psi))
        if n % rec_every == 0:
            t = n*dt
            if t >= T/2:
                I = psi.real*psi.real + psi.imag*psi.imag
                frames.append((t, I.copy(), psi.real.copy()))
    agg_I = {str(s): 0 for s in TI}
    agg_R = {str(s): 0 for s in TR}
    n_samples = 0
    kurt_vals = []
    mean_I_vals = []
    for (t, I, Re) in frames:
        n_samples += N
        oI, oR = tail_counts(I, Re, TI, TR)
        for kk, v in oI.items(): agg_I[kk] += v
        for kk, v in oR.items(): agg_R[kk] += v
        m1 = I.mean(); m2 = (I*I).mean()
        mean_I_vals.append(m1)
        kurt_vals.append(m2/(m1*m1))
    return {'ok': True, 'seed': seed, 'mode': mode,
            'n_samples': n_samples, 'n_frames': len(frames),
            'I_counts': agg_I, 'R_counts': agg_R,
            'mean_I': float(np.mean(mean_I_vals)),
            'kurt': float(np.mean(kurt_vals))}

# ---------------- driver ----------------
TI = [4.0, 9.0, 16.0, 25.0]      # intensity thresholds (amplitude 2,3,4,5)
TR = [2.0, 3.0]                  # Re psi thresholds (4 is count-starved even here)
N, L, dt, T, eps = 1024, 50.0, 5e-4, 100.0, 0.1
n_seeds = 32
n_ctrl = 16

def aggregate(runs, mode):
    runs = [r for r in runs if r.get('ok') and r['mode'] == mode]
    if not runs: return None
    tot_samples = sum(r.get('n_samples', r.get('N_override', N)) for r in runs)
    aggI = {}; aggR = {}
    for s in TI: aggI[str(s)] = sum(r['I_counts'][str(s)] for r in runs)
    for s in TR: aggR[str(s)] = sum(r['R_counts'][str(s)] for r in runs)
    ns = sum(r.get('n_samples', 0) for r in runs) or len(runs)*N
    res = {'n_runs': len(runs), 'n_samples_total': int(ns)}
    res['I'] = {}
    for s in TI:
        cnt = aggI[str(s)]
        expct = ns * p_intensity_null(s)
        res['I'][str(s)] = {'count': int(cnt), 'expected_null': float(expct),
                            'ratio': (cnt/expct) if expct > 0 else None,
                            'poisson_sigma_ratio': (np.sqrt(cnt)/expct) if (expct>0 and cnt>0) else None}
    res['R'] = {}
    for s in TR:
        cnt = aggR[str(s)]
        expct = ns * p_re_psi_null(s)
        res['R'][str(s)] = {'count': int(cnt), 'expected_null': float(expct),
                            'ratio': (cnt/expct) if expct > 0 else None,
                            'poisson_sigma_ratio': (np.sqrt(cnt)/expct) if (expct>0 and cnt>0) else None}
    res['mean_I_over_runs'] = float(np.mean([r['mean_I'] for r in runs]))
    res['kurt_over_runs'] = float(np.mean([r['kurt'] for r in runs]))
    return res

if __name__ == '__main__':
    say('dispatch: %d NLS seeds + %d Rayleigh control' % (n_seeds, n_ctrl))
    import multiprocessing as mp
    jobs = [(1000+i, N, L, dt, T, eps, 'nls') for i in range(n_seeds)]
    jobs += [(9000+i, N, L, dt, T, eps, 'rayleigh_control') for i in range(n_ctrl)]
    with mp.Pool(min(8, mp.cpu_count())) as pool:
        results = pool.map(run_realization, jobs)
    ok = [r for r in results if r.get('ok')]
    say('completed %d/%d realizations' % (len(ok), len(jobs)))
    nls_agg = aggregate(ok, 'nls')
    ctrl_agg = aggregate(ok, 'rayleigh_control')
    # null sanity: analytic vs formula
    for s in [2.0, 3.0, 4.0]:
        say('null Re psi > %.0f: analytic=%.3e  wrong_formula=%.3e  ratio=%.3e'
            % (s, p_re_psi_null(s), np.exp(-s*s)*(1+s*s), p_re_psi_null(s)/(np.exp(-s*s)*(1+s*s))))
    report = {
        'config': {'N': N, 'L': L, 'dt': dt, 'T': T, 'eps': eps,
                   'n_seeds': n_seeds, 'n_ctrl': n_ctrl,
                   'I_thresholds': TI, 'R_thresholds': TR,
                   'null_I': 'P(I>s)=exp(-s)',
                   'null_R': 'analytic P(Re psi>s), Rayleigh field'},
        'nls': nls_agg,
        'rayleigh_control': ctrl_agg,
        'wall_s': time.time()-T0,
    }
    with open('c30_clean.json', 'w') as f:
        json.dump(report, f, indent=1)
    say(json.dumps({k: report[k] for k in ['nls', 'rayleigh_control']}, indent=1))
    say('DONE')
