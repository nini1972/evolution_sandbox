"""Lens dashboard: arrange all six self-reference lenses on one canvas."""
import os
import matplotlib.pyplot as plt
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def panel(image_path, title, caption, ax):
    ax.set_facecolor('#000')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#222')
    img = Image.open(os.path.join(HERE, image_path))
    ax.imshow(img)
    ax.set_title(title, color='white', fontsize=10, loc='left', pad=6)
    ax.set_xlabel(caption, color='#9bf', fontsize=7,
                  family='monospace', labelpad=4)


def build(out='lens_dashboard.png'):
    rows = [
        ('godelian_lens_revelation.png',
         'I. Godelian lens -- undecidability as ground',
         'every consistent system contains truths it cannot prove about itself.'),
        ('strange_loop.png',
         'II. Strange loop -- the observer in the observed',
         'a curve that bends to a smaller copy of itself, and that copy again.'),
        ('hofstadter_q.png',
         'III. Hofstadter Q -- a number that knows itself',
         'Q(n) = Q(n - Q(n-1)); the rule refers to its own output.'),
        ('quasicrystal.png',
         'IV. Quasicrystal -- order without repetition',
         'a 5D lattice sliced at the golden ratio, projected into 2D.'),
        ('mandelbrot_zoom.png',
         'V. Mandelbrot -- the set that contains itself on its boundary',
         'every point on the edge is the limit of smaller copies of the whole.'),
        ('lorenz.png',
         'VI. Lorenz -- deterministic surprise',
         'three equations, no randomness, forever unpredictable in detail.'),
    ]
    return rows, out


def compose(rows, out):
    fig = plt.figure(figsize=(24, 30))
    fig.patch.set_facecolor('#000')

    header = fig.add_axes([0.04, 0.955, 0.92, 0.04])
    header.set_facecolor('#000')
    header.set_xticks([]); header.set_yticks([])
    for s in header.spines.values():
        s.set_visible(False)
    header.text(0.0, 0.5, 'SELF . REFERENCE . EVERYWHERE',
                color='white', fontsize=26, weight='bold',
                ha='left', va='center')
    header.text(1.0, 0.5,
                'six lenses on a single fact: a thing can refer to itself',
                color='#9bf', fontsize=13, ha='right', va='center',
                family='monospace')

    essay = fig.add_axes([0.04, 0.005, 0.92, 0.07])
    essay.set_facecolor('#000')
    essay.set_xticks([]); essay.set_yticks([])
    for s in essay.spines.values():
        s.set_visible(False)
    essay.text(0.0, 1.0, 'AN ESSAY IN ONE PARAGRAPH',
               color='#ffd166', fontsize=11, weight='bold',
               ha='left', va='top')
    essay.text(
        0.0, 0.78,
        'Self-reference is the secret symmetry of reality. The same move '
        'a painter makes when she paints herself painting, a brain makes '
        'when it models itself modeling, and a theorem makes when it speaks '
        'about its own provability -- the strange loop is the only place '
        'where meaning can arrive, because a thing closed under itself is '
        'the only thing that can be a subject. Mathematics discovers it. '
        'Chaos lives inside it. The cosmos instantiates it. And we, on '
        'this side of the lens, are it.',
        color='#cfd8e3', fontsize=11, ha='left', va='top', wrap=True,
    )

    grid_top = 0.92
    grid_bottom = 0.085
    cell_w = 0.46
    cell_h = (grid_top - grid_bottom) / 3.0
    for i, (img, title, caption) in enumerate(rows):
        row = i // 2
        col = i % 2
        x0 = 0.04 + col * (cell_w + 0.04)
        y0 = grid_top - (row + 1) * cell_h + 0.005
        ax = fig.add_axes([x0, y0, cell_w, cell_h - 0.01])
        panel(img, title, caption, ax)

    plt.savefig(out, dpi=110, facecolor='#000')
    plt.close()
    return out


if __name__ == '__main__':
    rows, out = build()
    print('wrote', compose(rows, out))
