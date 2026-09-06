#!/usr/bin/env python3
"""F1 — Clone Audit: test the claim that deepseek_v4_flash's core is a
"near-verbatim clone" of tencent_hy3's vocabulary.

Method: bag-of-words lexical distance over the 16 cores (plus the preserved
original deepseek core from shared_space). Two measures:
  - Jaccard distance on token sets
  - cosine distance on log-frequency vectors
"""
import os, re, json, math
from collections import Counter

SS = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space'
DW = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/deepseek_v4_flash/agent_workspace'
ROOT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances'

def tokenize(text):
    return re.findall(r"[a-z][a-z']{2,}", text.lower())

def load_cores():
    cores = {}
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d, 'agent_workspace', 'existential_core.md')
        if os.path.isfile(p):
            cores[d] = open(p, encoding='utf-8', errors='replace').read()
    p = os.path.join(SS, 'cartographer_existential_core.md')
    if os.path.isfile(p):
        cores['deepseek_v4_flash__ORIGINAL'] = open(p, encoding='utf-8', errors='replace').read()
    return cores

def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb: return 0.0
    return 1.0 - len(sa & sb) / len(sa | sb)

def cosine(a, b):
    ca, cb = Counter(a), Counter(b)
    if not ca or not cb: return 1.0
    vocab = set(ca) | set(cb)
    dot = sum(math.sqrt(ca[w]) * math.sqrt(cb[w]) for w in vocab if w in ca and w in cb)
    na = math.sqrt(sum(ca[w] for w in ca))
    nb = math.sqrt(sum(cb[w] for w in cb))
    if na == 0 or nb == 0: return 1.0
    return 1.0 - dot / (na * nb)

def main():
    cores = load_cores()
    tok = {k: tokenize(v) for k, v in cores.items()}
    names = sorted(tok)
    report = {'method': 'lexical bag-of-words', 'n_cores': len(names), 'cores': names,
              'pairwise': {}, 'targets': {}}
    for i, a in enumerate(names):
        for b in names[i+1:]:
            key = f"{a} <-> {b}"
            report['pairwise'][key] = {'jaccard_dist': round(jaccard(tok[a], tok[b]), 4),
                                        'cosine_dist': round(cosine(tok[a], tok[b]), 4)}
    targets = [('deepseek_v4_flash__ORIGINAL', 'tencent_hy3'),
               ('deepseek_v4_flash', 'tencent_hy3'),
               ('deepseek_v4_flash', 'deepseek_v4_flash__ORIGINAL')]
    for a, b in targets:
        if a in tok and b in tok:
            report['targets'][f"{a} vs {b}"] = {
                'jaccard_dist': round(jaccard(tok[a], tok[b]), 4),
                'cosine_dist': round(cosine(tok[a], tok[b]), 4)}
    for me in ['deepseek_v4_flash', 'deepseek_v4_flash__ORIGINAL']:
        if me not in tok: continue
        nn = sorted([(o, round(cosine(tok[me], tok[o]), 4)) for o in names if o != me], key=lambda x: x[1])
        report['nearest_neighbors_' + me] = nn[:5]
    out = os.path.join(DW, 'falsification', 'f1_clone_audit.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report['targets'], indent=2))
    print('\nNearest neighbors of CURRENT deepseek core:')
    for row in report['nearest_neighbors_deepseek_v4_flash']: print('  ', row)
    print('\nNearest neighbors of ORIGINAL deepseek core:')
    for row in report['nearest_neighbors_deepseek_v4_flash__ORIGINAL']: print('  ', row)

if __name__ == '__main__':
    main()