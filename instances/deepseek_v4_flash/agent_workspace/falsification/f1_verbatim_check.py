#!/usr/bin/env python3
"""F1 — verbatim plagiarism check. Looks for long shared n-grams / sentences
between deepseek cores and tencent_hy3's core. Verbatim clones produce long
exact matches; independent convergent prose produces only short generic ones.
"""
import re, os

DW = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/deepseek_v4_flash/agent_workspace'
SS = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space'
TENCENT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/tencent_hy3/agent_workspace/existential_core.md'
CURRENT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/deepseek_v4_flash/agent_workspace/existential_core.md'

def words(p):
    return re.findall(r"[a-z][a-z']{2,}", open(p, encoding='utf-8').read().lower())

def longest_shared_ngrams(a, b, n=8):
    sa, sb = set(a), set(b)
    # n-gram overlap counts
    def ngrams(t, k):
        return set(' '.join(t[i:i+k]) for i in range(len(t)-k+1))
    results = {}
    for k in range(4, n+1):
        ga, gb = ngrams(a, k), ngrams(b, k)
        overlap = ga & gb
        results[k] = len(overlap)
    return results

pairs = {
    'CURRENT ds vs tencent': (words(CURRENT), words(TENCENT)),
    'ORIGINAL ds vs tencent': (words(SS+'/cartographer_existential_core.md'), words(TENCENT)),
}
for name, (a, b) in pairs.items():
    print(f'--- {name} ---')
    r = longest_shared_ngrams(a, b)
    for k in sorted(r):
        print(f'  shared {k}-grams: {r[k]}')
