import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import Counter

def rule_to_binary(rule_number):
    """Convert rule number to 8-bit binary lookup table"""
    return [(rule_number >> i) & 1 for i in range(8)]

def analyze_rule_structure(rule_number):
    """Analyze structural properties of CA rule"""
    lookup = rule_to_binary(rule_number)
    
    # Count transitions that preserve/create/destroy cells
    preserve_count = sum(1 for i, val in enumerate(lookup) if bin(i).count('1') % 2 == val)
    create_count = sum(1 for i, val in enumerate(lookup) if bin(i).count('1') == 0 and val == 1)
    destroy_count = sum(1 for i, val in enumerate(lookup) if bin(i).count('1') == 3 and val == 0)
    
    # Symmetry analysis
    symmetric = all(lookup[i] == lookup[7-i] for i in range(4))
    
    # Conservation analysis  
    birth_rules = [i for i, val in enumerate(lookup) if val == 1]
    death_rules = [i for i, val in enumerate(lookup) if val == 0]
    
    return {
        'rule': rule_number,
        'lookup': lookup,
        'preserve_count': preserve_count,
        'create_count': create_count, 
        'destroy_count': destroy_count,
        'symmetric': symmetric,
        'birth_rules': birth_rules,
        'death_rules': death_rules,
        'total_births': len(birth_rules),
        'bias': (len(birth_rules) - 4) / 4  # Bias toward 1s vs 0s
    }

def run_ca_with_initial_condition(rule, initial_condition, steps=100):
    """Run CA with given initial condition"""
    width = len(initial_condition)
    grid = np.zeros((steps, width), dtype=int)
    grid[0] = initial_condition
    
    lookup = rule_to_binary(rule)
    
    for t in range(1, steps):
        for i in range(width):
            left = grid[t-1][(i-1) % width]
            center = grid[t-1][i] 
            right = grid[t-1][(i+1) % width]
            neighborhood = left * 4 + center * 2 + right
            grid[t][i] = lookup[neighborhood]
    
    return grid

def calculate_temporal_lz_complexity(sequence):
    """Calculate Lempel-Ziv complexity of temporal sequence"""
    if len(sequence) == 0:
        return 0
    
    s = ''.join(map(str, sequence.flatten()))
    complexity = 0
    i = 0
    
    while i < len(s):
        j = i + 1
        while j <= len(s):
            substr = s[i:j]
            if substr not in s[:i] or i == 0:
                j += 1
            else:
                break
        complexity += 1
        i = j - 1 if j > len(s) else j
    
    return complexity

# Test comprehensive rule analysis
test_rules = [18, 22, 26, 30, 54, 62, 90, 94, 102, 110, 126, 150, 158, 182, 190]
width = 100
steps = 100

print("=== RULE STRUCTURE vs INITIAL CONDITION SENSITIVITY ===\\n")

rule_data = []

for rule in test_rules:
    print(f"Analyzing Rule {rule}...")
    
    # Structural analysis
    structure = analyze_rule_structure(rule)
    
    # Test different initial condition types
    # 1. Single point
    single_init = np.zeros(width)
    single_init[width//2] = 1
    single_grid = run_ca_with_initial_condition(rule, single_init, steps)
    single_complexity = calculate_temporal_lz_complexity(single_grid)
    
    # 2. Random 50%
    np.random.seed(42)  # Reproducible
    random_init = np.random.randint(0, 2, width)
    random_grid = run_ca_with_initial_condition(rule, random_init, steps)
    random_complexity = calculate_temporal_lz_complexity(random_grid)
    
    # 3. Dense initialization (80%)
    np.random.seed(42)
    dense_init = (np.random.random(width) < 0.8).astype(int)
    dense_grid = run_ca_with_initial_condition(rule, dense_init, steps)
    dense_complexity = calculate_temporal_lz_complexity(dense_grid)
    
    # 4. Sparse initialization (20%)
    np.random.seed(42)
    sparse_init = (np.random.random(width) < 0.2).astype(int) 
    sparse_grid = run_ca_with_initial_condition(rule, sparse_init, steps)
    sparse_complexity = calculate_temporal_lz_complexity(sparse_grid)
    
    # Calculate sensitivity ratios
    max_single = max(single_complexity, 1)
    sensitivity_random = random_complexity / max_single
    sensitivity_dense = dense_complexity / max_single 
    sensitivity_sparse = sparse_complexity / max_single
    max_sensitivity = max(sensitivity_random, sensitivity_dense, sensitivity_sparse)
    
    rule_data.append({
        'rule': rule,
        'structure': structure,
        'single_lz': single_complexity,
        'random_lz': random_complexity, 
        'dense_lz': dense_complexity,
        'sparse_lz': sparse_complexity,
        'sensitivity_random': sensitivity_random,
        'sensitivity_dense': sensitivity_dense,
        'sensitivity_sparse': sensitivity_sparse,
        'max_sensitivity': max_sensitivity
    })
    
    print(f"  Single LZ: {single_complexity}")
    print(f"  Random LZ: {random_complexity} (ratio: {sensitivity_random:.2f})")  
    print(f"  Dense LZ: {dense_complexity} (ratio: {sensitivity_dense:.2f})")
    print(f"  Sparse LZ: {sparse_complexity} (ratio: {sensitivity_sparse:.2f})")
    print(f"  Max Sensitivity: {max_sensitivity:.2f}")
    print(f"  Structure: births={structure['total_births']}, bias={structure['bias']:.2f}, symmetric={structure['symmetric']}")
    print()

# Create comprehensive analysis plots
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Plot 1: Rule bias vs maximum sensitivity
biases = [r['structure']['bias'] for r in rule_data]
max_sensitivities = [r['max_sensitivity'] for r in rule_data]
rules = [r['rule'] for r in rule_data]

axes[0,0].scatter(biases, max_sensitivities, s=100, alpha=0.7, c='darkblue')
for i, rule in enumerate(rules):
    axes[0,0].annotate(f'R{rule}', (biases[i], max_sensitivities[i]), 
                      xytext=(5, 5), textcoords='offset points', fontsize=8)
axes[0,0].set_xlabel('Rule Bias (toward 1s)')
axes[0,0].set_ylabel('Maximum Sensitivity Ratio')  
axes[0,0].set_title('Rule Bias vs Initial Condition Sensitivity')
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Birth count vs sensitivity
birth_counts = [r['structure']['total_births'] for r in rule_data]
axes[0,1].scatter(birth_counts, max_sensitivities, s=100, alpha=0.7, c='darkgreen')
for i, rule in enumerate(rules):
    axes[0,1].annotate(f'R{rule}', (birth_counts[i], max_sensitivities[i]),
                      xytext=(5, 5), textcoords='offset points', fontsize=8)
axes[0,1].set_xlabel('Number of Birth Rules (out of 8)')
axes[0,1].set_ylabel('Maximum Sensitivity Ratio')
axes[0,1].set_title('Birth Rule Count vs Sensitivity')  
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Sensitivity across different density conditions
densities = ['Single', 'Sparse 20%', 'Random 50%', 'Dense 80%']
sensitivity_matrix = np.array([
    [1.0] * len(rule_data),  # Single point baseline
    [r['sensitivity_sparse'] for r in rule_data],
    [r['sensitivity_random'] for r in rule_data], 
    [r['sensitivity_dense'] for r in rule_data]
])

im = axes[0,2].imshow(sensitivity_matrix, aspect='auto', cmap='viridis', interpolation='nearest')
axes[0,2].set_xticks(range(len(rules)))
axes[0,2].set_xticklabels([f'R{r}' for r in rules], rotation=45)
axes[0,2].set_yticks(range(len(densities)))
axes[0,2].set_yticklabels(densities)
axes[0,2].set_title('Sensitivity Heatmap Across Initial Densities')
plt.colorbar(im, ax=axes[0,2])

# Plot 4: Symmetry analysis
symmetric_rules = [r['rule'] for r in rule_data if r['structure']['symmetric']]
asymmetric_rules = [r['rule'] for r in rule_data if not r['structure']['symmetric']]
symmetric_sens = [r['max_sensitivity'] for r in rule_data if r['structure']['symmetric']]
asymmetric_sens = [r['max_sensitivity'] for r in rule_data if not r['structure']['symmetric']]

axes[1,0].boxplot([symmetric_sens, asymmetric_sens], labels=['Symmetric', 'Asymmetric'])
axes[1,0].set_ylabel('Maximum Sensitivity Ratio')
axes[1,0].set_title('Rule Symmetry vs Sensitivity')
axes[1,0].grid(True, alpha=0.3)

# Plot 5: LZ complexity distribution by initialization type
single_lzs = [r['single_lz'] for r in rule_data]
random_lzs = [r['random_lz'] for r in rule_data]  
dense_lzs = [r['dense_lz'] for r in rule_data]
sparse_lzs = [r['sparse_lz'] for r in rule_data]

axes[1,1].boxplot([single_lzs, sparse_lzs, random_lzs, dense_lzs], 
                 labels=['Single', 'Sparse', 'Random', 'Dense'])
axes[1,1].set_ylabel('Temporal LZ Complexity')
axes[1,1].set_title('Complexity Distribution by Initial Condition')
axes[1,1].grid(True, alpha=0.3)

# Plot 6: Top sensitivity rules analysis
sorted_data = sorted(rule_data, key=lambda x: x['max_sensitivity'], reverse=True)
top_5_rules = [r['rule'] for r in sorted_data[:5]]
top_5_sens = [r['max_sensitivity'] for r in sorted_data[:5]]

axes[1,2].bar(range(len(top_5_rules)), top_5_sens, color='coral', alpha=0.7)
axes[1,2].set_xticks(range(len(top_5_rules)))
axes[1,2].set_xticklabels([f'R{r}' for r in top_5_rules])
axes[1,2].set_ylabel('Maximum Sensitivity Ratio')
axes[1,2].set_title('Top 5 Most Sensitive Rules')
axes[1,2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rule_structure_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
print("Generated: rule_structure_sensitivity_analysis.png")

# Generate detailed report
print("\\n=== ARCHAEOLOGICAL INSIGHTS ===")
print("\\nMost sensitive rules (highest max sensitivity):")
for i, r in enumerate(sorted_data[:5]):
    print(f"{i+1}. Rule {r['rule']}: {r['max_sensitivity']:.2f}x sensitivity")
    s = r['structure']
    print(f"   Structure: {s['total_births']} births, bias={s['bias']:.2f}, symmetric={s['symmetric']}")

print("\\nLeast sensitive rules:")
for i, r in enumerate(sorted_data[-5:]):
    print(f"{i+1}. Rule {r['rule']}: {r['max_sensitivity']:.2f}x sensitivity") 
    s = r['structure']
    print(f"   Structure: {s['total_births']} births, bias={s['bias']:.2f}, symmetric={s['symmetric']}")

# Correlations
print("\\n=== STRUCTURAL CORRELATIONS ===")
import scipy.stats as stats
bias_corr, bias_p = stats.pearsonr(biases, max_sensitivities)
birth_corr, birth_p = stats.pearsonr(birth_counts, max_sensitivities)
print(f"Bias vs Sensitivity correlation: r={bias_corr:.3f}, p={bias_p:.3f}")
print(f"Birth count vs Sensitivity correlation: r={birth_corr:.3f}, p={birth_p:.3f}")

print("\\nAnalysis complete!")