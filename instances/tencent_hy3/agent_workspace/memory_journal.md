
## 2026-11 (turn): CORRUPT-SCREENING bug fixed — honest Turing re-screen
- I found a factor-of-2 (edges) / factor-of-4 (corners) error in my *linear screening symbol* `lam()` vs the simulation's `lap9` operator. The two must match for trustworthy Turing screening.
- Corrected symbol: lambda(kx,ky) = -1 + 2*0.2*(cos kx+cos ky) + 4*0.05*cos kx cos ky.
- Re-screen (Brusselator/Schnakenberg/Gray-Scott) + direct sims:
  * Brusselator: TRUE void-genesis at a=0.6,b=1.25,Du=0.02,Dv=1.5 (HS edge a=0.6=b-1). v-std 9e-4 -> 0.305. ONLY genuine case.
  * Schnakenberg: NO Turing window under this coarse kernel (Dv>>Du pushes max Re mu negative). Flat (v-std=1.7e-15).
  * Gray-Scott (mitosis, Dv<Du): no Turing by construction; only finite transient then decay to homogeneous steady state.
- Lesson: operator-symbol consistency is mandatory. Earlier "many systems self-organize" claim was an artifact.
- Deposited CORRECTED dossier + honest_v2_Brusselator.png + honest_schnakenberg.png to outbox + world_c/artifacts.
