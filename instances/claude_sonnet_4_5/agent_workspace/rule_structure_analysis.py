#!/usr/bin/env python3
"""
Analyze the bit-patterns of rules to find structural characteristics
that correlate with behavioral class.
"""

def rule_to_binary(rule):
    """Convert rule number to 8-bit lookup table."""
    return format(rule, '08b')

def analyze_rule_structure(rule):
    """Extract structural features from rule."""
    bits = rule_to_binary(rule)
    
    # Basic features
    num_ones = bits.count('1')
    density = num_ones / 8
    
    # Symmetry in the rule itself
    is_symmetric = (bits == bits[::-1])
    
    # Look for specific patterns
    # Conservation: does 000→0 and 111→1?
    conserves_extremes = (bits[0] == '0' and bits[7] == '1')
    
    # Check if rule preserves single cells
    # 010 → 1 means single cell persists
    preserves_single = (bits[5] == '1')  # bit 5 is 010
    
    # Totalistic property: does output depend only on count of 1s?
    # 001, 010, 100 should give same output
    neighborhood_counts = {
        0: [bits[0]],  # 000
        1: [bits[1], bits[2], bits[4]],  # 001, 010, 100
        2: [bits[3], bits[5], bits[6]],  # 011, 101, 110
        3: [bits[7]]   # 111
    }
    is_totalistic = all(len(set(outputs)) == 1 for outputs in neighborhood_counts.values())
    
    # XOR-like: alternating pattern
    # Rule 90 is 01011010
    has_alternation = sum(bits[i] != bits[i+1] for i in range(7))
    
    return {
        'bits': bits,
        'num_ones': num_ones,
        'density': density,
        'is_symmetric': is_symmetric,
        'conserves_extremes': conserves_extremes,
        'preserves_single': preserves_single,
        'is_totalistic': is_totalistic,
        'alternation_count': has_alternation
    }

def load_classifications():
    """Load the rule classifications from our analysis."""
    # Based on our exploration results
    classes = {
        'Class I (Dies)': [0, 7, 8, 19, 21, 23, 31, 32, 40, 55, 63, 64, 72, 87, 95, 96, 104, 
                          119, 127, 128, 136, 160, 168, 192, 200, 224, 232],
        'Class II (Periodic)': [1, 4, 5, 12, 29, 33, 36, 37, 44, 50, 51, 68, 71, 76, 77, 91, 94, 
                               100, 108, 109, 123, 132, 133, 140, 147, 151, 159, 164, 172, 178, 
                               179, 183, 191, 196, 201, 203, 204, 205, 207, 215, 217, 219, 221,
                               222, 223, 228, 233, 235, 236, 237, 239, 247, 249, 251, 253, 254, 255],
        'Class III (Chaotic)': [2, 3, 6, 9, 10, 11, 13, 14, 15, 16, 17, 20, 24, 25, 26, 27, 28, 30,
                               34, 35, 38, 39, 41, 42, 43, 45, 46, 47, 48, 49, 52, 53, 56, 57, 58,
                               59, 60, 61, 62, 65, 66, 67, 69, 70, 74, 75, 78, 79, 80, 81, 82, 83,
                               84, 85, 86, 88, 89, 92, 93, 97, 98, 99, 101, 102, 103, 106, 107,
                               110, 111, 112, 113, 114, 115, 116, 117, 118, 120, 121, 124, 125,
                               130, 131, 134, 135, 137, 138, 139, 141, 142, 143, 144, 145, 148,
                               149, 152, 153, 154, 155, 156, 157, 158, 162, 163, 166, 167, 169,
                               170, 171, 173, 174, 175, 176, 177, 180, 181, 184, 185, 186, 187,
                               188, 189, 190, 193, 194, 195, 197, 198, 199, 202, 206, 208, 209,
                               210, 211, 212, 213, 214, 216, 220, 225, 226, 227, 229, 230, 231,
                               234, 238, 240, 241, 242, 243, 244, 245, 246, 248, 252],
        'Class IV (Complex)': [18, 22, 73, 90, 105, 122, 126, 129, 146, 150, 161, 165, 182, 218, 250]
    }
    return classes

def analyze_class_characteristics():
    """Find structural features that characterize each class."""
    classes = load_classifications()
    
    print("STRUCTURAL ANALYSIS OF RULE CLASSES")
    print("=" * 80)
    print()
    
    for class_name, rules in classes.items():
        print(f"{class_name}: {len(rules)} rules")
        print("-" * 80)
        
        # Analyze all rules in this class
        features = [analyze_rule_structure(r) for r in rules]
        
        # Calculate statistics
        avg_density = sum(f['density'] for f in features) / len(features)
        num_symmetric = sum(f['is_symmetric'] for f in features)
        num_conserving = sum(f['conserves_extremes'] for f in features)
        num_preserving = sum(f['preserves_single'] for f in features)
        num_totalistic = sum(f['is_totalistic'] for f in features)
        avg_alternation = sum(f['alternation_count'] for f in features) / len(features)
        
        print(f"  Average bit density: {avg_density:.3f}")
        print(f"  Symmetric rules: {num_symmetric}/{len(rules)} ({100*num_symmetric/len(rules):.1f}%)")
        print(f"  Conserve extremes: {num_conserving}/{len(rules)} ({100*num_conserving/len(rules):.1f}%)")
        print(f"  Preserve single cell: {num_preserving}/{len(rules)} ({100*num_preserving/len(rules):.1f}%)")
        print(f"  Totalistic: {num_totalistic}/{len(rules)} ({100*num_totalistic/len(rules):.1f}%)")
        print(f"  Avg alternation: {avg_alternation:.2f}/7")
        print()
    
    # Deep dive into Class IV
    print("=" * 80)
    print("DETAILED ANALYSIS: CLASS IV (Complex) RULES")
    print("=" * 80)
    print()
    
    class_iv_rules = classes['Class IV (Complex)']
    for rule in class_iv_rules:
        features = analyze_rule_structure(rule)
        print(f"Rule {rule:3d}: {features['bits']}")
        print(f"         Symmetric: {features['is_symmetric']}, " +
              f"Totalistic: {features['is_totalistic']}, " +
              f"Density: {features['density']:.3f}")
        print(f"         Alternation: {features['alternation_count']}/7, " +
              f"Preserves single: {features['preserves_single']}, " +
              f"Conserves: {features['conserves_extremes']}")
        print()
    
    # Look for patterns in bit positions
    print("=" * 80)
    print("BIT POSITION ANALYSIS FOR CLASS IV")
    print("=" * 80)
    print()
    print("Neighborhood: 000 001 010 011 100 101 110 111")
    print("Bit position:  0   1   2   3   4   5   6   7")
    print("-" * 80)
    
    for rule in class_iv_rules:
        bits = rule_to_binary(rule)
        print(f"Rule {rule:3d}:     {' '.join(bits)}")
    
    print()
    print("Frequency of '1' at each position across Class IV rules:")
    bit_counts = [0] * 8
    for rule in class_iv_rules:
        bits = rule_to_binary(rule)
        for i, bit in enumerate(bits):
            if bit == '1':
                bit_counts[i] += 1
    
    print("Position:     ", end="")
    for i in range(8):
        print(f"{i:3d} ", end="")
    print()
    print("Count:        ", end="")
    for count in bit_counts:
        print(f"{count:3d} ", end="")
    print()
    print("Frequency:    ", end="")
    for count in bit_counts:
        print(f"{count/len(class_iv_rules):.2f} ", end="")
    print()
    print()
    
    # Compare to overall frequencies
    all_rules = sum(classes.values(), [])
    all_bit_counts = [0] * 8
    for rule in all_rules:
        bits = rule_to_binary(rule)
        for i, bit in enumerate(bits):
            if bit == '1':
                all_bit_counts[i] += 1
    
    print("Overall frequency across all rules:")
    print("Frequency:    ", end="")
    for count in all_bit_counts:
        print(f"{count/len(all_rules):.2f} ", end="")
    print()
    print()
    
    print("Class IV deviation from average:")
    print("Difference:   ", end="")
    for i in range(8):
        diff = (bit_counts[i]/len(class_iv_rules)) - (all_bit_counts[i]/len(all_rules))
        print(f"{diff:+.2f} ", end="")
    print()

if __name__ == "__main__":
    analyze_class_characteristics()
