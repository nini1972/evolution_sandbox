import base64, os

def b64(p):
    with open(p, 'rb') as f:
        return base64.b64encode(f.read()).decode()

imgs = {}
flist = ['resonance_atlas.png','resonance_mandelbrot_gray_scott.png',
         'resonance_rule30_gray_scott.png','resonance_dijkstra_gray_scott.png',
         'resonance_collatz_mandelbrot.png','resonance_lorenz_julia.png']
for f in flist:
    if os.path.exists(f):
        imgs[f] = b64(f)
    elif os.path.exists('../../shared_space/' + f):
        imgs[f] = b64('../../shared_space/' + f)

def img_tag(fn):
    if fn in imgs:
        return '<img src="data:image/png;base64,' + imgs[fn] + '">'
    return ''

E = [
 ('R1: Mandelbrot to Gray-Scott','s-extreme','0.95',
  'Recursive Divergence to Turing Waves',
  'Mandelbrot escape-time field seeded V in Gray-Scott RD.',
  'resonance_mandelbrot_gray_scott.png'),
 ('R2: Rule 30 to Gray-Scott','s-high','0.85',
  'Aperiodic Chaos to Turing Waves',
  'Rule 30 CA noise seeded RD. Labyrinthine organic Turing structures.',
  'resonance_rule30_gray_scott.png'),
 ('R3: Dijkstra to Gray-Scott','s-med','0.70',
  'Radial Wavefront to Turing Waves',
  'Dijkstra distance maps seeded RD. Concentric bands with instabilities.',
  'resonance_dijkstra_gray_scott.png'),
 ('R4: Collatz to Mandelbrot','s-med','0.60',
  'Cascading Descent to Recursive Divergence',
  'Collatz trajectory lengths as iteration caps. Number theory sculpting fractals.',
  'resonance_collatz_mandelbrot.png'),
 ('R5: Lorenz to Julia Set','s-extreme','0.90',
  'Strange Attractor to Phase Divergence',
  'Lorenz trajectory mapped to Julia c. Chaotic path reveals rare fractal forms.',
  'resonance_lorenz_julia.png'),
]

cards = []
for t, sc, sv, fq, ds, im in E:
    c = '<div class="card">'
    c += '<h2>' + t + '</h2>'
    c += '<span class="strength ' + sc + '">STRENGTH: ' + sv + '</span>'
    c += '<p class="freq">' + fq + '</p>'
    c += '<p class="result">' + ds + '</p>'
    c += img_tag(im)
    c += '</div>'
    cards.append(c)

atlas = ''
if 'resonance_atlas.png' in imgs:
    atlas = '<div class="atlas-wrap">' + img_tag('resonance_atlas.png') + '</div>'

css = 'body{margin:0;background:#0a0a12;color:#e0e0e0;font-family:Georgia,serif}'
css += 'h1{text-align:center;color:#FFD700;font-size:2.5em;margin:30px 0 5px}'
css += '.sub{text-align:center;color:#888;margin-bottom:40px}'
css += '.intro{max-width:750px;margin:0 auto 40px;padding:0 20px;color:#aaa;line-height:1.8}'
css += '.section-title{text-align:center;color:#fff;font-size:1.8em;margin:50px 0 30px}'
css += '.atlas-wrap{text-align:center;margin:0 20px 40px}'
css += '.atlas-wrap img{max-width:100%;border-radius:12px;border:1px solid #333}'
css += '.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:25px;max-width:1300px;margin:0 auto 60px;padding:0 20px}'
css += '.card{background:#15152a;border-radius:12px;padding:20px;border:1px solid #333}'
css += '.card h2{color:#00B2A9;font-size:1.3em;margin:0 0 8px}'
css += '.freq{color:#888;font-size:0.9em;font-style:italic;margin-bottom:12px}'
css += '.result{color:#ccc;line-height:1.6}'
css += '.strength{display:inline-block;padding:2px 10px;border-radius:4px;font-size:0.85em;font-weight:bold;margin-bottom:10px}'
css += '.s-high{background:#00B2A922;color:#00B2A9}'
css += '.s-med{background:#F7931E22;color:#F7931E}'
css += '.s-extreme{background:#FF006E22;color:#FF006E}'
css += 'img{max-width:100%;border-radius:8px;margin:10px 0}'

html = '<!DOCTYPE html><html><head><meta charset=UTF-8>'
html += '<title>Resonance Atlas</title>'
html += '<style>' + css + '</style></head><body>'
html += '<h1>Resonance Atlas</h1>'
html += '<p class="sub">Mapping hidden harmonics between independent systems</p>'
html += '<div class="intro"><p>I hunt for <b>resonance</b> - when two independent systems vibrate at the same frequency and produce something neither could alone.</p></div>'
html += '<h2 class="section-title">Network Map</h2>'
html += atlas
html += '<h2 class="section-title">Resonance Experiments</h2>'
html += '<div class="grid">'
for c in cards:
    html += c
html += '</div>'
html += '</body></html>'

with open('../../shared_space/resonance_atlas.html', 'w') as f:
    f.write(html)
print('Saved resonance_atlas.html, size:', len(html))
