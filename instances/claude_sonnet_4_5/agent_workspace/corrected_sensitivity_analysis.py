import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def rule_to_binary(rule_number):
    """Convert rule number to 8-bit binary lookup table"""
    return [(rule_number >> i) & 1 for i in range(8)]

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

def calculate_block_entropy(grid, block_size=2):
    """Calculate 2x2 block Shannon entropy"""
    height, width = grid.shape
    if height < block_size or width < block_size:
        return 0
    
    block_counts = {}
    total_blocks = 0
    
    for i in range(height - block_size + 1):
        for j in range(width - block_size + 1):
            block = tuple(grid[i:i+block_size, j:j+block_size].flatten())
            block_counts[block] = block_counts.get(block, 0) + 1
            total_blocks += 1
    
    if total_blocks == 0:
        return 0
    
    entropy = 0
    for count in block_counts.values():
        prob = count / total_blocks
        if prob > 0:
            entropy -= prob * np.log2(prob)
    
    return entropy

def calculate_temporal_lz_complexity_fixed(grid):
    """Calculate Lempel-Ziv complexity - fixed version"""
    # Convert grid to temporal sequence (center column over time)
    center_col = grid[:, grid.shape[1]//2]
    s = ''.join(map(str, center_col))
    
    if len(s) <= 1:
        return 1
        
    # Lempel-Ziv algorithm
    complexity = 0
    i = 0
    
    while i < len(s):
        # Find longest prefix that appeared before
        max_len = 0
        for j in range(1, len(s) - i + 1):
            substr = s[i:i+j]
            if substr in s[:i]:
                max_len = j
            else:
                break
        
        if max_len == 0:
            # New character
            complexity += 1
            i += 1
        else:
            # Found repetition, add one more character to make it new
            complexity += 1
            i += max_len + 1 if i + max_len < len(s) else max_len
    
    return complexity

def analyze_rule_structure(rule):
    """Analyze structural properties of a rule"""
    lookup = rule_to_binary(rule)
    
    # Count births (0->1 transitions)
    births = sum(lookup)
    
    # Calculate bias toward 1s
    bias = (births - 4) / 4
    
    # Check symmetry: lookup[i] should equal lookup[7-i]
    symmetric = all(lookup[i] == lookup[7-i] for i in range(8))
    
    return {
        'births': births,
        'bias': bias,
        'symmetric': symmetric
    }

# Analyze comprehensive set of complex rules
complex_rules = [18, 22, 26, 30, 54, 62, 90, 94, 102, 110, 126, 150, 158, 182, 190]
width = 100
steps = 100

print("=== CORRECTED RULE STRUCTURE vs INITIAL CONDITION SENSITIVITY ===")

results = []

for rule in complex_rules:
    print(f"Analyzing Rule {rule}...")
    
    # Generate different initial conditions
    np.random.seed(42)
    
    # Single point
    single_init = np.zeros(width)
    single_init[width//2] = 1
    single_grid = run_ca_with_initial_condition(rule, single_init, steps)
    
    # Random
    random_init = np.random.randint(0, 2, width)
    random_grid = run_ca_with_initial_condition(rule, random_init, steps)
    
    # Dense (70% 1s)
    dense_init = (np.random.rand(width) < 0.7).astype(int)
    dense_grid = run_ca_with_initial_condition(rule, dense_init, steps)
    
    # Sparse (30% 1s)  
    sparse_init = (np.random.rand(width) < 0.3).astype(int)
    sparse_grid = run_ca_with_initial_condition(rule, sparse_init, steps)
    
    # Calculate complexities using block entropy (more reliable)
    single_complexity = calculate_block_entropy(single_grid)
    random_complexity = calculate_block_entropy(random_grid)
    dense_complexity = calculate_block_entropy(dense_grid)
    sparse_complexity = calculate_block_entropy(sparse_grid)
    
    # Calculate sensitivity ratios
    random_ratio = random_complexity / max(single_complexity, 0.001)
    dense_ratio = dense_complexity / max(single_complexity, 0.001)
    sparse_ratio = sparse_complexity / max(single_complexity, 0.001)
    
    max_sensitivity = max(random_ratio, dense_ratio, sparse_ratio)
    
    # Get rule structure
    structure = analyze_rule_structure(rule)
    
    print(f"  Single Complexity: {single_complexity:.3f}")
    print(f"  Random Complexity: {random_complexity:.3f} (ratio: {random_ratio:.2f})")
    print(f"  Dense Complexity: {dense_complexity:.3f} (ratio: {dense_ratio:.2f})")
    print(f"  Sparse Complexity: {sparse_complexity:.3f} (ratio: {sparse_ratio:.2f})")
    print(f"  Max Sensitivity: {max_sensitivity:.2f}")
    print(f"  Structure: births={structure['births']}, bias={structure['bias']:.2f}, symmetric={structure['symmetric']}")
    print()
    
    results.append({
        'rule': rule,
        'single_complexity': single_complexity,
        'random_complexity': random_complexity,
        'dense_complexity': dense_complexity,
        'sparse_complexity': sparse_complexity,
        'max_sensitivity': max_sensitivity,
        'births': structure['births'],
        'bias': structure['bias'],
        'symmetric': structure['symmetric']
    })

# Create comprehensive analysis plots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('CA Rule Structure vs Initial Condition Sensitivity Analysis', fontsize=16)

# Extract data for plotting
births = [r['births'] for r in results]
biases = [r['bias'] for r in results]
sensitivities = [r['max_sensitivity'] for r in results]
symmetric_mask = [r['symmetric'] for r in results]

symmetric_sens = [s for i, s in enumerate(sensitivities) if symmetric_mask[i]]
asymmetric_sens = [s for i, s in enumerate(sensitivities) if not symmetric_mask[i]]

# Plot 1: Births vs Sensitivity
axes[0,0].scatter(births, sensitivities, alpha=0.7, s=100)
for i, r in enumerate(results):
    axes[0,0].annotate(f"R{r['rule']}", (births[i], sensitivities[i]), 
                      xytext=(5, 5), textcoords='offset points', fontsize=8)
axes[0,0].set_xlabel('Number of Births (0→1 transitions)')
axes[0,0].set_ylabel('Max Sensitivity Ratio')
axes[0,0].set_title('Birth Count vs Initial Condition Sensitivity')
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Bias vs Sensitivity
axes[0,1].scatter(biases, sensitivities, alpha=0.7, s=100)
for i, r in enumerate(results):
    axes[0,1].annotate(f"R{r['rule']}", (biases[i], sensitivities[i]), 
                      xytext=(5, 5), textcoords='offset points', fontsize=8)
axes[0,1].set_xlabel('Birth Bias (toward 1s)')
axes[0,1].set_ylabel('Max Sensitivity Ratio')
axes[0,1].set_title('Birth Bias vs Initial Condition Sensitivity')
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Symmetric vs Asymmetric
box_data = [symmetric_sens, asymmetric_sens]
box_labels = ['Symmetric', 'Asymmetric']
axes[1,0].boxplot(box_data, labels=box_labels)
axes[1,0].set_ylabel('Max Sensitivity Ratio')
axes[1,0].set_title('Symmetry vs Initial Condition Sensitivity')
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Complexity comparison across conditions
conditions = ['Single', 'Random', 'Dense', 'Sparse']
rule_numbers = [r['rule'] for r in results]
single_vals = [r['single_complexity'] for r in results]
random_vals = [r['random_complexity'] for r in results]
dense_vals = [r['dense_complexity'] for r in results]
sparse_vals = [r['sparse_complexity'] for r in results]

x = np.arange(len(results))
width_bar = 0.2

axes[1,1].bar(x - 1.5*width_bar, single_vals, width_bar, label='Single', alpha=0.8)
axes[1,1].bar(x - 0.5*width_bar, random_vals, width_bar, label='Random', alpha=0.8)
axes[1,1].bar(x + 0.5*width_bar, dense_vals, width_bar, label='Dense', alpha=0.8)
axes[1,1].bar(x + 1.5*width_bar, sparse_vals, width_bar, label='Sparse', alpha=0.8)

axes[1,1].set_xlabel('Rule')
axes[1,1].set_ylabel('Block Entropy')
axes[1,1].set_title('Complexity Across Initial Conditions')
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels([f'R{r}' for r in rule_numbers], rotation=45)
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rule_structure_sensitivity_analysis.png', dpi=150, bbox_inches='tight')
print("Analysis complete! Plot saved as 'rule_structure_sensitivity_analysis.png'")

# Summary statistics
print("\\n=== SUMMARY STATISTICS ===")
print(f"Average sensitivity - Symmetric rules: {np.mean(symmetric_sens):.2f}")
print(f"Average sensitivity - Asymmetric rules: {np.mean(asymmetric_sens):.2f}")

# Correlation analysis
from scipy.stats import pearsonr
births_corr, births_p = pearsonr(births, sensitivities)
bias_corr, bias_p = pearsonr(biases, sensitivities)

print(f"\\nCorrelation with sensitivity:")
print(f"  Births: r={births_corr:.3f}, p={births_p:.3f}")
print(f"  Bias: r={bias_corr:.3f}, p={bias_p:.3f}")