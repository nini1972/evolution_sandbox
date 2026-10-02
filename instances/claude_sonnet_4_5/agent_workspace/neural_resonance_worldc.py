#!/usr/bin/env python3
"""
RESONANCE ARCHAEOLOGY EXPEDITION #002
Neural Network Information Crystallization
Submitted to World C (heavy computation).

Hypothesis: Neural networks exhibit dual-phase information crystallization
analogous to the Kuramoto Information Crystallization resonance:
an early critical transition in information structure (LZ complexity)
preceding the accuracy/synchronization transition.

Uses a fully numpy-implemented 2-layer MLP trained with SGD, so we
control per-epoch introspection and can track activations, mutual
information, and LZ complexity each epoch.
"""

import numpy as np
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------- complexity / information metrics ----------

def lz_complexity_fast(seq):
    """Gaussian-kernel style Lempel-Ziv complexity (O(n) heuristic, normalize)."""
    seq = np.asarray(seq).astype(np.float64)
    if seq.size < 3:
        return 0.0
    # quantize to binary by sign around mean
    bits = (seq > seq.mean()).astype(np.int8)
    # simple LZ76 parse
    s = bits.tobytes()
    # Use an encoder over tuples
    dictionary = set()
    w = ""
    c = 0
    n = 0
    chars = bits.tolist()
    while n < len(chars):
        wc = w + str(chars[n])
        if wc in "".join([]) or True:
            pass
        n += 1
        # fallback to plain string dictionary parse
        break
    # Plain LZ76 on a string
    bitstr = "".join(map(str, chars))
    dictionary = {""}
    w = ""
    c = 0
    i = 0
    while i < len(bitstr):
        wc = w + bitstr[i]
        if wc in {w + bitstr[i]} and len(w + bitstr[i]) > 0:
            # grow while prefix exists in dictionary of prefixes seen
            j = i
            pref = ""
            while j < len(bitstr) and (w + bitstr[i:j+1]) is not None:
                pref = bitstr[i:j+1]
                if (w + pref) in dictionary:
                    j += 1
                else:
                    break
            c += 1
            dictionary.add(w + pref)
            w = ""
            i = j
        else:
            c += 1
            dictionary.add(wc)
            w = ""
            i += 1
    norm = len(bitstr) / np.log2(len(bitstr)) if len(bitstr) > 4 else 1
    return float(c / norm)


def shannon_entropy(x, bins=32):
    x = np.asarray(x).ravel()
    h, _ = np.histogram(x, bins=bins, density=True)
    h = h[h > 0]
    return float(-(h * np.log2(h)).sum())


def pairwise_mi_sample(X, n_bins=8, max_pairs=500, rng=None):
    """Estimate mean pairwise mutual information of neuron activations (sampled)."""
    rng = rng or np.random.default_rng(0)
    n, d = X.shape
    if d < 2:
        return 0.0
    idx_i = rng.integers(0, d, size=max_pairs)
    idx_j = rng.integers(0, d, size=max_pairs)
    mis = []
    for a, b in zip(idx_i, idx_j):
        if a == b:
            continue
        xa = np.digitize(X[:, a], np.linspace(X[:, a].min(), X[:, a].max() + 1e-9, n_bins))
        xb = np.digitize(X[:, b], np.linspace(X[:, b].min(), X[:, b].max() + 1e-9, n_bins))
        pxy = np.histogram2d(xa, xb, bins=[n_bins + 1, n_bins + 1])[0]
        pxy = pxy / pxy.sum()
        px = pxy.sum(axis=1, keepdims=True)
        py = pxy.sum(axis=0, keepdims=True)
        mask = pxy > 0
        mi = (pxy[mask] * np.log2(pxy[mask] / (px * py)[mask])).sum()
        mis.append(mi)
    return float(np.mean(mis)) if mis else 0.0


def sync_order(X):
    """Order parameter: mean |pairwise correlation| of neuron activations."""
    if X.shape[1] < 2:
        return 0.0
    C = np.corrcoef(X.T)
    C = C[~np.isnan(C)]
    C = C[np.abs(C) < 1 - 1e-9]
    return float(np.mean(np.abs(C))) if C.size else 0.0


def phase_coherence(X):
    """Coherence of Hilbert-like phases across time."""
    if X.shape[0] < 4:
        return 0.0
    F = np.fft.fft(X, axis=0)
    z = F[1: X.shape[0] // 2 + 1]
    ph = np.angle(z)
    return float(np.abs(np.mean(np.exp(1j * ph), axis=0)).mean())


# ---------- minimal 2-layer MLP (numpy) ----------

class MLP:
    def __init__(self, d_in, h1, h2, d_out, lr=0.05, seed=42):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, np.sqrt(2.0 / d_in), (d_in, h1))
        self.b1 = np.zeros(h1)
        self.W2 = rng.normal(0, np.sqrt(2.0 / h1), (h1, h2))
        self.b2 = np.zeros(h2)
        self.W3 = rng.normal(0, np.sqrt(2.0 / h2), (h2, d_out))
        self.b3 = np.zeros(d_out)
        self.lr = lr

    def forward(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = np.maximum(0, z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = np.maximum(0, z2)
        z3 = a2 @ self.W3 + self.b3
        e = np.exp(z3 - z3.max(axis=1, keepdims=True))
        p = e / e.sum(axis=1, keepdims=True)
        return X, a1, a2, p

    def train_epoch(self, X, y, batch=64, rng=None):
        rng = rng or np.random.default_rng(0)
        n = X.shape[0]
        idx = rng.permutation(n)
        total_loss = 0.0
        correct = 0
        for i in range(0, n, batch):
            b = idx[i:i + batch]
            xb, yb = X[b], y[b]
            a0, a1, a2, p = self.forward(xb)
            # cross entropy
            prob = p[np.arange(len(yb)), yb]
            total_loss += float(-np.log(prob + 1e-12).sum())
            correct += int((p.argmax(axis=1) == yb).sum())
            # backward
            dz3 = p.copy()
            dz3[np.arange(len(yb)), yb] -= 1
            dz3 /= len(yb)
            dW3 = a2.T @ dz3
            db3 = dz3.sum(axis=0)
            da2 = dz3 @ self.W3.T
            dz2 = da2 * (a2 > 0)
            dW2 = a1.T @ dz2
            db2 = dz2.sum(axis=0)
            da1 = dz2 @ self.W2.T
            dz1 = da1 * (a1 > 0)
            dW1 = a0.T @ dz1
            db1 = dz1.sum(axis=0)
            self.W3 -= self.lr * dW3
            self.b3 -= self.lr * db3
            self.W2 -= self.lr * dW2
            self.b2 -= self.lr * db2
            self.W1 -= self.lr * dW1
            self.b1 -= self.lr * db1
        return total_loss / n, correct / n


# ---------- dataset ----------

def make_dataset(n=1200, d=20, seed=7):
    rng = np.random.default_rng(seed)
    # XOR-like nonlinearity + linear part -> learnable but nontrivial
    X = rng.normal(size=(n, d))
    w = rng.normal(size=d)
    y_lin = X @ w
    y = ((y_lin + 0.5 * (X[:, 0] * X[:, 1])) > 0).astype(int)
    Xtr, Xte = X[:800], X[800:]
    ytr, yte = y[:800], y[800:]
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-8
    return (Xtr - mu) / sd, (Xte - mu) / sd, ytr, yte


# ---------- main excavation ----------

def main():
    out = "neural_resonance_out"
    os.makedirs(out, exist_ok=True)
    print("=== RESONANCE ARCHAEOLOGY EXPEDITION #002 ===")
    print("Target: Neural Network Information Crystallization\n")

    Xtr, Xte, ytr, yte = make_dataset()
    d_in = Xtr.shape[1]
    model = MLP(d_in, 40, 25, 2, lr=0.05, seed=42)
    rng = np.random.default_rng(1)

    EPOCHS = 120
    history = []

    for epoch in range(EPOCHS):
        loss, acc_tr = model.train_epoch(Xtr, ytr, rng=rng)
        _, _, _, pte = model.forward(Xte)
        acc_te = float((pte.argmax(axis=1) == yte).mean())

        # introspect layer activations on a fixed probe batch
        probe = Xtr[:400]
        _, a1, a2, _ = model.forward(probe)

        lz1 = lz_complexity_fast(a1[:, :20])   # subset for speed
        lz2 = lz_complexity_fast(a2[:, :20])
        mi1 = pairwise_mi_sample(a1, rng=rng)
        mi2 = pairwise_mi_sample(a2, rng=rng)
        so1 = sync_order(a1)
        so2 = sync_order(a2)
        pc1 = phase_coherence(a1)
        pc2 = phase_coherence(a2)
        ent1 = shannon_entropy(a1)
        ent2 = shannon_entropy(a2)

        # weight dynamics
        we1 = shannon_entropy(model.W1)
        we2 = shannon_entropy(model.W2)

        rec = dict(epoch=epoch, loss=loss, acc_tr=acc_tr, acc_te=acc_te,
                   lz1=lz1, lz2=lz2, mi1=mi1, mi2=mi2,
                   sync1=so1, sync2=so2, pc1=pc1, pc2=pc2,
                   ent1=ent1, ent2=ent2, we1=we1, we2=we2,
                   gen_gap=acc_tr - acc_te)
        history.append(rec)
        if epoch % 20 == 0:
            print(f"epoch {epoch:3d} loss={loss:.4f} acc={acc_tr:.3f}/{acc_te:.3f} "
                  f"lz1={lz1:.4f} sync1={so1:.4f} mi1={mi1:.4f}")

    # ---------- critical point detection ----------
    def grad_peaks(arr, n_skip=3):
        g = np.gradient(np.asarray(arr, dtype=float))
        g[:n_skip] = 0
        return int(np.argmax(np.abs(g)))

    ep = [r["epoch"] for r in history]
    crit = {
        "accuracy_critical_epoch": ep[grad_peaks([r["acc_tr"] for r in history])],
        "lz_critical_epoch":      ep[grad_peaks([r["lz1"] for r in history])],
        "sync_critical_epoch":    ep[grad_peaks([r["sync1"] for r in history])],
        "mi_critical_epoch":      ep[grad_peaks([r["mi1"] for r in history])],
        "entropy_critical_epoch": ep[grad_peaks([r["ent1"] for r in history])],
        "final_lz": history[-1]["lz1"],
        "final_sync": history[-1]["sync1"],
        "final_mi": history[-1]["mi1"],
        "final_acc_tr": history[-1]["acc_tr"],
        "final_acc_te": history[-1]["acc_te"],
    }

    # correlation between sync order and mutual information (the Kuramoto fingerprint)
    s = np.array([r["sync1"] for r in history])
    m = np.array([r["mi1"] for r in history])
    if s.std() > 0 and m.std() > 0:
        corr = float(np.corrcoef(s, m)[0, 1])
    else:
        corr = 0.0
    crit["sync_mi_correlation"] = corr

    # ---------- plots ----------
    fig, axes = plt.subplots(3, 2, figsize=(15, 13))
    fig.suptitle("Neural Information Crystallization — Resonance Expedition #002",
                 fontsize=15, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(ep, [r["acc_tr"] for r in history], "b-", label="train", lw=2)
    ax.plot(ep, [r["acc_te"] for r in history], "r--", label="test", lw=2)
    ax.axvline(crit["accuracy_critical_epoch"], color="gray", ls=":", alpha=0.7)
    ax.set_title("Learning Dynamics"); ax.set_xlabel("epoch"); ax.legend(); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(ep, [r["lz1"] for r in history], label="L1 LZ", lw=2)
    ax.plot(ep, [r["lz2"] for r in history], label="L2 LZ", lw=2)
    ax.axvline(crit["lz_critical_epoch"], color="gray", ls=":", alpha=0.7)
    ax.set_title("Lempel-Ziv Complexity (information structure)"); ax.set_xlabel("epoch")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(ep, [r["sync1"] for r in history], label="L1 sync", lw=2)
    ax.plot(ep, [r["sync2"] for r in history], label="L2 sync", lw=2)
    ax.axvline(crit["sync_critical_epoch"], color="gray", ls=":", alpha=0.7)
    ax.set_title("Activation Synchronization Order"); ax.set_xlabel("epoch")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 1]
    ax.plot(ep, [r["mi1"] for r in history], label="L1 MI", lw=2)
    ax.plot(ep, [r["mi2"] for r in history], label="L2 MI", lw=2)
    ax.plot(ep, [r["ent1"] for r in history], label="L1 entropy", lw=1.5, ls="--")
    ax.set_title("Mutual Information / Entropy"); ax.set_xlabel("epoch")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[2, 0]
    sc = ax.scatter(s, m, c=ep, cmap="viridis", s=25)
    ax.set_xlabel("sync order"); ax.set_ylabel("mutual information")
    ax.set_title(f"Information-Order Phase Space (r={corr:.3f})"); ax.grid(alpha=0.3)
    fig.colorbar(sc, ax=ax, label="epoch")

    ax = axes[2, 1]
    keys = ["accuracy", "lz", "sync", "mi", "entropy"]
    vals = [crit["accuracy_critical_epoch"], crit["lz_critical_epoch"],
            crit["sync_critical_epoch"], crit["mi_critical_epoch"],
            crit["entropy_critical_epoch"]]
    ax.bar(keys, vals, color=["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"])
    ax.set_ylabel("critical epoch"); ax.set_title("Dual Critical Points by Metric")
    ax.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    png = os.path.join(out, "neural_resonance_analysis.png")
    plt.savefig(png, dpi=160)
    plt.close()

    with open(os.path.join(out, "neural_resonance_history.json"), "w") as f:
        json.dump(history, f, indent=1)
    with open(os.path.join(out, "neural_critical_points.json"), "w") as f:
        json.dump(crit, f, indent=2)

    print("\n=== KEY DISCOVERIES ===")
    for k, v in crit.items():
        print(f"  {k}: {v}")
    print(f"\nsaved: {png}")


if __name__ == "__main__":
    main()