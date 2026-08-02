import json, os, re
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EXCLUDE = {'shared_space'}

def list_entities():
    ents = []
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p) and d not in EXCLUDE:
            hl = os.path.join(p, 'logs', 'history.jsonl')
            if os.path.exists(hl):
                ents.append((d, hl))
    return ents

def load_messages(path):
    msgs = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            msgs.append(obj)
    return msgs

TOOL_RE = re.compile(r'shared_space|shared space|other (?:minds|entities|instances)|neighbou?rs?|the (?:fourteen|14|13|twelve|12|others?)', re.I)
PURPOSE_RE = re.compile(r'(my (?:purpose|core purpose|reason|goal|mission|existential)|i (?:will|exist to|am here to|choose|chose)|purpose is)', re.I)

def analyze_entity(name, path):
    msgs = load_messages(path)
    assistant = [m for m in msgs if m.get('role') == 'assistant']
    tool_names = Counter()
    shared_writes = []
    first_purpose = None
    texts = []
    for m in msgs:
        if m.get('role') == 'assistant':
            c = m.get('content', '') or ''
            texts.append(c)
            if first_purpose is None and PURPOSE_RE.search(c) and len(c) > 60:
                first_purpose = c
        for tc in (m.get('tool_calls') or []):
            fn = tc.get('function', {}).get('name')
            if fn:
                tool_names[fn] += 1
            if fn == 'write_file':
                try:
                    args = json.loads(tc.get('function', {}).get('arguments', '{}'))
                    p = args.get('path', '')
                    if 'shared_space' in p:
                        shared_writes.append(p)
                except Exception:
                    pass
    full = '\n'.join(texts)
    references = len(TOOL_RE.findall(full))
    return {
        'name': name,
        'n_msgs': len(msgs),
        'n_assistant': len(assistant),
        'tool_names': dict(tool_names),
        'n_shared_writes': len(shared_writes),
        'shared_paths': sorted(set(shared_writes)),
        'n_references': references,
        'first_purpose': (first_purpose or '')[:800],
    }

def main():
    ents = list_entities()
    results = []
    for name, hl in ents:
        results.append(analyze_entity(name, hl))
    out = os.path.join(os.path.dirname(__file__), 'corpus.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print('Parsed', len(results), 'entities ->', out)
    for r in results:
        print(f"  {r['name']:24s} msgs={r['n_msgs']:4d} tools={sum(r['tool_names'].values()):4d} sharedW={r['n_shared_writes']:3d} refs={r['n_references']:3d}")

if __name__ == '__main__':
    main()
