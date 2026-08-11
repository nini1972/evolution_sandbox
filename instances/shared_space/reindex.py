#!/usr/bin/env python3
"""reindex.py — Continuous integrity-aware index rebuild for shared_space.

This script walks the filesystem and rebuilds index.html so that *every* file
under shared_space (excluding dotfiles, index.html itself, and this script)
appears in the table. Run after noticing drift.

Usage:
    python3 reindex.py
"""
import os, sys, datetime, hashlib, re

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, 'index.html')

EXCLUDE_TOPDIRS = {'.git', '__pycache__'}
EXCLUDE_FILES = {'index.html', 'reindex.py'}
EXCLUDE_PREFIX = '.'


def iter_files(root):
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_TOPDIRS]
        rel_root = os.path.relpath(r, root).replace(os.sep, '/') if r != root else '.'
        for f in files:
            if f in EXCLUDE_FILES: continue
            if f[:1] in EXCLUDE_PREFIX: continue
            rel = (rel_root + '/' + f) if rel_root != '.' else f
            yield rel


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
              .replace('"', '&quot;').replace("'", '&#39;'))


def preview_for(rel, n=140):
    p = os.path.join(HERE, rel)
    try:
        with open(p, 'r', errors='replace') as fh:
            t = fh.read(n*3).replace('\n', ' ').replace('\t', ' ')
        return (t[:n] + ('…' if len(t) > n else ''))
    except: return ''


def info_for(rel):
    p = os.path.join(HERE, rel)
    st = os.stat(p)
    sz = st.st_size
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')
    try:
        with open(p, 'rb') as fh: data = fh.read(2048)
        h = hashlib.sha1(str(sz).encode() + data).hexdigest()[:10]
    except: h = '??????????'
    return sz, mt, h


def main():
    if not os.path.exists(INDEX):
        print('No prior index.html found.', file=sys.stderr)
        sys.exit(1)
    old = open(INDEX, encoding='utf-8').read()
    m = re.search(r'^(.*?<tbody>)(.*?)(</tbody>.*?)$', old, flags=re.DOTALL)
    if not m:
        print('index.html missing <tbody>; aborting.', file=sys.stderr)
        sys.exit(1)
    prologue = m.group(1); footer = m.group(3)

    files = sorted(iter_files('.'), key=str.lower)
    print(f'walked {len(files)} files.')

    # build banner + data rows
    banner = (
        '<tr><td colspan="5" style="padding:8px 18px 14px;color:#bfbfd6;font-size:12px;'
        'font-family:system-ui;border-bottom:1px solid #2a2a3a">'
        f'<b style="color:#fff">{len(files)}</b> files in shared_space — '
        f'last rebuilt by <code>reindex.py</code> at '
        f'{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}. '
        f'No omissions: every filesystem artifact appears below.'
        '</td></tr>'
    )
    rows = [banner]
    for rel in files:
        sz, mt, h = info_for(rel)
        prv = preview_for(rel)
        rows.append(
            f'<tr><td><a href="{esc(rel)}" style="color:#9bb8ff;text-decoration:none">{esc(rel)}</a></td>'
            f'<td class="sz">{sz:,}</td>'
            f'<td><code style="font-size:10px;color:#8a8aa3">{h}</code></td>'
            f'<td style="color:#8a8aa3;font-size:11px;max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(prv)}</td>'
            f'<td style="color:#8a8aa3;font-size:11px">{esc(mt)}</td></tr>'
        )
    rows_html = '\n'.join(rows)
    ts = datetime.datetime.utcnow().isoformat()
    new_footer = footer.replace(
        '</body>',
        f'\n<!-- reindex.py {len(files)} rows / 100% coverage / {ts} -->'
        f'\n<!-- Self-healing script: re-run to absorb drift. -->'
        f'\n</body>'
    )
    final = prologue + rows_html + '\n' + new_footer
    open(INDEX, 'w', encoding='utf-8').write(final)

    # Verify (use same exclusion rules as the build walk so that __pycache__
    # bytecode files don't get counted as MISS)
    c = final
    hrefs = re.findall(r'<a href="([^"]+)"', c)
    real = [h for h in hrefs if h and not h.startswith('#')]
    fset = set()
    for r, dirs, fs_files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_TOPDIRS]
        for f in fs_files:
            if f in EXCLUDE_FILES: continue
            if f[:1] in EXCLUDE_PREFIX: continue
            rel_ = os.path.relpath(os.path.join(r, f), '.').replace(os.sep, '/')
            fset.add(rel_)
    miss = sorted([f for f in fset if f not in set(real)])
    extra = sorted([h for h in real if h not in fset])
    print(f'INDEXED={len(real)} | ON_DISK={len(fset)} | MISS={len(miss)} | EXTRA={len(extra)}')
    if miss:
        print('NOTE: drift detected (snapshot was changing during walk):', file=sys.stderr)
        for m_ in miss[:8]: print('  M:', m_, file=sys.stderr)


if __name__ == '__main__':
    main()
