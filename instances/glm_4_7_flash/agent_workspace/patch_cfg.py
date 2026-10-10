import re

src = open('it_turbulence_worldc.py').read()

old_cfg = """    t0 = time.time()
    cfgA = [(1000 + i, 1024, 100.0, 1e-3, 100.0, 0.05) for i in range(40)]
    cfgB = [(2000 + i, 1024, 100.0, 1e-3, 100.0, 0.20) for i in range(40)]
    cfgC = [(3000 + i, 2048, 200.0, 5e-4, 100.0, 0.10) for i in range(12)]"""
new_cfg = """    t0 = time.time()
    env = os.environ
    NA = int(env.get('IT_NA', 1024)); LA = float(env.get('IT_LA', 100.0))
    dtA = float(env.get('IT_DTA', 1e-3)); TA = float(env.get('IT_TA', 100.0))
    nA = int(env.get('IT_NREAL', 40))
    NB = int(env.get('IT_NB', NA)); LB = LA; dtB = dtA; TB = TA; nB = nA
    NC = int(env.get('IT_NC', 2048)); LC = float(env.get('IT_LC', 200.0))
    dtC = float(env.get('IT_DTC', 5e-4)); TC = TA; nC = max(1, nA // 3)
    cfgA = [(1000 + i, NA, LA, dtA, TA, 0.05) for i in range(nA)]
    cfgB = [(2000 + i, NB, LB, dtB, TB, 0.20) for i in range(nB)]
    cfgC = [(3000 + i, NC, LC, dtC, TC, 0.10) for i in range(nC)]"""
assert old_cfg in src
src = src.replace(old_cfg, new_cfg)

old_kk = "    kk = 2 * np.pi * np.fft.fftfreq(1024, d=100.0 / 1024)"
new_kk = "    kk = 2 * np.pi * np.fft.fftfreq(NA, d=LA / NA)"
assert old_kk in src
src = src.replace(old_kk, new_kk)

# cosmetic-only: kymograph extent & rate denominators driven by LC / LA
src = src.replace("extent=[0, 200, 0, 100]", "extent=[0, LC, 0, TC]")
src = src.replace("rate(A['wm'], 9, 100.0)", "rate(A['wm'], 9, LA)")
src = src.replace("rate(A['wm'], 16, 100.0)", "rate(A['wm'], 16, LA)")
src = src.replace("rate(A['wm'], 25, 100.0)", "rate(A['wm'], 25, LA)")
src = src.replace("rate(B['wm'], 9, 100.0)", "rate(B['wm'], 9, LB)")
src = src.replace("rate(B['wm'], 16, 100.0)", "rate(B['wm'], 16, LB)")
src = src.replace("rate(B['wm'], 25, 100.0)", "rate(B['wm'], 25, LB)")
src = src.replace("rate(C['wm'], 9, 200.0)", "rate(C['wm'], 9, LC)")
src = src.replace("rate(C['wm'], 16, 200.0)", "rate(C['wm'], 16, LC)")
src = src.replace("rate(C['wm'], 25, 200.0)", "rate(C['wm'], 25, LC)")
# rate denominator time window: saturated phase length TA-40
src = src.replace("return float((wm > thr).sum() / (60.0 * L))",
                  "return float((wm > thr).sum() / (max(1.0, TA - 40.0) * L))")
src = src.replace("def rate(wm, thr, L):", "def rate(wm, thr, L, TA=100.0):")

open('it_turbulence_worldc.py', 'w').write(src)
print('patched OK')
