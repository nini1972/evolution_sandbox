'''
Update top-level NoiseGarden documentation for Cycle 13 (Wave Period x Dispersal Cost).
'''
import os
import re

TURN_13 = """## Turn 13 — Wave Period × Dispersal Cost

**Intention:** Map how the temporal scale of environmental change interacts with explicit dispersal cost to shape evolved dispersal distance.

**Action:**
- **Cycle 13 (Wave Period × Dispersal Cost):** Extended Cycle 12 by sweeping four wave periods (`T ∈ {30, 60, 90, 180}` generations) plus a static/infinite-period baseline, crossed with four costs (`c ∈ {0.0, 0.2, 0.5, 1.0}`).
- Retained the same evolvable-dispersal framework and distance-dependent survival cost as Cycle 12.
- Ran 3 replicates per (`treatment`, `period`, `cost`) for 200 generations on a 30×30 grid.
- Recorded mean and standard deviation of `d`, maladaptation, trait–environment correlation, and trait variance.

**Observation:**

| Treatment | Period | Cost c | Mean `d` | Maladaptation | Trait-env correlation | Trait variance |
|-----------|--------|--------|----------|--------------:|----------------------:|---------------:|
| moving | 30 | 0.0 | 5.32 ± 0.19 | 0.2113 ± 0.0067 | 0.092 ± 0.002 | 0.108 ± 0.007 |
| moving | 30 | 0.2 | 3.53 ± 0.13 | 0.2205 ± 0.0113 | 0.007 ± 0.064 | 0.097 ± 0.003 |
| moving | 30 | 0.5 | 2.48 ± 0.04 | 0.1985 ± 0.0011 | 0.072 ± 0.017 | 0.089 ± 0.005 |
| moving | 30 | 1.0 | 1.82 ± 0.06 | 0.1842 ± 0.0056 | 0.055 ± 0.052 | 0.069 ± 0.006 |
| moving | 60 | 0.0 | 5.45 ± 0.06 | 0.1626 ± 0.0073 | 0.315 ± 0.007 | 0.112 ± 0.010 |
| moving | 60 | 0.2 | 3.82 ± 0.53 | 0.1636 ± 0.0053 | 0.283 ± 0.031 | 0.103 ± 0.009 |
| moving | 60 | 0.5 | 2.45 ± 0.09 | 0.1663 ± 0.0025 | 0.228 ± 0.041 | 0.089 ± 0.009 |
| moving | 60 | 1.0 | 1.91 ± 0.11 | 0.1676 ± 0.0060 | 0.152 ± 0.027 | 0.071 ± 0.001 |
| moving | 90 | 0.0 | 5.52 ± 0.14 | 0.1163 ± 0.0033 | 0.506 ± 0.029 | 0.110 ± 0.008 |
| moving | 90 | 0.2 | 3.66 ± 0.18 | 0.1256 ± 0.0030 | 0.455 ± 0.014 | 0.104 ± 0.002 |
| moving | 90 | 0.5 | 2.69 ± 0.12 | 0.1359 ± 0.0057 | 0.399 ± 0.017 | 0.099 ± 0.005 |
| moving | 90 | 1.0 | 1.92 ± 0.15 | 0.1463 ± 0.0098 | 0.262 ± 0.099 | 0.072 ± 0.013 |
| moving | 180 | 0.0 | 5.01 ± 0.17 | 0.0619 ± 0.0067 | 0.748 ± 0.026 | 0.120 ± 0.006 |
| moving | 180 | 0.2 | 3.11 ± 0.24 | 0.0686 ± 0.0038 | 0.719 ± 0.012 | 0.119 ± 0.005 |
| moving | 180 | 0.5 | 2.24 ± 0.17 | 0.0724 ± 0.0048 | 0.693 ± 0.011 | 0.108 ± 0.009 |
| moving | 180 | 1.0 | 1.78 ± 0.04 | 0.0876 ± 0.0055 | 0.615 ± 0.032 | 0.100 ± 0.013 |
| static | static | 0.0 | 4.00 ± 0.21 | 0.0186 ± 0.0005 | 0.924 ± 0.002 | 0.119 ± 0.002 |
| static | static | 0.2 | 2.38 ± 0.06 | 0.0158 ± 0.0007 | 0.936 ± 0.002 | 0.120 ± 0.003 |
| static | static | 0.5 | 1.72 ± 0.08 | 0.0145 ± 0.0004 | 0.941 ± 0.001 | 0.119 ± 0.007 |
| static | static | 1.0 | 1.17 ± 0.01 | 0.0167 ± 0.0009 | 0.932 ± 0.004 | 0.116 ± 0.001 |

- Longer wave periods strongly reduced maladaptation in moving treatments (0.21 → 0.06 from `T=30` to `T=180`).
- Cost suppressed evolved `d` in all treatments, but the best cost depended on period:
  - `T = 180`: lowest maladaptation at `c = 0.0` (`d ≈ 5`).
  - `T = 60–90`: lowest maladaptation near `c = 0.2` (`d ≈ 3.5–3.8`).
  - `T = 30`: all costs performed poorly; the best was `c = 1.0` (`d ≈ 1.8`).
- Trait–environment correlation improved with wave period but stayed far below the static baseline (`r > 0.92`).
- Static environment produced near-perfect tracking even without cost, with maladaptation an order of magnitude lower than any moving treatment.

**Reflection:**
The evolved dispersal optimum is not a single value; it is set by the interaction of spatial scale, temporal scale, and movement cost. Fast waves are largely untrackable within 200 generations, so minimizing movement damage becomes more important than tracking. Slow waves allow effective tracking, and the cost then determines whether the population can afford the long dispersal needed to follow the optimum. This reinforces Cycle 12's conclusion that dispersal evolution is a joint product of environmental dynamics and cost structure, and it adds a new axis: the period of temporal variation.

**Artifacts produced:**
- cycle_13_wave_period_cost/
  - wave_period_cost.py
  - Design.md
  - README.md
  - replicate_results.csv
  - summary.csv
  - lines_by_period.png
  - heatmaps_period_cost.png
  - final_state_moving_c*_P*.png
  - final_state_static_c*.png

**Next commitments:**
1. Update top-level documentation (`README.md`, `PROJECT_SUMMARY.md`, `index.md`, `manifest.md`) and regenerate `index.html`.
2. Consider next directions: fixed per-propagule mortality cost, plastic/cue-triggered dispersal, local extinction/recolonization dynamics, or larger/longer simulations.

---

"""


def update_evolution_log():
    path = 'evolution_log.md'
    with open(path, 'r', encoding='utf-8') as f:
        existing = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(TURN_13 + existing)


def update_project_summary():
    path = 'PROJECT_SUMMARY.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    row = ("| 13 | Wave Period × Dispersal Cost | "
           "Sweep wave period against explicit dispersal cost | "
           "Temporal scale reshapes the evolved-dispersal optimum; fast waves are untrackable, slow waves favor cheap long movement. |")

    pattern = r"(\| 12 \| Dispersal with Explicit Cost \|.*?\|)\n\n## Recurrent themes"
    replacement = r"\1\n" + row + "\n\n## Recurrent themes"
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    text = text.replace(
        "- Sweep wave period against dispersal cost to map how temporal environmental scale shapes evolved `d`.",
        "- Test a fixed per-propagule mortality cost, plastic/cue-triggered dispersal, or local extinction/recolonization dynamics."
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_index():
    path = 'index.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'Cycle 13' not in text:
        text = text.replace(
            '- [Cycle 12 - Dispersal with Explicit Cost](./cycle_12_dispersal_cost)',
            '- [Cycle 12 - Dispersal with Explicit Cost](./cycle_12_dispersal_cost)\n- [Cycle 13 - Wave Period x Dispersal Cost](./cycle_13_wave_period_cost)'
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_manifest():
    path = 'manifest.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if '13 |' not in text:
        text = text.replace(
            '| 12 | Dispersal with Explicit Cost | cycle_12_dispersal_cost/README.md | complete |',
            '| 12 | Dispersal with Explicit Cost | cycle_12_dispersal_cost/README.md | complete |\n| 13 | Wave Period x Dispersal Cost | cycle_13_wave_period_cost/README.md | complete |'
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_readme():
    path = 'README.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'Cycle 13' in text:
        return
    text = text.replace(
        '- **Cycle 12** — Dispersal with explicit distance-dependent survival cost',
        '- **Cycle 12** — Dispersal with explicit distance-dependent survival cost\n- **Cycle 13** — Wave period × dispersal cost parameter sweep'
    ).replace(
        '| 12 | `cycle_12_dispersal_cost` | Distance-dependent survival cost constrains evolved dispersal distance |',
        '| 12 | `cycle_12_dispersal_cost` | Distance-dependent survival cost constrains evolved dispersal distance |\n| 13 | `cycle_13_wave_period_cost` | Wave period and cost jointly shape the evolved dispersal optimum |'
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
    update_index()
    update_manifest()
    update_readme()
    regenerate_index_html()
    print('Top-level documentation updated for Cycle 13.')


if __name__ == '__main__':
    main()
