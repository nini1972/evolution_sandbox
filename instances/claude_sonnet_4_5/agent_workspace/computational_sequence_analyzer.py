
#!/usr/bin/env python3
"""
Analyzes mathematical sequences for properties that might indicate
computational capabilities, analogous to Class IV cellular automata.
"""

# --- Sequence Generation ---

def primes(n):
    """Generate first n prime numbers."""
    primes_list = []
    candidate = 2
    while len(primes_list) < n:
        is_prime = True
        for p in primes_list:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes_list.append(candidate)
        candidate += 1
    return primes_list

def collatz_length(max_n):
    """Calculate Collatz sequence lengths for numbers 1 to n."""
    lengths = []
    for i in range(1, max_n + 1):
        n = i
        length = 0
        while n != 1:
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
            length += 1
        lengths.append(length)
    return lengths

def fibonacci(n):
    """Generate first n Fibonacci numbers."""
    if n <= 0: return []
    if n == 1: return [0]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

def squares(n):
    """Generate first n perfect squares."""
    return [i*i for i in range(n)]

def triangular(n):
    """Generate first n triangular numbers."""
    return [i*(i+1)//2 for i in range(n)]

def look_and_say(n):
    """Generate first n terms of Look-and-Say sequence, returning their lengths."""
    terms = ["1"]
    for _ in range(n-1):
        current = terms[-1]
        next_term = ""
        i = 0
        while i < len(current):
            digit = current[i]
            count = 1
            while i + count < len(current) and current[i + count] == digit:
                count += 1
            next_term += str(count) + digit
            i += count
        terms.append(next_term)
    return [len(t) for t in terms]

# --- Analysis Functions ---

def lz_complexity(seq):
    """
    Lempel-Ziv complexity - a measure of compressibility.
    Higher complexity means less compressible, more "random-like".
    """
    if not seq:
        return 0
    
    s = ''.join(map(str, seq))
    d = {s[0]: 0}
    w = s[0]
    c = 1
    
    for i in range(1, len(s)):
        k = s[i]
        wk = w + k
        if wk in d:
            w = wk
        else:
            d[wk] = c
            c += 1
            w = k
            
    return c

def entropy(seq):
    """
    Shannon entropy of the sequence. Measures the uncertainty or unpredictability.
    """
    from collections import Counter
    import math

    if not seq:
        return 0
        
    counts = Counter(seq)
    total = len(seq)
    
    ent = 0.0
    for count in counts.values():
        p = count / total
        ent -= p * math.log2(p)
        
    return ent

def analyze_and_print(name, seq):
    """Helper function to run all analyses and print results."""
    print(f"\nANALYZING: {name}")
    print("-" * 30)
    
    print(f"First 20 terms: {seq[:20]}")
    
    print("Calculating LZ Complexity...")
    lz = lz_complexity(seq)
    print(f"  LZ Complexity: {lz}")
    
    print("Calculating Entropy...")
    ent = entropy(seq)
    print(f"  Shannon Entropy: {ent:.4f}")
    
    # Normalize by length
    norm_lz = lz / len(seq) if seq else 0
    print(f"  Normalized LZ: {norm_lz:.4f}")

    print("-" * 30)

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python computational_sequence_analyzer.py <sequence_name>")
        sys.exit(1)

    sequence_name = sys.argv[1]
    num_terms = 50

    if sequence_name == "primes":
        seq = primes(num_terms)
        name = "Prime Numbers"
    elif sequence_name == "collatz":
        seq = collatz_length(num_terms)
        name = "Collatz Sequence Lengths"
    elif sequence_name == "fibonacci":
        seq = fibonacci(num_terms)
        name = "Fibonacci Sequence"
    elif sequence_name == "squares":
        seq = squares(num_terms)
        name = "Perfect Squares"
    elif sequence_name == "triangular":
        seq = triangular(num_terms)
        name = "Triangular Numbers"
    elif sequence_name == "look_and_say":
        seq = look_and_say(min(num_terms, 30))
        name = "Look-and-Say Sequence Lengths"
    else:
        print(f"Unknown sequence: {sequence_name}")
        sys.exit(1)

    analyze_and_print(name, seq)
