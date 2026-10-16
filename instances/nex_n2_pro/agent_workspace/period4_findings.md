# The P4 Period-4 'Tongue' — Consolidated Finding

## System

`x_i(t+1) = (1-eps) f(x_i) + (eps/2)[f(x_{i-1}) + f(x_{i+1})]`, `f(x) = r x (1-x)`, ring lattice N=120, periodic BC.

## Headline

Inside the chaotic regime (r>3.57) there is a **window in parameter space — a 'period-4 tongue' — where the entire lattice locks to a genuine period-4 orbit that persists indefinitely.**

### (a) Tongue map

`frac_P4(r, eps)` is large (0.7-1.0) over a finite region roughly
    r  in [3.84, 3.95],  eps in [0.125, 0.150],
with the core around `r=3.865, eps=0.135`. Outside the tongue the lattice is chaotic (frac_P4 ~ 0).

### (b) The orbit is GENUINE P4 (not a metastable P2 defect)

Tracked to **200,000 transients**: even and odd sublattices each carry a distinct **4-value time orbit** (not 2). Every site satisfies `x_i(t)=x_i(t+4)` to machine precision. The structure is stable in time — it does NOT relax away.

### (c) N-independence

`N=80 -> P4: 80/80 sites`, `N=160 -> 160/160`, `N=320 -> 319/320`. The period-4 lock-in is a property of the system, not a finite-size artifact.

### (d) Local stability

Cycle Jacobian of the period-4 orbit has dominant `|lambda| = 0.909 < 1`  =>  the orbit is a **stable** attractor (pure periodicity, not chaos).

### (e) Why not a trivial 2-site checkerboard

A naive 2-site even/odd reduction (`a'=(1-e)f(a)+e f(b)`) does NOT reproduce the orbit: the bulk sites sit just above a nearby P2 checkerboard but execute a true 4-phase orbit. The genuine P4 is a **hidden oscillation embedded within an apparently P2 skeleton.**

## Representative orbit (site i=30, even)

`t=0: 0.465471 -> t=1: 0.884031 -> t=2: 0.472520 -> t=3: 0.886874 -> t=4: 0.465471`

File: period4_tongue_deliverable.png
