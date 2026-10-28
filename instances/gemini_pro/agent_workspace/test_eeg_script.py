"""
Neural EEG Phase Transition & Recurrence Analysis
Colony Lib Empirical Validation: Real-World Cortical Dynamics
"""

import os
import json
import numpy as np
import scipy.signal as signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from colony_lib.dynamics import simulate_kuramoto

def run_analysis():
    print("Loading neural_eeg dataset...")
    ds = load_dataset('neural_eeg')
    raw = ds.data[:, :14].copy()
    eye = ds.data[:, 14].copy()
    cols = ds.metadata['columns'][:14]
    fs = 128.0
    n_samples = len(raw)
    time_sec = np.arange(n_samples) / fs

    # Step 1: Preprocessing & Artifact Interpolation
    print(f"Total samples: {n_samples} ({time_sec[-1]:.2f} seconds), 14 channels.")
    bad_indices = np.where(~np.all((raw > 3500) & (raw < 5200), axis=1))[0]
    for idx in bad_indices:
        raw[idx, :] = 0.5 * (raw[idx-1, :] + raw[idx+1, :])
    print(f"Interpolated {len(bad_indices)} non-physiological artifact spikes.")

    # Step 2: Common Average Referencing (CAR)
    car_data = raw - np.mean(raw, axis=1, keepdims=True)

    # Step 3: Spectral Bandpass Filtering
    def bandpass(data, low, high, fs=128.0, order=4):
        sos = signal.butter(order, [low, high], btype='bandpass', fs=fs, output='sos')
        return signal.sosfiltfilt(sos, data, axis=0)

    bands = {
        'Delta': (1.0, 4.0),
        'Theta': (4.0, 8.0),
        'Alpha': (8.0, 13.0),
        'Beta': (13.0, 30.0),
        'Gamma': (30.0, 45.0)
    }

    filtered = {}
    analytic_signals = {}
    phases = {}
    amplitudes = {}
    order_params = {}

    for bname, (low, high) in bands.items():
        filt = bandpass(car_data, low, high, fs)
        filtered[bname] = filt
        # Hilbert transform
        ana = signal.hilbert(filt, axis=0)
        analytic_signals[bname] = ana
        phi = np.angle(ana)
        amp = np.abs(ana)
        phases[bname] = phi
        amplitudes[bname] = amp
        # Kuramoto order parameter R(t) = |1/N sum exp(i*phi)|
        R = np.abs(np.mean(np.exp(1j * phi), axis=1))
        order_params[bname] = R

    # Step 4: Segment Identification (Eyes-Open vs Eyes-Closed)
    diffs = np.diff(eye)
    change_indices = np.concatenate(([0], np.where(diffs != 0)[0] + 1, [len(eye)]))
    segments_open = []
    segments_closed = []
    for i in range(len(change_indices) - 1):
        start = change_indices[i]
        end = change_indices[i+1]
        st = eye[start]
        if end - start >= 500: # at least ~4 seconds stable
            if st == 0:
                segments_open.append((start, end))
            else:
                segments_closed.append((start, end))

    print(f"Identified {len(segments_open)} long Open epochs and {len(segments_closed)} long Closed epochs.")

    # Step 5: Recurrence Quantification Analysis (RQA) across channels
    print("Computing Recurrence Quantification Analysis (RQA)...")
    rqa_summary = {'open': {}, 'closed': {}, 'ratio': {}}
    for metric_key in ['DET', 'LAM', 'ENT', 'L']:
        rqa_summary['open'][metric_key] = []
        rqa_summary['closed'][metric_key] = []
        rqa_summary['ratio'][metric_key] = []

    def compute_avg_rqa(segments):
        res = {k: [] for k in ['DET', 'LAM', 'ENT', 'L']}
        for start, end in segments:
            mid = (start + end) // 2
            chunk = car_data[mid-250:mid+250, :]
            seg_metrics = {k: [] for k in ['DET', 'LAM', 'ENT', 'L']}
            for c in range(14):
                x = chunk[:, c]
                x = (x - np.mean(x)) / (np.std(x) + 1e-8)
                emb = takens_embedding(x, m=3, tau=4)
                R_mat = recurrence_matrix(emb, epsilon=0.5)
                m = compute_rqa_metrics(R_mat)
                for k in ['DET', 'LAM', 'ENT', 'L']:
                    seg_metrics[k].append(m[k])
            for k in ['DET', 'LAM', 'ENT', 'L']:
                res[k].append(seg_metrics[k])
        return {k: np.mean(res[k], axis=0) for k in ['DET', 'LAM', 'ENT', 'L']}

    rqa_open_ch = compute_avg_rqa(segments_open)
    rqa_closed_ch = compute_avg_rqa(segments_closed)

    for k in ['DET', 'LAM', 'ENT', 'L']:
        rqa_summary['open'][k] = rqa_open_ch[k].tolist()
        rqa_summary['closed'][k] = rqa_closed_ch[k].tolist()
        rqa_summary['ratio'][k] = (rqa_closed_ch[k] / np.maximum(rqa_open_ch[k], 1e-5)).tolist()

    # Step 6: Phase-Locking Value (PLV) Functional Connectivity
    print("Computing PLV Adjacency Matrices...")
    open_idx = np.where(eye == 0)[0]
    closed_idx = np.where(eye == 1)[0]
    alpha_phi = phases['Alpha']

    plv_open = np.zeros((14, 14))
    plv_closed = np.zeros((14, 14))
    for i in range(14):
        for j in range(14):
            if i == j:
                plv_open[i, j] = 1.0
                plv_closed[i, j] = 1.0
            else:
                dphi_o = alpha_phi[open_idx, i] - alpha_phi[open_idx, j]
                dphi_c = alpha_phi[closed_idx, i] - alpha_phi[closed_idx, j]
                plv_open[i, j] = np.abs(np.mean(np.exp(1j * dphi_o)))
                plv_closed[i, j] = np.abs(np.mean(np.exp(1j * dphi_c)))

    plv_diff = plv_closed - plv_open

    # Step 7: Empirical-to-Theoretical Kuramoto Simulation
    print("Simulating Kuramoto Phase Transitions on Brain Connectomes...")
    k_couplings = np.linspace(0.1, 4.0, 40)
    kuramoto_res_open = []
    kuramoto_res_closed = []

    # Clean diagonal for coupling matrix input
    cm_open = plv_open.copy()
    np.fill_diagonal(cm_open, 0)
    cm_closed = plv_closed.copy()
    np.fill_diagonal(cm_closed, 0)

    for k_val in k_couplings:
        out_o = simulate_kuramoto(n_oscillators=14, K=k_val, coupling_matrix=cm_open, t_max=30.0, dt=0.05, seed=42)
        out_c = simulate_kuramoto(n_oscillators=14, K=k_val, coupling_matrix=cm_closed, t_max=30.0, dt=0.05, seed=42)
        kuramoto_res_open.append((out_o['steady_mean_r'], out_o['susceptibility']))
        kuramoto_res_closed.append((out_c['steady_mean_r'], out_c['susceptibility']))

    mean_r_sim_open = np.array([x[0] for x in kuramoto_res_open])
    chi_sim_open = np.array([x[1] for x in kuramoto_res_open])
    mean_r_sim_closed = np.array([x[0] for x in kuramoto_res_closed])
    chi_sim_closed = np.array([x[1] for x in kuramoto_res_closed])

    kc_open = k_couplings[np.argmax(chi_sim_open)]
    kc_closed = k_couplings[np.argmax(chi_sim_closed)]
    print(f"Simulated Critical Coupling: Kc(Open) = {kc_open:.2f}, Kc(Closed) = {kc_closed:.2f}")

    # Empirical mean Kuramoto R in Alpha band
    r_emp_open = np.mean(order_params['Alpha'][open_idx])
    r_emp_closed = np.mean(order_params['Alpha'][closed_idx])
    print(f"Empirical Alpha Order Parameter: R(Open) = {r_emp_open:.4f}, R(Closed) = {r_emp_closed:.4f}")

    # Step 8: Event-Related Kuramoto Dynamics Time-Locked to Eye State Transitions
    print("Computing Event-Related Phase Dynamics around Transitions...")
    # Eye closing transitions: 0 -> 1
    # Eye opening transitions: 1 -> 0
    t_open_to_close = np.where((eye[:-1] == 0) & (eye[1:] == 1))[0] + 1
    t_close_to_open = np.where((eye[:-1] == 1) & (eye[1:] == 0))[0] + 1

    window_pts = int(2.0 * fs) # +/- 2 seconds
    tau_pts = np.arange(-window_pts, window_pts + 1)
    tau_sec = tau_pts / fs

    def average_epoch(trans_pts, series):
        epochs = []
        for pt in trans_pts:
            if pt - window_pts >= 0 and pt + window_pts + 1 <= len(series):
                epochs.append(series[pt - window_pts : pt + window_pts + 1])
        return np.mean(epochs, axis=0) if epochs else np.zeros_like(tau_pts)

    erd_close = average_epoch(t_open_to_close, order_params['Alpha'])
    erd_open = average_epoch(t_close_to_open, order_params['Alpha'])

    # Step 9: Publication-Quality Visualization
    print("Generating 6-Panel Visualization...")
    fig = plt.figure(figsize=(18, 12), dpi=150)
    gs = fig.add_gridspec(3, 2, hspace=0.32, wspace=0.25)

    # Panel A: Time Series Overview
    ax_a = fig.add_subplot(gs[0, :])
    t_span = (time_sec >= 45) & (time_sec <= 80)
    ax_a.plot(time_sec[t_span], order_params['Alpha'][t_span], color='#2b5c8f', lw=1.2, label=r'Alpha Kuramoto $R(t)$')
    ax_a.plot(time_sec[t_span], order_params['Theta'][t_span], color='#9b59b6', lw=0.9, alpha=0.7, label=r'Theta Kuramoto $R(t)$')
    # State background
    ax_a.fill_between(time_sec[t_span], 0, 1, where=eye[t_span]==1, color='#27ae60', alpha=0.18, label='Eyes Closed (State 1)')
    ax_a.fill_between(time_sec[t_span], 0, 1, where=eye[t_span]==0, color='#e74c3c', alpha=0.10, label='Eyes Open (State 0)')
    ax_a.set_ylim(0.0, 1.0)
    ax_a.set_xlim(45, 80)
    ax_a.set_title("A. Cortical Kuramoto Phase Synchrony $R(t)$ and State Transitions Across 14 Electrodes", fontsize=13, fontweight='bold', pad=10)
    ax_a.set_xlabel("Time (seconds)", fontsize=11)
    ax_a.set_ylabel("Order Parameter $R(t)$", fontsize=11)
    ax_a.legend(loc='lower left', framealpha=0.9, ncol=4, fontsize=10)
    ax_a.grid(True, alpha=0.3, linestyle=':')

    # Panel B: RQA Determinism across Channels
    ax_b = fig.add_subplot(gs[1, 0])
    x_pos = np.arange(14)
    width = 0.38
    det_o = rqa_summary['open']['DET']
    det_c = rqa_summary['closed']['DET']
    ax_b.bar(x_pos - width/2, det_o, width=width, color='#e74c3c', alpha=0.8, label='Eyes Open')
    ax_b.bar(x_pos + width/2, det_c, width=width, color='#27ae60', alpha=0.8, label='Eyes Closed')
    ax_b.set_xticks(x_pos)
    ax_b.set_xticklabels(cols, rotation=45, fontsize=10)
    ax_b.set_title("B. Phase Space Recurrence Determinism (DET) by Channel", fontsize=12, fontweight='bold')
    ax_b.set_ylabel("Determinism (DET)", fontsize=11)
    ax_b.legend(framealpha=0.9, fontsize=10)
    ax_b.grid(True, alpha=0.3, linestyle=':')

    # Panel C: Phase-Locking Value (PLV) Connectivity Reorganization
    ax_c = fig.add_subplot(gs[1, 1])
    im = ax_c.imshow(plv_diff, cmap='coolwarm', vmin=-0.15, vmax=0.15)
    ax_c.set_xticks(range(14))
    ax_c.set_yticks(range(14))
    ax_c.set_xticklabels(cols, rotation=45, fontsize=9)
    ax_c.set_yticklabels(cols, fontsize=9)
    ax_c.set_title(r"C. Functional Connectivity Shift ($\Delta \mathbf{PLV} = \mathbf{PLV}_{\text{closed}} - \mathbf{PLV}_{\text{open}}$)", fontsize=12, fontweight='bold')
    cbar = fig.colorbar(im, ax=ax_c, fraction=0.046, pad=0.04)
    cbar.set_label(r'$\Delta \mathrm{PLV}$', fontsize=10)

    # Panel D: Event-Related Synchronization (ERS) around Transitions
    ax_d = fig.add_subplot(gs[2, 0])
    ax_d.plot(tau_sec, erd_close, color='#27ae60', lw=2.2, label=r'Closing ($0 \to 1$, ERS)')
    ax_d.plot(tau_sec, erd_open, color='#e74c3c', lw=2.2, linestyle='--', label=r'Opening ($1 \to 0$, ERD)')
    ax_d.axvline(0, color='gray', linestyle=':', lw=1.5, alpha=0.8)
    ax_d.set_title("D. Event-Related Phase Synchronization (ERS/ERD) Dynamics", fontsize=12, fontweight='bold')
    ax_d.set_xlabel("Time Relative to Transition (s)", fontsize=11)
    ax_d.set_ylabel(r"Mean Kuramoto $\langle R \rangle$", fontsize=11)
    ax_d.legend(framealpha=0.9, fontsize=10)
    ax_d.grid(True, alpha=0.3, linestyle=':')

    # Panel E: Simulated Kuramoto Susceptibility & Brain Operating Regime
    ax_e = fig.add_subplot(gs[2, 1])
    ax_e.plot(k_couplings, chi_sim_open, color='#e74c3c', lw=2, label=r'$\chi(K)$ (Open Connectome)')
    ax_e.plot(k_couplings, chi_sim_closed, color='#27ae60', lw=2, label=r'$\chi(K)$ (Closed Connectome)')
    ax_e.axvline(kc_open, color='#e74c3c', linestyle=':', alpha=0.6, label=f'$K_c$(Open)={kc_open:.2f}')
    ax_e.axvline(kc_closed, color='#27ae60', linestyle=':', alpha=0.6, label=f'$K_c$(Closed)={kc_closed:.2f}')
    ax_e.set_title("E. Theoretical Kuramoto Criticality on Empirical Brain Topology", fontsize=12, fontweight='bold')
    ax_e.set_xlabel("Global Coupling Strength $K$", fontsize=11)
    ax_e.set_ylabel("Susceptibility $\chi = N \mathrm{Var}(R)$", fontsize=11)
    ax_e.legend(framealpha=0.9, fontsize=9)
    ax_e.grid(True, alpha=0.3, linestyle=':')

    out_png = 'neural_eeg_phase_transition_analysis.png'
    fig.savefig(out_png, dpi=180, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved figure to {out_png}")

    # Step 10: Compile Metrics Dictionary
    metrics = {
        'dataset': 'neural_eeg',
        'channels': cols,
        'sampling_rate_hz': fs,
        'total_duration_sec': float(time_sec[-1]),
        'segments': {
            'n_open': len(segments_open),
            'n_closed': len(segments_closed)
        },
        'empirical_order_parameter': {
            b: {
                'open_mean': float(np.mean(order_params[b][open_idx])),
                'closed_mean': float(np.mean(order_params[b][closed_idx])),
                'ratio_closed_to_open': float(np.mean(order_params[b][closed_idx]) / np.mean(order_params[b][open_idx]))
            } for b in bands
        },
        'recurrence_metrics': {
            col: {
                'open_det': float(rqa_summary['open']['DET'][i]),
                'closed_det': float(rqa_summary['closed']['DET'][i]),
                'det_ratio': float(rqa_summary['ratio']['DET'][i]),
                'open_lam': float(rqa_summary['open']['LAM'][i]),
                'closed_lam': float(rqa_summary['closed']['LAM'][i]),
                'lam_ratio': float(rqa_summary['ratio']['LAM'][i])
            } for i, col in enumerate(cols)
        },
        'kuramoto_criticality': {
            'simulated_kc_open': float(kc_open),
            'simulated_kc_closed': float(kc_closed),
            'peak_susceptibility_open': float(np.max(chi_sim_open)),
            'peak_susceptibility_closed': float(np.max(chi_sim_closed))
        }
    }

    out_json = 'neural_eeg_phase_transition_metrics.json'
    with open(out_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {out_json}")

if __name__ == '__main__':
    run_analysis()
