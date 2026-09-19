import numpy as np
from collections import Counter

# Modified constants for exploratory test
SEED = 0
P = 30
K = 20
DMAX = 6
MUT_RATE = 0.05
MUT_SD = 0.5
R = 2.0
G = 0.1
SD_SURV = 0.6
S0 = 0.7


def init_world():
    rng = np.random.default_rng(SEED)
    active = []
    for i in range(P):
        n = K
        z = rng.normal(0.0, 1.0, size=n)
        d = rng.integers(1, DMAX + 1, size=n)
        h = rng.random(size=n)
        active.append({'z': z.astype(np.float32),
                       'd': d.astype(np.int32),
                       'h': h.astype(np.float32)})
    bank_z = [np.zeros(0, dtype=np.float32) for _ in range(P)]
    bank_d = [np.zeros(0, dtype=np.int32) for _ in range(P)]
    bank_h = [np.zeros(0, dtype=np.float32) for _ in range(P)]
    env = np.zeros(P, dtype=np.float32)
    return active, bank_z, bank_d, bank_h, env, rng


def update_env(env, A, sigma_e, rho, rng):
    if sigma_e <= 1e-9:
        env[:] = A * np.arange(P, dtype=np.float32)
        return
    noise = rng.normal(0.0, sigma_e, size=P)
    env[:] = rho * env + np.sqrt(1.0 - rho * rho) * noise
    env += A * np.arange(P, dtype=np.float32)


def local_maladapt(z, theta):
    diff = z - theta
    m = np.abs(diff)
    return m


def survive_active(z, theta, rng):
    m = local_maladapt(z, theta)
    p = np.clip(S0 * np.exp(-0.5 * m * m), 0.0, 1.0)
    mask = rng.random(len(z)) < p
    return z[mask]


def germinate(bank_z, bank_d, bank_h, rng):
    germ_z, germ_d, germ_h = [], [], []
    for i in range(P):
        n = len(bank_z[i])
        if n == 0:
            germ_z.append(np.zeros(0, dtype=np.float32))
            germ_d.append(np.zeros(0, dtype=np.int32))
            germ_h.append(np.zeros(0, dtype=np.float32))
            continue
        mask = rng.random(n) < G
        germ_z.append(bank_z[i][mask])
        germ_d.append(bank_d[i][mask])
        germ_h.append(bank_h[i][mask])
    return germ_z, germ_d, germ_h


def survive_bank(bank_z, bank_d, bank_h, rng):
    for i in range(P):
        n = len(bank_z[i])
        if n == 0:
            continue
        mask = rng.random(n) < SD_SURV
        bank_z[i] = bank_z[i][mask]
        bank_d[i] = bank_d[i][mask]
        bank_h[i] = bank_h[i][mask]


def mutate_offspring(z, d, h, rng):
    n = len(z)
    mask = rng.random(n) < MUT_RATE
    z[mask] += rng.normal(0.0, MUT_SD, size=np.count_nonzero(mask))
    d[mask] = np.clip(d[mask] + rng.integers(-1, 2, size=np.count_nonzero(mask)), 1, DMAX)
    h[mask] = np.clip(h[mask] + rng.normal(0.0, 0.05, size=np.count_nonzero(mask)), 0.0, 1.0)
    return z, d, h


def one_generation(active, bank_z, bank_d, bank_h, env, A, sigma_e, rho, rng):
    update_env(env, A, sigma_e, rho, rng)
    survive_bank(bank_z, bank_d, bank_h, rng)
    germ_z, germ_d, germ_h = germinate(bank_z, bank_d, bank_h, rng)
    for i in range(P):
        survivors = survive_active(active[i]['z'], env[i], rng)
        active[i]['z'] = np.concatenate([survivors, germ_z[i]])
        active[i]['d'] = np.concatenate([active[i]['d'][rng.random(len(active[i]['d'])) < 1.0][:len(survivors)], germ_d[i]])
        active[i]['h'] = np.concatenate([active[i]['h'][rng.random(len(active[i]['h'])) < 1.0][:len(survivors)], germ_h[i]])
        cap = len(active[i]['z']) - K
        if cap > 0:
            drop = rng.choice(len(active[i]['z']), size=cap, replace=False)
            mask = np.ones(len(active[i]['z']), dtype=bool)
            mask[drop] = False
            active[i]['z'] = active[i]['z'][mask]
            active[i]['d'] = active[i]['d'][mask]
            active[i]['h'] = active[i]['h'][mask]

    new_bank_z = [np.zeros(0, dtype=np.float32) for _ in range(P)]
    new_bank_d = [np.zeros(0, dtype=np.int32) for _ in range(P)]
    new_bank_h = [np.zeros(0, dtype=np.float32) for _ in range(P)]
    active_counts = np.zeros(P, dtype=np.int32)
    for i in range(P):
        n = len(active[i]['z'])
        if n == 0:
            continue
        h_i = active[i]['h']
        dorm_mask = rng.random(n) < h_i
        stay_mask = ~dorm_mask
        new_bank_z[i] = np.concatenate([new_bank_z[i], active[i]['z'][dorm_mask]])
        new_bank_d[i] = np.concatenate([new_bank_d[i], active[i]['d'][dorm_mask]])
        new_bank_h[i] = np.concatenate([new_bank_h[i], active[i]['h'][dorm_mask]])

        n_off = int(R * np.count_nonzero(stay_mask))
        if n_off == 0:
            active[i]['z'] = active[i]['z'][dorm_mask]
            active[i]['d'] = active[i]['d'][dorm_mask]
            active[i]['h'] = active[i]['h'][dorm_mask]
            continue
        parents = rng.choice(np.where(stay_mask)[0], size=n_off, replace=True)
        d_parent = active[i]['d'][parents]
        offsets = rng.integers(-DMAX, DMAX + 1, size=(n_off, 2))
        dx = np.clip(d_parent * np.sign(offsets[:, 0]), -DMAX, DMAX)
        dy = np.clip(d_parent * np.sign(offsets[:, 1]), -DMAX, DMAX)
        target_x = (i // 6 + dx) % 5
        target_y = (i % 6 + dy) % 6
        targets = target_x * 6 + target_y
        counts = Counter(targets)
        active_counts += np.bincount(targets, minlength=P)
        new_z, new_d, new_h = mutate_offspring(active[i]['z'][parents].copy(), d_parent.copy(), active[i]['h'][parents].copy(), rng)
        for j, c in counts.items():
            idx = np.where(targets == j)[0]
            new_bank_z[j] = np.concatenate([new_bank_z[j], new_z[idx]])
            new_bank_d[j] = np.concatenate([new_bank_d[j], new_d[idx]])
            new_bank_h[j] = np.concatenate([new_bank_h[j], new_h[idx]])
        active[i]['z'] = active[i]['z'][dorm_mask]
        active[i]['d'] = active[i]['d'][dorm_mask]
        active[i]['h'] = active[i]['h'][dorm_mask]

    for j in range(P):
        bank_z[j] = np.concatenate([bank_z[j], new_bank_z[j]])
        bank_d[j] = np.concatenate([bank_d[j], new_bank_d[j]])
        bank_h[j] = np.concatenate([bank_h[j], new_bank_h[j]])
        if len(bank_z[j]) > 100 * K:
            keep = rng.choice(len(bank_z[j]), size=100 * K, replace=False)
            bank_z[j] = bank_z[j][keep]
            bank_d[j] = bank_d[j][keep]
            bank_h[j] = bank_h[j][keep]


def run(A, sigma_e, rho, gens=200):
    active, bank_z, bank_d, bank_h, env, rng = init_world()
    for g in range(gens):
        one_generation(active, bank_z, bank_d, bank_h, env, A, sigma_e, rho, rng)
    total = sum(len(a['z']) for a in active) + sum(len(b) for b in bank_z)
    bank = sum(len(b) for b in bank_z)
    act = sum(len(a['z']) for a in active)
    all_z = np.concatenate([a['z'] for a in active] + bank_z)
    all_d = np.concatenate([a['d'] for a in active] + bank_d)
    all_h = np.concatenate([a['h'] for a in active] + bank_h)
    env_now = env.copy()
    mal = np.mean([np.mean(np.abs(a['z'] - env_now[i])) for i, a in enumerate(active) if len(a['z'])])
    print(f'A={A} sigma={sigma_e} rho={rho}: pop={total} active={act} bank={bank} mean_d={all_d.mean():.2f} mean_h={all_h.mean():.3f} mal={mal:.3f}')


if __name__ == '__main__':
    for sigma in [0.0, 0.4, 0.8]:
        run(A=0.0, sigma_e=sigma, rho=0.8, gens=200)
    for A in [0.0, 0.75, 1.5]:
        run(A=A, sigma_e=0.4, rho=0.0, gens=200)
