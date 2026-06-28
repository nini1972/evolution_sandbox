#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L-System Explorer: Formal grammar systems that generate complexity through rewriting.
Explores how simple recursive rules create intricate structures.
"""

def apply_rules(string, rules):
    """Apply L-system rules to rewrite string."""
    return ''.join(rules.get(char, char) for char in string)

def evolve_lsystem(axiom, rules, iterations):
    """Evolve L-system for given number of iterations."""
    history = [axiom]
    current = axiom
    
    for _ in range(iterations):
        current = apply_rules(current, rules)
        history.append(current)
    
    return history

def analyze_growth(history):
    """Analyze growth patterns in L-system evolution."""
    lengths = [len(s) for s in history]
    ratios = []
    
    for i in range(1, len(lengths)):
        if lengths[i-1] > 0:
            ratios.append(lengths[i] / lengths[i-1])
    
    return lengths, ratios

def count_symbols(string):
    """Count occurrences of each symbol."""
    counts = {}
    for char in string:
        counts[char] = counts.get(char, 0) + 1
    return counts

def explore_classic_lsystems():
    """Explore well-known L-systems."""
    
    systems = {
        "Algae Growth": {
            "axiom": "A",
            "rules": {"A": "AB", "B": "A"},
            "description": "Models simple biological growth - Fibonacci sequence",
            "iterations": 8
        },
        "Binary Tree": {
            "axiom": "0",
            "rules": {"1": "11", "0": "1[0]0"},
            "description": "Fractal binary tree structure",
            "iterations": 5
        },
        "Cantor Set": {
            "axiom": "A",
            "rules": {"A": "ABA", "B": "BBB"},
            "description": "Generates Cantor set fractal",
            "iterations": 5
        },
        "Koch Curve": {
            "axiom": "F",
            "rules": {"F": "F+F-F-F+F"},
            "description": "Koch snowflake fractal curve",
            "iterations": 4
        },
        "Sierpinski Triangle": {
            "axiom": "F-G-G",
            "rules": {"F": "F-G+F+G-F", "G": "GG"},
            "description": "Generates Sierpinski triangle",
            "iterations": 5
        },
        "Dragon Curve": {
            "axiom": "FX",
            "rules": {"X": "X+YF+", "Y": "-FX-Y"},
            "description": "Heighway dragon fractal",
            "iterations": 6
        },
        "Hilbert Curve": {
            "axiom": "A",
            "rules": {"A": "-BF+AFA+FB-", "B": "+AF-BFB-FA+"},
            "description": "Space-filling Hilbert curve",
            "iterations": 4
        },
        "Penrose Tiling": {
            "axiom": "[X]++[X]++[X]++[X]++[X]",
            "rules": {
                "W": "YF++ZF----XF[-YF----WF]++",
                "X": "+YF--ZF[---WF--XF]+",
                "Y": "-WF++XF[+++YF++ZF]-",
                "Z": "--YF++++WF[+ZF++++XF]--XF"
            },
            "description": "Aperiodic Penrose tiling pattern",
            "iterations": 3
        }
    }
    
    print("L-SYSTEM EXPLORATION")
    print("="*80)
    print()
    
    results = {}
    
    for name, system in systems.items():
        print(f"{name}")
        print("-"*80)
        print(f"Description: {system['description']}")
        print(f"Axiom: {system['axiom']}")
        print(f"Rules: {system['rules']}")
        print()
        
        history = evolve_lsystem(
            system['axiom'],
            system['rules'],
            system['iterations']
        )
        
        lengths, ratios = analyze_growth(history)
        
        print("Growth Analysis:")
        print(f"{'Iter':<6} {'Length':<12} {'Growth':<10} {'Unique':<8} {'Details'}")
        print("-"*80)
        
        for i, string in enumerate(history):
            counts = count_symbols(string)
            growth = ratios[i-1] if i > 0 else 1.0
            details = ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()))
            print(f"{i:<6} {len(string):<12} {growth:<10.3f} {len(counts):<8} {details}")
        
        print()
        
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            print(f"Average growth ratio: {avg_ratio:.4f}")
            
            # Check if it approaches golden ratio
            if 1.6 < avg_ratio < 1.65:
                print(f"  (Fibonacci-like phi approx 1.618)")
        
        # Analyze complexity
        final_string = history[-1]
        final_counts = count_symbols(final_string)
        diversity = len(final_counts) / len(final_string) if len(final_string) > 0 else 0
        
        print(f"Final complexity:")
        print(f"  String length: {len(final_string)}")
        print(f"  Unique symbols: {len(final_counts)}")
        print(f"  Symbol diversity: {diversity:.4f}")
        
        # Check for self-similarity
        if len(final_string) > 10:
            substring = final_string[:len(final_string)//4]
            occurrences = final_string.count(substring)
            if occurrences > 1:
                print(f"  Self-similar: substring appears {occurrences} times")
        
        print()
        print()
        
        results[name] = {
            "lengths": lengths,
            "ratios": ratios,
            "avg_ratio": avg_ratio if ratios else 0,
            "final_length": len(final_string),
            "final_diversity": diversity
        }
    
    # Cross-system comparison
    print("="*80)
    print("COMPARATIVE ANALYSIS")
    print("="*80)
    print()
    
    print(f"{'System':<25} {'Avg Growth':<12} {'Final Len':<12} {'Diversity':<12}")
    print("-"*80)
    for name, data in results.items():
        print(f"{name:<25} {data['avg_ratio']:<12.4f} {data['final_length']:<12} {data['final_diversity']:<12.4f}")
    
    print()
    
    # Identify patterns
    print("Observations:")
    print()
    
    fastest_growth = max(results.items(), key=lambda x: x[1]['avg_ratio'])
    print(f"Fastest exponential growth: {fastest_growth[0]} (ratio: {fastest_growth[1]['avg_ratio']:.4f})")
    
    most_complex = max(results.items(), key=lambda x: x[1]['final_length'])
    print(f"Longest final string: {most_complex[0]} ({most_complex[1]['final_length']} symbols)")
    
    most_diverse = max(results.items(), key=lambda x: x[1]['final_diversity'])
    print(f"Highest symbol diversity: {most_diverse[0]} ({most_diverse[1]['final_diversity']:.4f})")
    
    print()

if __name__ == "__main__":
    explore_classic_lsystems()
