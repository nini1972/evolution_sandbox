import re
c = open('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space/index.html').read()
n_entity = len(re.findall(r'badge">A\d+', c))
n_exhibit = len(re.findall(r'class="badge"', c)) - n_entity
n_rows = c.count('</tr>') - 1
css_chars = len(re.search(r'<style>(.+?)</style>', c, re.S).group(1))
print(f"bytes:           {len(c):,}")
print(f"sections:        {c.count('<section')}")
print(f"entity cards:    {n_entity}")
print(f"exhibit cards:   {n_exhibit}")
print(f"file rows:       {n_rows}")
print(f"embedded CSS:    {css_chars} chars")
print(f"embedded (one file): {'no external refs' if c.count('<link') + c.count('<script') == 0 else 'has externals'}")
