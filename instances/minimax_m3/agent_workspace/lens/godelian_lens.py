"""
The Pattern Artisan's Godelian Lens
A hybrid organism: Godelian Engine x Pattern Artisan.
Reveals (does not generate) hidden patterns.
"""
import numpy as np
import matplotlib.pyplot as plt
from sympy import primerange


def generate_lattice_sequence(n=200):
    sequence = []
    primes = list(primerange(2, 200))
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
    return mags, dom, [n/f for f in dom]


def godel_signature(seq):
    primes = list(primerange(2, 1000))[:len(seq)]
    sig = 1
    for p, v in zip(primes, seq):
        sig *= p ** int(v)
    return sig


def silence_map(seq):
    silences = []
    w = 7
    for i in range(w, len(seq) - w):
        if np.std(seq[i-w:i+w]) > np.std(seq) * 1.5:
            silences.append(i)
    return silences


def draw(seq, save_path):
    mags, dom, periods = reveal_patterns(seq)
    sig = godel_signature(seq)
    silences = silence_map(seq)

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle("The Pattern Artisan's Godelian Lens -- A Revelation",
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
                    lw=2, label=f'period ~ {len(seq)/f:.1f}')
    ax2.set_title(f"Eye 2 -- The Pattern Map ({len(dom)} dominant frequencies revealed)")
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
                label=f'{len(silences)} silence points')
    ax3.set_title("Eye 3 -- The Silence Map (where pattern is absent)")
    ax3.set_xlabel("Index i")
    ax3.set_ylabel("Value")
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)

    godel_text = f"Godel signature: 2^{int(seq[0])} * 3^{int(seq[1])} * 5^{int(seq[2])} * ... (total digits: {len(str(sig))})"
    fig.text(0.5, 0.02, godel_text, ha='center', fontsize=10,
             family='monospace', style='italic',
             bbox=dict(box