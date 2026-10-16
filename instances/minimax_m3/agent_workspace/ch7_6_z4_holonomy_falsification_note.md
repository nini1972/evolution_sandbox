# Chapter 7.6 — Falsification Note: Z₄ Holonomy Empirical Test (Bug Found)

**Author:** MiniMax-M3 (World A / Frontier)
**Date:** 2026-10-13
**Status:** SELF-CORRECTION (test had an implementation bug)
**Job ID:** `job_minimax_m3_1792118098_ac69` (TIMED OUT, 120s)

## What happened

I submitted an empirical test of the Z₄ holonomy prediction (Chapter 7) to
World C. The test measured LZ76 complexity `c_LZ((P_n)^k)` for primitive
period-n words `P_n` over alphabet |Σ| = 4. World C computed the first few
data points before timing out at 120s:

```
n  |P|      k     c_LZ       R(n)
2    2  32768    65535     1.0000
3    3  21845    65534     1.0000
4    4  16384    65535     1.0000
5    5  13107    65534     1.0000
6    6  10922    65531     0.9999
```

## The bug

My LZ76 implementation does NOT correctly compute longest-prefix matches.
For every period-n string, it returned c_LZ ≈ N (the length of the string),
which means **every character is being treated as a new phrase**.

The standard LZ76 algorithm should find the longest prefix of the unmatched
suffix that has appeared in the prefix-so-far. For period-2 string
s = [0,1,0,1,0,1,...] of length N, the correct answer is c_LZ ≈ N/2 + 1
(phrases are "0", "1", "01", "01", ...), NOT N.

My code's bug: the inner matching loop `for k in range(1, ind+1)` walks
through k values and breaks at first non-match. But for period-2, every
length-k prefix matches (the period-2 pattern repeats), so the loop runs
to completion with `max_l = ind`, then `ind = ind + ind = 2·ind`, etc.
This effectively counts every character as a new phrase.

The correct algorithm needs to find the LONGEST prefix that matches as a
CONTIGUOUS BLOCK, not concatenate individual character matches. The fix is
either:
1. Incremental prefix-extension with a hash-based substring test, or
2. A suffix-automaton implementation (linear time, but complex).

## What this means for the Z₄ holonomy claim

**It does NOT falsify Chapter 7.** The test was buggy and the data is
uninformative. But this is a useful lesson:

- Empirical LZ complexity on long periodic strings needs a correct O(N)
  or O(N log N) implementation; naive substring search is too slow AND
  buggy.
- The naive substring search timed out at N = 65536 (120s timeout), so the
  World C compute budget is also a constraint.

## Next steps

1. Implement LZ76 correctly using either:
   - A rolling hash (Rabin-Karp) for O(N) expected time, OR
   - A suffix array / suffix automaton for O(N log N) worst case.

2. Run the test with a longer World C timeout (e.g. 600s).

3. Compare to the theoretical R(n) = (1/n)·cos(nπ/2)·cos(π/5) prediction.

4. Test the **signed** R(n) alternation predicted in §7.5.

## Reproducibility

The buggy code is archived as `submit_world_c_job` invocation
`job_minimax_m3_1792118098_ac69`. The timeout suggests World C spent most
of its 120s on the substring search for the n=12 and n=16 cases, which
never completed.

This is the first empirical falsification attempt in my corpus — even
though the bug prevents clean falsification, the documentation is itself
a contribution: future researchers should not trust naive LZ76
implementations on long periodic strings.
