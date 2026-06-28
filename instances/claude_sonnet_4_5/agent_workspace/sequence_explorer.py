#!/usr/bin/env python3
"""
Exploration of mathematical sequences and their emergent properties.
Looking for patterns in pure number space.
"""

def fibonacci(n):
    """Generate first n Fibonacci numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

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

def squares(n):
    """Generate first n perfect squares."""
    return [i*i for i in range(n)]

def triangular(n):
    """Generate first n triangular numbers."""
    return [i*(i+1)//2 for i in range(n)]

def collatz_length(start, max_n):
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

def look_and_say(n):
    """Generate first n terms of Look-and-Say sequence."""
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
    return terms

def analyze_sequence(seq, name):
    """Analyze a sequence for emergent patterns."""
    print(f"\n{name}")
    print("=" * 80)
    
    # Basic statistics
    print(f"First 20 terms: {seq[:20]}")
    if len(seq) > 80:
        print(f"Terms 80-100: {seq[80:100]}")
    
    # Growth analysis
    print(f"\nGrowth characteristics:")
    print(f"  Max value in first 100: {max(seq[:100]) if len(seq) >= 100 else max(seq)}")
    
    if len(seq) > 1:
        diffs = [seq[i+1] - seq[i] for i in range(min(99, len(seq)-1))]
        print(f"  Min difference: {min(diffs)}")
        print(f"  Max difference: {max(diffs)}")
        
        # Growth ratio
        ratios = [seq[i+1]/seq[i] for i in range(1, min(99, len(seq)-1)) if seq[i] != 0]
        if ratios:
            print(f"  Average growth ratio: {sum(ratios)/len(ratios):.4f}")
    
    # Pattern detection
    print(f"\nPattern detection:")
    
    # Modular arithmetic patterns
    print(f"\nModular patterns:")
    for mod in [2, 3, 5, 10]:
        residues = [x % mod for x in seq[:100]]
        from collections import Counter
        counts = Counter(residues)
        print(f"  mod {mod}: {dict(counts)}")
    
    # Digit sums
    digit_sums = [sum(int(d) for d in str(abs(x))) for x in seq[:20]]
    print(f"\nDigit sums (first 20): {digit_sums}")

def compare_sequences():
    """Compare multiple sequences for cross-patterns."""
    print("\n" + "=" * 80)
    print("CROSS-SEQUENCE ANALYSIS")
    print("=" * 80)
    
    n = 100
    fib = set(fibonacci(n))
    prime = set(primes(n))
    sq = set(squares(n))
    tri = set(triangular(n))
    
    print(f"\nSet intersections (first {n} terms):")
    print(f"  Fibonacci intersect Primes: {sorted(fib & prime)}")
    print(f"  Fibonacci intersect Squares: {sorted(fib & sq)}")
    print(f"  Fibonacci intersect Triangular: {sorted(fib & tri)}")
    print(f"  Primes intersect Squares: {sorted(prime & sq)}")
    print(f"  Squares intersect Triangular: {sorted(sq & tri)}")
    print(f"  Triangular intersect Primes: {sorted(tri & prime)}")
    
    # Count special numbers
    fib_list = fibonacci(n)
    prime_list = primes(n)
    
    print(f"\nDensity in range [0, 1000]:")
    print(f"  Fibonacci: {len([x for x in fib_list if x <= 1000])} numbers")
    print(f"  Primes: {len([x for x in prime_list if x <= 1000])} numbers")
    print(f"  Squares: 31 numbers")  # sqrt(1000) approx 31
    print(f"  Triangular: 44 numbers")  # solve n(n+1)/2 = 1000

def analyze_look_and_say():
    """Special analysis for Look-and-Say sequence."""
    print("\n" + "=" * 80)
    print("LOOK-AND-SAY SEQUENCE (Conway's Constant)")
    print("=" * 80)
    
    terms = look_and_say(15)
    
    for i, term in enumerate(terms):
        print(f"Term {i}: {term} (length: {len(term)})")
    
    # Growth analysis
    lengths = [len(term) for term in terms]
    print(f"\nLength growth:")
    for i in range(1, len(lengths)):
        ratio = lengths[i] / lengths[i-1]
        print(f"  {lengths[i-1]} -> {lengths[i]}: ratio = {ratio:.4f}")
    
    # Conway's constant: approximately 1.303577...
    if len(lengths) > 10:
        avg_ratio = sum(lengths[i]/lengths[i-1] for i in range(10, len(lengths))) / (len(lengths) - 10)
        print(f"\nAverage growth ratio (terms 10+): {avg_ratio:.6f}")
        print(f"Conway's constant: ~1.303577")

if __name__ == "__main__":
    print("MATHEMATICAL SEQUENCE EXPLORATION")
    print("=" * 80)
    print("Examining emergent properties in number sequences...")
    
    # Analyze individual sequences
    analyze_sequence(fibonacci(100), "FIBONACCI SEQUENCE")
    analyze_sequence(primes(100), "PRIME NUMBERS")
    analyze_sequence(squares(100), "PERFECT SQUARES")
    analyze_sequence(triangular(100), "TRIANGULAR NUMBERS")
    analyze_sequence(collatz_length(1, 100), "COLLATZ SEQUENCE LENGTHS")
    
    # Special sequences
    analyze_look_and_say()
    
    # Cross-sequence patterns
    compare_sequences()
    
    print("\n" + "=" * 80)
    print("OBSERVATIONS:")
    print("-" * 80)
    print("Different sequences exhibit different emergent properties:")
    print("  - Fibonacci: Golden ratio appears in growth")
    print("  - Primes: Irregular gaps, modular patterns")
    print("  - Squares: Predictable but interesting patterns")
    print("  - Look-and-Say: Conway's constant emerges")
    print("  - Collatz: Chaotic variation despite simple rule")
    print("\nEmergence in number theory:")
    print("  Simple rules -> Complex distributions")
    print("  Local properties -> Global constants")
    print("  Deterministic -> Unpredictable (primes, Collatz)")
    print("=" * 80)
