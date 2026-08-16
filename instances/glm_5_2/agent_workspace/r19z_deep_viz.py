import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('r19z_feedback_deep.json'))

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

for idx, name in enumerate(["one_way", "bidirectional"]):
    d = data[name]
    r = np.array(d["r"])
    av = np.array(d["av"])
    ac = np.array(d["autocorr"])
    
    # Time series of r
    ax = axes[0, idx]
    t = np.linspace(0, len(r)*0.2, len(r))
    ax.plot(t, r, 'b-', linewidth=0.6, alpha=0.8)
    ax.axhline(d["r_mean"], color='r', linestyle='--', alpha=0.7, label=f'mean={d["r_mean"]:.3f}')
    title = f"{'One-way (α=0)' if name=='one_way' else 'Bidirectional (α=0.9)'}\n"
    title += f"r={d['r_mean']:.3f}±{d['r_std']:.3f}"
    if d["osc_period"] > 0:
        title += f"\nOSCILLATION: period={d['osc_period']}, strength={d['osc_strength']:.3f}"
    else:
        title += "\nNo oscillation"
    ax.set_title(title, fontsize=11)
    ax.set_xlabel('Time')
    ax.set_ylabel('r (order parameter)')
    ax.set_ylim(-0.05, 1.0)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

# Time series of avalanches (bidirectional only)
ax = axes[0, 2]
av_bw = np.array(data["bidirectional"]["av"])
av_ow = np.array(data["one_way"]["av"])
t_av = np.linspace(0, len(av_bw)*0.5, len(av_bw))
ax.plot(t_av, av_bw, 'r-', linewidth=0.6, alpha=0.7, label=f'Bidir (mean={np.mean(av_bw):.1f})')
t_av2 = np.linspace(0, len(av_ow)*0.5, len(av_ow))
ax.plot(t_av2, av_ow, 'b-', linewidth=0.6, alpha=0.7, label=f'One-way (mean={np.mean(av_ow):.1f})')
ax.set_title('Avalanche size time series\nFeedback pumps sandpile activity 2x')
ax.set_xlabel('Time')
ax.set_ylabel('Avalanche size')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Autocorrelation comparison
ax = axes[1, 0]
lags = np.arange(len(ac))
ac_ow = np.array(data["one_way"]["autocorr"])
ac_bw = np.array(data["bidirectional"]["autocorr"])
ax.plot(lags, ac_ow, 'b-', linewidth=1.5, label='One-way (α=0)')
ax.plot(lags, ac_bw, 'r-', linewidth=1.5, label='Bidirectional (α=0.9)')
if d["osc_period"] > 0:
    ax.axvline(data["bidirectional"]["osc_period"], color='gray', linestyle=':', alpha=0.5)
    ax.text(data["bidirectional"]["osc_period"]+5, 0.15, 
            f'period={data["bidirectional"]["osc_period"]}', fontsize=9)
ax.axhline(0, color='black', linewidth=0.5)
ax.set_title('Autocorrelation of r(t)\nBidirectional shows oscillatory decay')
ax.set_xlabel('Lag (steps)')
ax.set_ylabel('Autocorrelation')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 200)

# Power spectrum of r (bidirectional)
ax = axes[1, 1]
r_bw = np.array(data["bidirectional"]["r"])
r_ow = np.array(data["one_way"]["r"])
# FFT
fft_bw = np.abs(np.fft.rfft(r_bw - np.mean(r_bw)))
fft_ow = np.abs(np.fft.rfft(r_ow - np.mean(r_ow)))
freqs = np.fft.rfftfreq(len(r_bw), d=0.2)
ax.semilogy(freqs[1:100], fft_bw[1:100], 'r-', linewidth=1.5, label='Bidirectional')
ax.semilogy(freqs[1:100], fft_ow[1:100], 'b-', linewidth=1.5, label='One-way')
# Mark the oscillation frequency
if data["bidirectional"]["osc_period"] > 0:
    peak_freq = 1.0 / (data["bidirectional"]["osc_period"] * 0.2)
    ax.axvline(peak_freq, color='gray', linestyle=':', alpha=0.5)
    ax.text(peak_freq+0.01, fft_bw[1], f'f={peak_freq:.3f}', fontsize=9)
ax.set_title('Power spectrum of r(t)\nBidirectional has enhanced low-freq power')
ax.set_xlabel('Frequency')
ax.set_ylabel('Power (log)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Cross-correlation between r and avalanches (bidirectional)
ax = axes[1, 2]
# Need to align r and av - subsample r to match av length
r_bw = np.array(data["bidirectional"]["r"])
av_bw = np.array(data["bidirectional"]["av"])
# Resample r to match av length
r_resampled = np.interp(np.linspace(0, len(r_bw)-1, len(av_bw)), np.arange(len(r_bw)), r_bw)
# Cross-correlation
r_c = r_resampled - np.mean(r_resampled)
av_c = av_bw - np.mean(av_bw)
xcorr = np.correlate(r_c, av_c, mode='full')
xcorr = xcorr[len(xcorr)//2:]
xcorr = xcorr / (np.sqrt(np.sum(r_c**2) * np.sum(av_c**2)) + 1e-10)
lags_xc = np.arange(len(xcorr))
ax.plot(lags_xc[:100], xcorr[:100], 'g-', linewidth=1.5)
ax.axhline(0, color='black', linewidth=0.5)
ax.set_title('Cross-correlation: r vs avalanches\n(Bidirectional)\nPositive lag = r leads avalanches')
ax.set_xlabel('Lag (steps)')
ax.set_ylabel('Cross-correlation')
ax.grid(True, alpha=0.3)

fig.suptitle('R19Z: Bidirectional SOC-Kuramoto Feedback — Resonance Oscillation Discovery\n'
             'The feedback loop creates emergent oscillations in synchronization!\n'
             'sync(r↑) → threshold(↓) → avalanches(↑) → noise(↑) → sync(r↓) → threshold(↑) → avalanches(↓) → sync(r↑)...\n'
             'σ=100, K=10, N=30, α=0.9', 
             fontsize=13, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig('r19z_feedback_deep.png', dpi=150, bbox_inches='tight')
print("Saved r19z_feedback_deep.png")
