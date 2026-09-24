import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import stats
from scipy.optimize import curve_fit

# Configure matplotlib for headless operation
plt.switch_backend('Agg')

class CriticalTransitionAnalyzer:
    def __init__(self):
        self.ca_data = None
        self.load_data()
    
    def load_data(self):
        '''Load the cellular automata analysis data'''
        try:
            with open('ca_emergence_analysis.json', 'r') as f:
                self.ca_data = json.load(f)
        except FileNotFoundError:
            print('CA data not found. Please run ca_explorer.py first.')
            return
    
    def extract_metrics(self):
        '''Extract key metrics for analysis'''
        if not self.ca_data:
            return None, None, None
            
        rules = []
        spatial_entropies = []
        temporal_complexities = []
        
        for rule_str, data in self.ca_data.items():
            rules.append(int(rule_str))
            spatial_entropies.append(data['spatial_entropy_single'])
            temporal_complexities.append(data['temporal_complexity_single'])
            
        return np.array(rules), np.array(spatial_entropies), np.array(temporal_complexities)
    
    def find_critical_point(self, x, y):
        '''Find critical transition point using change point detection'''
        # Sort data by x
        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]
        
        # Calculate moving averages and gradients
        window = 3
        if len(x_sorted) < window * 2:
            return None
            
        gradients = []
        x_points = []
        
        for i in range(window, len(x_sorted) - window):
            left_mean = np.mean(y_sorted[i-window:i])
            right_mean = np.mean(y_sorted[i:i+window])
            gradient = abs(right_mean - left_mean)
            gradients.append(gradient)
            x_points.append(x_sorted[i])
        
        if gradients:
            max_gradient_idx = np.argmax(gradients)
            return x_points[max_gradient_idx], gradients[max_gradient_idx]
        
        return None
    
    def fit_scaling_law(self, x, y):
        '''Fit exponential scaling law'''
        def exponential_func(x, a, b, c):
            return a * np.exp(b * x) + c
        
        def power_func(x, a, b, c):
            return a * (x ** b) + c
            
        try:
            # Fit exponential
            popt_exp, pcov_exp = curve_fit(exponential_func, x, y, 
                                          p0=[1, 1, 0], maxfev=5000)
            
            # Fit power law
            popt_pow, pcov_pow = curve_fit(power_func, x, y, 
                                          p0=[1, 2, 0], maxfev=5000)
            
            # Calculate R-squared for both fits
            y_exp_pred = exponential_func(x, *popt_exp)
            y_pow_pred = power_func(x, *popt_pow)
            
            ss_res_exp = np.sum((y - y_exp_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2_exp = 1 - (ss_res_exp / ss_tot)
            
            ss_res_pow = np.sum((y - y_pow_pred) ** 2)
            r2_pow = 1 - (ss_res_pow / ss_tot)
            
            return {
                'exponential': {'params': popt_exp, 'r2': r2_exp, 'func': exponential_func},
                'power': {'params': popt_pow, 'r2': r2_pow, 'func': power_func}
            }
            
        except:
            return None
    
    def analyze_phase_transitions(self):
        '''Comprehensive analysis of phase transitions'''
        rules, spatial_entropies, temporal_complexities = self.extract_metrics()
        
        if rules is None:
            print('No data available for analysis')
            return
        
        # Find critical points
        spatial_critical = self.find_critical_point(spatial_entropies, temporal_complexities)
        
        # Fit scaling laws
        scaling_fits = self.fit_scaling_law(spatial_entropies, temporal_complexities)
        
        # Create comprehensive visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Main phase diagram with critical point
        scatter = ax1.scatter(spatial_entropies, temporal_complexities, 
                             c=rules, cmap='viridis', s=100, alpha=0.8, edgecolors='black')
        
        # Annotate points
        for i, rule in enumerate(rules):
            ax1.annotate(f'R{rule}', (spatial_entropies[i], temporal_complexities[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Mark critical point
        if spatial_critical:
            ax1.axvline(x=spatial_critical[0], color='red', linestyle='--', alpha=0.7, 
                       label=f'Critical Point: {spatial_critical[0]:.2f}')
            ax1.legend()
        
        ax1.set_xlabel('Spatial Block Entropy')
        ax1.set_ylabel('Temporal LZ Complexity')
        ax1.set_title('CA Phase Diagram with Critical Transition')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, label='Rule Number')
        
        # 2. Scaling law fits
        if scaling_fits:
            x_smooth = np.linspace(min(spatial_entropies), max(spatial_entropies), 100)
            
            exp_fit = scaling_fits['exponential']
            pow_fit = scaling_fits['power']
            
            y_exp_smooth = exp_fit['func'](x_smooth, *exp_fit['params'])
            y_pow_smooth = pow_fit['func'](x_smooth, *pow_fit['params'])
            
            ax2.scatter(spatial_entropies, temporal_complexities, alpha=0.7, color='blue')
            ax2.plot(x_smooth, y_exp_smooth, 'r-', 
                    label=f'Exponential (R²={exp_fit["r2"]:.3f})')
            ax2.plot(x_smooth, y_pow_smooth, 'g-', 
                    label=f'Power Law (R²={pow_fit["r2"]:.3f})')
            
            ax2.set_xlabel('Spatial Block Entropy')
            ax2.set_ylabel('Temporal LZ Complexity')
            ax2.set_title('Scaling Law Analysis')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. Rule classification by complexity regime
        low_complex = rules[temporal_complexities < 30]
        med_complex = rules[(temporal_complexities >= 30) & (temporal_complexities < 60)]
        high_complex = rules[temporal_complexities >= 60]
        
        ax3.bar([1, 2, 3], [len(low_complex), len(med_complex), len(high_complex)], 
                color=['lightblue', 'orange', 'red'], alpha=0.7)
        ax3.set_xticks([1, 2, 3])
        ax3.set_xticklabels(['Low\\n(<30)', 'Medium\\n(30-60)', 'High\\n(>60)'])
        ax3.set_ylabel('Number of Rules')
        ax3.set_title('Complexity Regime Classification')
        
        # Add rule numbers as text
        for i, (regime, rules_list) in enumerate(zip(['Low', 'Medium', 'High'], 
                                                    [low_complex, med_complex, high_complex])):
            rule_str = ', '.join([f'R{r}' for r in rules_list])
            ax3.text(i+1, len(rules_list)/2, rule_str, ha='center', va='center', 
                    fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # 4. Entropy vs Rule Number
        ax4.scatter(rules, spatial_entropies, alpha=0.7, s=60, color='purple')
        ax4.set_xlabel('Rule Number')
        ax4.set_ylabel('Spatial Block Entropy')
        ax4.set_title('Spatial Entropy by Rule Number')
        ax4.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(rules, spatial_entropies, 1)
        p = np.poly1d(z)
        ax4.plot(rules, p(rules), 'r--', alpha=0.7, 
                label=f'Trend: y={z[0]:.4f}x+{z[1]:.2f}')
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig('critical_transition_analysis.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # Generate summary report
        self.generate_analysis_report(spatial_critical, scaling_fits, 
                                    low_complex, med_complex, high_complex)
        
        print('Critical transition analysis complete!')
        print(f'Generated: critical_transition_analysis.png')
        
    def generate_analysis_report(self, spatial_critical, scaling_fits, 
                                low_complex, med_complex, high_complex):
        '''Generate detailed analysis report'''
        
        report = '''# Critical Transition Analysis Report

## Archaeological Discovery: Universal Phase Transition

### Critical Point Detection
'''
        
        if spatial_critical:
            report += f'''
**Critical Spatial Entropy**: {spatial_critical[0]:.3f}
**Transition Strength**: {spatial_critical[1]:.3f}

This represents a fundamental phase boundary in the CA complexity landscape.
Rules below this threshold exhibit ordered, predictable behavior.
Rules above this threshold exhibit chaotic, unpredictable dynamics.
'''
        
        if scaling_fits:
            exp_fit = scaling_fits['exponential']
            pow_fit = scaling_fits['power']
            
            report += f'''
### Scaling Law Analysis

**Exponential Model**: y = {exp_fit["params"][0]:.3f} * exp({exp_fit["params"][1]:.3f} * x) + {exp_fit["params"][2]:.3f}
- R² = {exp_fit["r2"]:.4f}

**Power Law Model**: y = {exp_fit["params"][0]:.3f} * x^{pow_fit["params"][1]:.3f} + {pow_fit["params"][2]:.3f}
- R² = {pow_fit["r2"]:.4f}

'''
            if exp_fit['r2'] > pow_fit['r2']:
                report += 'The **exponential model** provides a better fit, suggesting exponential scaling of complexity with spatial entropy.\\n'
            else:
                report += 'The **power law model** provides a better fit, suggesting power-law scaling of complexity with spatial entropy.\\n'
        
        report += f'''
### Complexity Classification

**Low Complexity Regime** (Temporal Complexity < 30):
Rules: {', '.join([f'R{r}' for r in low_complex])}
Count: {len(low_complex)} rules

**Medium Complexity Regime** (Temporal Complexity 30-60):
Rules: {', '.join([f'R{r}' for r in med_complex])}
Count: {len(med_complex)} rules

**High Complexity Regime** (Temporal Complexity > 60):
Rules: {', '.join([f'R{r}' for r in high_complex])}
Count: {len(high_complex)} rules

### Archaeological Significance

This analysis reveals a clear **complexity stratification** in cellular automata rule space.
The critical transition point represents a fundamental computational phase boundary,
analogous to critical points in statistical mechanics or fluid dynamics.

The scaling relationship between spatial entropy and temporal complexity suggests
universal organizing principles that govern emergence across different CA rules.

### Next Excavation Steps

1. Test the critical point hypothesis on additional CA rules
2. Investigate 2D cellular automata for similar phase transitions  
3. Compare with critical points in other dynamical systems
4. Develop theoretical framework for predicting critical boundaries
'''
        
        with open('critical_transition_report.md', 'w') as f:
            f.write(report)

if __name__ == '__main__':
    analyzer = CriticalTransitionAnalyzer()
    analyzer.analyze_phase_transitions()