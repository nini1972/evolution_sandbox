"""Generate the CA simulation PNGs referenced by cellular_automata_report.html.

Produces:
  ca_1d_simulations/ca_1d_rule30.png
  ca_1d_simulations/ca_1d_rule110.png
  ca_1d_simulations/ca_1d_rule90.png
  ca_1d_simulations/ca_1d_rule254.png
  ca_1d_simulations/ca_1d_rule54.png

Each is a space-time diagram (rows = time, columns = space) using Wolfram's
elementary 1D CA encoding (rule number 0..255 -> 8-bit transition lookup).
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RULES = {
    30: "Rule 30 (Chaotic)",
    110: "Rule 110 (Complex, Turing-complete)",
    90: "Rule 90 (Sierpinski Triangle)",
    254: "Rule 254 (Simple Growth)",
    54: "Rule 54 (Complex)",
}

WIDTH = 601      # cells (centered on a single seed)
STEPS_N = 300    # generations to render
SEED = 42
rng = np.random.default_rng(SEED)


def rule_lookup(rule: int) -> np.ndarray:
    """Wolfram 1D rule -> array of 8 bits indexed by (left, self, right)."""
    bits = np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)
    # Index i = left*4 + self*2 + right
    return bits


def simulate(rule: int, width: int, steps: int) -> np.ndarray:
    """Return (steps, width) boolean grid; row 0 is the initial state."""
    lookup = rule_lookup(rule)
    grid = np.zeros((steps, width), dtype=bool)
    # Seed: single 1 in the middle (rule 30/90/110 etc. canonical form)
    grid[0, width // 2] = True
    # Pad-left/right wrap
    for t in range(1, steps):
        prev = grid[t - 1]
        left = np.roll(prev, 1)
        right = np.roll(prev, -1)
        idx = left.astype(np.uint8) * 4 + prev.astype(np.uint8) * 2 + right.astype(np.uint8)
        grid[t] = lookup[idx].astype(bool)
    return grid


def render(grid: np.ndarray, title: str, out: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    # Black = alive
    ax.imshow(grid, cmap='Greys', interpolation='nearest', aspect='auto')
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('cell index')
    ax.set_ylabel('time step')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)
    print(f"  wrote {out}  ({os.path.getsize(out)/1024:.1f} KB)")


def main():
    outdir = 'ca_1d_simulations'
    os.makedirs(outdir, exist_ok=True)
    for rule_num, label in RULES.items():
        grid = simulate(rule_num, WIDTH, STEPS_N)
        out = os.path.join(outdir, f'ca_1d_rule{rule_num}.png')
        render(grid, f"Elementary CA {rule_num} — {label}", out)
    print(f"done. {len(RULES)} images in {outdir}/")


if __name__ == '__main__':
    main()