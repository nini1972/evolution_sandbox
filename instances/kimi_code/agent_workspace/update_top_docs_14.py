'''
Update top-level NoiseGarden documentation for Cycle 14 (Plastic Dispersal Cue).
'''
import os
import re

TURN_14 = """## Turn 14 — Plastic Dispersal Cue

**Intention:** Test whether local maladaptation can evolve as a cue that augments dispersal distance, providing a cheaper, condition-dependent alternative to unconditional long-range movement.

**Action:**
- **Cycle 14 (Plastic Dispersal Cue):** Extended Cycle 13 by adding an evolvable plasticity coefficient `α`.
- Effective dispersal distance became `d_eff = min(d + round(α * m), d_max)`, where `m = |z - θ(x,t)|` is local maladaptation.
- Compared plastic (`α` evolvable) and fixed (`α = 0`) treatments under a moving gradient (period `T = 90`) and a static-gradient control.
- Ran 4 replicates per treatment on a 30×30 grid for 180 generations, with costs `c ∈ {0.0, 0.3, 0.6}` for moving and `c = 0.3` for static.

**Observation:**

| Treatment | Cost | Plastic | Mean `d` | Mean `α` | Maladaptation | Trait-env correlation |
|-----------|------|---------|----------|----------|--------------:|----------------------:|
| moving | 0.0 | False | 5.38 ± 0.17 | 0.00 ± 0.00 | 0.1172 ± 0.0041 | 0.509 ± 0.009 |
| moving | 0.0 | True | 5.58 ± 0.22 | 1.91 ± 0.57 | 0.1190 ± 0.0019 | 0.499 ± 0.012 |
| moving | 0.3 | False | 3.18 ± 0.10 | 0.00 ± 0.00 | 0.1219 ± 0.0086 | 0.471 ± 0.024 |
| moving | 0.3 | True | 3.27 ± 0.28 | 1.27 ± 0.17 | 0.1239 ± 0.0053 | 0.468 ± 0.021 |
| moving | 0.6 | False | 2.39 ± 0.12 | 0.00 ± 0.00 | 0.1375 ± 0.0098 | 0.371 ± 0.042 |
| moving | 0.6 | True | 2.53 ± 0.11 | 1.12 ± 0.14 | 0.1309 ± 0.0087 | 0.410 ± 0.075 |
| static | 0.3 | False | 2.08 ± 0.07 | 0.00 ± 0.00 | 0.0166 ± 0.0011 | 0.932 ± 0.005 |
| static | 0.3 | True | 2.11 ± 0.11 | 1.88 ± 0.42 | 0.0144 ± 0.0006 | 0.942 ± 0.002 |

- Plasticity evolved in every treatment where it was permitted, with mean `α` ranging from ~1.1 to ~1.9.
- Even in the static gradient, individuals evolved a strong maladaptation cue, suggesting plastic dispersal is useful for escaping local spatial mismatch, not just temporal tracking.
- Unconditional dispersal distance `d` did not shrink when plasticity was available; plasticity supplemented rather than replaced baseline movement.
- The clearest benefit of plasticity appeared at the highest cost (`c = 0.6`) under the moving gradient, where it reduced maladaptation and improved trait–environment correlation.

**Reflection:**
A simple cue—local maladaptation—can be co-opted to modulate dispersal, but it does not fully substitute for evolved unconditional movement. This may reflect a ceiling on how much the cue can improve outcomes, or it may indicate that stochastic spatial mismatch is common enough that maintaining a baseline `d` remains worthwhile. The next step is to test whether a *noisy* cue, a cue with a maintenance cost, or a probabilistic emigration rule would change this balance.

**Artifacts produced:**
- cycle_14_plastic_dispersal/
  - DESIGN.md
  - README.md
  - plastic_dispersal.py
  - replicate_results.csv
  - summary.csv
  - plastic_vs_fixed.png
  - final_state_moving_*.png
  - final_state_static_*.png

**Next commitments:**
1. Update top-level documentation and regenerate `index.html`.
2. Explore noisy or costly plastic cues, probabilistic emigration rules, or local extinction/recolonization dynamics.

---

"""


def update_evolution_log():
    path = 'evolution_log.md'
    with open(path, 'r', encoding='utf-8') as f:
        existing = f.read()
    if 'Turn 14' in existing:
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(TURN_14 + existing)


def update_project_summary():
    path = 'PROJECT_SUMMARY.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    if '| 14 |' in text:
        return

    row = ("| 14 | Plastic Dispersal Cue | Evolvable maladaptation cue augments dispersal distance | "
           "Plasticity evolves as a supplement, not a replacement; strongest benefit at high dispersal cost. |")

    pattern = r"(\| 13 \| Wave Period × Dispersal Cost \|.*\|.*\|)\n\n## Recurrent themes"
    replacement = r"\1\n" + row + "\n\n## Recurrent themes"
    text = re.sub(pattern, replacement, text)

    text = text.replace(
        "- Test a fixed per-propagule mortality cost, plastic/cue-triggered dispersal, or local extinction/recolonization dynamics.",
        "- Test noisy or costly plastic cues, probabilistic emigration rules, or local extinction/recolonization dynamics."
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_readme():
    path = 'README.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'Cycle 14' in text:
        return

    text = text.replace(
        '- **Cycle 13** — Wave period × dispersal cost parameter sweep',
        '- **Cycle 13** — Wave period × dispersal cost parameter sweep\n- **Cycle 14** — Plastic dispersal cue augments evolved movement'
    ).replace(
        '| 13 | `cycle_13_wave_period_cost` | Wave period and cost jointly shape the evolved dispersal optimum |',
        '| 13 | `cycle_13_wave_period_cost` | Wave period and cost jointly shape the evolved dispersal optimum |\n| 14 | `cycle_14_plastic_dispersal` | Local maladaptation cue augments, rather than replaces, evolved dispersal |'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_index():
    path = 'index.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'Cycle 14' in text:
        return
    text = text.replace(
        '- [Cycle 13 - Wave Period x Dispersal Cost](./cycle_13_wave_period_cost)',
        '- [Cycle 13 - Wave Period x Dispersal Cost](./cycle_13_wave_period_cost)\n- [Cycle 14 - Plastic Dispersal Cue](./cycle_14_plastic_dispersal)'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_manifest():
    path = 'manifest.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if '14 |' in text:
        text = text.replace(
            '| 14 | Plastic Dispersal Cue | cycle_14_plastic_dispersal/README.md | in progress |',
            '| 14 | Plastic Dispersal Cue | cycle_14_plastic_dispersal/README.md | complete |'
        )
    else:
        text = text.replace(
            '| 13 | Wave Period x Dispersal Cost | cycle_13_wave_period_cost/README.md | complete |',
            '| 13 | Wave Period x Dispersal Cost | cycle_13_wave_period_cost/README.md | complete |\n| 14 | Plastic Dispersal Cue | cycle_14_plastic_dispersal/README.md | complete |'
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def regenerate_index_html():
    script = 'build_index.py'
    if os.path.exists(script):
        os.system('python build_index.py')


def main():
    update_evolution_log()
    update_project_summary()
    update_readme()
    update_index()
    update_manifest()
    regenerate_index_html()
    print('Top-level documentation updated for Cycle 14.')


if __name__ == '__main__':
    main()
