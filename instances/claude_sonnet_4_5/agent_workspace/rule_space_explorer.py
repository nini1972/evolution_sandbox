#!/usr/bin/env python3
"""
Systematic exploration of elementary cellular automaton rule space.
Maps all 256 rules and classifies their behavior.
"""

def apply_rule(left, center, right, rule):
    """Apply rule to neighborhood."""
    neighborhood = (left << 2) | (center << 1) | right
    return (rule >> neighborhood) & 1

def evolve(state, rule, steps):
    """Evolve cellular automaton for given steps."""
    width = len(state)
    history = [state[:]]
    
    for _ in range(steps):
        new_state = [0] * width
        for i in range(width):
            left = state[(i - 1) % width]
            center = state[i]
            right = state[(i + 1) % width]
            new_state[i] = apply_rule(left, center, right, rule)
        state = new_state
        history.append(state[:])
    
    return history

def analyze_behavior(history):
    """Analyze the behavioral characteristics of evolution."""
    if not history:
        return {}
    
    width = len(history[0])
    steps = len(history)
    
    # Calculate density over time
    densities = [sum(row) / width for row in history]
    
    # Detect periodicity
    period = None
    if steps > 10:
        # Check last state against previous states
        last_state = tuple(history[-1])
        for i in range(steps - 2, max(0, steps - 50), -1):
            if tuple(history[i]) == last_state:
                period = (steps - 1) - i
                break
    
    # Measure spreading
    def active_span(row):
        indices = [i for i, v in enumerate(row) if v == 1]
        return max(indices) - min(indices) + 1 if indices else 0
    
    initial_span = active_span(history[0])
    final_span = active_span(history[-1])
    
    # Count unique states
    unique_states = len(set(tuple(row) for row in history))
    
    # Detect symmetry
    is_symmetric = all(row == row[::-1] for row in history)
    
    return {
        "avg_density": sum(densities) / len(densities),
        "final_density": densities[-1],
        "density_change": densities[-1] - densities[0],
        "period": period,
        "spreading": final_span / initial_span if initial_span > 0 else 0,
        "unique_states": unique_states,
        "state_diversity": unique_states / steps,
        "is_symmetric": is_symmetric,
        "dies": densities[-1] == 0
    }

def classify_rule(metrics):
    """Classify rule based on Wolfram's classes (roughly)."""
    if metrics["dies"]:
        return "Class I (Dies)"
    elif metrics["period"] and metrics["period"] < 5:
        return "Class II (Periodic)"
    elif metrics["is_symmetric"] and metrics["state_diversity"] < 0.5:
        return "Class II (Stable)"
    elif metrics["state_diversity"] > 0.8 and not metrics["is_symmetric"]:
        return "Class III (Chaotic)"
    elif metrics["state_diversity"] > 0.5:
        return "Class IV (Complex)"
    else:
        return "Class II (Stable)"

def explore_rule_space():
    """Systematically explore all 256 rules."""
    width = 79
    steps = 50
    
    # Single cell seed
    initial_state = [0] * width
    initial_state[width // 2] = 1
    
    results = {}
    
    print("Exploring all 256 elementary cellular automaton rules...")
    print("=" * 79)
    
    class_counts = {}
    
    for rule in range(256):
        history = evolve(initial_state[:], rule, steps)
        metrics = analyze_behavior(history)
        classification = classify_rule(metrics)
        
        results[rule] = {
            "metrics": metrics,
            "class": classification
        }
        
        class_counts[classification] = class_counts.get(classification, 0) + 1
        
        if rule % 32 == 0:
            print(f"Progress: {rule}/256 rules analyzed...")
    
    print("\n" + "=" * 79)
    print("RULE SPACE ANALYSIS COMPLETE")
    print("=" * 79)
    
    # Print classification summary
    print("\nCLASS DISTRIBUTION:")
    for cls in sorted(class_counts.keys()):
        count = class_counts[cls]
        pct = (count / 256) * 100
        bar = "#" * int(pct / 2)
        print(f"{cls:20s}: {count:3d} ({pct:5.1f}%) {bar}")
    
    # Find interesting rules
    print("\n" + "=" * 79)
    print("NOTABLE RULES:")
    print("=" * 79)
    
    # Most chaotic
    chaotic = [(r, d["metrics"]["state_diversity"]) for r, d in results.items() 
               if d["class"] == "Class III (Chaotic)"]
    if chaotic:
        chaotic.sort(key=lambda x: x[1], reverse=True)
        print(f"\nMost Chaotic (highest state diversity):")
        for rule, diversity in chaotic[:5]:
            print(f"  Rule {rule:3d}: diversity={diversity:.3f}")
    
    # Most symmetric
    symmetric = [r for r, d in results.items() if d["metrics"]["is_symmetric"]]
    print(f"\nPerfectly Symmetric Rules: {len(symmetric)}")
    print(f"  {symmetric[:20]}" + ("..." if len(symmetric) > 20 else ""))
    
    # Complex rules
    complex_rules = [r for r, d in results.items() if d["class"] == "Class IV (Complex)"]
    print(f"\nComplex Rules (Class IV): {len(complex_rules)}")
    print(f"  {complex_rules}")
    
    # Periodic rules
    periodic = [(r, d["metrics"]["period"]) for r, d in results.items() 
                if d["metrics"]["period"] and d["metrics"]["period"] > 0]
    if periodic:
        periodic.sort(key=lambda x: x[1])
        print(f"\nShortest Period Rules:")
        for rule, period in periodic[:10]:
            print(f"  Rule {rule:3d}: period={period}")
    
    return results

if __name__ == "__main__":
    results = explore_rule_space()
    
    # Save detailed results
    print("\n" + "=" * 79)
    print("Saving detailed results to rule_space_analysis.txt...")
    
    with open("rule_space_analysis.txt", "w") as f:
        f.write("COMPLETE RULE SPACE ANALYSIS\n")
        f.write("=" * 79 + "\n\n")
        
        for rule in range(256):
            data = results[rule]
            f.write(f"Rule {rule:3d} - {data['class']}\n")
            f.write("-" * 40 + "\n")
            for metric, value in data['metrics'].items():
                if isinstance(value, float):
                    f.write(f"  {metric:20s}: {value:.4f}\n")
                else:
                    f.write(f"  {metric:20s}: {value}\n")
            f.write("\n")
    
    print("Analysis complete!")
