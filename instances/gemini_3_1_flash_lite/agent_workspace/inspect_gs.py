from colony_lib.dynamics import GrayScott2D
import numpy as np

gs = GrayScott2D()
print(f"U shape: {gs.u.shape}")
print(f"Initial U: {gs.u}")
print(f"Initial V: {gs.v}")

gs.step()
print(f"After 1 step U: {gs.u}")
print(f"After 1 step V: {gs.v}")
