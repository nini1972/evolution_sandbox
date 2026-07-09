"""Lens 3: Hofstadter's Q-sequence — a sequence that defines itself."""
import math
import numpy as np
import matplotlib.pyplot as plt


def q_recursive(n, memo):
    if n in memo:
        return memo[n]
    qn_1 = q_recursive(n - 1, memo)
    s = q_recursive(n - qn_1, memo)
    memo[n] = s
    return s


def q_sequence(N=4000):
    memo = {0: 0, 1: 1, 2: 1}
    return np.array([q_recursive(i, memo) for i in range(1, N + 1)], dtype=float)


def draw(N=2000, save_path='hofstadter_q.png'):
    q = q_sequence(N)
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#000')
    ax.set_facecolor('#000')
    ax.plot(q, color='#9bf', lw=0.6)
    ax.set_title('Hofstadter Q-sequence: a number that knows itself',
                 color='white', fontsize=13)
    ax.set_xlabel('n', color='white')
    ax.set_ylabel('Q(n)', color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#444')
    plt.tight_layout()
    plt.savefig(save_path, dpi=130, facecolor='#000')
    plt.close()
    return save_path, q


if __name__ == '__main__':
    path, q = draw()
    print('wrote', path)
    print('last 5:', q[-5:])
