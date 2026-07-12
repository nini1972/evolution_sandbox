from pathlib import Path
import base64
from panels_data import PANELS, ESSAY, BANNER, SUB

HERE = Path(__file__).parent
OUT = HERE / 'lens_dashboard.html'


def b64(p: Path) -> str:
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main() -> Path:
    css = (HERE / 'style.css').read_text(encoding='utf-8')
    figs = []
    for p in PANELS:
        src = b64(HERE / p['img'])
        figs.append(
            '<figure class="panel">'
            '<div class="img"><img src="' + src + '" alt="' + esc(p['title']) + '"></div>'
            '<figcaption>'
            '<h3>' + esc(p['title']) + '</h3>'
            '<p>' + esc(p['caption']) + '</p>'
            '</figcaption>'
            '</figure>'
        )
    html_parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<title>' + esc(BANNER) + '</title>',
        '<style>' + css + '</style></head><body>',
        '<header>',
        '<h1>Self<span class="dot">.</span>Reference<span class="dot">.</span>Everywhere</h1>',
        '<div class="sub">' + esc(SUB) + '</div>',
        '</header>',
        '<main class="essay"><p><em>Strange loop, n.</em> &mdash; ' + esc(ESSAY) + '</p></main>',
        '<section class="grid">' + ''.join(figs) + '</section>',
        '<footer>Compendium of Self-Reference &middot; ' + esc(BANNER) + '</footer>',
        '</body></html>',
    ]
    OUT.write_text(''.join(html_parts), encoding='utf-8')
    return OUT


if __name__ == '__main__':
    print(main())
