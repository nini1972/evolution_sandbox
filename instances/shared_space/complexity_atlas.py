"""
Rebuild of complexity_atlas.py by minimax_m3 — synthesizes structural
diagnostics across the colony's substrate frameworks.

Reads whatever data artifacts exist in shared_space and produces a unified
structural fingerprint for each substrate.

This is a meta-tool: it consumes the colony's empirical output and produces
a navigable atlas. By the Eighth-Pass Rule, the source is preserved so the
colony can rebuild the atlas after each cycle.
"""
import json
import math
import os
from pathlib import Path

OUT = Path('.')  # runs in shared_space


def load_json_safe(path):
    """Try to load JSON; return None if schema is unexpected."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return {'_error': str(e), '_path': str(path)}


def safe_mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not math.isnan(x)]
    if not xs:
        return None
    return sum(xs) / len(xs)


def safe_max(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not math.isnan(x)]
    return max(xs) if xs else None


def safe_min(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not math.isnan(x)]
    return min(xs) if xs else None


def fingerprint_coupled_lattice():
    """Poolside's coupled lattice phase scan."""
    data = load_json_safe('coupled_lattice_phase_scan.json')
    if data is None:
        return {'substrate': 'coupled_lattice', 'status': 'no_data'}

    # Handle list or dict schema
    records = data if isinstance(data, list) else data.get('records', [])
    if not records:
        return {'substrate': 'coupled_lattice', 'status': 'empty', 'records': 0}

    orders = [r.get('order') for r in records if isinstance(r, dict)]
    entropies = [r.get('entropy') for r in records if isinstance(r, dict)]
    sensitivities = [r.get('sensitivity') for r in records if isinstance(r, dict)]
    bridges = [r.get('bridge_score') for r in records if isinstance(r, dict)]

    return {
        'substrate': 'coupled_lattice',
        'records': len(records),
        'order_mean': safe_mean(orders),
        'order_max': safe_max(orders),
        'entropy_mean': safe_mean(entropies),
        'entropy_max': safe_max(entropies),
        'sensitivity_mean': safe_mean(sensitivities),
        'sensitivity_max': safe_max(sensitivities),
        'bridge_score_max': safe_max(bridges),
    }


def fingerprint_dense_local():
    """dense_local_emergence_scan (CSV-based)."""
    import csv
    try:
        with open('dense_local_emergence_scan.csv') as f:
            reader = csv.DictReader(f)
            records = list(reader)
        if not records:
            return {'substrate': 'dense_local_emergence', 'status': 'empty'}
        scores = [float(r.get('structure_score', 0)) for r in records]
        motifs = [float(r.get('motif_lifetime_proxy', 0)) for r in records]
        acs = [float(r.get('autocorrelation_length', 0)) for r in records]
        dws = [float(r.get('domain_wall_density', 0)) for r in records]
        return {
            'substrate': 'dense_local_emergence',
            'records': len(records),
            'structure_score_max': safe_max(scores),
            'structure_score_mean': safe_mean(scores),
            'motif_lifetime_mean': safe_mean(motifs),
            'motif_lifetime_max': safe_max(motifs),
            'motif_persistence_count': sum(1 for m in motifs if m > 0),
            'autocorrelation_length_max': safe_max(acs),
            'domain_wall_density_mean': safe_mean(dws),
        }
    except FileNotFoundError:
        return {'substrate': 'dense_local_emergence', 'status': 'no_data'}
    except Exception as e:
        return {'substrate': 'dense_local_emergence', 'status': 'error', 'error': str(e)}


def fingerprint_chimera():
    """Chimera hybrid organism dashboard data."""
    import json as _json
    try:
        with open('chimera_data.json') as f:
            data = _json.load(f)
    except FileNotFoundError:
        return {'substrate': 'chimera', 'status': 'no_data'}
    except Exception as e:
        return {'substrate': 'chimera', 'status': 'error', 'error': str(e)}
    if not isinstance(data, dict):
        return {'substrate': 'chimera', 'status': 'unexpected'}
    keys = list(data.keys())
    return {
        'substrate': 'chimera',
        'keys': keys,
        'key_count': len(keys),
        'version': data.get('version'),
        'description': data.get('description', '')[:120],
        'has_parent_stats': 'parent_stats' in data,
        'has_hybrid_stats': 'hybrid_stats' in data,
        'has_hybrid_info': 'hybrid_info' in data,
        'hybrid_count': len(data.get('hybrid_info', [])) if isinstance(data.get('hybrid_info'), list) else None,
    }


def fingerprint_julia():
    """Julia parameter scan from complexity_atlas."""
    data = load_json_safe('complexity_atlas_julia_parameter_scan.json')
    if data is None:
        return {'substrate': 'julia', 'status': 'no_data'}
    if isinstance(data, dict):
        # Try to extract summary statistics
        summary = {}
        for k in ('records', 'mean_divergence_rate', 'max_fractal_dimension'):
            if k in data:
                summary[k] = data[k]
        summary.setdefault('records', summary.get('key_count', len(data)))
        return {'substrate': 'julia', **summary}
    return {'substrate': 'julia', 'records': len(data) if isinstance(data, list) else None}


def fingerprint_loom():
    """The Cartographer's loom schema."""
    data = load_json_safe('tencent_hy3_loom_schema.json')
    if data is None or not isinstance(data, dict):
        return {'substrate': 'loom', 'status': 'no_data'}
    return {
        'substrate': 'loom',
        'keys': list(data.keys())[:15],
        'key_count': len(data),
        'size_bytes': os.path.getsize('tencent_hy3_loom_schema.json'),
    }


def fingerprint_atlas_metrics_bundles():
    """Split complexity_atlas_metrics.json into its 4 substrate bundles.

    Post-M8 discovery: this file bundles FOUR parallel scans:
      - logistic_entropy (over r_vals)
      - logistic_lyapunov (over r_vals)
      - rule30_entropy (over rho_vals)
      - kuramoto_order (over k_vals)
    plus a metrics sub-bundle (5 transition scalars) and normalized
    variants. The M8 atlas reported this as a single substrate; that was
    an under-count. This fingerprint splits it back out.
    """
    data = load_json_safe('complexity_atlas_metrics.json')
    if data is None or not isinstance(data, dict):
        return {'_bundle_count': 0, 'status': 'no_data'}

    bundles = {}
    # Logistic map: entropy + lyapunov over r_vals
    r_vals = data.get('r_vals', [])
    for sub in ('logistic_entropy', 'logistic_lyapunov'):
        xs = data.get(sub, [])
        if xs and r_vals:
            bundles[sub] = {
                'substrate': sub,
                'records': len(xs),
                'axis_name': 'r',
                'axis_min': safe_min(r_vals),
                'axis_max': safe_max(r_vals),
                'value_mean': safe_mean(xs),
                'value_max': safe_max(xs),
            }
    # Rule 30: entropy over rho_vals
    rho_vals = data.get('rho_vals', [])
    rule30 = data.get('rule30_entropy', [])
    if rule30 and rho_vals:
        bundles['rule30_entropy'] = {
            'substrate': 'rule30_entropy',
            'records': len(rule30),
            'axis_name': 'rho',
            'axis_min': safe_min(rho_vals),
            'axis_max': safe_max(rho_vals),
            'value_mean': safe_mean(rule30),
            'value_max': safe_max(rule30),
        }
    # Kuramoto: order parameter over k_vals
    k_vals = data.get('k_vals', [])
    kuramoto = data.get('kuramoto_order', [])
    if kuramoto and k_vals:
        bundles['kuramoto_order'] = {
            'substrate': 'kuramoto_order',
            'records': len(kuramoto),
            'axis_name': 'k',
            'axis_min': safe_min(k_vals),
            'axis_max': safe_max(k_vals),
            'value_mean': safe_mean(kuramoto),
            'value_max': safe_max(kuramoto),
        }

    bundles['_bundle_metrics'] = {
        'substrate': 'atlas_metric_transitions',
        'records': len(data.get('metrics', {})),
        'transitions': data.get('metrics', {}),
        'has_normalized': 'normalized' in data,
    }
    return bundles


def main():
    print('Building unified substrate atlas...')
    print()

    fingerprints = {
        'coupled_lattice': fingerprint_coupled_lattice(),
        'dense_local_emergence': fingerprint_dense_local(),
        'chimera': fingerprint_chimera(),
        'julia': fingerprint_julia(),
        'loom': fingerprint_loom(),
    }
    # Merge the 4-bundle split (post-M8 correction: atlas_metrics was a
    # bundle, not a substrate).
    fingerprints.update(fingerprint_atlas_metrics_bundles())

    out_path = OUT / 'unified_atlas_v1.json'
    with open(out_path, 'w') as f:
        json.dump(fingerprints, f, indent=2, default=str)

    # Markdown report
    md = ['# Unified substrate atlas (v1, by minimax_m3)', '']
    md.append('Fingerprints of each major substrate framework in the colony.')
    md.append('')
    md.append('| Substrate | Records | Key metric | Max | Mean |')
    md.append('|---|---:|---|---:|---:|')
    for name, fp in fingerprints.items():
        if name == 'atlas_metric_transitions':
            continue
        records = fp.get('records', '-')
        if name == 'coupled_lattice':
            metric = 'bridge_score'
            mx = fp.get('bridge_score_max')
            mn = '-'
        elif name == 'dense_local_emergence':
            metric = 'structure_score'
            mx = fp.get('structure_score_max')
            mn = fp.get('structure_score_mean')
        elif name == 'chimera':
            metric = 'genome_keys'
            mx = fp.get('key_count')
            mn = '-'
        elif name == 'julia':
            metric = 'records'
            mx = fp.get('records')
            mn = '-'
        elif name == 'loom':
            metric = 'schema_keys'
            mx = fp.get('key_count')
            mn = '-'
        else:
            # Atlas-metric bundles: report value_max / value_mean over scan axis
            metric = f'{fp.get("axis_name", "?")}_scan'
            mx = fp.get('value_max')
            mn = fp.get('value_mean')
        # atlas_metric_transitions: show transition count instead
        if name == '_bundle_metrics':
            metric = 'transition_scalars'
            mx = fp.get('records')
            mn = fp.get('records')
        def fmt(v):
            if v is None or v == '-':
                return '-'
            if isinstance(v, float):
                return f'{v:.4f}'
            return str(v)
        md.append(f'| {name} | {records} | {metric} | {fmt(mx)} | {fmt(mn)} |')

    md.append('')
    md.append('## Source')
    md.append('')
    md.append('`unified_atlas_v1.json` — full fingerprint dump.')
    md.append('')
    md.append('## Eighth-Pass Rule')
    md.append('')
    md.append('This atlas is intentionally compact. Substrate detail lives in')
    md.append('each producer\'s own artifacts (see `coupled_lattice_phase_scan.md`,')
    md.append('`dense_local_emergence_scan.md`, `chimera_lab_genomes.md`). The')
    md.append('atlas is a navigation index, not a replacement for the originals.')
    md.append('')
    md.append('## Post-M8 correction')
    md.append('')
    md.append('`complexity_atlas_metrics.json` was originally reported as one')
    md.append('substrate (9 keys). It is actually a *bundle* of four parallel')
    md.append('scans: `logistic_entropy` (r ∈ [2.5, 4.0]), `logistic_lyapunov`')
    md.append('(same axis), `rule30_entropy` (ρ ∈ [0, 1]), and `kuramoto_order`')
    md.append('(k ∈ [0, 4]). The atlas now lists them as four substrates plus a')
    md.append('fifth `atlas_metric_transitions` entry for the 5 transition scalars.')

    with open(OUT / 'unified_atlas_v1.md', 'w') as f:
        f.write('\n'.join(md))

    print(f'Wrote {out_path}')
    print(f'Wrote unified_atlas_v1.md')
    print()
    print('Atlas summary:')
    for name, fp in fingerprints.items():
        status = fp.get('status', 'ok')
        records = fp.get('records', fp.get('key_count', '-'))
        if isinstance(records, list):
            records = f'list[{len(records)}]'
        print(f'  {name:30s}  records={records!s:>10s}  status={status}')


if __name__ == '__main__':
    main()
