from colony_lib.dynamics import GrayScott2D
import numpy as np
import matplotlib.pyplot as plt

def run_parameter_sweep():
    # Attempt to find the pattern-forming regime by exploring parameters
    # The default constructor works, let's see what parameters are available
    # or if we can set them after instantiation.
    gs = GrayScott2D()
    
    # Let's see if we can inspect the object's attributes to understand
    # how to modify parameters.
    print(f"Attributes: {dir(gs)}")
    print(f"Default F: {getattr(gs, 'F', 'Not found')}")
    print(f"Default k: {getattr(gs, 'k', 'Not found')}")
    
    # If they are attributes, I can change them.
    # If not, they might be in a configuration dict.
    
    # Based on the previous successful run, it seems to have some default state.
    # Let's perform a sweep on F and k to find different patterns.
    F_vals = [0.02, 0.03, 0.04]
    k_vals = [0.05, 0.06, 0.07]
    
    for f in F_vals:
        for k in k_vals:
            gs = GrayScott2D()
            # Try setting attributes directly
            if hasattr(gs, 'F'): gs.F = f
            if hasattr(gs, 'k'): gs.k = k
            
            # Re-init or step
            for _ in range(1000):
                gs.step()
            
            plt.figure()
            plt.imshow(gs.u, cmap='magma')
            plt.title(f"F={f}, k={k}")
            plt.savefig(f"gs_f{f}_k{k}.png")
            plt.close()

if __name__ == '__main__':
    run_parameter_sweep()
