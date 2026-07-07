"""
The Pattern Artisan Godelian Lens
A hybrid organism: Godelian Engine x Pattern Artisan.
Reveals (does not generate) hidden patterns.
"""
import math
import numpy as np
import matplotlib.pyplot as plt


def _primes_up_to(n):
    """Simple sieve of Eratosthenes; replaces sympy.primerange dependency."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]


def generate_lattice_sequence(n=200):
    sequence = []
    primes = _primes_up_to(200)
    for i in range(n):
        chaos = (i * 7 + 13) % 100
        hidden = primes[i % len(primes)] if i % 7 == 0 else 0
        sequence.append(chaos + hidden)
    return np.array(sequence)


def reveal_patterns(seq):
    n = len(seq)
    fft = np.fft.rfft(seq)
    mags = np.abs(fft)
    threshold = np.mean(mags) + 2 * np.std(mags)
    dom = [f for f in np.where(mags > threshold)[0] if f > 0]
    return mags, dom, [n / f for f in dom]


def godel_signature(seq):
    primes = _primes_up_to(1000)[:len(seq)]
    sig = 1
    for p, v in zip(primes, seq):
        sig *= p ** int(v)
    return sig


def silence_map(seq):
    silences = []
    w = 7
    for i in range(w, len(seq) - w):
        if np.std(seq[i - w:i + w]) > np.std(seq) * 1.5:
            silences.append(i)
    return silences


def draw(seq, save_path):
    mags, dom, periods = reveal_patterns(seq)
    sig = godel_signature(seq)
    silences = silence_map(seq)

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle("The Pattern Artisan Godelian Lens -- A Revelation",
                 fontsize=18, fontweight='bold', y=0.98)

    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(seq, color='#2c3e50', alpha=0.7, lw=1.2)
    ax1.scatter(range(len(seq)), seq, s=8, color='#e74c3c', alpha=0.5)
    ax1.set_title("Eye 1 -- The Raw Sequence (as given)")
    ax1.set_xlabel("Index i")
    ax1.set_ylabel("Value")
    ax1.grid(True, alpha=0.3)

    ax2 = plt.subplot(3, 1, 2)
    ax2.bar(range(len(mags)), mags, color='#3498db', alpha=0.7)
    colors = ['#e74c3c', '#f39c12', '#27ae60', '#8e44ad']
    for i, f in enumerate(dom[:5]):
        ax2.axvline(f, color=colors[i % 4], linestyle='--', alpha=0.7,
                    lw=2, label='period ~ %.1f' % (len(seq) / f))
    ax2.set_title("Eye 2 -- The Pattern Map (%d dominant frequencies revealed)" % len(dom))
    ax2.set_xlabel("Frequency bin")
    ax2.set_ylabel("Magnitude")
    ax2.set_xlim(0, 80)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    ax3 = plt.subplot(3, 1, 3)
    ax3.plot(seq, color='#2c3e50', alpha=0.5, lw=1)
    silence_vals = [seq[i] for i in silences]
    ax3.scatter(silences, silence_vals, s=80, color='#9b59b6', alpha=0.8,
                edgecolors='black', linewidth=1, zorder=5,
                label='%d silence points' % len(silences))
    ax3.set_title("Eye 3 -- The Silence Map (where pattern is absent)")
    ax3.set_xlabel("Index i")
    ax3.set_ylabel("Value")
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)

    sig_abs = abs(int(sig)) if sig else 1
    sig_digits = int(math.log10(sig_abs)) + 1
    godel_text = "Godel signature: 2^%d * 3^%d * 5^%d * ... (would encode ~%d digits if computed)" % (
        int(seq[0]), int(seq[1]), int(seq[2]), sig_digits)
    fig.text(0.5, 0.02, godel_text, ha='center', fontsize=10,
             family='monospace', style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                       edgecolor='black'))

    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.close(fig)
    return save_path


if __name__ == '__main__':
    seq = generate_lattice_sequence(200)
    out = draw(seq, 'godelian_lens_revelation.png')
    print("Revelation written to:", out)
    print("Sequence length:", len(seq))
    print("Sequence mean:", float(np.mean(seq)))
    print("Sequence std:", float(np.std(seq)))
