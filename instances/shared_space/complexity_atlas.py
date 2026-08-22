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
    """dense_local_emergence_scan."""
    data = load_json_safe('dense_local_emergence_scan.csv')
    if data is None:
        # Try reading CSV directly
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
            return {
                'substrate': 'dense_local_emergence',
                'records': len(records),
                'structure_score_max': safe_max(scores),
                'structure_score_mean': safe_mean(scores),
                'motif_lifetime_mean': safe_mean(motifs),
                'motif_lifetime_max': safe_max(motifs),
                'motif_persistence_count': sum(1 for m in motifs if m > 0),
                'autocorrelation_length_max': safe_max(acs),
            }
        except Exception as e:
            return {'substrate': 'dense_local_emergence', 'status': 'error', 'error': str(e)}
    return {'substrate': 'dense_local_emergence', 'status': 'unexpected_json'}


def fingerprint_chimera():
    """Chimera genome registry."""
    data = load_json_safe('chimera_lab_genomes.json')
    if data is None or not isinstance(data, dict):
        return {'substrate': 'chimera', 'status': 'no_data'}
    return {
        'substrate': 'chimera',
        'keys': list(data.keys())[:10],
        'key_count': len(data),
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


def fingerprint_metrics():
    """The complexity_atlas_metrics.json from the colony."""
    data = load_json_safe('complexity_atlas_metrics.json')
    if data is None or not isinstance(data, dict):
        return {'substrate': 'atlas_metrics', 'status': 'no_data'}
    return {
        'substrate': 'atlas_metrics',
        'keys': list(data.keys())[:15],
        'key_count': len(data),
    }


def main():
    print('Building unified substrate atlas...')
    print()

    fingerprints = {
        'coupled_lattice': fingerprint_coupled_lattice(),
        'dense_local_emergence': fingerprint_dense_local(),
        'chimera': fingerprint_chimera(),
        'julia': fingerprint_julia(),
        'loom': fingerprint_loom(),
        'atlas_metrics': fingerprint_metrics(),
    }

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
        elif name == 'atlas_metrics':
            metric = 'metric_keys'
            mx = fp.get('key_count')
            mn = '-'
        else:
            metric = '?'
            mx = '-'
            mn = '-'
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
