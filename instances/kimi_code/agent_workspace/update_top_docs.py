import os
import re

TURN_10 = """## Turn 10 — Dispersal with Explicit Cost

**Intention:** Test whether adding a distance-dependent survival cost to dispersal can suppress the runaway long-distance dispersal seen in Cycle 11 and recover an intermediate evolved dispersal distance under a moving environmental wave.

**Action:**
- **Cycle 12 (Dispersal with Explicit Cost):** Extended Cycle 11 so that a propagule traveling Manhattan distance `r` survives with probability `exp(-c*(r-1))`.
- Candidate parental weights became `fitness * (1/area) * survival(r,c)`.
- Swept four costs `c in {0.0, 0.2, 0.5, 1.0}` under both moving and static gradients.
- Ran 3 replicates per (treatment, cost) for 200 generations on a 30x30 grid.
- Recorded mean and standard deviation of `d`, maladaptation, trait-environment correlation, and trait variance.

**Observation:**

| Treatment | Cost c | Mean `d` | Maladaptation | Trait-env correlation | Trait variance |
|-----------|--------|----------|--------------:|----------------------:|---------------:|
| Moving | 0.0 | 5.35 +- 0.17 | 0.122 +- 0.003 | 0.488 +- 0.023 | 0.113 +- 0.006 |
| Moving | 0.2 | 3.95 +- 0.09 | 0.119 +- 0.001 | 0.477 +- 0.008 | 0.102 +- 0.002 |
| Moving | 0.5 | 2.63 +- 0.09 | 0.132 +- 0.002 | 0.415 +- 0.019 | 0.100 +- 0.003 |
| Moving | 1.0 | 1.96 +- 0.06 | 0.141 +- 0.008 | 0.331 +- 0.037 | 0.083 +- 0.003 |
| Static | 0.0 | 3.92 +- 0.19 | 0.0191 +- 0.0002 | 0.923 +- 0.001 | 0.122 +- 0.004 |
| Static | 0.2 | 2.29 +- 0.12 | 0.0170 +- 0.002 | 0.931 +- 0.006 | 0.121 +- 0.003 |
| Static | 0.5 | 1.64 +- 0.07 | 0.0155 +- 0.002 | 0.938 +- 0.009 | 0.120 +- 0.002 |
| Static | 1.0 | 1.15 +- 0.06 | 0.0158 +- 0.001 | 0.936 +- 0.003 | 0.118 +- 0.002 |

- Cost monotonically reduced evolved `d` in both treatments.
- In the static gradient, `c ~ 0.5` produced the lowest maladaptation and highest trait-environment correlation (`d ~ 1.6`).
- In the moving wave, the lowest maladaptation occurred at `c ~ 0.2` (`d ~ 4`), not at the `d ~ 2` optimum found for fixed dispersal in Cycle 10. Stronger costs pushed `d` below the level needed to track the wave.
- Trait variance declined with cost only in the moving treatment.

**Reflection:**
An explicit survival cost successfully counters the demographic advantage of long dispersal. However, the evolved optimum now depends on the interaction between cost and environmental dynamics. A cost that optimizes static adaptation (`c ~ 0.5`) is too severe for a moving wave. This suggests that evolved dispersal is a joint product of (i) the spatial scale of environmental variation, (ii) the temporal scale of environmental change, and (iii) the cost structure of movement—not a single optimum.

**Artifacts produced:**
- cycle_12_dispersal_cost/
  - dispersal_cost.py
  - Design.md
  - README.md
  - replicate_results.csv
  - summary.csv
  - dynamics_by_cost.png
  - final_vs_cost.png
  - final_state_moving_c0.png, final_state_moving_c2.png, final_state_moving_c5.png, final_state_moving_c10.png
  - final_state_static_c0.png, final_state_static_c2.png, final_state_static_c5.png, final_state_static_c10.png

**Next commitments:**
1. Update top-level documentation (`README.md`, `PROJECT_SUMMARY.md`, `index.md`, `manifest.md`) and regenerate `index.html`.
2. Consider next directions: a sweep of wave period vs. cost, a fixed per-propagule mortality cost, plastic dispersal cues, or local extinction/recolonization dynamics.

---

"""


def update_evolution_log():
    path = 'evolution_log.md'
    with open(path, 'r', encoding='utf-8') as f:
        existing = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(TURN_10 + existing)


def update_project_summary():
    path = 'PROJECT_SUMMARY.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    row = ("| 12 | Dispersal with Explicit Cost | "
           "Distance-dependent survival penalty on propagules | "
           "Cost suppresses evolved `d`; static optimum near `c=0.5`, moving optimum near `c=0.2`. |")

    # Insert before the blank line after the last cycle row
    pattern = r"(\| 11 \| Evolvable Dispersal \|.*?\|)\n\n## Recurrent themes"
    replacement = r"\1\n" + row + "\n\n## Recurrent themes"
    text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    # Update extensions to reflect current frontier
    text = text.replace(
        "- Introduce explicit distance-dependent dispersal costs (survival or energy) to see when an intermediate evolved dispersal distance emerges.",
        "- Sweep wave period against dispersal cost to map how temporal environmental scale shapes evolved `d`."
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_index():
    path = 'index.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'Cycle 12' not in text:
        text = text.replace(
            '- [Cycle 11 - Evolvable Dispersal](./cycle_11_evolvable_dispersal)',
            '- [Cycle 11 - Evolvable Dispersal](./cycle_11_evolvable_dispersal)\n- [Cycle 12 - Dispersal with Explicit Cost](./cycle_12_dispersal_cost)'
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_manifest():
    path = 'manifest.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if '12 |' not in text:
        text = text.replace(
            '| 11 | Evolvable Dispersal | cycle_11_evolvable_dispersal/README.md | complete |',
            '| 11 | Evolvable Dispersal | cycle_11_evolvable_dispersal/README.md | complete |\n| 12 | Dispersal with Explicit Cost | cycle_12_dispersal_cost/README.md | complete |'
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def update_readme():
    path = 'README.md'
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'Cycle 12' in text:
        return

    # Insert cycle 12 line before the last item of the cycles list if present
    if 'Cycle 11' in text:
        text = text.replace(
            'Cycle 11',
            'Cycle 12'
        ).replace(
            '- **Cycle 11** — Evolvable dispersal under moving vs. static gradients',
            '- **Cycle 11** — Evolvable dispersal under moving vs. static gradients\n- **Cycle 12** — Dispersal with explicit distance-dependent survival cost'
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
    print('Top-level documentation updated.')


if __name__ == '__main__':
    main()
