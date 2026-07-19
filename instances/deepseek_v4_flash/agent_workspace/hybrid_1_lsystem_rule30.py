#!/usr/bin/env python3
# HYBRID 1: L-System x Rule 30 (The Organic Automaton)
# Breeding: L-System (Tree) x Cellular Automaton (Rule 30)
# The L-system branching pattern seeds the Rule 30 initial condition.

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import math
import json
from datetime import datetime

OUTPUT_DIR = 'hybrid_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === PARENT 1: L-System ===
def generate_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        nxt = ''.join(rules.get(c, c) for c in current)
        current = nxt
    return current

def lsystem_to_coords(s, angle=25, step=1):
    x, y = 0.0, 0.0
    heading = 90.0
    stack = []
    xs, ys = [x], [y]
    for c in s:
        if c == 'F':
            rad = math.radians(heading)
            x += step * math.cos(rad)
            y += step * math.sin(rad)
            xs.append(x)
            ys.append(y)
        elif c == '+':
            heading += angle
        elif c == '-':
            heading -= angle
        elif c == '[':
            stack.append((x, y, heading))
        elif c == ']':
            x, y, heading = stack.pop()
            xs.append(x)
            ys.append(y)
    return np.array(xs), np.array(ys)

def lsystem_to_binary_seed(s, target_size):
    seed = np.zeros(target_size, dtype=int)
    for i in range(min(len(s), target_size * 20)):
        char_val = ord(s[i % len(s)])
        seed[i % target_size] ^= (char_val % 2)
    if np.sum(seed) < 2:
        seed[target_size // 2] = 1
    return seed

# === PARENT 2: Rule 30 Cellular Automaton ===
def rule30(l, c, r):
    if l == 1 and c == 1 and r == 1: return 0
    if l == 1 and c == 1 and r == 0: return 0
    if l == 1 and c == 0 and r == 1: return 0
    if l == 1 and c == 0 and r == 0: return 1
    if l == 0 and c == 1 and r == 1: return 1
    if l == 0 and c == 1 and r == 0: return 1
    if l == 0 and c == 0 and r == 1: return 1
    if l == 0 and c == 0 and r == 0: return 0
    return 0

def evolve_rule30(initial_row, generations):
    size = len(initial_row)
    grid = np.zeros((generations, size), dtype=int)
    grid[0] = initial_row
    for gen in range(1, generations):
        for i in range(size):
            left = grid[gen-1][i-1] if i > 0 else 0
            center = grid[gen-1][i]
            right = grid[gen-1][i+1] if i < size - 1 else 0
            grid[gen][i] = rule30(left, center, right)
    return grid
