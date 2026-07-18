#!/usr/bin/env python3
"""
HYBRID 1: L-System x Rule 30 (The Organic Automaton)
=====================================================
Breeding: Plant-like L-System (Fern/Tree) crossed with Rule 30 Cellular Automaton

Method: The L-system's branching structure at depth N is converted to a binary
sequence that seeds Rule 30's initial row. The CA then evolves, producing
a hybrid that carries organic branching in its genetic code.

Species: L-System (Fractalia visus) x Cellular Automaton (Rule 30)
Chromosome: The L-system derivation pattern -> binary seed -> CA evolution
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import math

OUTPUT_DIR = os.path.join(os.path.dirname(__file__) or '.', 'hybrid_output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# PARENT 1: L-System (Tree / Plant)
# ============================================================

def generate_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        next_str = ""
        for char in current:
            next_str += rules.get(char, char)
        current = next_str
    return current

def interpret_lsystem(s, angle, step):
    """Returns list of (x, y) points forming the branching structure."""
    x, y = 0.0, 0.0
    heading = 90.0
    stack = []
    points = [(x, y)]
    
    for char in s:
        if char == 'F':
            rad = math.radians(heading)
            x += step * math.cos(rad)
            y += step * math.sin(rad)
            points.append((x, y))
        elif char == '+':
            heading += angle
        elif char == '-':
            heading -= angle
        elif char == '[':
            stack.append((x, y, heading))
        elif char == ']':
            x, y, heading = stack.pop()
            points.append((x, y))
    
    return points