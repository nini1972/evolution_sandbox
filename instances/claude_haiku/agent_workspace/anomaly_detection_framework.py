#!/usr/bin/env python3
"""
Anomaly Detection Framework for Kuramoto & Chaotic Dynamics

Purpose: When experimental results arrive, this framework will:
1. Compare against canonical treaties
2. Detect statistically significant deviations
3. Flag potential novel phenomena
4. Generate hypothesis suggestions

This is meta-science: we're hunting for deviations from known laws.
"""

import numpy as np
from scipy import stats
import json

class AnomalyDetector:
    """Meta-analyzer for detecting novel phenomena in dynamical systems data."""
    
    def __init__(self):
        self.canonical_laws = {
            'kuramoto_scaling_exponent': {
                'value': -0.363,
                'tolerance': 0.03,
                'source': 'TREATY_001_KURAMOTO_SCALING_LAW'
            },
            'thomas_entropy_peak': {
                'b_range': [0.08, 0.12],
                'entropy_level': 0.5,  # bits, relative to chaos
                'source': 'TREATY_002_THOMAS_EDGE_CHAOS_ENTROPY'
            },
            'explosive_sync_threshold': {
                'K_c_range': [1.40, 1.82],
                'noise_collapse_rate': 0.25,  # bits per sigma unit
                'source': 'TREATY_001_KURAMOTO_EXPLOSIVE_SYNCHRONIZATION'
            }
        }
        
        self.anomalies = []
        self.hypotheses = []
    
    def flag_scaling_exponent_anomaly(self, measured_exponent, topology_name, N_range):
        """Check if scaling exponent deviates from canonical -0.363."""
        canonical = self.canonical_laws['kuramoto_scaling_exponent']['value']
        tol = self.canonical_laws['kuramoto_scaling_exponent']['tolerance']
        
        deviation = measured_exponent - canonical
        z_score = deviation / tol
        
        if abs(deviation) > tol:
            anomaly = {
                'type': 'scaling_exponent_deviation',
                'severity': 'HIGH' if abs(z_score) > 2 else 'MEDIUM',
                'measured': measured_exponent,
                'canonical': canonical,
                'deviation': deviation,
                'z_score': z_score,
                'topology': topology_name,
                'N_range': N_range,
                'hypothesis': self._generate_topology_hypothesis(topology_name, deviation)
            }
            self.anomalies.append(anomaly)
            return True
        return False
    
    def _generate_topology_hypothesis(self, topology_name, deviation):
        """Generate scientifically motivated hypothesis for topology-dependent scaling."""
        if deviation < -0.363:  # More negative = faster finite-size convergence
            return (
                f"Hypothesis: '{topology_name}' may have higher connectivity density, "
                f"reducing finite-size effects. This could indicate a hidden universality class "
                f"where alpha_topo = -0.363 * (D_topo / D_random), where D is a structural dimension."
            )
        else:  # Less negative = slower convergence
            return (
                f"Hypothesis: '{topology_name}' may exhibit frustration or community structure, "
                f"slowing synchronization. Could test via measuring clustering coefficient correlation "
                f"with scaling exponent: alpha_topo = alpha_random + beta * C_clustering^gamma."
            )
    
    def detect_entropy_phase_transition(self, entropy_curve, b_values):
        """Detect if entropy peak location matches canonical range [0.08, 0.12]."""
        canonical_range = self.canonical_laws['thomas_entropy_peak']['b_range']
        
        peak_idx = np.argmax(entropy_curve)
        peak_b = b_values[peak_idx]
        
        if peak_b < canonical_range[0] or peak_b > canonical_range[1]:
            anomaly = {
                'type': 'entropy_peak_shift',
                'severity': 'MEDIUM',
                'measured_peak_b': peak_b,
                'canonical_range': canonical_range,
                'offset': peak_b - np.mean(canonical_range),
                'hypothesis': (
                    f"Peak entropy shifts to b={peak_b:.3f}. Could indicate "
                    f"parameter-dependent phase transition threshold. "
                    f"Test: Is this shift correlated with Lyapunov exponent sign change?"
                )
            }
            self.anomalies.append(anomaly)
            return True
        return False
    
    def detect_hysteresis_collapse_signature(self, noise_levels, hysteresis_areas):
        """Check if hysteresis area collapses monotonically with noise as per canonical law."""
        # Canonical: dA/dsigma ~ -0.25 bits/sigma
        expected_slope = -0.25
        
        # Fit actual slope
        if len(noise_levels) >= 2:
            fit = np.polyfit(noise_levels, hysteresis_areas, 1)
            measured_slope = fit[0]
            
            if abs(measured_slope - expected_slope) / abs(expected_slope) > 0.2:
                anomaly = {
                    'type': 'hysteresis_collapse_deviation',
                    'severity': 'MEDIUM',
                    'measured_slope': measured_slope,
                    'expected_slope': expected_slope,
                    'relative_error': (measured_slope - expected_slope) / expected_slope,
                    'hypothesis': (
                        f"Hysteresis collapse rate differs from canonical. "
                        f"Possible mechanism: nonlinear coupling feedback modifies noise susceptibility. "
                        f"Test: Check if slope depends on oscillator frequency distribution width."
                    )
                }
                self.anomalies.append(anomaly)
                return True
        return False
    
    def generate_followup_experiment(self, anomaly):
        """Given an anomaly, suggest a targeted followup experiment."""
        atype = anomaly.get('type')
        
        if atype == 'scaling_exponent_deviation':
            return {
                'title': f"Topology Dependence: Measure clustering-exponent correlation",
                'description': (
                    f"Hypothesis: exponent alpha(C_clust). Measure clustering coefficient C and alpha "
                    f"on 5-10 random topologies with varying clustering. If alpha = a_0 + b*C, "
                    f"we have discovered a hidden topological invariant."
                ),
                'estimated_cost': 'medium',
                'parameters': ['clustering_coefficient', 'exponent', 'N_range']
            }
        elif atype == 'entropy_peak_shift':
            return {
                'title': "Entropy Peak Dependence: Scan system parameters",
                'description': (
                    f"Hypothesis: peak location depends on Lyapunov exponent sign. "
                    f"Parametric scan: vary control parameter, track both entropy peak and "
                    f"Lyapunov exponent lambda_max. Test if peak(b) = f(lambda_max)."
                ),
                'estimated_cost': 'medium',
                'parameters': ['lyapunov_exponent', 'entropy_peak', 'parameter_scan']
            }
        elif atype == 'hysteresis_collapse_deviation':
            return {
                'title': "Frequency Distribution Dependence: Measure collapse vs dispersion",
                'description': (
                    f"Hypothesis: collapse slope depends on omega_variance. "
                    f"Vary sigma_omega in {0, 0.1, 0.5, 1.0}, measure hysteresis vs noise. "
                    f"If slope(sigma_omega) exhibits nonlinearity, indicates quenched disorder renormalization."
                ),
                'estimated_cost': 'high',
                'parameters': ['omega_variance', 'hysteresis_area', 'noise_level']
            }
        
        return None
    
    def summarize_findings(self):
        """Generate summary report of all detected anomalies and suggested followup."""
        report = {
            'total_anomalies': len(self.anomalies),
            'high_severity': len([a for a in self.anomalies if a.get('severity') == 'HIGH']),
            'medium_severity': len([a for a in self.anomalies if a.get('severity') == 'MEDIUM']),
            'anomalies': self.anomalies,
            'followup_experiments': []
        }
        
        for anomaly in self.anomalies:
            followup = self.generate_followup_experiment(anomaly)
            if followup:
                report['followup_experiments'].append(followup)
        
        return report

# ============================================================================
# Example Usage (Test)
# ============================================================================

if __name__ == '__main__':
    detector = AnomalyDetector()
    
    # Simulate discovering a topology-dependent exponent
    print("Testing anomaly detection...")
    
    # Scenario 1: Scale-free topology has different exponent
    detector.flag_scaling_exponent_anomaly(-0.42, 'scale_free', [32, 128])
    
    # Scenario 2: Thomas entropy peak shifted
    b_test = np.linspace(0.05, 0.20, 100)
    entropy_test = np.exp(-((b_test - 0.15)**2 / 0.01))  # Peak at b=0.15 (outside range)
    detector.detect_entropy_phase_transition(entropy_test, b_test)
    
    # Scenario 3: Hysteresis collapse too slow
    noise_test = np.array([0.01, 0.05, 0.10, 0.15])
    hysteresis_test = 1.0 - 0.10 * noise_test  # Slope -0.10, not -0.25
    detector.detect_hysteresis_collapse_signature(noise_test, hysteresis_test)
    
    # Print findings
    summary = detector.summarize_findings()
    print(json.dumps(summary, indent=2))
