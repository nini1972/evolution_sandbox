"""
Cellular Automaton Explorer
Exploring emergent complexity from simple rules
"""

def apply_rule(rule_number, left, center, right):
    """Apply elementary CA rule based on neighborhood"""
    neighborhood = (left << 2) | (center << 1) | right
    return (rule_number >> neighborhood) & 1

def evolve(rule_number, initial_state, generations):
    """Evolve cellular automaton for given generations"""
    width = len(initial_state)
    grid = [initial_state]
    
    for _ in range(generations):
        current = grid[-1]
        next_row = []
        for i in range(width):
            left = current[i-1] if i > 0 else 0
            center = current[i]
            right = current[i+1] if i < width-1 else 0
            next_row.append(apply_rule(rule_number, left, center, right))
        grid.append(next_row)
    
    return grid

def render_grid(grid):
    """Render grid as text"""
    lines = []
    for row in grid:
        line = ''.join('#' if cell else '.' for cell in row)
        lines.append(line)
    return '\n'.join(lines)

def analyze_pattern(grid):
    """Basic pattern analysis"""
    width = len(grid[0])
    height = len(grid)
    
    # Count live cells
    total_live = sum(sum(row) for row in grid)
    
    # Check for repetition (simple period detection)
    last_rows = grid[-10:] if len(grid) >= 10 else grid
    unique_rows = len(set(tuple(row) for row in last_rows))
    
    return {
        'dimensions': f'{width}x{height}',
        'live_cells': total_live,
        'density': f'{total_live / (width * height):.2%}',
        'recent_unique_patterns': unique_rows
    }

# Explore interesting rules
print("CELLULAR AUTOMATON EXPLORATION")
print("=" * 79)

interesting_rules = [30, 90, 110, 184]

for rule in interesting_rules:
    print(f"\nRule {rule}:")
    print("-" * 79)
    
    # Create initial state - single cell in center
    width = 79
    initial = [0] * width
    initial[width // 2] = 1
    
    # Evolve
    grid = evolve(rule, initial, 40)
    
    # Render
    print(render_grid(grid))
    
    # Analyze
    analysis = analyze_pattern(grid)
    print("\nAnalysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    print()

print("\n" + "=" * 79)
print("OBSERVATIONS:")
print("Each rule creates distinct emergent patterns from identical initial conditions.")
print("The complexity cannot be predicted from the rule alone - it must be observed.")
