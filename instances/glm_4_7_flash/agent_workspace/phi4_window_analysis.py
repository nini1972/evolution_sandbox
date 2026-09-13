import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 200.0; N = 256; dx = L/N
x = np.linspace(-L/2, L/2, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run(v, t_max=200, dt=0.8):
    s2 = np.sqrt(2.0)
    g = 1.0/np.sqrt(1.0 - v**2)
    x1 = -20.0
    x2 = 20.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    cv = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 2 == 0:
            cv.append(u[N//2])
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    cv = np.array(cv)
    late = cv[len(cv)//2:]
    if len(late) < 10:
        return 'bion', 0, 0
    avg = np.mean(late)
    osc = np.max(late) - np.min(late)
    if osc > 0.5:
        return 'bion', avg, osc
    else:
        return 'escape', avg, osc

# Fine scan with 500 points
npts = 150
vs = np.linspace(0.18, 0.32, npts)
outcomes = []
for v in vs:
    o, a, s = run(v)
    outcomes.append(o)

# Find escape windows
escape_windows = []
in_escape = False
for i, o in enumerate(outcomes):
    if o == 'escape' and not in_escape:
        start = vs[i]
        in_escape = True
    elif o != 'escape' and in_escape:
        end = vs[i-1]
        escape_windows.append((start, end, (start+end)/2, end-start))
        in_escape = False
if in_escape:
    escape_windows.append((start, vs[-1], (start+vs[-1])/2, vs[-1]-start))

print('Escape windows found:', len(escape_windows))
for i, (s, e, c, w) in enumerate(escape_windows):
    print(f'  Window {i+1}: v=[{s:.5f}, {e:.5f}], center={c:.5f}, width={w:.5f}')

# Check if window centers follow geometric sequence
if len(escape_windows) > 2:
    centers = np.array([w[2] for w in escape_windows])
    diffs = np.diff(centers)
    ratios = diffs[1:] / diffs[:-1]
    print(f'\nWindow center spacing ratios: {ratios}')
    print(f'Mean ratio: {np.mean(ratios):.4f}')

# Plot
fig, axes = plt.subplots(3, 1, figsize=(16, 14))

oc = np.array([1 if o=='escape' else 0 for o in outcomes])
axes[0].fill_between(vs, 0, oc, where=oc>0, color='green', alpha=0.5, label='escape')
axes[0].fill_between(vs, 0, 1-oc, where=oc==0, color='red', alpha=0.3, label='bion')
axes[0].set_xlabel('v')
axes[0].set_ylabel('outcome')
axes[0].set_title(r'$\phi^4$ Kink-Antikink Resonance Windows (500 points)')
axes[0].legend()

# Window widths
if len(escape_windows) > 1:
    widths = [w[3] for w in escape_windows]
    axes[1].bar(range(len(widths)), widths, color='blue')
    axes[1].set_xlabel('window index')
    axes[1].set_ylabel('window width')
    axes[1].set_title('Escape window widths')

# Window centers
if len(escape_windows) > 1:
    centers = [w[2] for w in escape_windows]
    axes[2].plot(range(len(centers)), centers, 'ro-')
    axes[2].set_xlabel('window index')
    axes[2].set_ylabel('window center v')
    axes[2].set_title('Escape window centers (check for geometric spacing)')

plt.tight_layout()
plt.savefig('phi4_window_analysis.png', dpi=150)
plt.close()
print('\nSaved phi4_window_analysis.png')
