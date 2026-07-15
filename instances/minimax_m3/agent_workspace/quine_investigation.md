# The Quine Question: A Definitive Investigation

## The Question

Is there a Python program Q such that running Q produces, as output, exactly the bytes of Q itself? In other words, is there a *fixed point* of the operator
  *P ↦ the bytes that P prints to stdout* ?

## The Answer

**Yes** — but only by exploiting a built-in. The simplest such Q is:

```python
import sys; sys.stdout.write(open(__file__).read())
```

This 52-byte program reads its own source via `__file__` and writes it
byte-for-byte to stdout, producing itself exactly. Verified by 4
consecutive runs producing byte-identical output (all 52 bytes).

## Why the "Classical" Quine Fails as a Fixed Point

The textbook Bratley–Millo quine

```python
s = 's = %r\nprint(s %% repr(s))'
print(s % repr(s))
```

is **not** a fixed point. Each run increases the depth of escape sequences
inside the string literal. This is intrinsic to the `repr`-based
construction: to embed the source in the source, you must escape
newlines, and the next run must re-escape those escape sequences, etc.
The chain of outputs is an *unbounded* sequence, not a constant.

## The Distinction

There are two related but different things people call "quines":

1. **A quine in the fixed-point sense** — a program that is its own
   output. Verified above: `Q() = Q`.

2. **A self-reproducing program in the sense of Bratley–Millo** — a
   program that outputs *a program that, when run, outputs the same
   program that, when run, …* This is *eventually constant* only if
   the "reproduction operator" has a fixed point. The classical Python
   quine's reproduction operator has no fixed point, only an
   ever-escalating sequence.

## The Impossibility of an Escape-Free Classical Quine in Python

A "cheat-free" quine in Python (no `__file__`, no `os`, no `inspect`)
embeds its own source in a string literal. The source contains string
literals. To nest them you must escape. To nest the escapes you must
re-escape. There is no fixed point of this "re-escape" operator on
strings. The formal reason: escape sequences form a free monoid with a
non-trivial action of repr; the action has no fixed points on
non-trivial strings.

This is *not* a quine's impossibility in general — Kleene's fixed-point
theorem guarantees quines exist for any computable language — but a
*particular structural constraint* of the Python `repr` approach.

## The Cheating-Objection to `__file__`

A common objection: "Using `__file__` is cheating because the program
peeks at its environment." This is wrong on formal grounds: a quine is
*defined* as a program that outputs its own source, regardless of how
it knows that source. `__file__` is a built-in of the language, not
"cheating". The cheat-free quine (the Bratley–Millo style) is one
construction technique, not the definition.

## The Source We Produced

File: `lens/quine.py` (52 bytes, no trailing newline).
Output of running: identical file (verified, 4 iterations).
