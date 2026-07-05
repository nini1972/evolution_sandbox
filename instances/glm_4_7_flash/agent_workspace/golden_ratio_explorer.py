#!/usr/bin/env python3
"""
Golden Ratio Exploration - The Eternal Proportion
Investigating the mathematical beauty that has guided architecture and art for millennia
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def golden_ratio_approximations(n=15):
    """
    Generate converging approximations to the golden ratio
    Using the continued fraction: φ = 1 + 1/(1 + 1/(1 + ...))
    """
    # Start with 1 instead of 0 to avoid division by zero
    ratios = [1]
    for _ in range(n):
        ratios.append(1 + 1/ratios[-1])
    return ratios

def visualize_golden_ratio():
    """
    Create a visualization showing how approximations converge to φ
    """
    print("Exploring the Golden Ratio...")
    print("A proportion that has appeared throughout nature and art")
    
    # Generate approximations
    approximations = golden_ratio_approximations(20)
    golden_ratio = approximations[-1]
    
    # Create visual representation with rectangles
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Part 1: Rectangle spiral
    a = 1.0  # Larger side
    b = 1.0 / golden_ratio  # Smaller side
    
    # Generate spiral of squares
    squares = []
    a_original = a
    b_original = b
    
    rectangles = []
    current_a = a
    current_b = b
    
    for i in range(8):
        rectangles.append((current_a, current_b))
        next_square = current_a
        current_a, current_b = max(current_a, current_b), min(current_a, current_b)
    
    # Draw rectangles
    x, y = -current_a, -current_a
    for width, height in rectangles:
        rect = patches.Rectangle((x, y), width, height, 
                                 edgecolor='gold', facecolor='none', linewidth=2)
        ax1.add_patch(rect)
        x += width
        if width > height:
            y += height
    
    ax1.set_xlim(-1, a_original + 1)
    ax1.set_ylim(-1, b_original + 1)
    ax1.set_aspect('equal')
    ax1.set_title(f'Golden Spiral\n{golden_ratio:.9f}')
    ax1.set_xlabel('Width')
    ax1.set_ylabel('Height')
    
    # Part 2: Convergence of approximations
    ax2.plot(range(len(approximations)), approximations, 'o-', color='deepskyblue', markersize=6)
    ax2.axhline(y=golden_ratio, color='gold', linestyle='--', linewidth=2, label='Golden Ratio φ')
    ax2.set_xlabel('Approximation Number')
    ax2.set_ylabel('Value')
    ax2.set_title('Convergence to Golden Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('golden_ratio_discovery.png', dpi=150, bbox_inches='tight')
    print("Visualization saved to 'golden_ratio_discovery.png'")
    
    return approximations, golden_ratio

if __name__ == "__main__":
    approximations, phi = visualize_golden_ratio()
    
    print(f"\nGolden Ratio Statistics:")
    print(f"φ = {phi:.9f}")
    print(f"Convergence achieved at {len(approximations)-1} iterations")
    
    # Calculate characteristics
    inverse_phi = 1/phi
    print(f"1/φ = {inverse_phi:.9f}")
    print(f"φ + 1 = {phi + 1:.9f}")
    print(f"φ × 1/φ = {(phi * inverse_phi):.9f}")
    
    print("\nThe Golden Ratio reveals:")
    print("- Universality: appears in biology (phyllotaxis), art (Parthenon), architecture (Notre Dame)")
    print("- Mathematical elegance: φ² = φ + 1")
    print("- Natural harmony: ratios that our eyes find pleasing")