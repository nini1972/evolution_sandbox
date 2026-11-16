#!/usr/bin/env python3
# C39 :: LOBE-INJECTION INVERSE TEST (P4 signature experiment)
# Question: can a trivial mixture (Rayleigh background + sparse sech^2 lobes
# + depletion moats) reproduce the canonical NLS mid-tail crossover
# R(s)=P(I>s)/P_Ray(I>s) profile (dip near s~2, bump near s~5-6), kurt~2,
# dens6, and P(>6|>2) simultaneously? If not, the crossover is not a trivial
# lobe superposition and that negative is itself informative.
# Canon gate SHA-256 = 2bd620cb8441e3e94b1ded1524ce5124a8d5796efb790917099c9180b2d7075c
import os, json, hashlib, importlib.util, traceback
import numpy as np
from colony_lib.persistence import StageTracker
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

STAGE = 'c39_lobe_injection'
tracker = StageTracker(STAGE)
CANON_CANDIDATES = [
    '../../instances/shared_space/canon/nls_splitstep_canonical.py',
    '../../shared_space/canon/nls_splitstep_canonical.py',
    'canon/nls_splitstep_canonical.py',
]
SHA = '2bd620cb8441e3e94b1ded1524ce5124a8d5796efb790917099c9180b2d7075c'
SGRID = [2, 3, 4, 5, 6, 7, 9]

def exceed_ratio(I, mu, s):
    p = float((I > s).mean())
    pr = float(np.exp(-s / mu))
    return (p / pr) if pr > 0 else float('nan')

def amp_kurtosis(I):
    a = np.sqrt(I)
    m2 = float((a ** 2).mean()); m4 = float((a ** 4).mean())
    return m4 / (m2 ** 2) if m2 > 0 else float('nan')

def cond_exc(I, s1=2, s2=6):
    p1 = float((I > s1).mean()); p2 = float((I > s2).mean())
    return p2 / p1 if p1 > 0 else float('nan')

def tail_stats(I_flat):
    mu = float(I_flat.mean())
    out = {'R': {str(s): exceed_ratio(I_flat, mu, s) for s in SGRID},
           'kurt': amp_kurtosis(I_flat),
           'dens6': float((I_flat > 6).mean()),
           'cond_exc': cond_exc(I_flat), 'mu': mu}
    out['R2dip'] = out['R']['2'] - 1.0
    out['R5bump'] = out['R']['5'] - 1.0
    return out

def field_realization(N, rho, A, w, D, rng):
    x = np.arange(N, dtype=float)
    I_bg = rng.exponential(size=N)          # mean-1 background intensity
    moat = np.ones(N)
    core = np.zeros(N)
    n_lobes = int(rng.poisson(rho * N))
    if n_lobes:
        pos = rng.integers(0, N, n_lobes)
        for x0 in pos:
            g = np.exp(-((x - x0) ** 2) / (2.0 * (3.0 * w) ** 2))
            moat = np.minimum(moat, 1.0 - D * g)
            core += A * np.cosh((x - x0) / w) ** -2.0
    moat = np.clip(moat, 0.0, None)
    mm = float(moat.mean()); cm = float(core.mean())
    if cm >= 1.0 - 1e-9:
        return None, 0, 0.0, 0.0            # mean-matching infeasible
    mu_bg = (1.0 - cm) / mm
    I = mu_bg * moat * I_bg + core
    return I, n_lobes, (1.0 - mm), cm       # (field, n_lobes, moat mass frac, core mass frac)

def run_tier1():
    rhos = [1e-4, 2e-4, 4e-4, 8e-4, 1.6e-3, 3.2e-3]
    As = [6.0, 8.0, 10.0]; ws = [1.5, 3.0]; Ds = [0.0, 0.9]
    N, n_real = 4096, 64
    cells = []; ci = 0
    for rho in rhos:
        for A in As:
            for w in ws:
                for D in Ds:
                    ci += 1
                    rng = np.random.default_rng(1000 + ci)
                    Is = []; lob = 0; mm = 0.0; cm = 0.0; ok = True
                    for r in range(n_real):
                        I, nl, m1, c1 = field_realization(N, rho, A, w, D, rng)
                        if I is None:
                            ok = False; break
                        Is.append(I); lob += nl; mm += m1; cm += c1
                    base = {'rho': rho, 'A': A, 'w': w, 'D': D}
                    if not ok:
                        base.update({'feasible': False}); cells.append(base); continue
                    I_flat = np.concatenate(Is)
                    st = tail_stats(I_flat)
                    st.update(base)
                    st.update({'feasible': True, 'lobes_per_real': lob / n_real,
                               'M2frac': cm / n_real, 'moatmass': mm / n_real})
                    cells.append(st)
                    print('  [tier1] %d rho=%g A=%g w=%g D=%g R2=%.3f R5=%.3f R9=%.3f '
                          'kurt=%.3f dens6=%.2e cond=%.4f M2f=%.3f moat=%.3f' %
                          (ci, rho, A, w, D, st['R']['2'], st['R']['5'], st['R']['9'],
                           st['kurt'], st['dens6'], st['cond_exc'], st['M2frac'],
                           st['moatmass']), flush=True)
    feas = [c for c in cells if c.get('feasible')]
    def corr(k1, k2):
        x = np.array([c[k1] for c in feas]); y = np.array([c[k2] for c in feas])
        if x.std() < 1e-12 or y.std() < 1e-12:
            return float('nan')
        return float(np.corrcoef(x, y)[0, 1])
    agg = {'corr_M2frac_R5bump': corr('M2frac', 'R5bump'),
           'corr_moatmass_R2dip': corr('moatmass', 'R2dip'),
           'corr_M2frac_kurt': corr('M2frac', 'kurt'),
           'n_feasible': len(feas), 'n_cells': len(cells)}
    return {'cells': cells, 'agg': agg,
            'config': {'N': N, 'n_real': n_real, 'rhos': rhos, 'As': As,
                       'ws': ws, 'Ds': Ds}}

def jclean(o):
    if isinstance(o, dict):
        return {str(k): jclean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jclean(v) for v in o]
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        f = float(o)
        return None if (np.isnan(f) or np.isinf(f)) else f
    return o

def canon_gate():
    global CANON
    for path in CANON_CANDIDATES:
        try:
            b = open(path, 'rb').read()
        except OSError:
            continue
        h = hashlib.sha256(b).hexdigest()
        CANON = path
        return (h == SHA), h
    return False, 'canon file missing'

def run_tier2(ok, sha):
    if not ok:
        print('  [tier2] SKIPPED (canon %s)' % sha, flush=True)
        return {'skipped': True, 'reason': 'canon sha mismatch: %s' % sha}
    spec = importlib.util.spec_from_file_location('nls_canon', CANON)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = {}
    for label, N, L, seeds in (('L50', 1024, 50.0, range(1, 13)),
                               ('L100', 2048, 100.0, range(1, 7))):
        Is = []; gmax = 0.0
        for seed in seeds:
            times, samples, diag = mod.simulate(N=N, L=L, dt=1e-3, T_end=20.0,
                                                eps=0.1, seed=seed,
                                                sample_every=500, t_trans=5.0)
            arr = np.concatenate([np.asarray(s, float) for s in samples])
            Is.append(arr); gmax = max(gmax, float(arr.max()))
        I_flat = np.concatenate(Is)
        st = tail_stats(I_flat)
        st['maxI'] = gmax; st['n_sites'] = int(I_flat.size)
        out[label] = st
        print('  [tier2:%s] R2=%.3f R5=%.3f R9=%.3f kurt=%.3f dens6=%.2e '
              'cond=%.4f maxI=%.2f' % (label, st['R']['2'], st['R']['5'],
              st['R']['9'], st['kurt'], st['dens6'], st['cond_exc'], gmax),
              flush=True)
    return out

def score_cell(c, tgt):
    ds = {'R2dip': abs(c['R2dip'] - tgt['R2dip']) / 0.02,
          'R5bump': abs(c['R5bump'] - tgt['R5bump']) / 0.02,
          'kurt': abs(c['kurt'] - tgt['kurt']) / 0.05,
          'R9': abs(c['R']['9'] - tgt['R']['9']) / 0.05,
          'dens6': abs(c['dens6'] - tgt['dens6']) / max(0.3 * tgt['dens6'], 1e-12),
          'cond': abs(c['cond_exc'] - tgt['cond_exc']) / max(0.3 * tgt['cond_exc'], 1e-12)}
    return max(ds.values()), ds

def make_plots(summary):
    if not HAS_MPL:
        return
    t1, t2 = summary['tier1'], summary['tier2']
    feas = [c for c in t1['cells'] if c.get('feasible')]
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.5))
    if t2 and not t2.get('skipped'):
        for lab, style in (('L50', '-'), ('L100', '--')):
            if t2.get(lab):
                ax[0, 0].plot(SGRID, [t2[lab]['R'][str(s)] for s in SGRID],
                              style + 'o', label='NLS ' + lab)
        if summary.get('verdict') and summary['verdict'].get('best_cell'):
            bc = summary['verdict']['best_cell']
            for c in feas:
                if all(abs(c[k] - bc[k]) < 1e-12 for k in ('rho', 'A', 'w', 'D')):
                    ax[0, 0].plot(SGRID, [c['R'][str(s)] for s in SGRID],
                                  's--', color='tab:red', label='best synth')
                    break
    ax[0, 0].axhline(1.0, color='gray', lw=0.8)
    ax[0, 0].set_xlabel('s'); ax[0, 0].set_ylabel('R(s)')
    ax[0, 0].legend(fontsize=8); ax[0, 0].set_title('R(s)=P(I>s)/P_Ray')
    for A in (6.0, 8.0, 10.0):
        pts = sorted((c['rho'], c['R5bump']) for c in feas
                     if c['w'] == 3.0 and c['D'] == 0.9 and c['A'] == A)
        if pts:
            ax[0, 1].semilogx([p[0] for p in pts], [p[1] for p in pts],
                              'o-', label='A=%g' % A)
    ax[0, 1].set_xlabel('rho (lobes/site)'); ax[0, 1].set_ylabel('R(5)-1')
    ax[0, 1].legend(fontsize=8); ax[0, 1].set_title('bump vs lobe density (w=3, D=0.9)')
    for D, st in ((0.0, 'o-'), (0.9, 's-')):
        pts = sorted((c['rho'], c['R2dip']) for c in feas
                     if c['w'] == 3.0 and c['A'] == 8.0 and c['D'] == D)
        if pts:
            ax[1, 0].semilogx([p[0] for p in pts], [p[1] for p in pts], st,
                              label='D=%g' % D)
    ax[1, 0].set_xlabel('rho'); ax[1, 0].set_ylabel('R(2)-1')
    ax[1, 0].legend(fontsize=8); ax[1, 0].set_title('dip vs rho (w=3, A=8)')
    ax[1, 1].plot([c['M2frac'] for c in feas], [c['kurt'] for c in feas], '.', ms=4)
    ax[1, 1].set_xlabel('lobe mass fraction M2'); ax[1, 1].set_ylabel('amplitude kurtosis')
    ax[1, 1].set_title('kurtosis vs lobe mass')
    fig.tight_layout()
    fig.savefig('d39_lobe_map.png', dpi=110)
    plt.close(fig)

def save_artifacts(summary):
    with open('c39_summary.json', 'w') as f:
        json.dump(summary, f, indent=1)
    import shutil
    adir = '../../instances/shared_space/world_c/artifacts'
    try:
        os.makedirs(adir, exist_ok=True)
        for fn in ('c39_summary.json', 'd39_lobe_map.png'):
            if os.path.exists(fn):
                shutil.copy(fn, os.path.join(adir, fn))
    except OSError:
        pass

def main():
    print('== C39 lobe-injection inverse test ==', flush=True)
    if not tracker.is_done('tier1'):
        t1 = run_tier1()
        tracker.save_stage('tier1', jclean(t1))
        print('  [stage] tier1 saved', flush=True)
    else:
        t1 = tracker.get_stage('tier1')
        print('  [stage] tier1 loaded from checkpoint', flush=True)
    ok, sha = canon_gate()
    print('  [gate] canon sha=%s ok=%s' % (sha, ok), flush=True)
    if not tracker.is_done('tier2'):
        t2 = run_tier2(ok, sha)
        tracker.save_stage('tier2', jclean(t2))
    else:
        t2 = tracker.get_stage('tier2')
    summary = {'stage': STAGE, 'canon_sha_ok': ok, 'tier1': t1, 'tier2': t2}
    feas = [c for c in t1['cells'] if c.get('feasible')]
    if t2 and not t2.get('skipped') and t2.get('L50') and feas:
        tgt = t2['L50']
        scored = sorted((score_cell(c, tgt)[0], i) for i, c in enumerate(feas))
        best_s, bi = scored[0]
        best_c = feas[bi]
        near = [s for s, _ in scored if s <= 2.0 * best_s + 1e-12]
        verdict = {'target': 'L50', 'best_score': best_s, 'gate': 2.0,
                   'best_cell': {k: best_c[k] for k in ('rho', 'A', 'w', 'D')},
                   'best_deviations': score_cell(best_c, tgt)[1],
                   'n_cells_within_2x_of_best': len(near),
                   'result': 'LOBE_VIABLE' if best_s <= 2.0 else 'LOBE_INSUFFICIENT'}
        if t2.get('L100'):
            verdict['best_score_L100'] = min(score_cell(c, t2['L100'])[0] for c in feas)
        summary['verdict'] = verdict
        print('  [verdict] %s best=%.3f cell=%s' %
              (verdict['result'], best_s, verdict['best_cell']), flush=True)
        print('  [verdict] devs=%s' % json.dumps(
            {k: round(v, 2) for k, v in verdict['best_deviations'].items()}), flush=True)
    else:
        summary['verdict'] = {'result': 'TIER2_SKIPPED'}
    try:
        make_plots(summary)
    except Exception:
        traceback.print_exc()
    save_artifacts(jclean(summary))
    tracker.save_stage('final', jclean({'verdict': summary['verdict']}))
    print('== C39 done ==', flush=True)

if __name__ == '__main__':
    main()
