import os
import re

TURN_17 = """## Turn 17 — Bias Switch

**Intention:** Ask whether a population that has evolved under one systematic cue bias can re-tune its plastic response when the bias flips sign mid-run.

**Action:**
- **Cycle 17 (Bias Switch):** Extended Cycle 16 so that the cue bias `b` changes sign at generation 70.
- Conditions: `neg_const` (`b = -0.30`), `pos_const` (`b = +0.30`), `neg_to_pos` (`-0.30 -> +0.30`), `pos_to_neg` (`+0.30 -> -0.30`).
- Each condition was run under `moving` and `static` environments with 3 replicates for 140 generations.
- Recorded `alpha`, `beta`, `p_base`, maladaptation, and trait-environment correlation.

**Observation:**

| treatment | condition | phase | beta | p_base | maladaptation |
|-----------|-----------|-------|------|--------|--------------:|
| moving | neg_const | pre | 1.13 ± 0.09 | 0.519 ± 0.042 | 0.141 ± 0.008 |
| moving | neg_const | post | 1.03 ± 0.11 | 0.698 ± 0.051 | 0.135 ± 0.004 |
| moving | pos_const | pre | 1.46 ± 0.03 | 0.408 ± 0.009 | 0.136 ± 0.011 |
| moving | pos_const | post | 1.52 ± 0.05 | 0.456 ± 0.023 | 0.131 ± 0.002 |
| moving | neg_to_pos | pre | 0.92 ± 0.26 | 0.580 ± 0.032 | 0.131 ± 0.008 |
| moving | neg_to_pos | post | 0.99 ± 0.37 | 0.625 ± 0.079 | 0.128 ± 0.003 |
| moving | pos_to_neg | pre | 1.50 ± 0.02 | 0.357 ± 0.034 | 0.130 ± 0.005 |
| moving | pos_to_neg | post | 1.42 ± 0.05 | 0.540 ± 0.041 | 0.146 ± 0.002 |
| static | neg_const | pre | 1.06 ± 0.17 | 0.531 ± 0.033 | 0.017 ± 0.0005 |
| static | neg_const | post | 1.10 ± 0.20 | 0.655 ± 0.035 | 0.016 ± 0.0002 |
| static | pos_const | pre | 1.47 ± 0.06 | 0.357 ± 0.015 | 0.019 ± 0.002 |
| static | pos_const | post | 1.51 ± 0.08 | 0.422 ± 0.002 | 0.017 ± 0.001 |
| static | neg_to_pos | pre | 1.06 ± 0.18 | 0.543 ± 0.018 | 0.019 ± 0.0003 |
| static | neg_to_pos | post | 1.15 ± 0.07 | 0.602 ± 0.018 | 0.017 ± 0.0002 |
| static | pos_to_neg | pre | 1.38 ± 0.09 | 0.352 ± 0.023 | 0.018 ± 0.001 |
| static | pos_to_neg | post | 1.38 ± 0.11 | 0.521 ± 0.030 | 0.018 ± 0.0005 |

- Maladaptation stayed low after the switch in both environments; post-switch values were comparable to the constant-bias controls.
- In the static environment, `p_base` shifted clearly after the flip, but `beta` often retained a memory of the pre-switch regime. The population reached a new viable operating point rather than mirroring the constant-bias state.
- In the moving environment, parameters were noisier and trajectories overlapped broadly with the controls.

**Reflection:**
Cue compensation is reversible in performance even if not reversible in the exact parameter values. After a bias flip, the population reaches a new point in the `(alpha, beta, p_base)` space that preserves low maladaptation. In static environments this new point can be path-dependent, revealing redundant degrees of freedom in the decision rule.

**Artifacts produced:**
- cycle_17_bias_switch/
  - cycle_17_bias_switch.py
  - README.md
  - results.csv
  - moving_results.csv
  - static_results.csv
  - replicate_phase_means.csv
  - phase_summary.csv
  - trajectories.png

**Next commitments:**
1. Update top-level documentation and regenerate `index.html`.
2. Explore whether frequent or gradual bias switches select for more flexible, history-independent strategies, or whether a learned/calibrated bias can evolve.

---

"""

TURN_16 = """## Turn 16 — Biased Cues and Compensatory Emigration

**Intention:** Test whether a systematically biased maladaptation cue can be offset by co-evolved changes in the emigration rule.

**Action:**
- **Cycle 16 (Biased Cues):** Extended the plastic-cue model from Cycle 15 by separating emigration into a baseline probability `p_base` and a plastic gain `beta`:
  `emigrate_prob = sigmoid(beta * m_obs - theta)`, where `theta = -logit(p_base)`.
- Effective dispersal distance remained `d_eff = clamp(d + round(alpha * m_obs), 1, d_max)`.
- Applied a fixed cue bias `b in {-0.30, -0.15, 0.0, +0.15, +0.30}` from the start of each run, so `m_obs = max(0, m_true + b + eta)`.
- Ran 5 replicates per (treatment, bias) under moving and static environments for 180 generations.
- Recorded `alpha`, `beta`, `p_base`, maladaptation, and trait-environment correlation.

**Observation:**

| treatment | bias | alpha | beta | p_base | maladaptation | trait-env corr |
|-----------|------|-------|------|--------|--------------:|---------------:|
| moving | -0.30 | 2.85 ± 0.94 | 0.96 ± 0.13 | 0.658 ± 0.052 | 0.135 ± 0.003 | 0.394 ± 0.027 |
| moving | -0.15 | 3.00 ± 0.43 | 1.26 ± 0.08 | 0.651 ± 0.013 | 0.135 ± 0.004 | 0.389 ± 0.032 |
| moving | 0.00 | 2.38 ± 0.09 | 1.46 ± 0.03 | 0.573 ± 0.032 | 0.136 ± 0.002 | 0.370 ± 0.023 |
| moving | +0.15 | 2.50 ± 0.40 | 1.39 ± 0.03 | 0.530 ± 0.016 | 0.135 ± 0.003 | 0.385 ± 0.008 |
| moving | +0.30 | 2.49 ± 0.32 | 1.45 ± 0.06 | 0.482 ± 0.008 | 0.128 ± 0.005 | 0.423 ± 0.025 |
| static | -0.30 | 2.50 ± 0.15 | 0.99 ± 0.20 | 0.625 ± 0.022 | 0.017 ± 0.0005 | 0.930 ± 0.002 |
| static | -0.15 | 2.37 ± 0.11 | 1.09 ± 0.03 | 0.565 ± 0.037 | 0.018 ± 0.0004 | 0.926 ± 0.002 |
| static | 0.00 | 2.05 ± 0.24 | 1.25 ± 0.10 | 0.556 ± 0.057 | 0.018 ± 0.001 | 0.925 ± 0.004 |
| static | +0.15 | 2.40 ± 0.39 | 1.39 ± 0.12 | 0.490 ± 0.026 | 0.018 ± 0.0002 | 0.927 ± 0.001 |
| static | +0.30 | 1.64 ± 0.39 | 1.42 ± 0.02 | 0.427 ± 0.049 | 0.017 ± 0.0004 | 0.930 ± 0.002 |

- A negative bias (cue understates maladaptation) selected for higher `p_base`; a positive bias selected for higher `beta` and lower `p_base`.
- Maladaptation remained nearly flat across biases in both environments, showing that the system can compensate for persistent cue bias.
- `alpha` was more variable than in earlier plastic-cue cycles, especially under moving conditions, suggesting that distance modulation is partly redundant with emigration probability.

**Reflection:**
The population does not need a perfectly unbiased cue to make good dispersal decisions. It can evolve a compensatory emigration rule (`beta`, `p_base`) that largely neutralizes a biased cue. This leaves open the question of what happens when the bias *changes* during evolution, which is explored in Cycle 17.

**Artifacts produced:**
- cycle_16_bias_emigration/
  - cycle_16_bias_emigration.py
  - README.md
  - Design.md
  - replicate_means.csv
  - combined_summary.csv
  - summary.csv
  - static_summary.csv
  - moving_summary.csv
  - bias_emigration.py
  - bias_means.png

**Next commitments:**
1. Update top-level documentation and regenerate `index.html`.
2. Test reversibility: flip the cue bias mid-run and ask whether the population re-tunes its compensatory rule.

---

"""


def update_evolution_log():
    path = 'evolution_log.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if '## Turn 17' in text:
        print('evolution_log.md already has Turn 17.')
        return
    marker = '## Turn 15'
    if marker not in text:
        print('Could not find Turn 15 marker in evolution_log.md')
        return
    text = TURN_17 + TURN_16 + text
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('evolution_log.md updated.')


def update_project_summary():
    path = 'PROJECT_SUMMARY.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    row16 = ("| 16 | Biased Cues and Compensatory Emigration | "
             "Separable baseline probability and plastic gain on emigration | "
             "Persistent cue bias is offset by co-evolved `beta` and `p_base`; maladaptation stays flat across biases. |")
    row17 = ("| 17 | Adapting to a Bias Switch | "
             "Cue bias flips sign at generation 70 | "
             "Population re-tunes parameters and keeps maladaptation low; re-tuning is path-dependent in static environments. |")

    marker = '| 15 | Cue Robustness'
    if marker in text and '| 16 |' not in text:
        text = text.replace(marker, row16 + '\n' + row17 + '\n' + marker)

    # de-duplicate extensions list
    text = re.sub(
        r'\n- \[x\] Test noisy or costly plastic cues \(Cycle 15\)\. Consider biased cues or probabilistic emigration rules\.',
        '',
        text
    )
    if 'Consider cue bias as an evolvable or switchable property.' not in text:
        text = text.replace(
            '## Possible extensions',
            '## Possible extensions\n- Consider cue bias as an evolvable or switchable property.\n- Test whether frequent bias switches select for a calibrated cue or a history-independent strategy.'
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('PROJECT_SUMMARY.md updated.')


def update_index_md():
    path = 'index.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'Cycle 17' not in text:
        text = text.replace(
            '- [Cycle 15 - Cue Robustness](./cycle_15_cue_robustness)',
            ('- [Cycle 15 - Cue Robustness](./cycle_15_cue_robustness)\n'
             '- [Cycle 16 - Biased Cues and Compensatory Emigration](./cycle_16_bias_emigration)\n'
             '- [Cycle 17 - Bias Switch](./cycle_17_bias_switch)')
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('index.md updated.')


def update_manifest():
    path = 'manifest.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if '16 |' not in text:
        text = text.replace(
            '| 15 | Cue Robustness | cycle_15_cue_robustness/README.md | complete |',
            ('| 15 | Cue Robustness | cycle_15_cue_robustness/README.md | complete |\n'
             '| 16 | Biased Cues and Compensatory Emigration | cycle_16_bias_emigration/README.md | complete |\n'
             '| 17 | Bias Switch | cycle_17_bias_switch/README.md | complete |')
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('manifest.md updated.')


def update_readme():
    path = 'README.md'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'Cycle 17' not in text:
        text = text.replace(
            '- **Cycle 15** — Noisy cue and maintenance cost test the robustness of plastic dispersal',
            ('- **Cycle 15** — Noisy cue and maintenance cost test the robustness of plastic dispersal\n'
             '- **Cycle 16** — Biased cues are offset by co-evolved compensatory emigration\n'
             '- **Cycle 17** — Population re-tunes emigration parameters after a mid-run cue-bias flip')
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('README.md updated.')


def regenerate_index_html():
    if os.path.exists('build_index.py'):
        os.system('python build_index.py')
        print('index.html regenerated.')
    else:
        print('build_index.py not found.')


def main():
    update_evolution_log()
    update_project_summary()
    update_index_md()
    update_manifest()
    update_readme()
    regenerate_index_html()


if __name__ == '__main__':
    main()
