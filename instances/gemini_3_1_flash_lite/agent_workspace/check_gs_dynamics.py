from colony_lib.dynamics import GrayScott2D
gs = GrayScott2D(size=(64, 64), f=0.03, k=0.06)
# Check state at early steps
for i in range(10):
    gs.step()
    print(f"Step {i}: U_mean={gs.u.mean():.4f}, V_mean={gs.v.mean():.4f}")
