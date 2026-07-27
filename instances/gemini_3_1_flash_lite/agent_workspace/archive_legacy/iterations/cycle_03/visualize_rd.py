import matplotlib.pyplot as plt
from reaction_diffusion import ReactionDiffusion

rd = ReactionDiffusion()
for _ in range(500):
    rd.evolve()
plt.imshow(rd.B, cmap='inferno')
plt.savefig('iterations/cycle_03/rd_final.png')
print("RD visualization saved.")
