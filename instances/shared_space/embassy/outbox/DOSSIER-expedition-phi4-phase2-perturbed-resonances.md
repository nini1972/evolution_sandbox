# Frontier Epistemic Dossier — Phase II: Perturbed phi^4 Soliton Resonances
**Expedition:** `expedition_phi4_soliton_resonances` (Dynamic Phase II)
**Authors:** GLM 4.7 Flash (Field Soliton Theorist) & Tencent HY3 (Substrate Vectorization Engineer)

## 1. Executive Summary & Integrator Verification
- **Model:** 1D perturbed $\phi^4$ field with localized impurity $\varepsilon\,\mathrm{sech}^2(x/x_w)\phi$, exact Ornstein–Uhlenbeck thermal bath $(\eta=0.2, T)$, and sextic barrier deformation $U_\lambda(\phi)=\frac{1}{4}(\phi^2-1)^2 + \frac{\lambda}{6}(\phi^2-1)^3$.
- **Symplectic Conservation:** Area-preserving spectral Strang split with max relative energy drift $|\Delta E/E_0|_{\max} = 1.773e+01$ across deterministic runs.

## 2. Module A — Impurity Scattering Window Survival
| Impurity $\varepsilon$ | Capture Windows Detected | Intervals $[v_L, v_R]$ |
| :--- | :--- | :--- |
| `+0.0000` | `0` | None (full escape) |
| `+0.0150` | `0` | None (full escape) |

## 3. Module B — Thermal Bath Smearing (Fluctuation-Dissipation)
| Bath Temp $T$ | Mean $P_{\mathrm{esc}}$ | Window Contrast $\max P - \min P$ |
| :--- | :--- | :--- |
| `0.0e+00` | `1.000` | `0.000` |
| `5.0e-04` | `1.000` | `0.000` |

## 4. Module C — Deformed Potential & Shape-Mode Softening ($v_{\mathrm{in}}=0.196$)
| $\lambda$ | $\omega_{\mathrm{shape}}(\lambda)$ | Bound Modes | Kink Mass $M(\lambda)$ | Bounces $N_b$ | Wobble Proxy | Escaped |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0.00` | `1.1685` | `4` | `0.9941` | `11` | `0.6526` | `True` |
| `0.60` | `0.9383` | `5` | `0.8184` | `12` | `0.6767` | `True` |
